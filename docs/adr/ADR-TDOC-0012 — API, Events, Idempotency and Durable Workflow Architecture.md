# ADR-TDOC-0012 — API, Events, Idempotency and Durable Workflow Architecture

**Status:** Proposed — architecture review only; not accepted/implemented/production-certified  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Normative precedence:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and canonical TradeDocument v2, RTD-05 cross-engine reference and RTD-06/07/08 interfaces  
**Technology:** Proposed TDOC-TECH-01 self-hosted headless direction; code choices and certification remain separately gated  

> **Design vs operation:** This document defines engineering obligations and independently testable implementation gates. It cannot activate a provider, issue a sovereign Customs decision, move another engine's ownership or turn Shared's event registration into an executable publisher.


## 1. Decision
Trade Docs exposes **versioned, headless, IAM-authenticated, CP-context-bound APIs** for document identity/versioning, dossier and Customs workflow commands and read projections. Material document state changes and Shared events use a **transactional PostgreSQL outbox**, and incoming external/Shared facts use an authenticated, deduplicating **inbox**. All long-running issuer, signing, rendering and Customs submissions are persisted durable workflows.

~~~mermaid
sequenceDiagram
  participant C as Entitled caller
  participant A as Trade Docs API
  participant D as PostgreSQL
  participant O as Outbox worker
  participant B as Event consumer / authority adapter
  C->>A: Context-bound command, idempotency key
  A->>D: One transaction: domain revision + outbox + result
  D-->>A: Committed version/result
  A-->>C: Accepted document/workflow reference
  O->>D: Lease pending record
  O->>B: Shared event or authorised side-effect
  B-->>O: Ack or uncertain/failure
  O->>D: Ack / retry / reconcile / DLQ
~~~

## 2. Exact canonical surfaces
- **Shared `contracts/trade-document/v2`** is authoritative for document/version/content/artifact/relationship events and their schemas; the old v1 package is compatibility history.
- **POST /v1/regulatory-document-evidence/resolve** MUST follow the exact Shared `regulatory-document-exchange/v1/trade-docs.openapi.yaml` and return authorised, exact pinned DocumentVersion documentary facts. Read it as a query surface even if implemented with POST for structured input.
- **POST /v1/documentary-evidence/assessments** is a Regulations-owned assessment command per RTD-06, **not** a document-side fact or TMS local decision.
- **ADR-SHARED-023 / RTD-07** activates document v2 Shared event contract definitions and assigns Trade Docs event-context stewardship. **The runtime producer does not exist until independently implemented/tested.**
- Candidate dossier, CustomsCase and authority action APIs/events remain **local, non-canonical proposals** until Shared accepts contracts and relevant producer migration.

## 3. Idempotency and concurrency
| Operation | Durable safeguard |
|---|---|
| Create TradeDocument | tenant, actor/workload, subject, command, request digest and idempotency scope |
| Issue DocumentVersion | immutable input/source snapshot digest; optimistic document revision; identical retry returns same version |
| Upload content artifact | staged content digest and association transaction; crash-recoverable finalisation |
| Regulatory evidence resolve | pinned reference and authorised context, consistent verification/validity snapshots, no unscoped cache |
| Submit Customs declaration | exact version, broker/authority credential, stable attempt ID; reconcile unknown response before retry |
| Apply external authority callback | signature, tenant/provider binding, source event ID and digest; no last-writer-wins release |
| Publish Shared event | outbox in same domain transaction; at-least-once delivery with stable event ID |
| Run durable workflow | persisted step, timeout, retry, evidence, human handoff and compensating action |

No distributed ACID across S3, issuing systems, Regulations, customs authority, ERP or broker. Side effects that cannot be safely reversed must not be treated as arbitrary retryable internal tasks.

## 4. Message ordering and provenance
Event envelope/IDs and version major governed by Shared; no local replication of an event registry. The outbox payload describes a committed documentary fact, **not** a command to issue a document. Delivery is at least once; consumers must deduplicate by producer+event identity, content digest and canonical object revision. Late verification/validity notifications update separate projections without rewriting issued versions. Same source event identity with changed payload is quarantined.

## 5. Workflow state and fallbacks
Long-running durable steps: source fact collection -> documentary validation -> maker/checker -> signing/issuer delegation -> issuing content -> dossier assembly -> optional Customs submission -> await response -> reconciliation. Missing Regulations response produces incomplete/unknown condition; missing Customs gateway holds filing, not release. Renderer unavailable may block PDF-specific issue but not necessarily structured canonical document operations.

Workers must re-check current relevant scope/credential on consequential external side effects, preserving original initiator trace. Do not allow an untrusted event to create a higher-privilege workflow.

## 6. API compatibility and data minimisation
Version resource URLs and Shared-major bindings; pin Shared SHA, run consumer contract fixtures, return stable machine-readable errors, correlation IDs, pagination and purpose-specific projection freshness. Metadata and artifact access are separate. Document search must not leak content, issuer or commercial source references to cross-tenant callers.

## 7. Independent implementation gates
| Gate | Objective evidence |
|---|---|
| TDOC-API-01 | API/OpenAPI versioned auth-context, rate-limit and field-level access contract tests |
| TDOC-API-02 | TradeDocument v2 exact schema conformance and RTD-06 pinned resolve fixtures |
| TDOC-API-03 | Outbox/inbox crash, poison payload, duplicated event, event version and DLQ replay tests |
| TDOC-API-04 | Issue/correct/upload and optimistic lock/idempotency race tests |
| TDOC-API-05 | Simulated authority unknown-outcome and workflow timeout/human escalation proof |
| TDOC-API-06 | Registry/CP/EA-09 provider declaration only after implemented support, no simulated production claim |

No API, publisher, registry or activated provider is implemented merely by adopting this ADR.
## 8. Rejected alternatives and governance

Rejected: tenant identity from untrusted headers; file-as-document; document verified = requirement satisfied; Customs gateway HTTP success = released; mutable issued versions; global opaque vendor IDs as Baobab identity; new mandatory JVM/PHP operational suite; direct other-engine database sharing; self-certification from architecture. Canonical API/key/event changes must go through Shared, producer support through code and tests, CP capability activation through EA-09 and independent governance. Every gate requires a bounded PR with real source/test paths and explicit open issues.
