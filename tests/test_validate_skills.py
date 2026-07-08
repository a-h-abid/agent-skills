from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_skills import discover_skills, main, validate_collection  # noqa: E402


def write_skill(
    root: Path,
    name: str = "abd-example",
    declared_name: str | None = None,
    description: str = "An example skill.",
) -> Path:
    skill = root / "skills" / name
    skill.mkdir(parents=True)
    declared_name = declared_name or name
    (skill / "SKILL.md").write_text(
        f"---\nname: {declared_name}\ndescription: {description}\n---\n\n"
        "# Example\n\nRead `references/guide.md`.\n",
        encoding="utf-8",
    )
    (skill / "README.md").write_text("# Example\n", encoding="utf-8")
    (skill / "references").mkdir()
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return skill


class ValidateCollectionTests(unittest.TestCase):
    def test_accepts_a_valid_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root)

            self.assertEqual(validate_collection(root), [])

    def test_reports_collection_and_required_file_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = write_skill(root, name="example")
            (skill / "README.md").unlink()

            errors = validate_collection(root)

            self.assertTrue(any("must start with 'abd-'" in error for error in errors))
            self.assertTrue(any("README.md: missing" in error for error in errors))

    def test_reports_frontmatter_name_and_description_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, declared_name="abd-other", description="")

            errors = validate_collection(root)

            self.assertTrue(any("does not match directory" in error for error in errors))
            self.assertTrue(any("description" in error and "non-empty" in error for error in errors))

    def test_reports_quoted_empty_descriptions(self) -> None:
        for description in ('""', "''"):
            with self.subTest(description=description), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                write_skill(root, description=description)

                errors = validate_collection(root)

                self.assertTrue(any("description" in error and "non-empty" in error for error in errors))

    def test_reports_quoted_whitespace_descriptions(self) -> None:
        for description in ('"   "', "'   '"):
            with self.subTest(description=description), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                write_skill(root, description=description)

                errors = validate_collection(root)

                self.assertTrue(any("description" in error and "non-empty" in error for error in errors))

    def test_reports_unreadable_markdown_as_a_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = write_skill(root)
            (skill / "README.md").write_bytes(b"\xff")

            errors = validate_collection(root)

            self.assertTrue(any("skills/abd-example/README.md" in error and "expected" in error for error in errors))

    def test_discover_skills_sorts_and_excludes_hidden_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skills_root = Path(directory)
            for name in ("abd-zeta", ".hidden", "abd-alpha"):
                (skills_root / name).mkdir()
            (skills_root / "not-a-directory").write_text("", encoding="utf-8")

            discovered = discover_skills(skills_root)

            self.assertEqual([path.name for path in discovered], ["abd-alpha", "abd-zeta"])

    def test_main_reports_valid_and_invalid_collections_to_expected_streams(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid_root = Path(directory) / "valid"
            invalid_root = Path(directory) / "invalid"
            write_skill(valid_root)
            stdout, stderr = StringIO(), StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                valid_status = main(["--root", str(valid_root)])
                invalid_status = main(["--root", str(invalid_root)])

            self.assertEqual(valid_status, 0)
            self.assertEqual(invalid_status, 1)
            self.assertIn("Validated 1 skill(s).", stdout.getvalue())
            self.assertIn("ERROR: skills: missing or empty", stderr.getvalue())

    def test_reports_missing_and_escaping_resource_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = write_skill(root)
            (skill / "SKILL.md").write_text(
                "---\nname: abd-example\ndescription: Example.\n---\n\n"
                "Read `references/missing.md` and [outside](../../secret.md).\n",
                encoding="utf-8",
            )

            errors = validate_collection(root)

            self.assertTrue(any("references/missing.md" in error and "does not exist" in error for error in errors))
            self.assertTrue(any("../../secret.md" in error and "escapes skill directory" in error for error in errors))

    def test_reports_missing_or_empty_skills_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_collection(Path(directory))
            self.assertEqual(len(errors), 1)
            self.assertIn("skills", errors[0])


if __name__ == "__main__":
    unittest.main()
