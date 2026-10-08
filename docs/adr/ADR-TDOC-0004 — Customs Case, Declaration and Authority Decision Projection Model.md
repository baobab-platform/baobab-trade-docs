# ADR-TDOC-0004 — Customs Case, Declaration and Authority Decision Projection Model

**Status:** Proposed — engine-local decision for architecture review; not accepted, implemented, certified or production-ready  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Precedence:** Accepted ADR-TDOC-0001 / ADR-TDOC-0002; Shared ADR-SHARED-019..026 as applicable, `contracts/trade-document/v2`, `cross-engine-reference/v1` and `regulatory-document-exchange/v1`  
**Runtime direction:** Headless, self-hosted; TDOC-TECH-01 (separate Proposed technology decision)  
**Platform authority:** Shared owns canonical cross-engine contracts/producer registry; Control Plane owns binding/activation; IAM authenticates; external competent authorities own legal acts.  

> **Maturity:** `.baobab/rtd-conformance.yaml` remains `ARCHITECTURE_ONLY`. This ADR creates design guidance and gates, not application code, published messages, lawfully issued instruments or operational customs capability.


## 1. Decision
**CustomsCase** is the Trade Docs executable workflow aggregate for one governed customs procedure or related declared goods movement. **CustomsDeclaration** is a versioned declaration instrument/payload associated with a case. An **AuthoritySubmission** is an attempt to lodge a specific declaration version; an **AuthorityResponse** is a verified source observation; a **CustomsDecisionProjection** is a read model of externally issued decisions. **None** is equivalent to TradeShipment, LogisticsShipment, an invoice or RegulatoryDecision.

~~~mermaid
flowchart LR
  S["Trade/TMS source refs"] --> C["CustomsCase"]
  R["Regulations decisions/requirements"] --> C
  C --> D["CustomsDeclaration revision"]
  D --> A["AuthoritySubmission attempt"]
  A --> P["Verified AuthorityResponse"]
  P --> X["Decision projection and audit"]
  X --> T["TMS operational enforcement"]
~~~

## 2. Identity and state axes
| Aggregate | Fields / invariants | Who has authority |
|---|---|---|
| CustomsCase | case_id, procedure, legal-entity/market, responsible party, source refs, version and audit | Trade Docs workflow |
| CustomsDeclaration | declaration_id, revision, declaration type, lines, parties, valuation/currency, evidence refs, schema profile | Trade Docs submission representation, **not** value truth |
| AuthoritySubmission | attempt_id, pinned declaration revision, destination authority, external correlation, digest, deadline and outcome | Trade Docs attempt log |
| AuthorityResponse | receipt/decision/ref, signed or independently verified origin, raw digest, occurred/received times | external competent authority |
| DecisionProjection | admission/rejection, validation, assessment, clearance, release, transit/hold facets and confidence/freshness | Trade Docs read projection of authority claims |
| ProcedureReference | customs procedure, effective schema version, governed applicability | customs authority/Regulations as appropriate |

Separate **case process state**, **declaration version state**, **submission state**, **authority acknowledgement**, **assessment**, **release**, **transit** and **appeal/dispute**. A source Customs message cannot be simplified to one universal APPROVED enum.

## 3. Candidate transitions
Case: OPEN -> REQUIREMENTS_PENDING -> DOSSIER_READY -> DECLARATION_PREPARING -> READY_TO_SUBMIT -> SUBMISSION_PENDING -> RESPONDED -> PROCEDURE_COMPLETE. Side exits: NEEDS_INFORMATION, SUSPENDED, CONTESTED, ABANDONED. Declaration: DRAFT -> VALIDATED_TECHNICALLY -> SIGNABLE -> LODGED; material corrections generate a new version / amendment procedure, not an in-place mutation of lodged content.

Submission: QUEUED -> SENT -> UNKNOWN_OUTCOME -> RECEIVED/REJECTED/FAILED_CONFIRMED; timeout **never** implies no submission. Acceptance of a declaration does not establish customs release; release does not mean physical delivery. Customs decisions/receipts are only effective at the specific goods/party/procedure/time scope stated by the authority.

## 4. Source-of-truth boundaries
- Trade provides commercial facts and parties; ERP provides authoritative invoice/accounting amounts; TMS supplies physical movement/consignment facts.
- Regulations owns legal applicability, documentary requirements, risk/policy evaluation as contractually supported; Trade Docs must not compute domestic customs law from hard-coded tax tables.
- Trade Docs owns case/declaration assembly, workflow, exact submissions and verified authority response records; sovereign authorities retain legal release, duties/assessments and decisions.
- Case may reference multiple shipments, consignments, dossiers and transit legs. A shipment may have several cases in different customs jurisdictions or procedures.
- Evidence remains in TradeDocument/DocumentVersion; declaration is not treated as merely a PDF, nor as the TradeDocument identity itself. A declaration rendition may be linked as its own TradeDocument.

## 5. Invariants and failure
No unpinned source facts in a lodged declaration. Legal entity, declarant/representative authority, importing/exporting market, currency, line quantities, approved schema and signatory prerequisites validated before submission. Reconcile declared vs actual cargo changes through authorised correction/amendment. Out-of-order authority notifications do not overwrite a more authoritative decision. Raw authority message and parsed projection preserve provenance and mapping version.

## 6. Contracts and compatibility
The current Shared document v2/RTD-06 packages **do not yet define a complete CustomsCase/Declaration wire contract**. Propose any public contract, new event context, Customs stewardship transfer or canonical capability through Shared; no local schema masquerades as Shared authority.

## 7. Independent implementation gates
| Gate | Exit evidence |
|---|---|
| TDOC-CUS-01 | Case/declaration/source-reference model and independent status-axis state-machine tests |
| TDOC-CUS-02 | Immutable lodged revision, amendment lineage, invoice/transport source pinning and two-jurisdiction fixtures |
| TDOC-CUS-03 | Authority response validation, decision projection, late/conflicting response and unknown-outcome tests |
| TDOC-CUS-04 | Regulations and Trade/TMS/ERP reference/authorisation integration tests |
| TDOC-CUS-05 | Shared customs-domain contract and producer stewardship proposal accepted before publication |
| TDOC-CUS-06 | One jurisdiction-specific regulator/authority sandbox proof before declaring any country operational |

**Non-claims:** a running customs gateway, lawful filing, sovereign clearance or production-certified customs capability.
## 8. Traceability and decision consequences

Implementation must provide code-path evidence, unit/integration/contract fixtures, explicit denied/unknown outcomes, security/tenant isolation proof, Shared contract lock and a documented provider/operator scope. Existing accepted TradeDocument v2 document/version/content/relationship semantics and Shared event producer authority remain unchanged. This local ADR does not define a canonical Shared event/key or move authority from Regulations, Trade, TMS, ERP, CP, IAM or the competent external issuer. **No gate passes by merging this documentation.**
