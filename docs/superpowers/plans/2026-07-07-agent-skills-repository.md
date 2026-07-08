# Agent Skills Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the current project into an agent-agnostic, public/private monorepo for 10–30 `abd-` skills with structural validation and deterministic GitHub Release packaging.

**Architecture:** Keep independently installable skills as direct children of `skills/`, with human documentation beside each `SKILL.md`. Two dependency-free Python tools validate the collection and create deterministic archives; standard-library unit tests exercise them with temporary repositories. GitHub Actions reuses those same commands for read-only CI and tag-driven releases.

**Tech Stack:** Python 3.12 standard library, `unittest`, ZIP archives, SHA-256, GitHub Actions, GitHub CLI, Markdown.

## Global Constraints

- Every public skill directory is a direct child of `skills/` and starts with `abd-`.
- Every skill contains `SKILL.md` and a short `README.md`.
- Skill frontmatter contains non-empty `name` and `description`; `name` exactly matches the directory.
- A skill may reference only paths contained within its own directory.
- The collection uses one repository-wide `vMAJOR.MINOR.PATCH` version.
- Runtime and release tooling uses only Python 3's standard library; no project dependency installation is allowed.
- Generated artifacts live in ignored `dist/` and never enter Git history.
- Tagged releases contain one `.skill` archive per skill, one complete collection ZIP, and SHA-256 checksums.
- Prompt evals, seeded repositories, answer keys, benchmark reports, historical model outputs, and platform-specific plugin metadata are out of scope.
- Use `main` as the sole root repository's default branch and the MIT License.

## File Map

**Create**

- `scripts/validate_skills.py` — discovers skills, parses portable frontmatter, validates naming and local resource references, and exposes a CLI.
- `scripts/package_skills.py` — validates, builds deterministic archives in staging, verifies layouts and checksums, then publishes only the complete verified set.
- `tests/test_validate_skills.py` — isolated validator tests using temporary skill trees.
- `tests/test_package_skills.py` — archive layout, determinism, checksum, dry-run, and failure tests.
- `tests/test_repository_layout.py` — asserts the migrated repository contract and obsolete-directory removal.
- `tests/test_workflows.py` — asserts CI/release triggers, permissions, and commands.
- `skills/abd-code-review/README.md` — short human-facing purpose, installation, usage, and resource guide.
- `.github/workflows/ci.yml` — read-only push/PR validation.
- `.github/workflows/release.yml` — exact semantic tag validation, packaging, and GitHub Release publication.
- `CONTRIBUTING.md` — adding, validating, and releasing skills.
- `CHANGELOG.md` — repository-wide release history beginning with an Unreleased section.
- `LICENSE` — MIT License.
- `.gitignore` — ignores release artifacts and Python-local files.

**Move**

- `abd-code-review/` → `skills/abd-code-review/` without changing `SKILL.md` or its 14 references.

**Replace**

- `README.md` — replace benchmark-focused single-skill documentation with the collection catalog.

**Delete**

- `abd-code-review.skill`
- `fixtures/`
- `evals/`
- `abd-code-review-workspace/`
- `.agents/`
- `.codex/`

---

### Task 1: Collection Validator

**Files:**

- Create: `scripts/validate_skills.py`
- Create: `tests/test_validate_skills.py`

**Interfaces:**

- Consumes: a repository root containing `skills/<skill-name>/` directories.
- Produces: `discover_skills(skills_root: Path) -> list[Path]`, `validate_collection(root: Path) -> list[str]`, and CLI exit status `0` for valid or `1` for invalid.
- Error strings use `<relative-path>: <problem>; expected <correction>` so CI output is actionable.

- [x] **Step 1: Rename the initialized root branch**

Run:

```bash
git branch -m main
git branch --show-current
```

Expected: `main`.

- [x] **Step 2: Write the failing validator tests**

Create `tests/test_validate_skills.py`:

```python
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_skills import validate_collection  # noqa: E402


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
```

- [x] **Step 3: Run the validator tests and confirm the expected failure**

