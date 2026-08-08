from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTABLE_ORCHESTRATION_PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-08-08-abd-code-review-portable-orchestration.md"
)
REQUIRED = (
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "skills/abd-code-review/SKILL.md",
    "skills/abd-code-review/README.md",
    "skills/abd-jira-cloud/SKILL.md",
    "skills/abd-jira-cloud/README.md",
    "skills/abd-jira-cloud/scripts/jira.py",
    "skills/abd-jira-cloud/references/api-notes.md",
)
OBSOLETE = (
    ".agents",
    ".codex",
    "abd-code-review",
    "abd-code-review-workspace",
    "abd-code-review.skill",
    "evals",
    "fixtures",
)


def tracked_paths() -> set[str]:
    output = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return set(output.splitlines())


class RepositoryLayoutTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for relative in REQUIRED:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_obsolete_paths_are_not_tracked(self) -> None:
        tracked = tracked_paths()
        for relative in OBSOLETE:
            with self.subTest(relative=relative):
                self.assertFalse(
                    any(path == relative or path.startswith(relative + "/") for path in tracked),
                    relative,
                )

    def test_root_readme_catalog_links_to_skill_readmes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[abd-code-review](skills/abd-code-review/README.md)", readme)
        self.assertIn("[abd-jira-cloud](skills/abd-jira-cloud/README.md)", readme)

    def test_repository_has_one_git_root(self) -> None:
        nested = [path for path in ROOT.rglob(".git") if path != ROOT / ".git"]
        self.assertEqual(nested, [])

    def test_portable_orchestration_file_map_authorizes_layout_correction(self) -> None:
        plan = PORTABLE_ORCHESTRATION_PLAN.read_text(encoding="utf-8")
        file_map = plan.split("## File Map", maxsplit=1)[1].split("---", maxsplit=1)[0]

        self.assertIn(
            "- Modify `tests/test_repository_layout.py`: make repository layout "
            "validation branch-neutral while preserving nested Git-root detection.",
            file_map,
        )


if __name__ == "__main__":
    unittest.main()
