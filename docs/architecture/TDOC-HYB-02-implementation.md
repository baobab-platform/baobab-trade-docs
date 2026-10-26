# TDOC-HYB-02 — Deterministic kernel, Shared v2 conformance and ABI evidence

**Status: PARTIAL — not accepted or merged.** Governing baseline: Accepted TDOC-TECH-02, Shared owner commit `a9c53087d63caa356edf54ec8037ba1713c4827f`. RTD-10 remains `ARCHITECTURE_ONLY`.

## Evidence delivered in PR #19

| Layer | Implemented | Qualification limitation |
|---|---|---|
| Rust PyO3 | Pure exact-byte SHA-256 (16 MiB maximum), identifier grammars, separate state axes, conservative lifecycle candidate check | No authorisation, legal/regulatory assessment or database |
| Differential vectors | Python regex/enums/hashlib independently check Rust; malformed and boundary cases | Field-level, not full nested semantic parity |
| Schema inventory | Every definition in locked trade-document/v2 domain/events, cross-engine-reference, regulatory-document-exchange and event envelope is schema-compiled; owner bytes compared with packaged SHA-256 pins | Compiling and resolving definitions is not proof of complete valid/invalid instance coverage |
| Adversarial fuzz | 3,000 seeded mutation cases and binary digest vectors with stable seeds | Not libFuzzer/AFL coverage-guided fuzz; no corpus minimisation or sanitiser report |
| ABI smoke | CPython 3.14 native extension import, architecture whitelist, free-threaded rejection, export assertions | Only architectures actually executed in CI are qualified |

## Non-negotiable remaining exit proof

1. Produce owner-derived positive and negative nested instances for **every** Shared v2 definition and conditional; test Python packaged validator against independent owner validator, including cross-engine references and event payloads. Keep provenance and contract revision pinned. Never substitute Rust ad hoc validation for the normative JSON Schema engine.
2. Execute coverage-guided fuzzing with persisted seeds/crash corpus, panic/resource-bound negative tests and a documented fuzz-duration budget.
3. Run an explicit native-wheel matrix on Linux x86_64 **and** aarch64 for CPython 3.14 with wheel-tag inspection and import checks, using immutable runners/images. Report skipped architecture as unqualified.
4. Obtain all final-head CI, security, no-cache DevContainer and RTD-10 checks; record run IDs, artifact hashes and independent review.

The kernel's `transition_candidate` is a **structural hint only**, not an authoritative state-machine policy. Lifecycle policy must be accepted separately and fenced by IAM/CP in HYB-04. No issuing endpoint, artifact custody, outbox, Customs submission or regulatory sufficiency is created by this gate.

## Conformance execution

Existing RTD-10 tests execute the owner-byte comparison and schema inventory in the reference suite. HYB-01's native-wheel runtime test suite executes the PyO3 differential, seeded adversarial mutation and ABI smoke checks. CI job logs, not this document, determine the actual pass/fail result.
