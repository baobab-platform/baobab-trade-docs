# Baobab Trade Docs — Architecture Decision Register

**Repository:** `baobab-platform/baobab-trade-docs`  
**Reviewed:** 2026-10-08  
**Implementation maturity:** `ARCHITECTURE_ONLY` — runtime/application source paths and implementation test paths are not yet present in `.baobab/rtd-conformance.yaml`.

## Normative precedence

1. **Accepted ADR-TDOC-0001**: engine mission, document/case authority and the Regulations–Trade Docs–TMS–ERP boundary.
2. **Accepted ADR-TDOC-0002**: canonical TradeDocument, immutable DocumentVersion, DocumentContent/ContentArtifact, typed subjects, provenance, verification, status and relationship models.
3. **Accepted Shared ADR-SHARED-019..024 and 026**, according to their respective scope: Regulations–Trade Docs–Pulse ownership, `trade-document/v2` RTD-04, `cross-engine-reference/v1` RTD-05, documentary evidence/assessment RTD-06, `documents` producer/context activation RTD-07, Regulations event authority RTD-08, cross-repository conformance RTD-10.
4. [TDOC-TECH-01](../architecture/TDOC-TECH-01%20%E2%80%94%20Headless%20Self-Hosted%20Trade%20Document%20Runtime.md): separate **Proposed** self-hosted headless Python 3.14/Django 6.0/PostgreSQL 17 technology direction. This documentation was merged but not thereby accepted as production evidence.
5. **Proposed ADR-TDOC-0003..0019** specify executable design intent and distinct gate evidence, but **do not override** accepted ADRs or Shared wire contracts.

An engine-local ADR **does not** create canonical Shared keys, events, cross-engine types, Customs authority, customer legal permissions or an active Control Plane provider. Formal acceptance must be recorded deliberately, not inferred from PR merge.

## ADR catalogue

| ADR | Status | Decision |
|---|---|---|
| ADR-TDOC-0001 | **Accepted** | [ADR-TDOC-0001 — Baobab Trade Docs Mission, Authority, Executable Trade Document and Customs Workflow Boundary](./ADR-TDOC-0001%20%E2%80%94%20Baobab%20Trade%20Docs%20Mission%2C%20Authority%2C%20Executable%20Trade%20Document%20and%20Customs%20Workflow%20Boundary.md) |
| ADR-TDOC-0002 | **Accepted** | [ADR-TDOC-0002 — Canonical TradeDocument, Version, Content and Relationship Model](./ADR-TDOC-0002%20%E2%80%94%20Canonical%20TradeDocument%2C%20Version%2C%20Content%20and%20Relationship%20Model.md) |
| ADR-TDOC-0003 | **Proposed** | [ADR-TDOC-0003 — Document Dossier, Requirement and Completeness Architecture](./ADR-TDOC-0003%20%E2%80%94%20Document%20Dossier%2C%20Requirement%20and%20Completeness%20Architecture.md) |
| ADR-TDOC-0004 | **Proposed** | [ADR-TDOC-0004 — Customs Case, Declaration and Authority Decision Projection Model](./ADR-TDOC-0004%20%E2%80%94%20Customs%20Case%2C%20Declaration%20and%20Authority%20Decision%20Projection%20Model.md) |
| ADR-TDOC-0005 | **Proposed** | [ADR-TDOC-0005 — Customs Authority Adapter, Submission and Response Architecture](./ADR-TDOC-0005%20%E2%80%94%20Customs%20Authority%20Adapter%2C%20Submission%20and%20Response%20Architecture.md) |
| ADR-TDOC-0006 | **Proposed** | [ADR-TDOC-0006 — Transit, Guarantee, Seal and Acquittal Architecture](./ADR-TDOC-0006%20%E2%80%94%20Transit%2C%20Guarantee%2C%20Seal%20and%20Acquittal%20Architecture.md) |
| ADR-TDOC-0007 | **Proposed** | [ADR-TDOC-0007 — Issuer, Signature, Credential and Representative Authority](./ADR-TDOC-0007%20%E2%80%94%20Issuer%2C%20Signature%2C%20Credential%20and%20Representative%20Authority.md) |
| ADR-TDOC-0008 | **Proposed** | [ADR-TDOC-0008 — Evidence, Provenance, Verification and Discrepancy Architecture](./ADR-TDOC-0008%20%E2%80%94%20Evidence%2C%20Provenance%2C%20Verification%20and%20Discrepancy%20Architecture.md) |
| ADR-TDOC-0009 | **Proposed** | [ADR-TDOC-0009 — Document Content Storage, Encryption and Integrity Architecture](./ADR-TDOC-0009%20%E2%80%94%20Document%20Content%20Storage%2C%20Encryption%20and%20Integrity%20Architecture.md) |
| ADR-TDOC-0010 | **Proposed** | [CEFACT, EDI and National Message Interoperability](./CEFACT%2C%20EDI%20and%20National%20Message%20Interoperability.md) |
| ADR-TDOC-0011 | **Proposed** | [ADR-TDOC-0011 — Tenant, Isolation, Residency and Retention Architecture](./ADR-TDOC-0011%20%E2%80%94%20Tenant%2C%20Isolation%2C%20Residency%20and%20Retention%20Architecture.md) |
| ADR-TDOC-0012 | **Proposed** | [ADR-TDOC-0012 — API, Events, Idempotency and Durable Workflow Architecture](./ADR-TDOC-0012%20%E2%80%94%20API%2C%20Events%2C%20Idempotency%20and%20Durable%20Workflow%20Architecture.md) |
| ADR-TDOC-0013 | **Proposed** | [ADR-TDOC-0013 — Security, Audit and Privileged Customs Operations](./ADR-TDOC-0013%20%E2%80%94%20Security%2C%20Audit%20and%20Privileged%20Customs%20Operations.md) |
| ADR-TDOC-0014 | **Proposed** | [ADR-TDOC-0014 — Observability, Authority Outage, Reconciliation and DR](./ADR-TDOC-0014%20%E2%80%94%20Observability%2C%20Authority%20Outage%2C%20Reconciliation%20and%20DR.md) |
| ADR-TDOC-0015 | **Proposed** | [ADR-TDOC-0015 — Production Readiness, Capability Certification and Migration](./ADR-TDOC-0015%20%E2%80%94%20Production%20Readiness%2C%20Capability%20Certification%20and%20Migration.md) |
| ADR-TDOC-0016 | **Proposed** | [ADR-TDOC-0016 — Governed Document Type Registry, Schema Profiles and Template Policy](./ADR-TDOC-0016%20%E2%80%94%20Governed%20Document%20Type%20Registry%2C%20Schema%20Profiles%20and%20Template%20Policy.md) |
| ADR-TDOC-0017 | **Proposed** | [ADR-TDOC-0017 — Electronic Transferable Records, Exclusive Control and eBL Interoperability](./ADR-TDOC-0017%20%E2%80%94%20Electronic%20Transferable%20Records%2C%20Exclusive%20Control%20and%20eBL%20Interoperability.md) |
| ADR-TDOC-0018 | **Proposed** | [ADR-TDOC-0018 — Cross-Organisation Document Exchange, Disclosure and Consent Architecture](./ADR-TDOC-0018%20%E2%80%94%20Cross-Organisation%20Document%20Exchange%2C%20Disclosure%20and%20Consent%20Architecture.md) |
| ADR-TDOC-0019 | **Proposed** | [ADR-TDOC-0019 — Document Extraction, Semantic Normalisation and AI-Assisted Validation](./ADR-TDOC-0019%20%E2%80%94%20Document%20Extraction%2C%20Semantic%20Normalisation%20and%20AI-Assisted%20Validation.md) |

