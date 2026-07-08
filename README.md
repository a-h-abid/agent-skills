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
