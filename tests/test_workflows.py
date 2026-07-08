from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_ci_is_read_only_and_runs_all_structural_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("python3 scripts/validate_skills.py", workflow)
        self.assertIn("--version v0.0.0 --dry-run", workflow)

    def test_release_is_tag_only_and_uses_minimal_write_permission(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn("tags:", workflow)
        self.assertIn("'v*.*.*'", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("^v[0-9]+\\.[0-9]+\\.[0-9]+$", workflow)
        self.assertIn('package_skills.py --version "$GITHUB_REF_NAME" --output dist', workflow)
        self.assertIn('gh release create "$GITHUB_REF_NAME" dist/*', workflow)


if __name__ == "__main__":
    unittest.main()
