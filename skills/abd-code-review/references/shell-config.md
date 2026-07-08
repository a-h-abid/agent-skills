# Shell Scripts & Configuration Files — Cross-Cutting Checks

Apply when the diff touches shell scripts (`*.sh`, `*.bash`, shell embedded in CI steps, Dockerfiles, Makefiles, cron entries) or standalone configuration files (`.env*`, `*.yaml`/`*.yml`, `*.toml`, `*.ini`, `*.json` configs, nginx/apache configs, systemd units).

## Shell Scripts

### Failure behavior (the #1 shell bug class)

- **Error handling declared**: `set -euo pipefail` (or explicit per-command checks) — without it, a failed step is silently ignored and the script barrels on. Know the gaps even with `-e`: failures in `if`/`&&`/`||` contexts, command substitution in assignments, and functions called in conditionals don't trip it.
- `cmd1 | cmd2` without `pipefail` reports only `cmd2`'s status; `local var=$(cmd)` masks `cmd`'s failure (declare and assign separately).
- Cleanup on exit: `trap '...' EXIT` for temp files/locks/background jobs; partial-state cleanup if the script dies midway.
- Is the script **idempotent / re-runnable**? Deploy and migration scripts get re-run after failures — appending twice, re-creating existing resources, or re-applying a step must be safe.

### Quoting & injection

- **Unquoted variable expansions** (`rm -rf $DIR/` with empty or space-containing `$DIR` — potentially catastrophic); `"$@"` not `$*` for argument passthrough.
- Word splitting/globbing on filenames: `for f in $(ls ...)` breaks on spaces — use globs or `find -print0 | xargs -0`.
- User/external input interpolated into commands, `eval`, or SQL/`curl` bodies; `curl $URL | bash` patterns.
- `[ x = y ]` vs `[[ ]]`; unquoted test operands; `==` in POSIX `sh`.

### Portability & environment

- Shebang matches the syntax used (`#!/bin/sh` running bashisms breaks on dash/alpine); `#!/usr/bin/env bash` for bash scripts.
- Doesn't assume CWD — uses paths relative to `$(dirname "$0")`/`${BASH_SOURCE[0]}` or explicit cd with failure check (`cd ... || exit 1`).
- Required commands/env vars checked upfront with a clear error (`: "${API_KEY:?is required}"`), not a cryptic failure at line 200.
- Secrets: not echoed by `set -x` (disable around sensitive lines), not passed as CLI args (visible in `ps`), not left in temp files.
- Destructive operations (`rm -rf`, `DROP`, force-push, resource deletion): guarded by confirmation/flag, paths absolute and validated, never built from unvalidated variables.
- If the repo uses `shellcheck`, run it; its findings are strong leads.

## Configuration Files

### Correctness

- **YAML traps**: unquoted values coerce — `no`/`on`/`yes` → booleans (Norway problem), `3.10` → `3.1`, leading-zero strings → octal, `1e2` → float. Quote anything that must stay a string (versions, country codes, phone numbers). Indentation changes silently re-parent keys; anchors/merge keys (`<<:`) override in surprising order; duplicate keys silently last-wins in most parsers.
- `.env` semantics vary by loader (quoting, multiline, `export`, comment handling) — verify against the loader actually used; no spaces around `=`.
- TOML/INI: type of a changed value still matches what the code expects (string "5s" vs integer 5 vs duration).
- The **code reading the config** agrees with the change: key renamed here but not in the reader; new key with no default in the reader (startup crash or silent `null`).

### Environment consistency & safety

- Change applied to **all** relevant environments/files (`.env.example`, dev/staging/prod overlays, Helm values per env, compose overrides) — or intentionally divergent, stated. `.env.example` updated so new devs and CI don't break.
- Secrets: real credentials never in committed config — placeholders in examples, secret-manager references in real configs. A committed-then-removed secret is still in git history: flag for rotation.
- Safe defaults: debug/verbose off in prod configs; permissive CORS/hosts (`*`) deliberate; timeouts/limits present rather than unlimited.
- Renamed/removed config keys: old key's consumers all migrated (grep for the old name); deploy-time ordering if config and code must change together.

### Server / proxy configs (nginx, apache, load balancers)

- Route/location changes: new blocks don't shadow or open existing protected paths (`location` precedence); auth/IP restrictions preserved on moved blocks.
- Body-size, timeout, and buffer limits consistent with the app's expectations; websocket/upgrade headers where needed.
- TLS: protocols/ciphers not downgraded; redirects preserving HSTS assumptions.
- Header handling: `X-Forwarded-*`/`Host` trust chain correct (affects rate limiting, URL generation, IP allowlists behind proxies).

### systemd / cron / scheduled entries

- Units: `Restart=` policy, resource limits, `After=`/dependency ordering, non-root `User=`.
- Cron: schedule means what's intended (server timezone!), overlapping runs safe or locked (`flock`), output captured somewhere (not silently mailed to nobody), full paths used (cron's PATH is minimal).
