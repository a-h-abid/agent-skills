from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "abd-code-review" / "SKILL.md"
README = ROOT / "skills" / "abd-code-review" / "README.md"
CODEX = ROOT / "skills" / "abd-code-review" / "references" / "runtime-codex.md"
CLAUDE = ROOT / "skills" / "abd-code-review" / "references" / "runtime-claude-code.md"


class CodeReviewOrchestrationTests(unittest.TestCase):
    def test_readme_documents_adaptive_portable_delegation(self) -> None:
        text = README.read_text(encoding="utf-8").lower()

        self.assertIn("codex", text)
        self.assertIn("claude code", text)
        self.assertIn("adaptive", text)
        self.assertIn("without subagents", text)

    def test_readme_documents_host_prerequisites(self) -> None:
        text = " ".join(README.read_text(encoding="utf-8").lower().split())

        self.assertIn("host must be able to read repository files", text)
        self.assertIn("run normal git and verification commands", text)

    def test_core_routes_to_runtime_adapters_and_uses_portable_roles(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        for role in ("primary agent", "evidence scout", "reviewer worker"):
            self.assertIn(role, text.lower())
        self.assertIn("`references/runtime-codex.md`", text)
        self.assertIn("`references/runtime-claude-code.md`", text)
        self.assertIn("read exactly one", text.lower())
        self.assertNotIn("Explore subagents", text)
        self.assertNotIn("general-purpose reviewer subagents", text)

    def test_core_has_bounded_cost_aware_sizing(self) -> None:
        text = SKILL.read_text(encoding="utf-8").lower()

        self.assertRegex(text, r"small[^\n]*zero workers")
        self.assertRegex(text, r"medium[^\n]*zero or one evidence scout")
        self.assertIn("allocate by remaining worker capacity", text)
        self.assertIn("third", text)
        self.assertRegex(text, r"state its rationale in the allocation")
        self.assertIn("available worker capacity", text)

    def test_core_keeps_size_ceiling_precedence_and_covers_capacity_gaps(self) -> None:
        text = " ".join(SKILL.read_text(encoding="utf-8").lower().split())

        self.assertIn("ceilings remain binding even for high-risk changes", text)
        self.assertIn(
            "risk changes review depth and what the primary agent covers, not these ceilings",
            text,
        )
        self.assertRegex(text, r"small.*?zero workers")
        self.assertRegex(text, r"medium.*?zero or one evidence scout")
        self.assertIn("zero remaining worker slots", text)
        self.assertIn("complete the review inline", text)
        self.assertIn("one remaining worker slot", text)
        self.assertIn("one consolidated reviewer worker", text)
        self.assertIn("two remaining worker slots", text)
        self.assertIn("two reviewer workers; this is the default", text)
        self.assertIn("three or more remaining worker slots", text)
        self.assertIn("genuinely separate high-risk concern", text)
        self.assertIn("state its rationale", text)
        self.assertIn("never leave a high-risk slice unassigned", text)
        self.assertNotIn("cover its high-risk gap inline or disclose it", text)

    def test_codex_adapter_uses_fresh_context_and_shared_workspace_safety(self) -> None:
        text = " ".join(CODEX.read_text(encoding="utf-8").split())

        for tool in ("spawn_agent", "wait_agent"):
            self.assertIn(tool, text)
        self.assertIn('fork_turns="none"', text)
        self.assertIn("primary agent occupies", text.lower())
        self.assertIn("shared workspace", text.lower())
        self.assertIn("must not edit", text.lower())
        self.assertIn("must not spawn", text.lower())
        self.assertIsNone(
            re.search(r"\b(?:gpt|claude)-\d|\b(?:haiku|sonnet|opus)\b", text, re.IGNORECASE)
        )

    def test_every_orchestration_document_has_complete_workspace_contract(self) -> None:
        for path in (SKILL, CODEX, CLAUDE):
            with self.subTest(path=path.name):
                text = " ".join(path.read_text(encoding="utf-8").lower().split())
                self.assertIn(
                    "worker prompts restate applicable user and repository constraints",
                    text,
                )
                self.assertIn("must not edit files", text)
                self.assertIn("create artifacts", text)
                self.assertIn("change git state", text)
                self.assertIn("delegate", text)
                self.assertIn("discard its report", text)
                self.assertIn("disclose the mutation", text)
                self.assertIn("preserve user-owned changes", text)
                self.assertIn("cover the high-risk slice inline", text)

    def test_claude_adapter_preserves_native_worker_types(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("Explore", text)
        self.assertIn("general-purpose", text)
        self.assertIn("read-only", text.lower())
        self.assertIn("parallel", text.lower())
        self.assertIn("primary agent", text.lower())

    def test_every_orchestration_document_keeps_verdict_with_primary(self) -> None:
        for path in (SKILL, CODEX, CLAUDE):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("final verdict", text)
                self.assertIn("primary agent", text)


if __name__ == "__main__":
    unittest.main()
