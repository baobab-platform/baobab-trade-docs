# ADR-TDOC-0008 — Evidence, Provenance, Verification and Discrepancy Architecture

**Status:** Proposed — architecture decision for review, not runtime implementation/acceptance  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Authority:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and pinned canonical v2/RTD-05/06/07 contracts  
**Technology:** TDOC-TECH-01 separate Proposed headless/self-hosted Python/Django/PostgreSQL direction; no new mandatory platform stack  

> Source facts, documentary verification, legal authority and runtime capability certification are different. This is an **ARCHITECTURE_ONLY** proposal; no real issuer validation, secure object store, signed legal document or production provider is represented as deployed.


## 1. Decision
Maintain **documentary assertions**, **their origins**, **verification observations**, **temporal validity observations**, **evidence bundles**, **discrepancies** and **Regulations requirement outcomes** as independent concepts. Trade Docs may present exactly pinned documentary facts to Regulations; **Regulations alone determines legal requirement satisfaction**, and an external issuer alone is the authoritative source of its own claim.

~~~mermaid
flowchart LR
 A["Issuer / upload / authority / extraction"] --> P["Attributed assertion + evidence source"]
 P --> V["Pinned DocumentVersion"]
 V --> C["Verification checks / discrepancy"]
 C --> F["RTD-06 DocumentEvidenceFactBundle"]
 F --> R["Regulations assessment / decision"]
~~~

## 2. Provenance semantics
RTD-06 requires preserving exactly which actor or mechanism originated a fact:

| Assertion provenance | Meaning | Must never be rewritten as |
|---|---|---|
| ISSUER_ASSERTED | Issuer or authorised signatory claims a value | Independently verified truth |
| BAOBAB_EXTRACTED | OCR/parser/ML extracts content from artifact | Direct issuer assertion |
| BAOBAB_GENERATED | Baobab composes structured document from source business facts | Source system's new financial/transport authority |
| EXTERNAL_NORMALIZED | Adapter translates source-native payload | Independently authorised sovereign interpretation |

Every assertion carries owner DocumentVersion, exact source artifact/content path and offset/field where possible, source/ref, observation method+version, confidence if applicable, received/recorded times, validating actor, transformations and correction lineage. Avoid mutating immutable DocumentVersion to improve extraction; publish separate observations or new version as policy permits.

## 3. Independent axes
| Axis | Example values | Authority |
|---|---|---|
| Lifecycle | draft, issued, superseded, withdrawn as governed by type | Trade Docs |
| Technical integrity | digest match/mismatch/unverified | Trade Docs storage and cryptographic verifier |
| Document verification | checked/pending/verified-conditions/failed with explicit method | Trade Docs observation, with issuer and external source caveats |
| Temporal validity | within period, expired, revoked, unknown | issuer/authority source, projected by Trade Docs |
| Requirement satisfaction | satisfied/unsatisfied/indeterminate with legal evidence | Regulations |
| Customs outcome | submitted, accepted, assessed, released, held | Competent authority as projected via CustomsCase |

A "verified" document is not necessarily issued by a lawful party, legally sufficient, unexpired or suitable for a specific import. A hash match cannot prove a forged document is authentic.

## 4. RTD-06 documentary exchange
Implement the existing **POST /v1/regulatory-document-evidence/resolve** contract, honouring authorised tenant and exact IDENTITY_PINNED DocumentVersion references. Resolve a **DocumentEvidenceFactBundle** with issuer claims, verification/validity snapshots, typed subject refs, assertions, timestamps and content-artifact references according to the actual Shared schema; no invented extra wire properties. Event **com.baobab-platform.documents.regulatory-evidence.offered.v1** is contract-activated under RTD-07, but a deployed publisher is not proven here.

Regulations' assessment endpoint is a **command**, not an "evidence accepted" event from Trade Docs. If verification/validity changes, project a new fact event only in accordance with Shared event contract, and trigger **authorised** reassessment without declaring a new legal decision.

## 5. Discrepancy workflow
Record discrepancy_id, source field(s), compared versions/assertions, severity, owner, observed_at, review decision, evidence and resolution/correction lineage. Example: ERP invoice amount 200 vs uploaded commercial invoice 250; TMS delivered quantity 5 vs packing list 6; issuer certificate number reused. Trade Docs reports conflicting documentary assertions and may block document issuance/offer under policy, but **ERP remains amount authority and TMS remains physical execution authority**.

Never silently overwrite one value, assume OCR is right, or update the source Trade/ERP/TMS system using extracted PDF content. Preserve human review, reasons, maker/checker and immutable audit.

## 6. Failure and trust
Wrong tenant/issuer; signature invalid; source artifact unreadable; stale Regulations requirement reference; late revocation notice; inconsistent subject scope; corrupted digest; model confidence below threshold; duplicate issuer identifier; unsupported foreign certificate are explicit negative cases. Verification results must carry method and freshness and may be UNKNOWN if source unavailable.

## 7. Independent implementation gates
| Gate | Tests and evidence |
|---|---|
| TDOC-EVD-01 | Provenance/verification/validity/requirement separation and mapping fixtures |
| TDOC-EVD-02 | Immutable attribution, multiple disagreeing sources, confidence and reviewer correction tests |
| TDOC-EVD-03 | Exact RTD-06 pinned fact bundle conformance and wrong-tenant rejection |
| TDOC-EVD-04 | Event outbox/assessment reassessment with late verification/revocation and replay tests |
| TDOC-EVD-05 | Trade/ERP/TMS contradiction scenarios without foreign-authority mutation |
| TDOC-EVD-06 | Issuer trust/cryptographic evidence and legal coverage review for each verification claim |

No documentary verification service, production evidence resolver or regulatory satisfaction evaluator is implemented by this ADR.
## 8. Rejected alternatives and governance

Reject file-as-document or one overloaded status, mutable issued DocumentVersion, direct foreign DB writes, vendor account/ID as canonical TradeDocument, universal regulatory validity inferred from a PDF or digital signature, tenant/market hard-coding, and candidate capabilities/events called active. A conflicting cross-engine change belongs first in Shared. Each numbered gate needs a bounded implementation PR with source/test/evidence references and honest unsupported-operation reporting.
