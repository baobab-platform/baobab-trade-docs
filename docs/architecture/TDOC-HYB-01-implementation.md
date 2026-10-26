# TDOC-HYB-01 — Reproducible hybrid runtime and security qualification

**Governing authority:** Accepted [TDOC-TECH-02](TDOC-TECH-02.md), Shared EA v2.3, Accepted ADR-TDOC-0001/0002, existing RTD-10 conformance.  
**Gate:** TDOC-HYB-01.  
**Scope:** Development-runtime integrity ONLY; no canonical document issue, Customs submission or activated provider.  
**Decision status:** Architecture Accepted; HYB-01 qualification requires **all** mandatory final-head checks and retained evidence.  
**RTD-10 maturity:** `ARCHITECTURE_ONLY` remains authoritative until later gates provide operating source/domain acceptance.

## 1. Actual implementation

The repository has a Django 6/Python 3.14 diagnostics-only runtime, a native Rust/PyO3 integrity probe, and PostgreSQL 17 tests. All domain issuer, version, regulatory and Customs APIs remain deliberately absent. This gate asserts reproducible packaging and protected execution foundations, **not** business-authority qualification.

### Dependency closure

| Dependency | Governing version/proof | Enforcement |
|---|---|---|
| Python interpreter | CPython 3.14 in CI, Python 3.14 in DevContainer | GitHub Actions `setup-python`, pinned MCR multi-arch image |
| Django / Psycopg / maturin | Exact versions and SHA-256 distribution hashes in `runtime/requirements.lock` | `uv pip sync --require-hashes` with pinned `uv==0.13.5` |
| Rust | 1.90.0 | `rust-toolchain.toml`, pinned rust-toolchain action, Dockerfile argument |
| PyO3 and sha2 | Exact versions, registry checksums and dependencies in `rust-kernel/Cargo.lock` | `cargo test --locked` and `maturin build --locked` |
| DevContainer base | `mcr.microsoft.com/devcontainers/python:dev-3.14-bookworm@sha256:4a146bbf4b85b374c9d094f839cb377bd6dbd8f15a498a3bd39e4cec264294f3` | Immutable OCI index |
| PostgreSQL | `postgres:17.11-bookworm@sha256:858bb5e98eed02eb8cafbcdc007f9a65d1b613972028944a8ec2133ccaf80d27` | Immutable OCI index in CI and Compose |
| GitHub Actions | Every external action reference is a full 40-character commit SHA | Platform mandatory Enforce Action Pinning |
| Shared contract reference | Existing canonical `contracts.lock.yaml` and unchanged LA-05F reference vectors | Existing RTD-10 and LA-05F workflows |

Python package hash locking is distinct from the **locally built** `baobab-tdoc-kernel` wheel: that wheel is rebuilt on each cold CI run from exact Git source, checksummed Cargo.lock dependencies and pinned Rust, and installed from its own wheel directory with `--no-index --no-deps`; it is not looked up in PyPI.

The foundation does not attempt bit-for-bit deterministic native binary output across independent build hosts. That stronger requirement would need reproducible build comparisons, platform ABI and compiler/linker/environment normalization. At this gate, the correct claim is **dependency-resolved, cold-build reproducibility with independently verified runtime behaviour**.

### CI jobs and required evidence

1. **hybrid-runtime** — Python 3.14 and Rust 1.90, file digest guard, recompute Python lock and byte-compare, `cargo metadata --locked`, SHA-256 verified Python sync, `cargo test --locked`, native wheel build/import, Django 6 checks/migrations and a real PostgreSQL 17 DB version assertion.
2. **cold-devcontainer** — Docker Compose `build --no-cache --pull` with OCI digest-pinned base and PostgreSQL; bring up a disposable healthy DB and workspace, execute the same locked bootstrap as the configured Codespaces `postCreateCommand`, and tear down **with `down -v --remove-orphans` even after failures**.
3. **security-evidence** — Python lock vulnerability scan (pip-audit) and CycloneDX inventory, RustSec advisory scan for Rust Cargo.lock, Syft-derived repository CycloneDX SBOM, retained GitHub evidence artifacts. Scanner failures block qualification; no suppressions or fabricated clean scans.
4. **Repository gates** — RTD-10 cross-repository conformance, unchanged LA-05F issuer reference, secret scan and immutable GitHub Action references.

