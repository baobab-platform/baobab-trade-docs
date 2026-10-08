# ADR-TDOC-0014 — Observability, Authority Outage, Reconciliation and DR

**Status:** Proposed — architecture review only; not accepted/implemented/production-certified  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Normative precedence:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and canonical TradeDocument v2, RTD-05 cross-engine reference and RTD-06/07/08 interfaces  
**Technology:** Proposed TDOC-TECH-01 self-hosted headless direction; code choices and certification remain separately gated  

> **Design vs operation:** This document defines engineering obligations and independently testable implementation gates. It cannot activate a provider, issue a sovereign Customs decision, move another engine's ownership or turn Shared's event registration into an executable publisher.


## 1. Decision
Operate Trade Docs as a **durable, recoverable, audit-first documentary workflow service** and clearly distinguish outage/degradation of Trade Docs, object storage, signing service, Regulations, ERP/TMS/Trade sources and external Customs authorities. User-facing availability, legally effective document issuance and customs acceptance have different indicators and cannot be reported as one generic "up" status.

## 2. Service health and observability
| Signal | Evidence and meaning | Warning |
|---|---|---|
| HTTP API availability/latency | request class, authorised scope, error code and measured thresholds | green API != valid documents |
| Document issuance queue and retries | pending/committed versions, renderer/issuer dependency, recovery backlog | stuck issuance can leave unknown artifact state |
| Artifact integrity | hash mismatches, missing object, restore/checksum coverage, quarantine | DB metadata does not prove bytes are accessible |
| RTD-06 evidence API | signed/authed request rate, pinned resolve errors, stale validity and latency | evidence offered != Regulations assessment |
| Outbox/inbox | lag, retry, dead-letter count, old unacknowledged fact | Shared contract ACTIVE != runtime producer available |
| Customs authority exchange | submissions pending, receipts, unknown outcomes, source outages and retries | timeout cannot mean rejection or success |
| Credential/trust | expiring broker mandate, revoked key, validation errors | cannot bypass mandate |
| Privacy/security | wrongful denied cross-tenant reads, content-URL leaks, audit chain gaps | no PII in unbounded log labels |
| Backups/recovery | latest consistent DB+artifact backup, WAL gap, restore proof | untested backup != recoverability |

Set SLIs/SLO/RPO/RTO only after measured workload, legal requirements and business acceptance. Do not invent target percentages or national gateway latency.

## 3. Resilience strategy
- API/worker and storage components deploy using the existing Baobab stack, with bounded worker leases, backoff, isolated failure queues, per-adapter rate limits, circuit breakers and correlation IDs.
- If PDF renderer fails, preserve structured document and source artifacts, mark rendition PENDING, and block only the operation requiring that rendition.
- If Regulations is down, preserve facts and mark requirement decision UNKNOWN; never create "requirement satisfied".
- If Customs gateway times out, record UNKNOWN_OUTCOME and reconcile with external acknowledgement/status before any resubmission.
- If Trade/ERP/TMS updates source data after a document issued, preserve original pinned source snapshot and queue impact review; do not mutate issued version.
- If storage is inaccessible, content read is unavailable with explicit status; do not claim verification from metadata alone.
- Quarantine malformed authority payload/mapping drift rather than inferring legal release.

## 4. Reconciliation cases
| Divergence | Repair owner and non-destructive action |
|---|---|
| DB references missing artifact | Trade Docs quarantines version, restores bytes from backup or corrects via new audit observation |
| Stored artifact digest mismatch | Security incident; preserve evidence, stop content distribution until reviewed |
| Outbox event undelivered | durable retry / DLQ; re-emit with stable event ID, verify consumer idempotency |
| Customs gateway unclear receipt | authority-specific status lookup and manual escalation; no blind duplicate filing |
| Document validity changed during Regulations assessment | new version-pinned validity observation and authorised reassessment |
| ERP invoice amended after commercial invoice issued | dispute/correction workflow, preserve historical original source |
| Wrong-tenant disclosure detected | revoke future access, security incident, do not delete audit trail |
| Source actor credential revoked | suspend future privileged actions; preserve historical legal evidence |

## 5. Disaster recovery and legal custody
A valid restore includes PostgreSQL schema, immutable document versions, external references, content artifacts, encryption keys/config, tenant access policy, outbox/inbox status, workflow timers and historical provenance. Restore must test consistency between DB manifest and artifact bytes. External Customs filing side effects require reconciliation before replay. RPO/RTO and backups per data classification/legal hold require actual trials and regional data-residency review.

## 6. Incident drills
Stage synthetic cases: storage corruption, duplicate/late Customs release notification, authority gateway unavailability during lodged filing, revoked broker certificate, wrong-tenant evidence resolution and delayed event publication. Each runbook must identify responsible owner, affected cases, communication, pause/restart criteria, escalation, rollback limitations and postincident review.

## 7. Independent implementation gates
| Gate | Objective acceptance |
|---|---|
| TDOC-OPS-01 | Structured metrics/logs/traces with sensitive data redaction and actionable alert routing |
| TDOC-OPS-02 | Dependency failure injection for storage, renderer, Regulations and Customs adapter |
| TDOC-OPS-03 | Outbox/inbox/authority unknown-outcome reconciliation and replay drills |
| TDOC-OPS-04 | Consistent PostgreSQL+artifact+keys restore with version/digest/audit verification |
| TDOC-OPS-05 | Staged maker/checker, legal hold, source revision and credential-compromise incident exercises |
| TDOC-OPS-06 | Measured SLI/SLO/RPO/RTO and operator acceptance before production certification |

This architecture makes **no operational availability, audited data residency or disaster recovery proof claim**.
## 8. Rejected alternatives and governance

Rejected: tenant identity from untrusted headers; file-as-document; document verified = requirement satisfied; Customs gateway HTTP success = released; mutable issued versions; global opaque vendor IDs as Baobab identity; new mandatory JVM/PHP operational suite; direct other-engine database sharing; self-certification from architecture. Canonical API/key/event changes must go through Shared, producer support through code and tests, CP capability activation through EA-09 and independent governance. Every gate requires a bounded PR with real source/test paths and explicit open issues.