Run:

```bash
python3 -m unittest tests.test_validate_skills -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'validate_skills'`.

- [x] **Step 4: Implement the validator**

Create `scripts/validate_skills.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_PREFIX = "abd-"
REQUIRED_FILES = ("SKILL.md", "README.md")
KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
RESOURCE_REFERENCE = re.compile(r"`((?:references|scripts|assets)/[^`\s|]+)`")
MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
REMOTE_SCHEMES = ("http://", "https://", "mailto:", "data:")


class FrontmatterError(ValueError):
    pass


def discover_skills(skills_root: Path) -> list[Path]:
    if not skills_root.is_dir():
        return []
    return sorted(
        (path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith(".")),
        key=lambda path: path.name,
    )


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError("frontmatter must start with '---' on line 1")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise FrontmatterError("frontmatter is missing its closing '---'") from error

    values: dict[str, str] = {}
    current_key: str | None = None
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            if current_key is None:
                raise FrontmatterError(f"unexpected indentation on line {line_number}")
            values[current_key] += "\n" + line.strip()
            continue
        match = KEY_VALUE.fullmatch(line)
        if not match:
            raise FrontmatterError(f"invalid mapping entry on line {line_number}")
        key, value = match.group(1), (match.group(2) or "").strip()
        if key in values:
            raise FrontmatterError(f"duplicate key '{key}' on line {line_number}")
        values[key] = value
        current_key = key
    return values


def local_references(source: Path) -> set[str]:
    text = source.read_text(encoding="utf-8")
    references = set(RESOURCE_REFERENCE.findall(text))
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith("#") or target.startswith(REMOTE_SCHEMES):
            continue
        references.add(target.split("#", 1)[0])
    return references


def display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def validate_skill(skill: Path, root: Path) -> list[str]:
    errors: list[str] = []
    relative_skill = display(skill, root)
    if not skill.name.startswith(SKILL_PREFIX):
        errors.append(f"{relative_skill}: name must start with 'abd-'; expected {SKILL_PREFIX}<name>")

    for filename in REQUIRED_FILES:
        required = skill / filename
        if not required.is_file():
            errors.append(f"{display(required, root)}: missing; expected a regular file")

    skill_md = skill / "SKILL.md"
    if skill_md.is_file():
        try:
            frontmatter = parse_frontmatter(skill_md)
        except (OSError, UnicodeError, FrontmatterError) as error:
            errors.append(f"{display(skill_md, root)}: {error}; expected portable YAML frontmatter")
        else:
            name = frontmatter.get("name", "").strip("'\"")
            description = frontmatter.get("description", "")
            if not name:
                errors.append(f"{display(skill_md, root)}: name is empty; expected name: {skill.name}")
            elif name != skill.name:
                errors.append(
                    f"{display(skill_md, root)}: name '{name}' does not match directory; expected {skill.name}"
                )
            if not description or description in {"|", ">", "|-", ">-", "|+", ">+"}:
                errors.append(
                    f"{display(skill_md, root)}: description must be non-empty; expected a concise trigger description"
                )

    skill_root = skill.resolve()
    for markdown in sorted(skill.rglob("*.md")):
        for reference in sorted(local_references(markdown)):
            candidate = (markdown.parent / reference).resolve()
            try:
                candidate.relative_to(skill_root)
            except ValueError:
                errors.append(
                    f"{display(markdown, root)}: reference '{reference}' escapes skill directory; "
                    "expected an in-skill path"
                )
                continue
            if not candidate.exists():
                errors.append(
                    f"{display(markdown, root)}: reference '{reference}' does not exist; expected a valid local path"
                )
    return errors


def validate_collection(root: Path) -> list[str]:
    root = root.resolve()
    skills_root = root / "skills"
    skills = discover_skills(skills_root)
    if not skills:
        return [f"{display(skills_root, root)}: missing or empty; expected at least one direct child skill"]
    errors: list[str] = []
    for skill in skills:
        errors.extend(validate_skill(skill, root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the agent skill collection.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    args = parser.parse_args(argv)
    errors = validate_collection(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(discover_skills(args.root.resolve() / 'skills'))} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [x] **Step 5: Run the validator tests and check the CLI syntax**

Run:

```bash
python3 -m unittest tests.test_validate_skills -v
python3 scripts/validate_skills.py --help
```

Expected: 5 tests pass; help output includes `--root`.

- [x] **Step 6: Commit the validator**

```bash
git add scripts/validate_skills.py tests/test_validate_skills.py
git commit -m "feat: add skill collection validator"
```

---

### Task 2: Deterministic Packager

**Files:**

- Create: `scripts/package_skills.py`
- Create: `tests/test_package_skills.py`

**Interfaces:**

- Consumes: `validate_collection()` and `discover_skills()` from Task 1.
- Produces: `normalize_version(value: str) -> str`, `build_packages(root: Path, output: Path, version: str, dry_run: bool = False) -> list[Path]`, and a CLI with `--root`, `--output`, `--version`, and `--dry-run`.
- Archive layout: individual archive `<skill>/<files>`; collection archive `skills/<skill>/<files>`.

- [x] **Step 1: Write the failing packager tests**

Create `tests/test_package_skills.py`:

```python
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
```

- [x] **Step 2: Run the packager tests and confirm the expected failure**

Run:

```bash
python3 -m unittest tests.test_package_skills -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'package_skills'`.

- [x] **Step 3: Implement deterministic staged packaging**

Create `scripts/package_skills.py`:

```python
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
    return sorted((path for path in skill.rglob("*") if path.is_file()), key=lambda path: path.as_posix())


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
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".package-", dir=output.parent) as temporary:
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
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)

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
```

- [x] **Step 4: Run packager tests and the full tooling suite**

Run:

```bash
python3 -m unittest tests.test_package_skills -v
python3 -m unittest discover -s tests -v
```

Expected: 10 tests pass.

- [x] **Step 5: Commit the packager**

```bash
git add scripts/package_skills.py tests/test_package_skills.py
git commit -m "feat: add deterministic skill packaging"
```

---

### Task 3: Repository Migration, Cleanup, and Documentation

**Files:**

- Create: `tests/test_repository_layout.py`
- Move: `abd-code-review/` → `skills/abd-code-review/`
- Create: `skills/abd-code-review/README.md`
- Replace: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Delete: `abd-code-review.skill`, `fixtures/`, `evals/`, `abd-code-review-workspace/`, `.agents/`, `.codex/`

**Interfaces:**

- Consumes: validator and packager commands from Tasks 1–2.
- Produces: the final public repository layout and an independently installable `skills/abd-code-review/`.

- [ ] **Step 1: Write the failing repository contract test**

Create `tests/test_repository_layout.py`:

```python
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
```

- [ ] **Step 2: Run the repository test and confirm it fails for the old layout**

Run:

```bash
python3 -m unittest tests.test_repository_layout -v
```

Expected: FAIL because `skills/abd-code-review/` and root documentation do not yet exist and obsolete paths remain.

- [ ] **Step 3: Move the runtime skill intact**

Run:

```bash
mkdir -p skills
mv abd-code-review skills/abd-code-review
```

Verify the move retained the runtime files:

```bash
test -f skills/abd-code-review/SKILL.md
test "$(find skills/abd-code-review/references -type f | wc -l)" -eq 14
```

Expected: both commands exit `0`.

- [ ] **Step 4: Add the short skill README**

Create `skills/abd-code-review/README.md`:

```markdown
# abd-code-review

Deep, evidence-based code review for diffs, pull requests, branches, commit ranges, and selected files.

## Use it when

- You want a pre-merge review focused on correctness and production risk.
- A change needs security, data-integrity, reliability, performance, or rollout scrutiny.
- You want findings verified against surrounding code rather than a diff-only checklist.

## Install

Copy or symlink this directory into the skills directory used by your agent. The portable entry point is `SKILL.md`; no platform-specific plugin is required.

Prebuilt `.skill` archives are also attached to tagged GitHub Releases.

## Example prompts

```text
Use abd-code-review to review the current branch against main.
Review PR 482 and focus on authorization and migration safety.
Is this payment-worker change safe to ship?
```

## Bundled resources

`references/` contains stack-specific guidance for Go, Python, Java/Spring, PHP/Laravel, Node/TypeScript, React/Next, Vue/Nuxt, Rust, .NET, Kotlin/Android, databases, dependencies, infrastructure/CI, and shell/config files. The skill loads only references relevant to the reviewed change.

## Compatibility

The skill is agent-agnostic but expects the host agent to be able to read repository files and run the project's normal Git and verification commands.
```

- [ ] **Step 5: Replace the root README with the collection catalog**

Replace `README.md` with:

```markdown
# Abid's Agent Skills

An agent-agnostic collection of reusable engineering skills for private use and public distribution. Every skill follows the portable `SKILL.md` convention and uses the `abd-` prefix.

## Skills

| Skill | Purpose |
|---|---|
| [abd-code-review](skills/abd-code-review/README.md) | Deep, evidence-based review of diffs, pull requests, branches, commits, and selected files. |

## Install

Clone this repository, then copy or symlink the desired directory from `skills/` into the skills directory supported by your agent. Each directory is independently installable.

Tagged GitHub Releases provide one `.skill` archive per skill and an `abd-skills` ZIP containing the complete collection. Verify downloaded artifacts with the attached `SHA256SUMS` file.

## Develop

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for naming, documentation, validation, and release rules.

## License

[MIT](LICENSE)
```

- [ ] **Step 6: Add contribution, changelog, license, and ignore files**

Create `CONTRIBUTING.md`:

```markdown
# Contributing

## Add or update a skill

1. Create a direct child directory under `skills/` whose name starts with `abd-`.
2. Add `SKILL.md` with non-empty `name` and `description` frontmatter. `name` must equal the directory name.
3. Add a short `README.md` covering purpose, use cases, installation, examples, resources, and compatibility.
4. Keep skill-specific references, scripts, and assets inside the skill directory.
5. Add the skill to the root README catalog and the Unreleased section of `CHANGELOG.md`.

## Verify

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

## Release

The collection uses one semantic version. Update `CHANGELOG.md`, commit the release notes, and push an exact `vMAJOR.MINOR.PATCH` tag. GitHub Actions validates the repository and attaches individual `.skill` archives, the complete collection ZIP, and `SHA256SUMS` to the release.

Generated `dist/` files are local artifacts and must not be committed.
```

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this collection are documented here. The project uses one repository-wide semantic version.

## [Unreleased]

### Added

- Initial multi-skill repository structure.
- `abd-code-review` skill.
- Structural validation, deterministic packaging, and GitHub release automation.
```

Create `LICENSE`:

```text
MIT License

Copyright (c) 2026 Abid

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Create `.gitignore`:

```gitignore
dist/
__pycache__/
*.py[cod]
.venv/
.DS_Store
```

- [ ] **Step 7: Remove the explicitly retired evaluation system and generated package**

First confirm each target exactly matches the approved removal list:

```bash
find .agents .codex abd-code-review-workspace evals fixtures -maxdepth 1 -print
test -f abd-code-review.skill
```

Then remove them:

```bash
rm -rf .agents .codex abd-code-review-workspace evals fixtures abd-code-review.skill
```

Expected: `.agents`, `.codex`, all evaluation inputs/outputs, seven nested Git repositories, and the generated package are absent. Do not remove the root `.git`.

- [ ] **Step 8: Run migration tests and tooling against the real collection**

Run:

```bash
python3 -m unittest tests.test_repository_layout -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
python3 -m unittest discover -s tests -v
```

Expected: repository layout tests pass; validator reports `Validated 1 skill(s).`; dry run reports success; all 14 tests pass.

- [ ] **Step 9: Commit the migration**

```bash
git add .gitignore CHANGELOG.md CONTRIBUTING.md LICENSE README.md skills tests/test_repository_layout.py
git add -u
git commit -m "refactor: organize skills as a public collection"
```

---

### Task 4: CI and Tagged Release Automation

**Files:**

- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/release.yml`
- Create: `tests/test_workflows.py`

**Interfaces:**

- Consumes: validator, packager, and unit-test commands established in Tasks 1–3.
- Produces: read-only push/PR CI and exact semantic-tag releases with `contents: write` only in the release workflow.

- [ ] **Step 1: Write failing workflow contract tests**

Create `tests/test_workflows.py`:

```python
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
```

- [ ] **Step 2: Run workflow tests and confirm missing-file failures**

Run:

```bash
python3 -m unittest tests.test_workflows -v
```

Expected: two ERROR results with `FileNotFoundError` for the workflow files.

- [ ] **Step 3: Add read-only CI**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run structural tests
        run: python3 -m unittest discover -s tests -v

      - name: Validate skills
        run: python3 scripts/validate_skills.py

      - name: Verify packaging
        run: python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

- [ ] **Step 4: Add exact-tag release automation**

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Validate exact semantic version tag
        shell: bash
        run: |
          if [[ ! "$GITHUB_REF_NAME" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Invalid release tag: $GITHUB_REF_NAME; expected vMAJOR.MINOR.PATCH" >&2
            exit 1
          fi

      - name: Run structural tests
        run: python3 -m unittest discover -s tests -v

      - name: Validate skills
        run: python3 scripts/validate_skills.py

      - name: Build and verify release artifacts
        run: python3 scripts/package_skills.py --version "$GITHUB_REF_NAME" --output dist

      - name: Publish GitHub Release
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release create "$GITHUB_REF_NAME" dist/* --verify-tag --generate-notes --title "$GITHUB_REF_NAME"
```

- [ ] **Step 5: Run workflow and full structural verification**

Run:

```bash
python3 -m unittest tests.test_workflows -v
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v0.0.0 --dry-run
```

Expected: workflow tests pass; all 16 tests pass; validator and packaging dry run succeed.

- [ ] **Step 6: Commit workflow automation**

```bash
git add .github/workflows tests/test_workflows.py
git commit -m "ci: validate and package tagged releases"
```

---

### Task 5: Final Release Smoke Test and Acceptance Audit

**Files:**

- Verify only; no source changes expected.

**Interfaces:**

- Consumes: the completed repository.
- Produces: fresh evidence for every acceptance criterion without creating a Git tag or GitHub Release.

- [ ] **Step 1: Run the complete test and validation suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --version v1.0.0 --output dist
```

Expected: all 16 tests pass; validator reports one skill; `dist/` contains:

```text
SHA256SUMS
abd-code-review-v1.0.0.skill
abd-skills-v1.0.0.zip
```

- [ ] **Step 2: Independently verify checksums and archive layouts**

Run:

```bash
cd dist
sha256sum --check SHA256SUMS
unzip -l abd-code-review-v1.0.0.skill
unzip -l abd-skills-v1.0.0.zip
cd ..
```

Expected: both checksum lines report `OK`; the individual archive has one `abd-code-review/` root; the collection archive has one `skills/` root.

- [ ] **Step 3: Verify cleanup, Git scope, and ignored artifacts**

Run:

```bash
test ! -e fixtures
test ! -e evals
test ! -e abd-code-review-workspace
test ! -e abd-code-review.skill
test "$(find . -mindepth 2 -name .git -print | wc -l)" -eq 0
git check-ignore dist/abd-code-review-v1.0.0.skill
git status --short --branch
```

Expected: all assertions exit `0`; `dist` is ignored; status shows branch `main` with no uncommitted source changes.

- [ ] **Step 4: Remove local smoke artifacts and confirm a clean worktree**

Run:

```bash
rm -rf dist
git status --short --branch
git log --oneline --decorate -6
```

Expected: clean `main` worktree and separate commits for validator, packager, migration/docs, and workflows. Do not create or push `v1.0.0`; publishing remains an explicit future release action.
