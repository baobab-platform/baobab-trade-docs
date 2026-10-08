# ADR-TDOC-0015 — Production Readiness, Capability Certification and Migration

**Status:** Proposed — architecture review only; not accepted/implemented/production-certified  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Normative precedence:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and canonical TradeDocument v2, RTD-05 cross-engine reference and RTD-06/07/08 interfaces  
**Technology:** Proposed TDOC-TECH-01 self-hosted headless direction; code choices and certification remain separately gated  

> **Design vs operation:** This document defines engineering obligations and independently testable implementation gates. It cannot activate a provider, issue a sovereign Customs decision, move another engine's ownership or turn Shared's event registration into an executable publisher.


## 1. Decision
Trade Docs readiness is **per implemented canonical document/Customs capability, market, procedure, external partner adapter, environment and legal actor authority**. Accepted architecture, event-context stewardship, passing CI, having a self-hosted container and a Shared contract's ACTIVE status are **not** evidence of running producer software, sovereign integration or production permission.

~~~mermaid
flowchart TD
  A["Accepted local ADR and Shared contracts"] --> B["Runtime + security + isolated data tests"]
  B --> C["Exact RTD-10 conformance source and test evidence"]
  C --> D["Capability provider declaration with proven support"]
  D --> E["EA-09 certification / provider review"]
  E --> F["CP registration, deployment, context, bindings"]
  F --> G["Permitted tenant/market/operation activation"]
  G --> H["Observed operational acceptance"]
~~~

## 2. Current preconditions
- `.baobab/rtd-conformance.yaml` currently reports `ARCHITECTURE_ONLY`, with `source_paths: []` and `test_paths: []`. Leave these declarations unchanged by ADR-only work.
- Shared `trade-document/v2` and documents event context are contract-activated per ADR-SHARED-023. There is **no claim that Trade Docs has a publisher or outbox**.
- Existing v1 trade-document events were PROPOSED and producerless; keep v1 compatibility history, **do not** implement v1 as runtime target.
- Customs event producer migration from Trade and Customs capability refinement require **separate Shared governance**, not a local file edit.
- TDOC-TECH-01 (Python 3.14/Django 6/PostgreSQL17, self-hosted) is a proposal requiring a real dependency/operability/compatibility spike, not sufficient deployment authority.

## 3. Gates and measurable evidence
| Gate | Deliverables and exit |
|---|---|
| TDOC-REL-01 — Foundation activation | Replace template scaffolding, pin Shared SHA, runtime libraries/DB migrations/CI and DevContainer; honest provider declaration |
| TDOC-REL-02 — Canonical document slice | Issue/revise/resolve TradeDocument v2, immutable DocumentVersion, protected ContentArtifact and source provenance |
| TDOC-REL-03 — API and event conformance | RTD-06 exact evidence endpoint, durable outbox for actual Shared active events, idempotency/replay/negative tests |
| TDOC-REL-04 — Security and residency | CP/IAM caller-bound context, tenant isolation, encryption, PII/retention and maker/checker authorisation |
| TDOC-REL-05 — External source integration | ERP invoice source, TMS delivery/POD facts and Regulations requirements/assessment without authority theft |
| TDOC-REL-06 — Customs procedure pilot | Approved qualified declarant/authority gateway sandbox for a precisely identified procedure/market; logged real ACK semantics |
| TDOC-REL-07 — Recovery evidence | DB+content restore, integrity/secret rotation, queued Customs unknown-outcome reconciliation and operator drills |
| TDOC-REL-08 — Certification and deployment | Independent security/legal/business sign-off, provider support evidence, EA-09, CP bindings/tenant grants, real rollout/rollback proof |

A capability may be ready for TradeDocument v2 read/issue but not for Customs filings or transferable-record control. Do not bind an entire engine to production just because one isolated operation passed.

## 4. Migration and compatibility
| Current source | Required migration policy | Prohibited shortcut |
|---|---|---|
| Shared trade-document/v1 | Audit producers/consumers; map old IDs/statuses and maintain compatibility projections if justified | silently mutate v1 schema or declare VERIFIED a lifecycle state |
| Shared trade-document/v2 | canonical target with pinned release and consumer-driven fixtures | redefine v2 in this repository |
| Trade-owned document event assumptions | RTD-07 producer convergence; consumer-first cutover from any historical producers | invent old publisher or rewrite historical events |
| Trade/ERP generated invoices | preserve source business authority; mint independent document+version IDs and source snapshot refs | treat PDF file as ERP invoice record |
| TMS proof of delivery | document evidence tied to delivery reference; no physical delivery reassignment | update TMS delivery state by issuing POD |
| Legacy Customs event context | separate Shared producer/stewardship and consumer migration | unilateral event producer takeover |
| Older retained artifacts | import immutable bytes and original hash when verifiable, record unknown provenance where not | fabricate signatures, issuance dates or historical versions |

## 5. Release matrix
Maintain signed, reviewable matrix per **capability key, contract major, provider implementation SHA, engine-instance/config, tenant/legal entity, country/procedure, source partner, accepted evidence type, test/report path, known limitations and expiry**. Simulation is never production-permitted. Health probes do not confer provider certification.

## 6. Negative acceptance scenarios
Prove at minimum wrong-tenant resolve, forged issuer/Customs callback, altered content hash, duplicate issue/submission, expired document, unknown Customs outcome, stale Regulations assessment, failed object storage, mismatched document version, revoked representative credential, partial restore and cross-market independent entities.

## 7. Deployment control
Use existing tag-driven Baobab staging/release convention only when repository pipeline has actually been established. Respect approval segregation and reproducibility, pin action/dependency digests, SBOM, scanner findings and migration rollback. Rollback of code cannot un-submit a declaration or revoke an issued external legal instrument; reconcile irreversible side effects.

**Non-claims:** no live deployment, Customs approval, operating region, registration, active capability, legal transferable-record implementation or production readiness is conveyed by this document.
## 8. Rejected alternatives and governance

Rejected: tenant identity from untrusted headers; file-as-document; document verified = requirement satisfied; Customs gateway HTTP success = released; mutable issued versions; global opaque vendor IDs as Baobab identity; new mandatory JVM/PHP operational suite; direct other-engine database sharing; self-certification from architecture. Canonical API/key/event changes must go through Shared, producer support through code and tests, CP capability activation through EA-09 and independent governance. Every gate requires a bounded PR with real source/test paths and explicit open issues.
