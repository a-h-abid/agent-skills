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
