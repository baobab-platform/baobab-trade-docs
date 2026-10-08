# TDOC-TECH-01 — Headless, Self-Hosted Trade Document Runtime and Implementation Strategy

**Status:** Proposed — engine-local technology choice for review; documentation only, **NOT** runtime implementation or production acceptance  
**Date:** 2026-10-08  
**Repository:** baobab-platform/baobab-trade-docs  
**Scope:** engine technology, immutable document persistence, artifact handling, workflow execution, external integrations and staged delivery  
**Authority:** Accepted ADR-TDOC-0001/0002, Shared ADR-SHARED-019 through 024 and current RTD-04 through RTD-10 contracts  
**Initial consumers:** Thamani, ZuriBeans, Trade, TMS, Regulations, ERP  
**Current evidence:** repository is `ARCHITECTURE_ONLY` per `.baobab/rtd-conformance.yaml`; Shared has activated several document **contract/event definitions**, not a deployed Trade Docs publisher

## 1. Decision proposed

Build one **Baobab-owned, API-first, headless, self-hosted** Trade Docs engine. Proposed service baseline is **Python 3.14, Django 6.0, PostgreSQL 17**, using existing Baobab Python/PostgreSQL deployment patterns. No required admin/customer frontend and no direct dependency on third-party SaaS or a new JVM/PHP application family. Django is a proposed implementation technology, not a modification to any Shared wire contract.

Separate:

1. canonical document identity/version/content/relationship/verification domain (Baobab-owned);
2. transactional metadata, immutable history and workflow execution (PostgreSQL);
3. encrypted immutable content artifacts (approved S3-compatible self-hosted object storage; choice subject to infrastructure/security review);
4. optional **out-of-process rendering**, **signing**, **OCR**, **customs gateway** and **workflow adapters**, added only when corresponding business need, licence, legal and runtime evidence is accepted.

Gotenberg is a candidate self-hosted PDF renderer. It is **not** core document authority and **not** required for initial identity/version implementation. A new Java BPMN workflow product (e.g., Flowable) is **not** selected for the baseline. A signing product (e.g., Documenso) is **not** selected by default. This avoids bringing in extra mandatory operational stacks merely because such products provide useful auxiliary functions.

## 2. Normative contracts and precedence

| Source | Inherited rule | Technology implication |
|---|---|---|
| ADR-TDOC-0001 | Trade Docs owns executable document and Customs-workflow semantics but not customs/regulatory legal authority | Adapter-only customs decisions, no silent "released" action |
| ADR-TDOC-0002 | `TradeDocument`, `DocumentVersion`, `DocumentContent`, `ContentArtifact` and relationships are distinct | Separate relational aggregates and immutable artifacts |
| ADR-SHARED-020 / RTD-04 | `contracts/trade-document/v2` is implementation target; `v1` remains compatibility history | Validate against v2 schema and event shapes; no v1 reactivation |
| ADR-SHARED-021 / RTD-05 | Pinned `CrossEngineObjectReference`, tenant scoping and historical references | Do not copy other engines' aggregates or infer access from possession of reference |
| ADR-SHARED-022 / RTD-06 | Regulations -> Trade Docs requirement projection; Trade Docs -> Regulations documentary fact evidence | Implement exact `POST /v1/regulatory-document-evidence/resolve` wire shape |
| ADR-SHARED-023 / RTD-07 | Trade Docs steward/producer of canonical `documents.*` activated Shared event types | Event contract status != runtime event producer availability |
| ADR-SHARED-024 / RTD-08 | Regulations produces legal requirement and satisfaction events | Do not emit Regulations events |
| RTD-10 | Architecture conformance CI records known ADR/contracts and evidence | Keep maturity at ARCHITECTURE_ONLY until code/test evidence actually exists |

This document cannot supersede Shared, move producer authority, change canonical capability keys or declare a provider active. Resolve conflicts through Shared governance.

## 3. Open-source component strategy

