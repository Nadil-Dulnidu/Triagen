"""PullSense Server — GitHub: Async HTTP client for GitHub REST API."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from server.domains.github.auth import get_installation_token
from server.domains.github.schemas import (
    GitHubFileChange,
    GitHubPullRequest,
    PRDiffContext,
)
from server.infrastructure import get_logger

logger = get_logger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """Async client for interacting with the GitHub REST API on behalf of an installation."""

    def __init__(self, installation_id: int) -> None:
        self.installation_id = installation_id
        self._token: str | None = None

    async def _get_headers(self, accept: str = "application/vnd.github+json") -> dict[str, str]:
        token = await get_installation_token(self.installation_id)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "PullSense-AI-Reviewer",
        }

    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> GitHubPullRequest:
        """Fetch pull request metadata from GitHub."""
        headers = await self._get_headers()
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return GitHubPullRequest.model_validate(data)

    async def get_pull_request_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the unified diff of a pull request."""
        headers = await self._get_headers(accept="application/vnd.github.v3.diff")
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    async def get_pull_request_files(
        self, owner: str, repo: str, pr_number: int, per_page: int = 100
    ) -> list[GitHubFileChange]:
        """Fetch list of changed files in a pull request with their patches."""
        headers = await self._get_headers()
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        params = {"per_page": per_page}

        files: list[GitHubFileChange] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            page = 1
            while True:
                params["page"] = page
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for file_data in data:
                    files.append(GitHubFileChange.model_validate(file_data))

                if len(data) < per_page:
                    break
                page += 1

        return files

    async def get_file_content(
        self, owner: str, repo: str, file_path: str, ref: str = "main"
    ) -> str:
        """Fetch file content from GitHub at a specific commit SHA or branch ref."""
        headers = await self._get_headers()
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": ref}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("encoding") == "base64" and data.get("content"):
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return response.text

    async def get_full_pr_context(self, owner: str, repo: str, pr_number: int) -> PRDiffContext:
        """Fetch consolidated PR context (metadata, diff, files) for AI analysis."""
        pr = await self.get_pull_request(owner, repo, pr_number)
        raw_diff = await self.get_pull_request_diff(owner, repo, pr_number)
        files = await self.get_pull_request_files(owner, repo, pr_number)

        return PRDiffContext(
            repo_full_name=f"{owner}/{repo}",
            pr_number=pr_number,
            title=pr.title,
            description=pr.body or "",
            author=pr.user.login,
            base_branch=pr.base.ref,
            head_branch=pr.head.ref,
            head_sha=pr.head.sha,
            additions=pr.additions,
            deletions=pr.deletions,
            changed_files_count=len(files),
            files=files,
            raw_diff=raw_diff,
        )
