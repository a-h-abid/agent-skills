#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import stat
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath

from validate_skills import discover_skills, validate_collection

VERSION = re.compile(r"^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class PackagingError(RuntimeError):
    pass


def normalize_version(value: str) -> str:
    match = VERSION.fullmatch(value)
    if not match:
        raise PackagingError(f"invalid version '{value}'; expected vMAJOR.MINOR.PATCH")
    return "v" + ".".join(match.groups())


def source_files(skill: Path) -> list[Path]:
    paths = list(skill.rglob("*"))
    for path in paths:
        if path.is_symlink():
            relative = path.relative_to(skill).as_posix()
            raise PackagingError(f"{skill.name}: symlink source is not allowed: {relative}")
    return sorted((path for path in paths if path.is_file()), key=lambda path: path.as_posix())


def write_archive(archive_path: Path, entries: list[tuple[str, Path]]) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for archive_name, source in sorted(entries, key=lambda entry: entry[0]):
            info = zipfile.ZipInfo(archive_name, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            executable = bool(source.stat().st_mode & stat.S_IXUSR)
            mode = 0o755 if executable else 0o644
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def expected_individual_entries(skill: Path) -> list[tuple[str, Path]]:
    return [
        ((PurePosixPath(skill.name) / source.relative_to(skill).as_posix()).as_posix(), source)
        for source in source_files(skill)
    ]


def expected_collection_entries(skills: list[Path]) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for skill in skills:
        entries.extend(
            (
                (PurePosixPath("skills") / skill.name / source.relative_to(skill).as_posix()).as_posix(),
                source,
            )
            for source in source_files(skill)
        )
    return entries


def verify_archive(path: Path, expected_names: list[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names != sorted(expected_names):
            raise PackagingError(f"{path.name}: archive layout mismatch")
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                raise PackagingError(f"{path.name}: unsafe archive member '{name}'")
            archive.read(name)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_packages(
    root: Path,
    output: Path,
    version: str,
    dry_run: bool = False,
) -> list[Path]:
    root = root.resolve()
    output = output.resolve()
    normalized = normalize_version(version)
    errors = validate_collection(root)
    if errors:
        raise PackagingError("validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    skills = discover_skills(root / "skills")
    if not dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)

    staging_parent = None if dry_run else output.parent
    with tempfile.TemporaryDirectory(prefix=".package-", dir=staging_parent) as temporary:
        stage = Path(temporary) / "dist"
        stage.mkdir()
        archive_paths: list[Path] = []

        for skill in skills:
            entries = expected_individual_entries(skill)
            archive_path = stage / f"{skill.name}-{normalized}.skill"
            write_archive(archive_path, entries)
            verify_archive(archive_path, [name for name, _ in entries])
            archive_paths.append(archive_path)

        collection_entries = expected_collection_entries(skills)
        collection_path = stage / f"abd-skills-{normalized}.zip"
        write_archive(collection_path, collection_entries)
        verify_archive(collection_path, [name for name, _ in collection_entries])
        archive_paths.append(collection_path)

        checksum_path = stage / "SHA256SUMS"
        checksum_path.write_text(
            "".join(f"{sha256(path)}  {path.name}\n" for path in sorted(archive_paths)),
            encoding="utf-8",
            newline="\n",
        )
        published_names = [path.name for path in archive_paths] + [checksum_path.name]
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            digest, filename = line.split("  ", 1)
            if sha256(stage / filename) != digest:
                raise PackagingError(f"{filename}: checksum verification failed")

        if dry_run:
            return []
        backup: Path | None = None
        if output.exists():
            backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
            os.replace(output, backup)
        try:
            os.replace(stage, output)
        except OSError:
            if backup is not None:
                os.replace(backup, output)
            raise
        if backup is not None:
            if backup.is_dir():
                shutil.rmtree(backup)
            else:
                backup.unlink()

    return [output / name for name in published_names]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the agent skill collection.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--output", type=Path, default=Path("dist"), help="Artifact directory")
    parser.add_argument("--version", required=True, help="vMAJOR.MINOR.PATCH")
    parser.add_argument("--dry-run", action="store_true", help="Build and verify without publishing artifacts")
    args = parser.parse_args(argv)
    output = args.output if args.output.is_absolute() else args.root / args.output
    try:
        artifacts = build_packages(args.root, output, args.version, args.dry_run)
    except (OSError, PackagingError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("Packaging dry run passed.")
    else:
        for artifact in artifacts:
            print(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
