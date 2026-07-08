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
