# ADR-TDOC-0003 — Document Dossier, Requirement and Completeness Architecture

**Status:** Proposed — engine-local decision for architecture review; not accepted, implemented, certified or production-ready  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Precedence:** Accepted ADR-TDOC-0001 / ADR-TDOC-0002; Shared ADR-SHARED-019..026 as applicable, `contracts/trade-document/v2`, `cross-engine-reference/v1` and `regulatory-document-exchange/v1`  
**Runtime direction:** Headless, self-hosted; TDOC-TECH-01 (separate Proposed technology decision)  
**Platform authority:** Shared owns canonical cross-engine contracts/producer registry; Control Plane owns binding/activation; IAM authenticates; external competent authorities own legal acts.  

> **Maturity:** `.baobab/rtd-conformance.yaml` remains `ARCHITECTURE_ONLY`. This ADR creates design guidance and gates, not application code, published messages, lawfully issued instruments or operational customs capability.


## 1. Decision
A **DocumentDossier** is a tenant-scoped, purpose-bound collection of **pinned DocumentVersion references** and their relationships to business subjects and documentary **RequirementReferences** issued by Regulations. Dossier completeness is an operational check that the expected documentary items have been offered, are in the correct scope, and satisfy declared technical checks. It is **not** regulatory satisfaction, Customs approval, authenticity, or legal sufficiency.

~~~mermaid
flowchart TD
  A["Trade transaction / CustomsCase / Transport context"] --> D["DocumentDossier"]
  R["Regulations RequirementSet reference"] --> D
  D --> L["DossierEntry: exact DocumentVersion"]
  L --> V["Trade Docs content / verification / validity facts"]
  D --> C["Documentary completeness evaluation"]
  C --> E["Evidence offered to Regulations"]
  E --> F["Regulations assesses requirement satisfaction"]
~~~

## 2. Aggregate and reference model
| Concept | Identity / attributes | Authority |
|---|---|---|
| DocumentDossier | dossier_id, tenant/legal entity, purpose, document subject, active version, owner, lifecycle | Trade Docs |
| DossierEntry | entry_id, exact DocumentVersion ref, declared role, submitted-by, timestamp, historical version | Trade Docs |
| RequirementReference | identity-pinned Regulations requirement/set, source version, effective interval, subject/corridor | Regulations; cached projection only |
| CompletenessCheck | check_id, dossier version, requirement snapshot, check-rule version, observed outcome and gaps | Trade Docs **technical/documentary** outcome |
| DossierDisclosure | authorised audience/purpose, pinned disclosed version refs, expiry/receipt | Trade Docs disclosure (expanded by ADR-0018) |
| EvidenceOffer | accepted contract-shaped documentary assertions offered for review | Trade Docs; acceptance authority remains Regulations |

A requirement may need multiple distinct evidence documents; a document may be offered for several requirements. The model must support optional and conditional requirements only when resolved by Regulations, not invented by dossier-specific country logic.

## 3. Lifecycle and quantitative checks
Proposed dossier states: DRAFT -> COLLECTING -> ASSEMBLED -> SUBMITTED_FOR_ASSESSMENT -> ARCHIVED, with explicit REOPENED / WITHDRAWN / CONTESTED outcomes. The state of a dossier **does not modify** TradeDocument lifecycle, DocumentVersion verification, validity, regulatory assessment or CustomsCase acceptance.

Completeness outcomes: COMPLETE_FOR_SUBMISSION, INCOMPLETE, CONFLICTED, UNKNOWN and NOT_APPLICABLE, all carrying evidence/requirement version and evaluation timestamp. A missing required DocumentVersion or unresolved source requirement is not COMPLETE. A technically complete dossier can still be rejected by Regulations.

Validate subject references, version pinning, document type/profile, inclusion uniqueness, expiry/revocation, required fields, issuer claim and relationship graph. Do not infer legal document sufficiency from a syntactically valid PDF.

## 4. Cross-engine choreography
1. Authenticated consumer provides authorised business context and purpose (e.g., ZuriBeans UG→ZA export).
2. Trade Docs resolves the **pinned** Regulations requirement set via accepted RTD-06 source surfaces; a caller cannot construct a fake requirement.
3. Users/providers assemble immutable DocumentVersion entries; a changed version must be explicitly reselected, not silently followed.
4. Completeness is evaluated against the pinned requirement source and current documentary verification/validity projections.
5. Trade Docs emits or serves **DocumentEvidenceFactBundle** and, when implemented, the activated document-side regulatory-evidence-offered event.
6. Regulations alone issues a separate requirement satisfaction assessment. Changes in document verification or validity may cause reassessment according to Shared RTD-06/07/08 contracts.

## 5. Concurrency, security and failure
Optimistic dossier revision; concurrent additions are conflict-checked; do not duplicate entries by external file hash alone. An unavailable Regulations source creates PENDING/UNKNOWN with recorded freshness and retry, never a locally fabricated requirement. Redaction/metadata access can differ from content access. Cross-organisation disclosures must be explicit and revocable for future access, while preserving immutable audit.

## 6. Alternatives rejected
Reject document list as legal checklist, duplicated Regulations policy tables, one attachment per requirement, direct ERP/TMS foreign-key joins and "latest version" substitutions in historical assessment.

## 7. Independent implementation gates
| Gate | Deliverables and objective exit evidence |
|---|---|
| TDOC-DOS-01 | Dossier, entry, source requirement and completeness schema mapped to Shared v2 references |
| TDOC-DOS-02 | Version-pinned many-to-many and conditional requirement fixtures; chronology, duplication and optimistic concurrency tests |
| TDOC-DOS-03 | RTD-06 source requirement and EvidenceFactBundle conformance integration (Regulations simulator clearly labelled) |
| TDOC-DOS-04 | Incomplete/expired/revoked/conflicted/unknown negative scenarios and reassessment evidence |
| TDOC-DOS-05 | Two independent tenants/markets and authorised disclosure access denial proof |
| TDOC-DOS-06 | End-to-end source assessment integration after Regulations runtime readiness, without a legal sufficiency claim |

**Not granted:** registered dossier capability, Customs clearance, operating regulatory requirement evaluator or production readiness.
## 8. Traceability and decision consequences

Implementation must provide code-path evidence, unit/integration/contract fixtures, explicit denied/unknown outcomes, security/tenant isolation proof, Shared contract lock and a documented provider/operator scope. Existing accepted TradeDocument v2 document/version/content/relationship semantics and Shared event producer authority remain unchanged. This local ADR does not define a canonical Shared event/key or move authority from Regulations, Trade, TMS, ERP, CP, IAM or the competent external issuer. **No gate passes by merging this documentation.**
