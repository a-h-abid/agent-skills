# Agent Skills Repository Design

**Date:** 2026-07-07  
**Status:** Approved

## Purpose

Turn this project into the canonical source for Abid's reusable agent skills. The repository must work for private day-to-day use and public distribution while remaining agent-agnostic.

The collection is expected to contain roughly 10–30 skills. Every public skill uses the `abd-` prefix. The repository publishes source code through Git and generated archives through tagged GitHub Releases.

## Goals

- Keep every installable skill easy to discover and understand.
- Support portable `SKILL.md`-based agents without requiring a platform-specific plugin format.
- Use one repository-wide semantic version.
- Validate skills automatically on pushes and pull requests.
- Produce individual skill archives and a complete collection bundle from version tags.
- Keep generated packages and abandoned evaluation infrastructure out of Git history.

## Non-goals

- Retaining prompt evaluations, seeded repositories, answer keys, benchmark reports, or historical model outputs.
- Maintaining independent versions for individual skills.
- Organizing skills into nested categories.
- Shipping platform-specific metadata unless a future requirement justifies it.
- Evaluating the behavioral quality of model responses.

## Repository Architecture

```text
agent-skills/
├── skills/
│   └── abd-code-review/
│       ├── SKILL.md
│       ├── README.md
│       └── references/
├── scripts/
│   ├── validate-skills
│   └── package-skills
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── docs/
│   └── superpowers/specs/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

`skills/` is the canonical source. Each direct child is independently installable. Categories are represented by catalog text or metadata rather than directory nesting so installers can discover skills consistently.

Root-level scripts operate on the collection as a whole. Resources used by only one skill remain within that skill's directory.

## Skill Contract

Every skill directory must:

- Be a direct child of `skills/`.
- Start with the `abd-` prefix.
- Contain `SKILL.md` and `README.md`.
- Declare `name` and `description` in portable YAML frontmatter.
- Use a frontmatter name that exactly matches its directory name.
- Reference only files contained within its own directory.
- Keep skill-specific `references/`, `scripts/`, and `assets/` local to the skill.

`SKILL.md` contains agent instructions. `README.md` is short, human-facing documentation covering purpose, use cases, installation, example prompts, bundled resources, and compatibility notes where needed.

## Collection Documentation

The root `README.md` introduces the collection, provides agent-agnostic installation guidance, links to releases, and presents a compact catalog. Every catalog entry contains the skill name, a one-line purpose, and a link to that skill's README.

`CONTRIBUTING.md` documents naming, required files, validation, packaging, and release procedures. `CHANGELOG.md` records changes under the repository-wide version. The repository uses the MIT License.

## Validation

On every push and pull request, CI discovers direct children of `skills/` and verifies:

1. The directory uses the `abd-` prefix.
2. `SKILL.md` and `README.md` exist.
3. Required frontmatter is valid.
4. The declared skill name matches the directory.
5. Referenced local files exist and remain within the skill directory.
6. A packaging dry run succeeds.

Validation exits non-zero on failure and identifies the skill, file, violated rule, and expected correction.

## Packaging and Releases

Generated files are written to ignored `dist/` and never committed. Packaging uses standard, dependency-free tooling and produces deterministic archives.

A semantic-version tag such as `v1.2.0` triggers the release workflow. The workflow:

1. Validates the tag format and every skill.
2. Packages each skill as `<skill-name>-v<version>.skill`.
3. Packages the complete `skills/` collection as `abd-skills-v<version>.zip`.
4. Generates SHA-256 checksums.
5. Extracts and inspects the archives as a smoke test.
6. Creates a GitHub Release and attaches all archives and the checksum file.

Packaging builds in a temporary directory. Artifacts are published only after the complete build and smoke test succeed, preventing partial releases.

## Migration and Cleanup

The initial migration will:

- Move `abd-code-review/` to `skills/abd-code-review/`.
- Add `skills/abd-code-review/README.md`.
- Replace the root README with the collection catalog.
- Add collection validation, packaging, CI, release automation, contribution guidance, changelog, MIT license, and ignore rules.
- Delete the tracked/generated `abd-code-review.skill` package.
- Delete `fixtures/`, `evals/`, and `abd-code-review-workspace/` in full.
- Delete the empty `.agents/` and `.codex/` directories.
- Replace the incomplete empty `.git/` directory with a correctly initialized root repository.

The seven repositories under `fixtures/` currently contain the `main` and feature histories used by the old branch-diff evaluations. Removing only their `.git` directories would break those evaluations and leave misleading fixture source behind. Because evaluations are explicitly out of scope, the correct migration is to remove the fixture repositories and all evaluation infrastructure together.

The runtime `abd-code-review` skill does not reference fixtures, evals, workspaces, answer keys, or benchmarks, so this cleanup does not affect skill operation.

## Testing Strategy

Testing is structural rather than behavioral:

- Validate every source skill.
- Build every individual archive and the collection archive.
- Extract each archive and verify its expected layout.
- Confirm the collection contains every discovered skill.
- Confirm generated checksums match their artifacts.

No prompt evals, model-quality benchmarks, or test repositories will be retained.

## Acceptance Criteria

- `skills/abd-code-review/` is independently installable and retains all runtime references.
- The root README links to the skill README and documents installation.
- Validation passes locally and in CI.
- No generated archive is tracked by Git.
- A test version tag can produce individual archives, a collection archive, and valid checksums.
- The obsolete fixture, eval, benchmark workspace, and nested Git repositories are absent.
- The repository has a single initialized Git root and an MIT license.
