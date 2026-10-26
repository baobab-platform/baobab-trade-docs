# TDOC-HYB-02 — Deterministic Rust kernel

**Status:** PARTIAL; not qualified. **Authority:** Accepted TDOC-TECH-02, locked Shared trade-document/v2 at a9c53087d63caa356edf54ec8037ba1713c4827f. RTD-10 maturity remains ARCHITECTURE_ONLY.

## Implemented
- Pure PyO3 validation for exact Shared v2 opaque document, version, artifact, relationship identifiers and extensible document-type grammar.
- Exact enum checks for lifecycle, verification, validity and family; axes never conflated.
- Conservative lifecycle transition candidates, not an authorisation decision or an accepted complete lifecycle policy.
- Exact byte SHA-256 with a bounded input; no Unicode or JSON canonicalisation.
- Rust unit vectors and independent Python regex/enum/hashlib differential tests.

## Still required for full HYB-02 acceptance
1. Differential tests against **complete** locked Shared v2 JSON Schemas, including nested document versions, artifacts, relationships, cross-engine references, event payloads and conditional constraints.
2. Property-based and coverage-guided fuzzing with retained corpus, malformed-input denials, resource bounds and panic containment.
3. Explicit Python 3.14 wheel/ABI and Linux architecture matrix; do not assume abi3 or free-threaded compatibility.
4. Full final-head CI, RustSec, Python audit, clean Codespaces build and immutable evidence.

No IAM/CP issuer fence, documentary persistence, event producer, Customs privilege, legal sufficiency or activated provider is implemented or authorised by HYB-02.