| Function | Selection stance | Licence / operational consequence |
|---|---|---|
| Domain service and APIs | **Propose** Django 6 / Python 3.14 | Already-used Baobab language family; versions, library compatibility and CVEs must be verified at runtime-spike gate |
| Metadata, outbox, inbox, workflow transitions | **Propose** PostgreSQL 17 transactions and domain workers | Existing platform database family; distinct engine DB/schema, no shared operational DB |
| Artifact storage | S3-compatible object storage, **product to be approved** | Encryption, digest, versioning/immutability, private access and retention; no public buckets |
| Document rendering | **Evaluate** [Gotenberg](https://github.com/gotenberg/gotenberg) (MIT) | Separate self-hosted PDF worker; Chromium/LibreOffice increase operational footprint; optional after measured need |
| Electronic signatures | **Defer** [Documenso](https://github.com/documenso/documenso) or qualified provider | AGPL/commercial-feature and jurisdictional signature-law reviews; signing ≠ issuer authority |
| BPMN/CMMN | **Defer** [Flowable](https://github.com/flowable/flowable-engine) | Optional, but introduces JVM runtime; prefer Python domain-state workflow and audited approval transitions initially |
| OCR / extraction | Port only; **no vendor chosen** | Extracted assertions are `BAOBAB_EXTRACTED`, never silently `ISSUER_ASSERTED` |
| Customs gateway | Port per actual competent authority/intermediary | No invented universal Customs API, national credentials or submission success claims |
| Electronic transferable records | External scheme/provider only after legal/control assessment | PDFs or ordinary electronic signatures do not establish exclusive control or transferable-record validity |

No code from a prospective upstream product should be vendorized without pinned commit, SPDX licence and transitive-dependency verification, vulnerability scanning, maintainer review, upgrade plan and test evidence.

## 4. Proposed internal components

~~~text
Authenticated digital estate / Trade / TMS / Regulations / ERP
  -> CP trusted context + IAM identity
  -> Trade Docs HTTP API (Django ASGI-compatible)
     -> Document command/query application services
        -> TradeDocument identity and typed subjects
        -> immutable DocumentVersion + ContentArtifact manifest
        -> document graph and dossiers
        -> verification & temporal-validity projections (separate from lifecycle)
        -> documentary workflow with maker/checker, case transitions
        -> RTD-06 pinned fact bundle resolver
        -> CustomsCase / declaration ports (later gates)
     -> PostgreSQL domain records, revision locks, audit, inbox/outbox
     -> encrypted, private object-store artifact adapter
     -> optional PDF/render, signature, OCR, external customs adapters
     -> Shared documents fact events / regulatory-evidence.offered
~~~

Keep document data in this engine; let consumers resolve **authorised, purpose-bound projections** rather than distributing raw original files or direct object-storage addresses. TMS proof-of-delivery, Trade invoice, ERP accounting and Regulations decisions remain their owners' facts. Trade Docs may host documentary representations without claiming the underlying commercial, inventory or financial state.

## 5. Aggregate, storage and provenance invariants

- **Document identity:** owner-generated stable `trade_document_id`, separate from CP CanonicalEntity, business number and storage URI.
- **Immutable version:** `document_version_id` identifies a frozen semantic snapshot. Corrections become new version or new legal instrument under document-type policy; previously issued content is never overwritten.
- **Artifacts:** each `ContentArtifact` has opaque protected storage reference, role, media type, SHA-256 or approved content digest, length, integrity/format metadata, encryption version and relationship to a pinned version. Actual encoding, digest and availability requirements follow Shared v2 schema; local auxiliary fields shall not change canonical wire shape.
- **Verification:** distinguish issuer claim, extraction, external normalization, internal review, signature verification and legal sufficiency. A hash match proves integrity, not authenticity.
- **Validity:** time-bound validity and revocation facts are orthogonal to document lifecycle and Customs approval. Historical versions remain resolvable under retention/legal-hold policy.
- **References:** enforce RTD-05 `owner_engine_id / object_type / object_id / reference_mode / scope`, as permitted by the actual contract. Historical decisions must cite immutable version identities.
- **Tenant security:** CP-redeemed context, IAM principal/workload identity, operation entitlement, business relationships and per-artifact authorization. One tenant must never resolve another tenant's document merely by knowing an ID.
- **Persistence:** own DB transactions and optimistic version checks, outbox write in same transaction as issued fact, inbox deduplication, idempotent commands, replay-safe document issuance and version history. No distributed ACID.
- **Evidence retention:** audit who submitted, reviewed, approved, signed, issued, superseded or voided a document and the exact prior/current version, decision basis, local/event timestamps and causal correlation.
- **Data governance:** private objects, encryption at rest/in transit, key management, POPIA and market-specific retention/data-residency review, malware checks, content-type validation, access logging, backup/restore and deletion/legal-hold distinction.

Do not make a single table or S3 object serve as `TradeDocument`, `DocumentVersion`, document content and a CustomsCase simultaneously.

## 6. Workflows and guardrails

Initial workflow engine is a **code-defined, audited state transition model** in Python with PostgreSQL-backed durable command/work-item state. Long-running steps use persistent outbox/inbox messages and explicit timeouts, retry budgets, compensating steps and escalation; no indefinitely in-memory pending operation.

~~~text
Trade / TMS -> Regulations determines documentary requirements
         -> Trade Docs assembles dossier, obtains issuer/document assertions
         -> immutable version and verification facts recorded
         -> Trade Docs offers exact pinned version evidence
         -> Regulations assesses legal sufficiency
         -> if authorised, a separate customs submission workflow may proceed
         -> external authority accepts / rejects / releases via verified adapter
         -> TMS/Trade enforce business consequences with their own policies
~~~

**Hard separations:** `evidence offered != evidence accepted`; `verification != regulatory satisfaction`; `authority accepted != customs released`; `customs released != delivered`; `document issued != legally transferable`. Denial, timeout or missing authority proof must not become an optimistic business success.

## 7. Canonical API/event constraints

After implementation, the exact Shared `contracts/regulatory-document-exchange/v1/trade-docs.openapi.yaml` governs:

- `POST /v1/regulatory-document-evidence/resolve`: resolve documentary fact bundle(s) for **exact pinned** DocumentVersion reference(s) and authorised tenant.
- Normal document command/query surfaces must evolve under accepted Shared `trade-document/v2` or later contract approval, not ad hoc incompatible APIs.
- Event types such as `com.baobab-platform.documents.trade-document.created.v2`, `com.baobab-platform.documents.document-version.issued.v2` and `com.baobab-platform.documents.regulatory-evidence.offered.v1` are **contract-activated** under RTD-07; producer runtime is **not implemented in this PR**.
- Exactly once delivery cannot be assumed. Emit transactional outbox entries and design idempotent consumers; document issue remains safe under replay.
- The `documentary-evidence/assessments` operation is **a command owned by Regulations**, not a Trade Docs event nor a local legal determination.

Consumers must distinguish *an available API*, *a provider declaration*, *Shared event authority*, and *an activated certified CP provider*.

## 8. Distinct implementation gates

| Gate | Work and acceptance evidence | Explicit exit limitation |
|---|---|---|
| **TDOC-TECH-01A — Framework proof** | Django6/Python3.14/PostgreSQL17 matrix; frozen dependencies, ASGI/API proof, Docker/devcontainer and licence/security review | No runtime selected as production merely by container boot |
| **TDOC-TECH-01B — Artifact proof** | Private object-store option decision, verified digest/immutability, encryption, malware scan, restore and retention evidence | No public file URLs or claimed document verification |
| **TDOC-IMP-01 — Canonical domain** | Implement TradeDocument v2, immutable DocumentVersion, typed subjects, relationships, content artifacts; schema/contract tests | No v1 mutation or false issuance authority |
| **TDOC-IMP-02 — Context-bound APIs** | IAM workload/user auth, redeemed CP context, object/tenant policy, pagination and negative isolation tests | Reference possession is insufficient for access |
| **TDOC-IMP-03 — Durable event spine** | Transactional outbox/inbox, idempotent issue/supersede/void, ordered revisions, retry/replay reconciliation; exact activated Shared events | Publication claims require implementation and contract evidence |
| **TDOC-IMP-04 — RTD-06 evidence** | `/v1/regulatory-document-evidence/resolve` conformance; pinned immutable version, issuer/extracted provenance; integration with Regulations assessment API | No local decision on regulatory sufficiency |
| **TDOC-IMP-05 — Dossiers/workflow** | Maker/checker, document requirements references, state transitions, evidence bundles, expiry/revocation and audit tests | No automatic customs submission |
| **TDOC-IMP-06 — Rendition/signature adapter** | Optional Gotenberg/spin-up and render fidelity/performance; optional signing/legal/licence evaluation | Neither renderer nor signature implies legal authenticity |
| **TDOC-IMP-07 — Customs adapters** | One jurisdiction-specific authorised interface, signed/secured submission, authority receipt/callback verification and legal hold/release semantics | No generic Customs integration claim |
| **TDOC-REL-01 — Readiness** | Live deployment security, isolation tests, storage restore, provenance replay, ADR/contract conformance, CP provider registration and EA-09 certification | Production readiness requires external evidence beyond merge/CI |

Each gate uses a bounded PR and evidence. `.baobab/rtd-conformance.yaml` shall remain honest: currently `ARCHITECTURE_ONLY` and `source_paths: [] / test_paths: []`. Update only when *real code and tests exist*, not for this proposal.

## 9. Initial acceptance journey

Use one ZuriBeans UG -> ZA cross-border commercial transaction and one Thamani transport-document scenario:

1. Authenticated, tenant-scoped client creates TradeDocument with typed subject references; separate immutable document version and private artifact stored, integrity manifest tested.
2. Original, human-readable rendition and extracted values preserve their distinct provenance; untrusted OCR cannot mark verification as issuer-verified.
3. A new version supersedes the former only according to document-type policy; historical evidence resolves exact older version.
4. Regulations supplies a pinned documentary requirement and receives only a contract-valid `DocumentEvidenceFactBundle` after authorised resolve.
5. Regulations decides evidence sufficiency; Trade Docs does not implement that legal rule or infer Customs release.
6. Published `documents.*` facts are reproducible from durable outbox, idempotent on retry, tenant-scoped and provably emitted by runtime **only after TDOC-IMP-03**.
7. Rejection tests cover wrong-tenant reference, forged issuer metadata, manipulated artifact digest, stale/expired version, unauthorised issue, replay and missing external authority acknowledgement.

## 10. Explicit non-claims and follow-up

This PR delivers **no application source, tests, API runtime, content storage instance, published events, operating Customs integration, self-hosted infrastructure, licensed signature scheme, provider-support declaration, certification or production activation**. Contract activation in Shared is a governance status, not evidence of a running publisher. Do not claim otherwise.

**Approval sought:** same-stack headless/self-hosted approach, strict engine authority, component evaluation scope, and distinct gates. Exact library, renderer, storage and workflow choices remain subject to compatibility, licensing, cost and security proof.

## 11. Sources

- [Trade Docs ADR index](../adr/README.md)
- [RTD architecture conformance record](../../.baobab/rtd-conformance.yaml)
- [Shared TradeDocument v2](https://github.com/baobab-platform/shared/tree/main/contracts/trade-document/v2)
- [Shared regulatory-document exchange](https://github.com/baobab-platform/shared/tree/main/contracts/regulatory-document-exchange/v1)
- [Shared cross-engine reference](https://github.com/baobab-platform/shared/tree/main/contracts/cross-engine-reference/v1)