**Evidence authority:** GitHub Actions final-head run and its job logs/artifact digests. A passing old-head run or an architecture-only ADR never substitutes for final-head runtime evidence.

## 2. Reproduction from Codespaces

Open this repository in Codespaces; `.devcontainer/devcontainer.json` uses the pinned base and PG Compose service, automatically running:

```sh
bash scripts/hyb01-bootstrap.sh
```

The bootstrap:
- checks versions and database readiness;
- creates an isolated venv under `$HOME/.cache/baobab-tdoc/venv` (not the potentially read-only mounted checkout);
- verifies hash-locked Python dependency installations;
- uses `cargo test --locked`, `maturin build --locked` and installs the **locally built** wheel offline;
- runs Django checks, migrations and PostgreSQL-backed tests.

No public port or issuance endpoint is exposed by the DevContainer. Development DB credentials are local test-only; never reuse them in staging/production.

A local developer can verify freshness of locks using:

```sh
python -m pip install uv==0.13.5
cp runtime/requirements.lock /tmp/tdoc-python.lock
uv pip compile --python-version 3.14 --generate-hashes --output-file runtime/requirements.lock runtime/requirements.in
diff -u /tmp/tdoc-python.lock runtime/requirements.lock
(cd rust-kernel && cargo metadata --locked --format-version 1 --no-deps > /dev/null)
```

Lockfiles must be updated by reviewed dependency-upgrade PRs. Never run with `--ignore-rust-version`, disable vulnerability checks or replace lock files with unconstrained dependency ranges merely to make CI green.

## 3. Security hardening and known findings

An initial HYB-01 security run found two **published RustSec PyO3 0.27.1 advisories** (memory-safety/thread-safety invariants): the vulnerable version was **upgraded to PyO3 0.30.1** and `Cargo.lock` regenerated rather than accepting ignored vulnerabilities. Retained final-head RustSec audit must demonstrate that the advisories are not present.

Scripts avoid writing generated virtualenvs, Rust target directories or wheels to GitHub's host-mounted checkout, which can be owned by a different UID than `vscode`. Codespaces and CI must both run the documented bootstrap as the non-root workspace user.

The dependency-locked bootstrap uses TLS to install the pinned `uv` release and rustup distribution; supply-chain hardening for protected runtime images additionally requires build attestation, SBOM review, installer-origin verification, signed images, managed runtime credentials and regular CVE re-evaluation. None of these is waived by HYB-01 approval.

## 4. Gate boundaries and release prohibition

HYB-01 proves infrastructure reproducibility, not correct documentary policy. `ARCHITECTURE_ONLY` remains unchanged. **No activated issuer, live CP/IAM token resolution, protected artifact custody, audit/outbox, document event producer, Customs legal permission or cross-border regulatory certification** results from the passing scaffold. These are gated by HYB-02..07 and Shared/CP policy.

Required reviewer checklist:
- [ ] Immutable toolchain/dependency closure and SHA-pinned images/actions verified.
- [ ] Clean DevContainer no-cache build plus end-to-end bootstrap passed using Python 3.14, Rust and PostgreSQL 17.
- [ ] Real PostgreSQL migrations and negative native-import/DB assumptions verified.
- [ ] RustSec and Python vulnerability scans successful without suppressions; retained CycloneDX evidence.
- [ ] RTD-10, LA-05F, secret scanning, and action-pinning checks green at final PR head.
- [ ] CI evidence, run IDs, artifact IDs/hashes and limitations retained in the PR.
- [ ] HYB-02 implementation NOT started as substitute for incomplete HYB-01 evidence.

## 5. Sources for binary/image/version evidence

- Microsoft Artifact Registry — DevContainer Python OCI index: https://mcr.microsoft.com/product/devcontainers/python
- Docker Official Postgres 17.11 bookworm index: https://github.com/docker-library/repo-info/blob/master/repos/postgres/remote/17.11-bookworm.md
- Django 6.0: https://docs.djangoproject.com/en/6.0/releases/6.0/
- PyO3: https://pyo3.rs/ and https://github.com/PyO3/pyo3/releases
- maturin: https://www.maturin.rs/
- RustSec: https://rustsec.org/ and https://github.com/rustsec/rustsec
- uv: https://docs.astral.sh/uv/ and https://pypi.org/project/uv/0.13.5/

**No independently issued Customs, legally binding document or production access is tested in this gate.**
