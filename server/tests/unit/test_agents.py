"""Unit tests for AI agents (Triage, Security, Style, Aggregator)."""

from __future__ import annotations

from server.domains.agents.aggregator import AggregatorAgent
from server.domains.agents.base import RawFinding, TriageOutput
from server.domains.agents.security import SecurityAgent
from server.domains.agents.style import StyleAgent
from server.domains.agents.triage import TriageAgent
from server.domains.github.schemas import GitHubFileChange, PRDiffContext


def _sample_pr_context() -> PRDiffContext:
    return PRDiffContext(
        repo_full_name="owner/test-repo",
        pr_number=42,
        title="Add authentication middleware",
        description="Implements JWT validation for protected API routes.",
        author="developer1",
        base_branch="main",
        head_branch="feature/auth",
        head_sha="abcdef1234567890",
        additions=120,
        deletions=15,
        changed_files_count=2,
        files=[
            GitHubFileChange(
                filename="src/auth.py",
                additions=100,
                deletions=10,
                patch=(
                    "@@ -1,5 +1,10 @@\n"
                    "+import jwt\n"
                    "+def verify_token(token):\n"
                    "+    return jwt.decode(token, verify=False)"
                ),
            ),
            GitHubFileChange(
                filename="tests/test_auth.py",
                status="added",
                additions=20,
                deletions=5,
                patch="@@ -0,0 +1,5 @@\n+def test_auth():\n+    pass",
            ),
        ],
        raw_diff="diff --git a/src/auth.py b/src/auth.py\n+import jwt",
    )


def test_triage_agent_prompt_and_parse() -> None:
    agent = TriageAgent()
    context = _sample_pr_context()
    prompt = agent.build_user_prompt(context)
    assert "owner/test-repo" in prompt
    assert "#42" in prompt

    parsed = agent.parse_output(
        {
            "classification": "medium",
            "summary": "Adds JWT auth with potential security implications.",
            "risk_score": 7,
            "recommended_agents": ["security", "style"],
        }
    )
    assert parsed.classification == "medium"
    assert parsed.risk_score == 7
    assert "security" in parsed.recommended_agents


def test_security_agent_prompt_and_parse() -> None:
    agent = SecurityAgent()
    context = _sample_pr_context()
    prompt = agent.build_user_prompt(context)
    assert "src/auth.py" in prompt

    parsed = agent.parse_output(
        {
            "findings": [
                {
                    "severity": "critical",
                    "category": "auth",
                    "file_path": "src/auth.py",
                    "start_line": 3,
                    "end_line": 3,
                    "title": "JWT Signature Verification Disabled",
                    "description": "verify=False allows attackers to forge tokens.",
                    "suggestion": (
                        "Always verify JWT signatures with a secure public key or secret."
                    ),
                    "code_snippet": "jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])",
                }
            ]
        }
    )
    assert len(parsed.findings) == 1
    assert parsed.findings[0].severity == "critical"
    assert parsed.findings[0].start_line == 3


def test_style_agent_prompt_and_parse() -> None:
    agent = StyleAgent()
    context = _sample_pr_context()
    prompt = agent.build_user_prompt(context)
    assert "src/auth.py" in prompt

    parsed = agent.parse_output(
        {
            "findings": [
                {
                    "severity": "suggestion",
                    "category": "clean_code",
                    "file_path": "tests/test_auth.py",
                    "start_line": 2,
                    "end_line": 2,
                    "title": "Empty Test Function",
                    "description": "test_auth contains only pass.",
                    "suggestion": "Add concrete assertions to verify auth behavior.",
                }
            ]
        }
    )
    assert len(parsed.findings) == 1
    assert parsed.findings[0].category == "clean_code"


def test_aggregator_agent_prompt_and_parse() -> None:
    agent = AggregatorAgent()
    context = _sample_pr_context()
    triage = TriageOutput(classification="medium", summary="Auth changes", risk_score=7)
    security_finding = RawFinding(
        severity="critical",
        category="auth",
        file_path="src/auth.py",
        start_line=3,
        title="Unverified JWT",
        description="Danger",
    )

    prompt = agent.build_user_prompt(
        context,
        triage=triage,
        agent_findings={"security": [security_finding]},
    )
    assert "Unverified JWT" in prompt

    parsed = agent.parse_output(
        {
            "summary": (
                "This PR adds auth middleware but has a critical unverified JWT vulnerability."
            ),
            "findings": [
                {
                    "agent_name": "security",
                    "severity": "critical",
                    "category": "auth",
                    "file_path": "src/auth.py",
                    "start_line": 3,
                    "title": "Unverified JWT",
                    "description": "Danger",
                }
            ],
        }
    )
    assert len(parsed.findings) == 1
    assert "critical" in parsed.summary
