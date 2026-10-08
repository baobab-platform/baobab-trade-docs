# ADR-TDOC-0006 — Transit, Guarantee, Seal and Acquittal Architecture

**Status:** Proposed — engine-local decision for architecture review; not accepted, implemented, certified or production-ready  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Precedence:** Accepted ADR-TDOC-0001 / ADR-TDOC-0002; Shared ADR-SHARED-019..026 as applicable, `contracts/trade-document/v2`, `cross-engine-reference/v1` and `regulatory-document-exchange/v1`  
**Runtime direction:** Headless, self-hosted; TDOC-TECH-01 (separate Proposed technology decision)  
**Platform authority:** Shared owns canonical cross-engine contracts/producer registry; Control Plane owns binding/activation; IAM authenticates; external competent authorities own legal acts.  

> **Maturity:** `.baobab/rtd-conformance.yaml` remains `ARCHITECTURE_ONLY`. This ADR creates design guidance and gates, not application code, published messages, lawfully issued instruments or operational customs capability.


## 1. Decision
Model **CustomsTransitProcedure** as a legal CustomsCase-related procedure, distinct from TMS **TransportMovement**. Trade Docs coordinates referenced **TransitGuarantee**, **TransitDeclaration**, **CustomsSeal**, **TransitCheckpoint**, **AcquittalClaim** and source-authoritative **Discharge/NonDischargeObservation**. TMS owns actual physical transport and seal-handling observations; customs authority and the applicable guarantor remain legal decision makers.

~~~mermaid
flowchart LR
  C["CustomsCase / transit regime"] --> D["TransitDeclaration"]
  D --> G["Guarantee reference"]
  D --> S["Seal identifiers / control evidence"]
  D --> P["Authorized checkpoint evidence"]
  P --> A["Acquittal package"]
  A --> X["Competent authority discharge decision"]
  T["TMS movement & custody facts"] --> P
~~~

## 2. Distinct legal and operational concepts
| Item | Trade Docs responsibility | External legal/financial authority |
|---|---|---|
| TransitProcedure | Workflow, scope, status, source refs | Applicable Customs regime |
| TransitGuarantee | Provider, amount/currency, expiry, authenticity, attachment and evidence | Bank/guarantor and Customs; ERP for financial booking |
| CustomsSeal | Identifier, issuer, sealed items, applied/broken/resealed source assertions | Customs/authorised inspector/carrier source |
| TransitCheckpoint | Pin authority and TMS observation references for movement along controlled route | Competent border/control agency |
| AcquittalSubmission | Compile pinned declaration, arrival and seal evidence; send via adapter | Customs decides closure/discharge |
| DischargeOutcome | Verified external observation and timestamps | Customs/guarantor, not TMS or Trade Docs |

## 3. Lifecycle
Transit states as local projections: DRAFT -> GUARANTEE_PENDING -> AUTHORISED_FOR_TRANSIT -> IN_TRANSIT -> ARRIVAL_RECORDED -> ACQUITTAL_PENDING -> DISCHARGED, with SUSPENDED / NON_DISCHARGED / GUARANTEE_DISPUTED / UNKNOWN. **Arrival** is physical, **acquittal submission** is procedural, and **discharge** requires verified authority source. No auto-discharge on TMS delivered/arrived event.

A guarantee may cover several declarations/consignments depending on source legal conditions. Guarantee balance/exposure is **not** a local financial ledger; financial encumbrance belongs ERP/issuer. Record exact guarantee evidence, limit/currency, expiration, coverage, scope and verifier, without claiming validity in unsupported jurisdictions.

## 4. Seal and chain of custody
A physical seal change is an immutable TMS/inspection observation with reason, carrier/inspector and cargo/equipment association. Trade Docs links the relevant issuer or agency evidence as exact DocumentVersion. A broken seal causes exception and may require competent authority action; it is not automatic proof of smuggling or liability.

## 5. Cross-border design
A UG→ZA transport journey may involve transit jurisdictions and independent border/trade procedures. Jurisdiction, market, trade lane, transport route and customs office are different scope concepts. Never collapse multiple national procedures into one "African customs clearance" flag. Time bounds and response handling must be regime/authority specific.

## 6. Failure semantics
Unknown guarantee validity, stale legal decision, unmatched seal ID, quantity discrepancy, unacknowledged checkpoint or missing discharge source must prevent falsely showing discharged. Use durable submission attempts, receipts, exception queues and manual review. Do not infer bank guarantee draw/release from Customs response.

## 7. Independent implementation gates
| Gate | Objective evidence |
|---|---|
| TDOC-TRN-01 | Procedure/transit/guarantee/seal/discharge schema and source authority RACI |
| TDOC-TRN-02 | Guarantee scope/expiry and independent currency precision/coverage tests |
| TDOC-TRN-03 | Seal integrity, wrong consignment, partial handoff, re-sealing and TMS custody tests |
| TDOC-TRN-04 | Acquittal with late/non-discharge/duplicate/unknown authority outcomes |
| TDOC-TRN-05 | Multi-country synthetic passage with separate CustomsCase identifiers |
| TDOC-TRN-06 | Real regime/guarantor/legal/sandbox clearance only after competent external confirmation |

No guarantee issuance, customs bond, transit permission, source Customs discharge or financial settlement is implemented by this document.
## 8. Traceability and decision consequences

Implementation must provide code-path evidence, unit/integration/contract fixtures, explicit denied/unknown outcomes, security/tenant isolation proof, Shared contract lock and a documented provider/operator scope. Existing accepted TradeDocument v2 document/version/content/relationship semantics and Shared event producer authority remain unchanged. This local ADR does not define a canonical Shared event/key or move authority from Regulations, Trade, TMS, ERP, CP, IAM or the competent external issuer. **No gate passes by merging this documentation.**
