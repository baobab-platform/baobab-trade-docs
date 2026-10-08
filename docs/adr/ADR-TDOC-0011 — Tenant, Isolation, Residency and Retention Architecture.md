# ADR-TDOC-0011 — Tenant, Isolation, Residency and Retention Architecture

**Status:** Proposed — architecture review only; not accepted/implemented/production-certified  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Normative precedence:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and canonical TradeDocument v2, RTD-05 cross-engine reference and RTD-06/07/08 interfaces  
**Technology:** Proposed TDOC-TECH-01 self-hosted headless direction; code choices and certification remain separately gated  

> **Design vs operation:** This document defines engineering obligations and independently testable implementation gates. It cannot activate a provider, issue a sovereign Customs decision, move another engine's ownership or turn Shared's event registration into an executable publisher.


## 1. Decision
Trade Docs is headless and multi-tenant. **Control Plane** owns trusted tenant, legal-entity, market and context authority; **IAM** authenticates staff, delegates, issuers and workloads. Trade Docs enforces domain-level access across document metadata, **ContentArtifacts**, dossiers, cases, customs workflows, evidence resolution, search, async jobs, disclosures and backups. Shared holding-company parentage does **not** entitle Nabhold to read a subsidiary's privileged documents.

~~~mermaid
flowchart TD
  I["IAM-authenticated actor/workload"] --> C["Redeemed CP context"]
  C --> P["Domain purpose/resource/relationship policy"]
  P --> M["TradeDocument/DocumentVersion metadata"]
  P --> A["Private ContentArtifact"]
  P --> D["Dossier / CustomsCase / Evidence API"]
  P --> W["Tenant-bound inbox/outbox worker"]
~~~

## 2. Reference and scope invariants
| Source identity | Owner and usage | Prohibited inference |
|---|---|---|
| tenant_id, legal_entity_id, context_id | Control Plane; trusted operational scope | X-Tenant request header alone establishes access |
| DocumentVersion/document_id | Trade Docs; historical identity and scope | knowing document ID confers read rights |
| CrossEngineObjectReference | Shared portable reference + owner/scope/pinning | reference includes authorisation |
| ExternalReference | provider-native invoice, Customs, issuer or carrier IDs | provider ID replaces canonical identity |
| CanonicalEntity | Control Plane registry where applicable | CP mints TradeDocument domain ID |
| engine_instance_id | CP deployment/topology reference | changes business record identity |

Every repository method, SQL statement, search projection, worker, public token, cache entry, outbound partner request and callback MUST preserve verified tenant/legal-entity/operation scope. Tenant-associated foreign references need owner and scope check, not lexical UUID validation.

## 3. Data residency and classification
Define classifications for commercial pricing, invoice details, supplier/buyer identities, passports/importer IDs, driver/receiver signatures, origin certificates, Customs declaration payloads, personal addresses and issuer credentials. Market labels (UG/ZA) are not sufficient to decide residency: actual data subject, issuer/recipient, hosting region, legal entity, retention regime and transfer purposes must be reviewed per dataset.

Use configurable infrastructure placement and cryptographic key region policies with a documented approved cross-border transfer mechanism where necessary; do not assume POPIA permits all transfers or that every UG/ZA case must always stay inside one country. Residency assessment precedes an actual production storage region choice.

## 4. Retention and erasure
- Distinguish **temporal validity** (document expired) from **retention** (may/must preserve evidence) and **storage purge** (eligible physical erasure).
- Document issuer/legal/Customs retention, litigation hold, contractual audit and data-subject privacy rights may conflict; maintain reviewed disposition policy and reason. No automatic deletion of issued evidence merely because a Trade order closed.
- Encryption-key rotation preserves artifact digest and referenced ContentArtifact logical identity; deliberate cryptographic erasure requires authorised retention/legal review.
- Backup and replica data are subject to retention schedules and documented purge constraints; "deleted from UI" does not guarantee purge.
- Tenant exit/migration must preserve proof of legal custody/disclosure and historical version references without disclosing sibling tenants' data.

## 5. Secure collaboration
Cross-organisation exchange may grant **purpose-limited** access to precise DocumentVersion projections under ADR-0018. It never silently merges legal entities/tenants. A carrier or funder invited to one dossier must not gain global query access. Prevent enumeration through search, digest checking, file metadata, preview endpoints, batch downloads, logs and URL tokens.

## 6. Failure cases
Expired/revoked context, wrong actor, document cross-tenant reference, data-hosting mismatch, wrong market, absent legal hold classification, stale grant, background worker impersonation and accidentally public object URLs must reject or quarantine, with logged reason and monitored exception.

## 7. Independent implementation gates
| Gate | Acceptance proof |
|---|---|
| TDOC-TEN-01 | CP/IAM trust matrix for metadata, content, search, evidence, cases and background jobs |
| TDOC-TEN-02 | Tenant/legal-entity SQL/cache/search/outbox/worker/adapter negative integration tests |
| TDOC-TEN-03 | DocumentVersion permission vs content-artifact permission and foreign reference IDOR tests |
| TDOC-TEN-04 | Residency/classification/retention/legal hold policy profiles and UG/ZA review |
| TDOC-TEN-05 | Encrypted artifact purge/backup/restore and exit semantics without cross-tenant leaks |
| TDOC-TEN-06 | Independently authorised disclosure/partner-access pilot before broad activation |

This ADR approves neither actual cloud region nor legal cross-border transfer nor operating market capability.
## 8. Rejected alternatives and governance

Rejected: tenant identity from untrusted headers; file-as-document; document verified = requirement satisfied; Customs gateway HTTP success = released; mutable issued versions; global opaque vendor IDs as Baobab identity; new mandatory JVM/PHP operational suite; direct other-engine database sharing; self-certification from architecture. Canonical API/key/event changes must go through Shared, producer support through code and tests, CP capability activation through EA-09 and independent governance. Every gate requires a bounded PR with real source/test paths and explicit open issues.
