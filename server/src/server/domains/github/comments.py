"""PullSense Server — GitHub: Review comment formatting and submission."""

from __future__ import annotations

from typing import Any

import httpx

from server.domains.github.auth import get_installation_token
from server.domains.github.schemas import GitHubReviewPayload, InlineComment
from server.domains.reviews.models import Review, ReviewFinding
from server.infrastructure import get_logger

logger = get_logger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def format_inline_comment(finding: ReviewFinding) -> str:
    """Format an individual finding into a clean GitHub inline Markdown comment."""
    severity_badges = {
        "critical": "🔴 **Critical Issue**",
        "warning": "🟡 **Warning**",
        "suggestion": "🟢 **Suggestion**",
        "info": "ℹ️ **Note**",
    }
    badge = severity_badges.get(finding.severity.lower(), "🔍 **Finding**")
    category = f"`{finding.category}`" if finding.category else f"`{finding.agent_name}`"

    lines = [
        f"{badge} • {category} • **{finding.title}**",
        "",
        finding.description,
    ]

    if finding.suggestion:
        lines.extend(
            [
                "",
                "**Suggested Fix:**",
                finding.suggestion,
            ]
        )

    if finding.code_snippet:
        snippet = finding.code_snippet.strip()
        # Check if the snippet contains placeholder ellipses or conceptual patterns
        is_placeholder = any(
            marker in snippet
            for marker in [
                "# ...",
                "// ...",
                "/* ... */",
                "... other",
                "// other",
                "# other",
                "... rest of",
                "// rest of",
                "# rest of",
            ]
        )
        if is_placeholder:
            # Render as illustrative code block to avoid broken GitHub one-click commits
            lang = ""
            if finding.file_path:
                ext = finding.file_path.split(".")[-1]
                lang_map = {
                    "py": "python",
                    "ts": "typescript",
                    "js": "javascript",
                    "go": "go",
                    "rs": "rust",
                }
                lang = lang_map.get(ext, "")
            lines.extend(
                [
                    "",
                    "**Example Code:**",
                    f"```{lang}",
                    snippet,
                    "```",
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "```suggestion",
                    snippet,
                    "```",
                ]
            )

    lines.extend(
        [
            "",
            "---",
            f"*Reported by PullSense `{finding.agent_name}` agent*",
        ]
    )

    return "\n".join(lines)


def format_review_summary(review: Review, findings: list[ReviewFinding]) -> str:
    """Format the overarching review summary body for the GitHub PR review."""
    classification = (review.triage_classification or "Standard").capitalize()

    # Count by severity
    critical_count = sum(1 for f in findings if f.severity == "critical")
    warning_count = sum(1 for f in findings if f.severity == "warning")
    suggestion_count = sum(1 for f in findings if f.severity == "suggestion")

    summary_lines = [
        "## 🤖 PullSense AI Code Review",
        "",
        f"**PR Classification:** `{classification}` | **Total Findings:** `{len(findings)}`",
        "",
        "| Severity | Count |",
        "|:---|:---|",
        f"| 🔴 Critical | {critical_count} |",
        f"| 🟡 Warning | {warning_count} |",
        f"| 🟢 Suggestion | {suggestion_count} |",
        "",
    ]

    if review.summary:
        summary_lines.extend(
            [
                "### Summary",
                review.summary,
                "",
            ]
        )

    if findings:
        summary_lines.append("### Key Findings")
        for idx, finding in enumerate(findings[:10], start=1):
            sev_icon = {"critical": "🔴", "warning": "🟡", "suggestion": "🟢"}.get(
                finding.severity, "ℹ️"
            )
            file_ref = f"`{finding.file_path}`" if finding.file_path else "general"
            summary_lines.append(f"{idx}. {sev_icon} **[{file_ref}]** {finding.title}")

        if len(findings) > 10:
            summary_lines.append(f"\n*...and {len(findings) - 10} more inline findings below.*")

    summary_lines.extend(
        [
            "",
            "---",
            "💡 *PullSense provides automated first-pass AI reviews. "
            "Reviewers should still verify critical paths.*",
        ]
    )

    return "\n".join(summary_lines)


async def post_github_review(
    installation_id: int,
    owner: str,
    repo: str,
    pr_number: int,
    commit_sha: str,
    review: Review,
    findings: list[ReviewFinding],
) -> int:
    """Post a formal PR Review with inline comments to GitHub via the Reviews API.

    Returns the created GitHub review ID.
    """
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PullSense-AI-Reviewer",
    }

    # Prepare inline comments
    inline_comments: list[InlineComment] = []
    for f in findings:
        if f.file_path and f.start_line is not None:
            inline_comments.append(
                InlineComment(
                    path=f.file_path,
                    line=f.start_line,
                    body=format_inline_comment(f),
                )
            )

    summary_body = format_review_summary(review, findings)

    payload = GitHubReviewPayload(
        commit_id=commit_sha,
        body=summary_body,
        event="COMMENT",  # Never APPROVE or REQUEST_CHANGES
        comments=inline_comments,
    )

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload.model_dump(exclude_none=True),
        )

        if not response.is_success:
            logger.error(
                "github_post_review_failed",
                status_code=response.status_code,
                response=response.text,
                pr_number=pr_number,
            )
            response.raise_for_status()

        data: dict[str, Any] = response.json()
        github_review_id = data.get("id", 0)
        logger.info(
            "github_review_posted",
            github_review_id=github_review_id,
            findings_count=len(findings),
            inline_count=len(inline_comments),
            pr_number=pr_number,
        )
        return int(github_review_id)
