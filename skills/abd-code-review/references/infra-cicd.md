# Infrastructure, Containers & CI/CD — Cross-Cutting Checks

Apply when the diff touches Dockerfiles, Compose files, Kubernetes/Helm manifests, Terraform/IaC, or CI/CD pipeline definitions.

## Docker & Images

- Base image pinned to a specific tag (ideally digest), not `:latest`; image minimal (slim/alpine/distroless where compatible) — smaller surface, faster pulls.
- **Runs as non-root** (`USER`), or root justified; writable paths explicit.
- **No secrets in layers**: build args with tokens persist in history; secrets via BuildKit secret mounts or runtime env. `.dockerignore` excludes `.env`, `.git`, local configs.
- Layer/caching sanity: dependency install before source copy so code changes don't bust the dependency cache; multi-stage builds keep toolchains out of the runtime image.
- Correct signal handling: PID 1 forwards SIGTERM (exec-form ENTRYPOINT, tini/dumb-init for shell-wrapped processes) — otherwise graceful shutdown never happens.
- HEALTHCHECK (or orchestrator probes) reflects real readiness, not just "process exists".

## Kubernetes / Compose / Orchestration

- **Probes**: liveness vs readiness distinct — readiness gates traffic (include hard dependencies), liveness restarts (must NOT include dependencies, or a DB blip restart-storms the fleet); startup probe for slow boots.
- **Resources**: requests/limits set and updated for the workload change; memory limit vs actual usage (OOMKill risk); CPU throttling from tight limits.
- Rollout: strategy (rolling/canary/blue-green) matches change risk; `maxUnavailable`/`maxSurge` sane; PodDisruptionBudget for critical services; `terminationGracePeriodSeconds` ≥ actual drain time and app handles SIGTERM.
- Config: secrets in Secret objects (not ConfigMaps/env in manifests); config changes trigger pod restarts where required (checksum annotations); new env vars added to every relevant deployment (app + workers + cron).
- Security context: no privileged containers, RBAC least-privilege for new service accounts, network exposure only where needed (Service/Ingress types deliberate).
- Cron/scheduled workloads: `concurrencyPolicy` (overlap safe?), missed-run behavior, timezone assumptions.

## Terraform / IaC

- **Plan for destructive actions**: rename = destroy-and-recreate for many resources; `deletion_protection`/lifecycle `prevent_destroy` on stateful resources (DBs, buckets).
- Least privilege on new IAM roles/policies — no wildcard actions/resources without justification.
- Public exposure: new security-group rules, bucket policies, or load balancers open to 0.0.0.0/0 deliberately?
- State discipline: no secrets in state-visible outputs; module/provider versions pinned.

## CI/CD Pipelines

- **Secrets hygiene**: secrets not echoed to logs, not passed to untrusted steps; fork/PR-triggered workflows can't reach privileged secrets (`pull_request_target` misuse in GitHub Actions); minimal token permissions (`permissions:` block).
- Third-party actions/orbs/plugins pinned to a SHA or trusted version, not a floating tag someone else can repoint.
- Script injection: untrusted PR titles/branch names/inputs interpolated into `run:` shell — quote through env vars.
- Does the pipeline actually gate the merge? New checks required, not optional; tests can't be skipped silently; artifacts don't leak credentials.
- Deploy ordering encoded where it matters: migrations vs app rollout vs worker restarts vs cache clears — and a failed mid-step leaves a recoverable state.
- Caches keyed correctly (lockfile hash) — a stale dependency cache is a supply-chain and correctness hazard.

## Runtime & Ops

- New service/queue/cron has: log shipping, metrics, alerting, dashboard, and an owner — before it pages someone who's never heard of it.
- Capacity: new workload's connection-pool sizes vs DB max connections across all replicas; fan-out (N pods × M connections) computed, not assumed.
- Cost surprises: new instances/volumes/egress/log volume acknowledged for significant additions.
