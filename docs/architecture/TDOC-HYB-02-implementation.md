# TDOC-HYB-02 — Deterministic Rust domain kernel and Shared v2 qualification

**Status:** IMPLEMENTED IN DRAFT PR #19; **NOT ACCEPTED** until final-head CI and evidence pass.
**Authority:** Accepted TDOC-TECH-02, Shared owner commit `a9c53087d63caa356edf54ec8037ba1713c4827f`, RTD-10. Conformance maturity stays `ARCHITECTURE_ONLY`.

## Implementation and boundaries

| Gate | Executable implementation | Qualification claim |
|---|---|---|
| Deterministic kernel | Pure Rust bounded identifier and type checks, state axes, conservative transition candidates, exact-byte SHA-256; PyO3 Python 3.14 wheel | Structural validation only, never authorisation |
| Locked Shared v2 | Owner-byte/digest parity; every `$defs` definition in Trade Docs v2 domain/events, cross-engine references, regulatory exchange domain/events and event envelope is compiled/resolved | Schema inventory, not mathematical completeness |
| Differential vectors | Python regex/enums/hashlib independent native checks, plus a deterministic malformed JSON shape matrix across every Shared definition | Owner/packaged validator parity; complete semantic positive/negative coverage is still an open requirement |
| Adversarial mutation | Seeded 3,000-case Python/PyO3 tests; separate libFuzzer `identifier` target with native Rust oracle, 60-second bounded campaign, retained corpus/crashes | Coverage-guided fuzzing for identifier core; not all document parsers or Python FFI functions |
| ABI | Matrix `ubuntu-24.04` (x86_64) and `ubuntu-24.04-arm` (aarch64), CPython 3.14 wheel tag and architecture assertion, native import and DB-backed tests | Qualified only when both matrix jobs pass and artifacts are retained |

## CI commands

```sh
(cd rust-kernel && cargo test --locked)
(cd rust-kernel && maturin build --locked --release --interpreter ../.venv/bin/python --out ../dist-wheels)
(cd runtime && ../.venv/bin/python manage.py test tests -v2)
(cd rust-kernel && cargo +nightly-2026-10-20 fuzz run identifier -- -max_total_time=60 -timeout=5 -rss_limit_mb=1024)
```

The `pyo3/extension-module` feature is enabled for the maturin wheel only; Rust test and libFuzzer binaries must link to a Python interpreter normally. The fuzz campaign is deliberately limited in time and memory; it does not claim to establish the absence of all memory-safety defects.

## Acceptance checklist

- [ ] All mandatory final-head CI including both native ABI architectures, clean DevContainer, RustSec, Python vulnerability audit, RTD-10, LA-05F and action-pinning checks green.
- [ ] Coverage-guided libFuzzer job green with retained crash/corpus evidence.
- [ ] No drift from Shared v2 owner SHA and packaged contract digests.
- [ ] Independently reviewed **valid and invalid** nested document, version, artifact, relationship and event vectors with owner-origin provenance, beyond schema compilation and shape probes.
- [ ] Fuzz all consequential Rust parser/validator entry points (not just identifiers), and retain evidence for each target.
- [ ] Review and record wheel tags, architecture evidence and free-threaded/abi3 exclusion.

**Conservative release rule:** until every item is evidenced, HYB-02 is PARTIAL. HYB-03 implementation is not authorised by this PR. No issuer activation, IAM/CP authority fence, artifact custody, outbox, Customs action or documentary legal sufficiency is provided.
