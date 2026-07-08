from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_skills import PackagingError, build_packages, normalize_version  # noqa: E402


def write_skill(root: Path, name: str) -> None:
    skill = root / "skills" / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test {name}.\n---\n\nRead `references/guide.md`.\n",
        encoding="utf-8",
    )
    (skill / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")


class PackageSkillsTests(unittest.TestCase):
    def test_normalizes_semantic_versions(self) -> None:
        self.assertEqual(normalize_version("1.2.3"), "v1.2.3")
        self.assertEqual(normalize_version("v1.2.3"), "v1.2.3")
        with self.assertRaises(PackagingError):
            normalize_version("1.2")

    def test_builds_expected_archive_layouts_and_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            write_skill(root, "abd-beta")
            output = root / "dist"

            artifacts = build_packages(root, output, "v1.2.3")

            self.assertEqual(
                [path.name for path in artifacts],
                [
                    "abd-alpha-v1.2.3.skill",
                    "abd-beta-v1.2.3.skill",
                    "abd-skills-v1.2.3.zip",
                    "SHA256SUMS",
                ],
            )
            with zipfile.ZipFile(output / "abd-alpha-v1.2.3.skill") as archive:
                self.assertEqual(
                    archive.namelist(),
                    [
                        "abd-alpha/README.md",
                        "abd-alpha/SKILL.md",
                        "abd-alpha/references/guide.md",
                    ],
                )
            with zipfile.ZipFile(output / "abd-skills-v1.2.3.zip") as archive:
                self.assertEqual(
                    archive.namelist(),
                    [
                        "skills/abd-alpha/README.md",
                        "skills/abd-alpha/SKILL.md",
                        "skills/abd-alpha/references/guide.md",
                        "skills/abd-beta/README.md",
                        "skills/abd-beta/SKILL.md",
                        "skills/abd-beta/references/guide.md",
                    ],
                )
            checksum_lines = (output / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
            for line in checksum_lines:
                digest, filename = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((output / filename).read_bytes()).hexdigest(), digest)

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            first = root / "first"
            second = root / "second"

            build_packages(root, first, "v2.0.0")
            build_packages(root, second, "v2.0.0")

            self.assertEqual(
                {path.name: path.read_bytes() for path in first.iterdir()},
                {path.name: path.read_bytes() for path in second.iterdir()},
            )

    def test_dry_run_verifies_without_publishing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            output = root / "dist"

            artifacts = build_packages(root, output, "v1.0.0", dry_run=True)

            self.assertEqual(artifacts, [])
            self.assertFalse(output.exists())

    def test_validation_failure_does_not_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "alpha")
            output = root / "dist"

            with self.assertRaises(PackagingError):
                build_packages(root, output, "v1.0.0")

            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
