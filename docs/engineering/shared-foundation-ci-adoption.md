# Trade Docs — Shared CI adoption (2026-11-10)

**Source:** Shared Foundation Repository Gates and BA-SEC-DEP-001, pinned to
`584d7f3cd8426ffd3d1dc9f068f0b444dc74346e`. **Stacked on** the unmerged dependency-security PR #22.
The accepted TDOC-TECH-02 technology choice and private-scaffold maturity are
unchanged. No document issuer, Customs provider or protected runtime is enabled.

## Comparison and decisions

| Shared workflow family | Before this PR | After |
|---|---|---|
| Action pinning | Existing reusable consumer | Retained; Foundation baseline additionally checks trusted SHA-locked actions |
| Dependabot policy | PR #22 adds expanded native security and maintenance policy | Reused as stacked prerequisite; no competing configuration or override |
| Secret scanning | Existing reusable consumer | Retained; Foundation adds scoped PR / branch / deep checks |
| RTD-10 / contract conformance | Existing reusable consumer | Retained unchanged |
| Foundation classification, baseline, reproducibility, runtime | Missing | Enabled from the single Shared immutable commit |
| Foundation portable security, Python/Rust dependency audit | Missing | Enabled, alongside PR #22's independent daily advisory jobs |
| Foundation CodeQL for Python/Rust | Inactive template | Activated via `security.sast_provider: codeql` (public repo) |
| GitHub dependency graph review | Missing | Activated on pull requests (`dependency_review_enabled: true`) |
| Foundation container release gate | No shipping OCI artifact | Classified *not applicable* (DevContainer is not product image) |
| Foundation baobab-dev image validation | This repo uses its own pinned DevContainer | Declared not required; no fabricated baobab-dev image eligibility |
| Shared Python uv security recipe | Template only, expects `uv.lock` + security group | Not activated: Trade Docs uses exact pip hashes; Foundation's native pip/Trivy audits apply |
| Release/staging/OCI publishing | No release approval | Not activated; requires protected EA/DEV-13 authorisation |
| Node/Go/Java/frontend CI | No such runtime | Not activated |
| Shared site/publishing/experience workflows | Inapplicable to headless engine | Not activated |

### Rust and Python workspace anchors

Shared's reproducibility/runtime workflows assume **root manifests and locks**.
Trade Docs' true code lives under `rust-kernel/` and `runtime/`. Therefore:

- Root `Cargo.toml` makes `rust-kernel` a **single-member Cargo workspace**;
  standalone `rust-kernel/fuzz` stays excluded. The canonical lock remains
  `rust-kernel/Cargo.lock`, referenced by a Git symlink at root—no divergent
  second lockfile or second Rust service.
- Root `requirements.lock` is a Git symlink to the canonical
  `runtime/requirements.lock`, preserving all hash pins for Shared's `pip`
  adapter and the existing Python 3.14 native runtime CI.
- The previously standalone `rustsec/audit-check` GitHub action is removed
  because Shared Foundation's trusted action-owner baseline deliberately
  disallows that action; Rust advisory coverage remains in Shared native
  cargo-audit and the PR #22 daily `cargo-audit --file` job. This is a
  consolidation of scanning, **not** a waiver.

### Gates and protected boundaries

PR/push/dispatch runs request the Shared `full` profile with baseline,
reproducibility, generic runtime, portable/native security, CodeQL and
dependency review **only after repository Dependency Graph is enabled**. Weekly schedule uses `security-deep`.
The aggregate `Foundation / Result` is the policy gate. All Shared code
refs are pinned to one 40-character commit. No `secrets: inherit`.

The generic Shared Python syntax gate uses Python 3.13 and Rust stable;
these are **additional source quality checks**, not replacements for
Trade Docs' Python 3.14, PostgreSQL 17, PyO3 ABI and cargo-fuzz workflows.
Security configuration declares public-repository CodeQL, not private GHAS
approval. No exceptions, waiver, or release override is introduced.

### Connected verification

- Shared Foundation `Foundation / Result` on final PR head
- Specific Foundation classification, reproducibility, Python/Rust runtime,
  CodeQL, Trivy, dependency review and native advisory outcomes
- Original Trade Docs conformance, Python 3.14, Rust native tests, GitHub
  Actions pinning and security policy checks
- Absence of any new released container/issuer capability

Do not merge the stacked PR while its foundation policy or dependency
maintenance base (#22) is unqualified. Upgrading to a different Shared SHA
requires explicit review and downstream validation.

### Dependency Review — repo-setting blocker, NOT a pass

On PR #26's first actual `dependency_review_enabled: true` run, the pinned
Shared `actions/dependency-review-action` failed with:

> Dependency review is not supported on this repository. Please ensure that Dependency graph is enabled.

No GitHub repository-setting mutation capability is available in this CI
adoption workflow. Until a repository administrator enables Dependency Graph
under `Settings → Security & analysis`, the Shared caller must explicitly
use `dependency_review_enabled: false`. This is tracked as **BLOCKED**, not
`PASSED` or a policy exception. Restore `true` after enabling the setting and
validate the PR-dependency-review evidence; native cargo-audit, pip-audit and
Trivy remain mandatory in the meantime.

### PyO3 compatibility with the Shared Rust all-feature test gate

The generic Shared `cargo test --workspace --all-features --locked` exposed a
real linker incompatibility: the crate-local feature named
`extension-module` activated `pyo3/extension-module` even for test executables.
That feature deliberately leaves Python C API symbols unresolved for a
Python-loaded shared library, so test executable linking fails on Linux.

The Rust crate no longer advertises that feature to general `--all-features`
workflows; maturin explicitly enables the **dependency** feature
`pyo3/extension-module` for CPython 3.14 wheel construction. This preserves
the required native extension ABI and does not weaken the Shared Rust
formatter, Clippy or test rules. HYB-01 independent wheel/ABI CI verifies it.

### Strict dependency-maintenance conformance

The merged Shared `enforce-dependabot-config.yml` at the same reviewed SHA
`584d7f3cd8426ffd3d1dc9f068f0b444dc74346e` replaces the older
baseline-only enforcement inherited from PR #22. The consumer now sets
`policy-level: strict` and requires `github-actions,pip,cargo,docker,docker-compose`.
The PR #22 independent policy-negatives and daily security audit remain.
This is a **stricter** gate, not an exception; the user-authorised
maintenance policy remains in force.
