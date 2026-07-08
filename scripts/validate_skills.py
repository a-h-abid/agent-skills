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
            description = frontmatter.get("description", "").strip("'\"")
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
