"""Unit tests for Phase 3 AI agents (Test Coverage, Codebase Context)."""

from __future__ import annotations

from server.domains.agents.codebase_context import CodebaseContextAgent
from server.domains.agents.test_coverage import TestCoverageAgent
from server.domains.github.schemas import GitHubFileChange, PRDiffContext
from server.domains.memory.schemas import MemoryContextBundle, OrgMemoryResponse


def _sample_context() -> PRDiffContext:
    return PRDiffContext(
        repo_full_name="acme/api",
        pr_number=99,
        title="Add payment processor",
        description="Integrates Stripe payment intents.",
        author="developer",
        base_branch="main",
        head_branch="feature/payments",
        head_sha="1234567890",
        additions=80,
        deletions=5,
        changed_files_count=1,
        files=[
            GitHubFileChange(
                filename="src/payments.py",
                status="added",
                additions=80,
                deletions=5,
                patch="@@ -0,0 +1,10 @@\n+def charge_card(card_id):\n+    pass",
            )
        ],
        raw_diff="+def charge_card(card_id):\n+    pass",
    )


def test_test_coverage_agent_prompt_and_parse() -> None:
    agent = TestCoverageAgent()
    context = _sample_context()
    prompt = agent.build_user_prompt(context)
    assert "src/payments.py" in prompt
    assert "#99" in prompt

    parsed = agent.parse_output(
        {
            "findings": [
                {
                    "severity": "critical",
                    "category": "missing_tests",
                    "file_path": "src/payments.py",
                    "start_line": 1,
                    "end_line": 2,
                    "title": "Untested payment processing logic",
                    "description": "charge_card has no unit tests or mock coverage.",
                    "suggestion": "Add test_charge_card unit test.",
                }
            ]
        }
    )
    assert len(parsed.findings) == 1
    assert parsed.findings[0].category == "missing_tests"


def test_codebase_context_agent_prompt_and_parse() -> None:
    agent = CodebaseContextAgent()
    context = _sample_context()
    bundle = MemoryContextBundle(
        org_memories=[
            OrgMemoryResponse(
                id="1",
                organization_id="org-1",
                memory_type="standard",
                key="idempotency",
                value="All payment calls must support idempotency keys.",
                created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )
        ]
    )
    rag_snippets = ["def existing_payment_gateway():\n    return GatewayClient()"]

    prompt = agent.build_user_prompt(
        context,
        memory_bundle=bundle,
        rag_snippets=rag_snippets,
    )
    assert "idempotency" in prompt
    assert "existing_payment_gateway" in prompt

    parsed = agent.parse_output(
        {
            "findings": [
                {
                    "severity": "warning",
                    "category": "convention_breach",
                    "file_path": "src/payments.py",
                    "start_line": 1,
                    "title": "Missing Idempotency Key Parameter",
                    "description": "Payment function violates company idempotency standard.",
                    "suggestion": "Add idempotency_key: str parameter.",
                }
            ]
        }
    )
    assert len(parsed.findings) == 1
    assert parsed.findings[0].severity == "warning"
