from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

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
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual((info.external_attr >> 16) & 0o777, 0o644)
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
            checksum_filenames = [line.split("  ", 1)[1] for line in checksum_lines]
            self.assertEqual(
                checksum_filenames,
                [
                    "abd-alpha-v1.2.3.skill",
                    "abd-beta-v1.2.3.skill",
                    "abd-skills-v1.2.3.zip",
                ],
            )
            self.assertEqual(len(checksum_filenames), len(set(checksum_filenames)))
            self.assertNotIn("SHA256SUMS", checksum_filenames)
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

    def test_dry_run_does_not_create_nested_output_parents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            output = root / "missing" / "nested" / "dist"

            artifacts = build_packages(root, output, "v1.0.0", dry_run=True)

            self.assertEqual(artifacts, [])
            self.assertFalse((root / "missing").exists())

    def test_replacement_failure_restores_existing_output_and_cleans_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            output = root / "dist"
            output.mkdir()
            (output / "last-good.txt").write_text("last good\n", encoding="utf-8")
            real_replace = __import__("os").replace

            def fail_stage_publish(source: Path, destination: Path) -> None:
                if Path(destination) == output and Path(source).name == "dist":
                    raise OSError("injected publish failure")
                real_replace(source, destination)

            with mock.patch("package_skills.os.replace", side_effect=fail_stage_publish):
                with self.assertRaisesRegex(OSError, "injected publish failure"):
                    build_packages(root, output, "v1.0.0")

            self.assertEqual((output / "last-good.txt").read_text(encoding="utf-8"), "last good\n")
            self.assertEqual(list(root.glob(".dist.backup-*")), [])

    def test_rejects_symlinked_source_outside_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            outside = root / "secret.txt"
            outside.write_text("secret\n", encoding="utf-8")
            link = root / "skills" / "abd-alpha" / "references" / "secret.md"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not supported")

            with self.assertRaisesRegex(PackagingError, "symlink.*references/secret.md"):
                build_packages(root, root / "dist", "v1.0.0")

            link.unlink()
            directory_link = root / "skills" / "abd-alpha" / "linked-references"
            directory_link.symlink_to(root / "skills" / "abd-alpha" / "references", target_is_directory=True)
            with self.assertRaisesRegex(PackagingError, "symlink.*linked-references"):
                build_packages(root, root / "dist", "v1.0.0")

    def test_validation_failure_does_not_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "alpha")
            output = root / "dist"

            with self.assertRaises(PackagingError):
                build_packages(root, output, "v1.0.0")

            self.assertFalse(output.exists())

    def test_excludes_bytecode_artifacts_from_archives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            skill = root / "skills" / "abd-alpha"
            cache = skill / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "x.cpython-312.pyc").write_bytes(b"\x00fake bytecode")
            (skill / "references" / "stale.pyo").write_bytes(b"\x00stale bytecode")
            output = root / "dist"

            build_packages(root, output, "v1.0.0")

            members: list[str] = []
            for archive_name in ("abd-alpha-v1.0.0.skill", "abd-skills-v1.0.0.zip"):
                with zipfile.ZipFile(output / archive_name) as archive:
                    members.extend(archive.namelist())
            forbidden = [
                name
                for name in members
                if "__pycache__" in name.split("/") or name.endswith((".pyc", ".pyo"))
            ]
            self.assertEqual(forbidden, [])

    def test_ignores_symlinks_inside_bytecode_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "abd-alpha")
            outside = root / "secret.txt"
            outside.write_text("secret\n", encoding="utf-8")
            cache = root / "skills" / "abd-alpha" / "__pycache__"
            cache.mkdir()
            try:
                (cache / "link.pyc").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not supported")

            build_packages(root, root / "dist", "v1.0.0")

            with zipfile.ZipFile(root / "dist" / "abd-alpha-v1.0.0.skill") as archive:
                self.assertEqual(
                    [name for name in archive.namelist() if "__pycache__" in name.split("/")],
                    [],
                )


if __name__ == "__main__":
    unittest.main()
