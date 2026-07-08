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


class RepositoryLayoutTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for relative in REQUIRED:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_obsolete_paths_are_absent(self) -> None:
        for relative in OBSOLETE:
            with self.subTest(relative=relative):
                self.assertFalse((ROOT / relative).exists(), relative)

    def test_root_readme_catalog_links_to_skill_readme(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[abd-code-review](skills/abd-code-review/README.md)", readme)

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
