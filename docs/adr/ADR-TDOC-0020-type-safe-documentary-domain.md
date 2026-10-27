# ADR-TDOC-0020 — Type-Safe Documentary Domain Modelling and Invariant Enforcement

**Status:** Accepted — architecture-owner approval on 2026-10-26
**Scope:** TDOC-HYB-02, HYB-03 and HYB-04
**Supersedes:** None
**References:** Accepted TDOC-TECH-02; Shared trade-document/v2 and regulatory contracts at their locked owner revision; Accepted Shared EA v2.3; RTD-10.

## Context
The selected Python 3.14/Django 6.0/Rust/PyO3/PostgreSQL 17 composition does not automatically reproduce Kotlin sealed-type and immutable-data safety. The HYB-02 kernel currently validates strings and returns a boolean transition candidate; neither proves legal issuer authority nor prevents invalid domain aggregates from being constructed. A type-safe internal model must remain subordinate to Shared wire contracts and CP/IAM/Regulations authority.

## Proposed decision
1. **Rust pure domain kernel:** model lifecycle and independent verification/validity axes as exhaustive enums. Use private fields, checked constructors and opaque newtypes for IDs, immutable version values, typed provenance and candidate transitions. Match exhaustively; no silent default for unknown wire variants. Use explicit `Result<T, DomainError>` and `Option<T>`, with stable versioned PyO3 error mapping.
2. **Do not collapse authority axes:** lifecycle is Trade Docs-owned; verification is independent; temporal validity is independently observed; issuer mandate freshness belongs to IAM/CP; regulatory applicability and sufficiency belong to Regulations; Customs decisions belong to national authorities. A type named `VerifiedIssuanceEvidence` cannot imply independently rechecked live authority.
3. **Python application boundary:** Django application services own request parsing, IAM/CP redemption, dependency injection through explicit ports/protocols, idempotency, audit, transactional writes and event outbox. Rust must not call providers, write SQL, mint authority or make regulatory sufficiency decisions.
4. **Durability:** HYB-03 persists distinct Document, immutable DocumentVersion, ContentArtifact, references, verification observations, authority-evidence references and lifecycle/audit facts. PostgreSQL 17 enforces unique and foreign keys, scoped tenant/Organisation boundaries, revision fences, append-only protections and verified artifact custody. Never mutate issued versions in place.
5. **Authorised transitions:** HYB-04 must re-evaluate CP/IAM evidence and applicable grants at commit-time, deny stale/unknown/revoked authority, and atomically commit version/audit/outbox. A Rust transition candidate is necessary at most, never sufficient. Preserve external revocation race-window documentation.
6. **Compatibility:** Shared v2 remains the normative public wire format; typed Rust/Python objects are internal and must round-trip without altering field meanings or introducing new canonical authority. Unknown values fail closed until explicitly governed.
7. **Testing:** property-based state invariants, exhaustive match compiler checks, Python/Rust differential and Shared v2 schema vectors, database mutation/tenant-isolation tests, revocation/TOCTOU negatives and crash/retry evidence. No acceptance by unit tests alone.

## Gate mapping
- **HYB-02:** introduce typed Rust enums/newtypes, checked constructors, stable error mapping, wire adapters, differential/property/fuzz tests and ABI qualification. Preserve existing external functions during migration.
- **HYB-03:** introduce immutable Django/PostgreSQL domain persistence, constraints, scoped repositories, application ports and append-only custody evidence; qualify SQL-level bypass attempts.
- **HYB-04:** implement real CP/IAM principal/mandate evidence, transaction commit fence, revocation negatives, idempotency, audit and outbox atomicity; qualify connected authority.
- **HYB-05+** remain separate and must not be implied by this decision.

## Rejected alternatives
- **Kotlin/Spring Boot migration:** adds a second runtime and migration burden without uniquely solving authority or transaction correctness.
- **Rust as a second canonical service:** violates TDOC-TECH-02's single-engine boundary.
- **Python typing alone:** type hints are not runtime or database enforcement.
- **Strings plus schema checks alone:** allows invalid internal combinations and non-exhaustive handling.

## Adoption
This ADR is Accepted by the architecture owner on 2026-10-26. Acceptance authorises its architectural requirements and implementation sequencing; it does **not** qualify HYB-02/03/04, activate an issuer, or waive connected acceptance, security, ABI, conformance, or authority evidence. No widening of CP/IAM/Regulations authority is permitted.
