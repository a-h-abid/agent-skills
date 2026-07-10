# Full Codebase Audit and Remediation Roadmap Design

**Date:** 2026-07-10
**Status:** Approved
**Repository:** `agent-skills`

## Context

This repository distributes portable agent skills, supporting Python utilities,
tests, and GitHub Actions release automation. Its executable trust surface is
larger than the Python line count alone: `SKILL.md` files and their references
are instructions consumed by agents, packaged archives cross a software supply
chain boundary, and the Jira skill can read local input, use credentials, call
an external service, and perform remote mutations.

The initial project exploration found 42 tracked files and two published skills.
The documented baseline is currently green: 54 unit tests pass, skill validation
passes, and the packaging dry run passes. Those results establish a starting
point; they do not replace file coverage or security validation.

## Goal

Produce an evidence-backed assessment of anything in the publishable repository
that needs attention, improvement, or security hardening, followed by a
prioritized and implementation-ready remediation roadmap. Demonstrate coverage
of every in-scope tracked file and distinguish validated findings from hypotheses
and accepted limitations.

## Scope

The audit covers:

- all tracked runtime and packaging code;
- all tracked skill instructions, references, and public skill documentation;
- all tracked tests and repository validation logic;
- all tracked CI and release workflows;
- all tracked repository metadata and policy files;
- root documentation and release-facing contracts; and
- current ignored or generated files only when their presence can change
  validation, packaging, or publication behavior.

Historical specifications, implementation plans, and tracked model/task reports
are contextual inputs and repository-hygiene evidence. They are not reviewed line
by line as production behavior, but contradictions are reported when they make a
current public contract, security claim, or operational instruction inaccurate.

The audit does not:

- change product code or tests;
- mutate live Jira data;
- publish packages, tags, releases, branches, or pull requests;
- install new dependencies merely to expand tool coverage; or
- treat stylistic preference as a defect without a concrete maintenance cost.

## Review Architecture

The review has four coordinated workstreams.

### 1. Coverage inventory and baseline

Create a canonical inventory from the tracked repository and classify every file
by role and risk. Record a review disposition for each file. Re-run the project's
documented tests, validation, and packaging dry run, then inventory any locally
available static-analysis or workflow checks.

### 2. Correctness and maintainability

Review executable code, tests, and public contracts for boundary-condition bugs,
unsafe filesystem behavior, resource exhaustion, error handling, compatibility,
test quality, documentation drift, and unnecessary coupling. Instruction-only
skills are treated as executable behavior: their trigger conditions, tool advice,
safety gates, output contracts, and reference routing are reviewed for clarity
and consistency.

### 3. Security

Use the standard repository security workflow with distinct phases:

1. repository threat model;
2. candidate-finding discovery;
3. candidate validation;
4. source-to-sink attack-path and severity analysis; and
5. final security artifact generation.

The threat model prioritizes agent prompt injection and confused-deputy behavior,
Jira credential confinement and local-data egress, packaging path and symlink
handling, CI/release token exposure and artifact provenance, and resource or
output privacy risks.

### 4. Release, documentation, and instruction supply chain

Review the path from repository content to validated archives and GitHub Releases.
Check workflow permissions, action pinning, artifact composition, deterministic
build claims, checksum behavior, catalog completeness, compatibility claims, and
the controls that prevent dangerous or misleading agent instructions from being
distributed.

Independent reviewers may be assigned bounded file or risk-surface ownership.
The primary reviewer owns the canonical inventory, cross-file reasoning,
deduplication, severity calibration, and final closure so parallel review cannot
silently create gaps or duplicate root causes.

## Evidence Flow

The audit uses this pipeline:

```text
tracked-file inventory
  -> per-file coverage receipts
  -> candidate issues
  -> targeted validation
  -> confidence and severity calibration
  -> cross-file deduplication
  -> audit report
  -> remediation roadmap
```

Each candidate records:

- a stable identifier and category;
- exact file and line evidence;
- affected behavior and concrete impact;
- entry point, control, and sink when security-relevant;
- validation commands, tests, or counterevidence;
- confidence and final disposition; and
- a practical remediation with verification criteria.

Security candidates require a plausible and evidenced attack path before they
are reportable. Non-security findings require demonstrated behavior, a violated
contract, or a specific reliability or maintenance cost. Multiple instances of
one root cause are grouped without losing affected locations.

## Severity, Confidence, and Roadmap Priority

The main report uses four reader-oriented severities:

- **Blocking:** plausible security compromise, data or credential exposure,
  destructive behavior, broken release integrity, or a failure that prevents
  safe use.
- **Should fix:** validated correctness, reliability, compatibility, or security
  weakness with meaningful but bounded impact.
- **Worth considering:** lower-risk design debt, defense-in-depth, or a credible
  concern whose remaining uncertainty is stated.
- **Nit:** small clarity or hygiene issue with a concrete benefit; kept sparse.

Every finding is tagged `confirmed`, `likely`, or `unverified`. An unverified
candidate cannot be Blocking and is either presented as an explicitly bounded
investigation item or deferred with the missing proof named.

Roadmap items use priorities that are separate from finding severity:

- **P0:** immediate containment or release-blocking correction;
- **P1:** next focused change set for material validated risks;
- **P2:** planned hardening, compatibility, and maintainability work; and
- **P3:** optional hygiene or future-scale improvement.

Each roadmap item includes effort (`S`, `M`, or `L`), dependencies, affected
files, acceptance criteria, and verification commands.

## Verification Strategy

The audit will:

- re-run `python3 -m unittest discover -s tests -v`;
- re-run `python3 scripts/validate_skills.py`;
- re-run `python3 scripts/package_skills.py --version v0.0.0 --dry-run`;
- use targeted, non-destructive tests or temporary-directory proofs for suspected
  defects;
- use safe security proofs without live Jira mutation or release publication;
- inspect repository history where intent affects a finding; and
- verify current external contracts against authoritative sources only when a
  conclusion depends on them.

No tool result becomes a finding without contextual validation. Tests that pass
are evidence for the behavior they exercise, not proof that neighboring behavior
is safe.

## Failure and Limitation Handling

If a check cannot run, the audit records the attempted command, failure, affected
coverage, and safe alternatives attempted. It does not silently narrow scope.
Inconclusive candidates are downgraded or deferred rather than reported as fact.

The audit does not expose secrets in artifacts. It does not make live Jira calls,
write to external systems, or publish releases. Read-only official documentation
lookups are permitted where temporal accuracy matters. Existing user files and
unrelated working-tree changes, if any appear, are preserved.

## Deliverables

1. `docs/audits/2026-07-10-codebase-audit.md`
   - executive verdict;
   - scope and coverage overview;
   - findings ordered by severity;
   - exact evidence and validation;
   - limitations and deferred items; and
   - concise strengths worth preserving.
2. `docs/audits/2026-07-10-remediation-roadmap.md`
   - ordered P0-P3 work;
   - dependencies and sequencing;
   - effort estimates;
   - acceptance criteria; and
   - verification commands.
3. The security workflow's required scan artifacts, referenced from the main
   audit report rather than duplicated.

## Completion Criteria

The work is complete only when:

- every in-scope tracked file has a review receipt or an explicit contextual or
  not-applicable disposition;
- every discovered candidate is reportable, suppressed, not applicable, or
  deferred with an exact reason;
- every reportable security issue has validation and attack-path evidence;
- documented baseline checks have been rerun and their results recorded;
- both deliverables are written and internally consistent;
- roadmap entries trace back to findings or explicitly labeled hardening goals;
  and
- no product-code or external-system mutation has occurred.