**Programme origin:** ADR-TDOC-0003..0015 implement the **initial future-ADR programme explicitly proposed in ADR-TDOC-0001 §93**. ADR-TDOC-0016..0019 are newly proposed extensions: document-type registry, ETR/eBL control, cross-organisation disclosure and assisted extraction.

## Implementation dependency and execution order

| Programme phase | Relevant ADRs | Measurable output |
|---|---|---|
| 0. Foundation / trusted service | TDOC-TECH-01, 0009, 0011, 0012, 0013 | Reproducible self-hosted runtime, verified IAM/CP context, protected PostgreSQL/object storage and durable API |
| 1. Canonical document | Accepted 0002 + proposed 0007, 0008, 0016 | Immutable versions, issuer/verification facts, governed document types, source provenance |
| 2. Dossier and extraction | 0003, 0019 | Pinned documentary requirements, dossiers, provenance-safe ingestion and RTD-06 evidence resolution |
| 3. Customs operations | 0004, 0005, 0006, 0010 | CustomsCase and declarations, national adapter, transit and standards-versioned messages |
| 4. External document exchange | 0017, 0018 | Legally gated transferable-record control and secure cross-party disclosure |
| 5. Certification and recovery | 0014, 0015 | Recoverable workflows, migration/conformance and independently approved capability/market activation |

**Gate names in the ADRs are planned implementation checkpoints**, not evidence that they have passed. Shared/cross-engine contract changes and consumer migration need separate PRs. Source-paths/test-paths may be added to the RTD-10 conformance record **only when real source and tests exist**.

## Initial vertical slice

~~~text
Authenticated ZuriBeans or Thamani caller with CP context
 -> Trade/ERP/TMS source references (each owner retains authority)
 -> Governed DocumentType + canonical TradeDocument
 -> Immutable DocumentVersion with protected ContentArtifact
 -> DocumentDossier with pinned Regulations RequirementSet
 -> Trade Docs RTD-06 DocumentEvidenceFactBundle resolve
 -> Regulations independent assessment
 -> Trade Docs documents.* outbox (only after actual implementation)
 -> Consumer reads document facts, not sovereign legal outcome invented locally
~~~

Prove negative scenarios: wrong tenant/issuer, absent requirements, stale evidence, revoked representative, corrupted content, duplicate issuance, out-of-order authority callbacks and replay. A synthetic Customs adapter shall be labelled simulation and never be production-permitted.

## Known contract/governance gaps

- Shared `documents.*.v2` and `regulatory-evidence.offered.v1` are **contract-level ACTIVE** with Trade Docs assigned producer; **no runtime publication has been demonstrated**.
- The Shared v1 document family is compatibility history, not an implementation target.
- Complete CustomsCase/CustomsDeclaration contracts, customs event stewardship migration from Trade, capability definitions and CP registration **remain separate governed work**.
- ADR-TDOC-0001 §91 contains an older "Regulations namespace convergence outstanding" status note; Shared subsequently established Regulations namespace/event authority in **ADR-SHARED-024**. Reconcile that historical note in a separate accepted-ADR amendment if needed; this register does not rewrite the accepted charter.
- External national Customs APIs, signature mandates and transferable-record law depend on actual schemes, authorities and applicable jurisdictions; no generic global support is asserted.

## Documentation review and readiness claims

These ADRs are **architecture proposals, not proof of runnable Django code, a storage platform, published events, authenticated Customs filing, national regulatory approval or production readiness**. A later implementation PR must link exact source, tests, Shared version, supported feature matrix, security and privacy review, failure/restore drills and independent Control Plane/EA-09 decision evidence.
