# Dependencies, Lockfiles & Supply Chain — Cross-Cutting Checks

Apply when the diff touches dependency manifests or lockfiles: `composer.json`/`composer.lock`, `package.json` + `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml`, `go.mod`/`go.sum`, `requirements*.txt`/`poetry.lock`/`uv.lock`/`Pipfile.lock`, `Cargo.toml`/`Cargo.lock`, `*.csproj`/`packages.lock.json`, Gradle/Maven files, `Gemfile.lock`, etc.

## Adding a Dependency

- **Is it needed at all?** Duplicates something already in the dependency tree, the standard library, or ~30 lines of first-party code? Every dependency is a permanent maintenance contract.
- Health: maintained (recent releases/commits), widely used enough for its risk position, not a one-maintainer package sitting in your auth/crypto/payment path.
- **Typosquatting/slopsquatting**: exact name verified against the intended package (`lodash` vs `1odash`); this matters double when a name came from an AI suggestion — hallucinated package names get registered by attackers.
- Install-time behavior: postinstall scripts (npm), build scripts (`build.rs`), setup.py — code that runs at install is code you're executing on every dev machine and CI runner.
- License compatible with the product; transitive licenses for anything vendored/bundled.
- Scope correct: dev/test tooling in dev dependencies, not production.

## Version Changes & Lockfiles

- **Manifest and lockfile move together** — a manifest change without its lockfile means CI/prod installs something other than what was reviewed.
- Lockfile-only churn with no manifest change: explainable (audit fix, transitive refresh)? Watch for **registry/source URL changes inside the lockfile** (a swapped registry or git URL is a classic attack), integrity-hash rewrites, and unexpected new transitive packages.
- Upgrades: major version = breaking changes — evidence the changelog was read (code adapted, or a note); minor/patch en-masse bumps still deserve a scan of anything security-adjacent.
- Pinning strategy consistent with the repo: apps pin (lockfile authoritative); libraries use ranges deliberately. A new `^`/`~`/wildcard where the repo pins exact is drift.
- Downgrades are suspicious — deliberate (regression escape) or accidental (lockfile regenerated from a stale manifest)?

## Known Vulnerabilities

- Run the ecosystem's audit if quick (`npm audit`, `composer audit`, `pip-audit`, `cargo audit`, `govulncheck`, `dotnet list package --vulnerable`); treat results as leads — is the vulnerable path actually reachable?
- A dependency added at a version with a known CVE fix available = ask why not the fixed version.

## Ecosystem Notes

- **npm**: lockfile `resolved`/`integrity` fields shouldn't change for unchanged versions; `overrides`/`resolutions` documented; watch new packages with near-zero downloads or day-old publish dates.
- **Composer**: `composer.lock` `dist`/`source` URLs on packagist or known VCS; new `repositories` entries (custom/VCS repos) are a trust decision; plugins/scripts execute code — `allow-plugins` deliberate.
- **Go**: `go.sum` accompanies `go.mod`; `replace` directives (esp. pointing at forks/local paths) are red flags in shipped code; pseudo-versions pinning un-tagged commits deliberate.
- **Python**: unpinned `requirements.txt` in an application = unreproducible builds; hash-checking mode where the repo uses it; `--index-url`/`--extra-index-url` changes are a dependency-confusion vector.
- **Cargo**: new `[patch]`/git dependencies are trust decisions; feature unification side effects on existing deps.
- **Private + public registry mixes** (any ecosystem): internal package names must not be resolvable from the public registry (dependency confusion) — scoping/namespacing or registry config must prevent it.
