from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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

    def test_repository_has_one_git_root_on_main(self) -> None:
        nested = [path for path in ROOT.rglob(".git") if path != ROOT / ".git"]
        self.assertEqual(nested, [])
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(branch, "main")


if __name__ == "__main__":
    unittest.main()
