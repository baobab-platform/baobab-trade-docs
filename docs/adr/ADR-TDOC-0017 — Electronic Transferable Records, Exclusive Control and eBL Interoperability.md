# ADR-TDOC-0017 — Electronic Transferable Records, Exclusive Control and eBL Interoperability

**Status:** Proposed — additional architecture decision, pending formal review; not code or production approval  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Programme note:** ADR-TDOC-0016..0019 are **extensions to the original ADR-TDOC-0001 charter programme**, which previously ended at ADR-TDOC-0015. Numbering/scope remain Proposed.  
**Inherited authority:** Accepted ADR-TDOC-0001/0002, Shared ADR-SHARED-019..026 and TradeDocument v2/RTD-05/06/07/08 governance, CP/IAM and competent external legal/issuer authority  
**Technology:** Headless self-hosting; TDOC-TECH-01 is separate Proposed technology strategy.  

> **Non-claim:** No new canonical Shared key, event, version contract, capability activation, legal authority, self-hosted integration or production readiness results from writing or merging this ADR.


## 1. Rationale and decision
Accepted ADR-TDOC-0002 separates **document identity**, **electronic representation**, **TransferabilityProfile**, **exclusive control**, **endorsement/transfer chain** and **legal validity**. An ordinary PDF plus digital signature does NOT constitute a transferable record. This ADR defines the execution seam for eligible electronic transferable records (ETRs), including potential electronic bills of lading (eBL), **without assuming that Baobab itself is a recognised control registry**.

Adopt a **provider-neutral TransferControlPort**. A formally qualified external control/service scheme holds authoritative control state unless a future separately accepted legal and cryptographic programme proves Baobab itself satisfies the instrument, scheme and jurisdictional requirements.

~~~mermaid
flowchart TD
  D["Issued eligible TradeDocument + exact DocumentVersion"] --> P["TransferabilityProfile + legal regime assessment"]
  P --> Q["Qualified control registry / scheme adapter"]
  Q --> E["Confirmed exclusive control evidence"]
  E --> T["Authorised endorsement / transfer command"]
  T --> A["New externally confirmed control holder"]
  A --> S["Surrender / discharge / change-of-medium"]
  S --> H["Historical immutable chain / audit"]
~~~

## 2. Domain and legal-control separation
| Object | Trade Docs role | Legal/source authority |
|---|---|---|
| TransferabilityProfile | document/instrument eligibility claim, external control method and governing law refs | issuing party, statutory regime, contract/scheme |
| ElectronicTransferableRecordReference | link to exact TradeDocument + DocumentVersion and external provider-native instrument ID | issuer and qualified control network |
| ControlStatusObservation | source holder reference, control receipt, trust method, timestamp, scheme version | external recognised control scheme |
| ControlTransferAttempt | request, claimant, mandate, recipient, payload digest and unknown-outcome tracking | Trade Docs orchestration |
| EndorsementEvidence | endorsement role, sequence, instrument reference and signed source assertion | appropriate endorser/holder and legal scheme |
| SurrenderOrDischargeObservation | exact confirmation, cancel/surrender reference, proof and status | carrier/issuer/control registry under applicable terms |
| ChangeOfMediumObservation | paper↔electronic conversion, retirement of old medium and evidence | competent legal process and instrument authority |

Control over an instrument is not the same as who owns the goods, who is the TradeDocument issuer, who may view metadata, who has a downloaded copy or which actor has a generic IAM role. Financial pledges/assignment/SCF encumbrances require independent legal evidence and cannot be inferred from a transfer event.

## 3. Transfer flow and state
Candidate observation states: NOT_APPLICABLE, CONTROL_NOT_ESTABLISHED, ESTABLISHMENT_PENDING, CONTROL_CONFIRMED, TRANSFER_PENDING, TRANSFER_CONFIRMED, SURRENDER_PENDING, SURRENDERED, DISPUTED, UNKNOWN. These are **projections of source evidence**, not claims that a local DB flag effects legal transfer.

An intended transfer requires qualifying eligible instrument, source proof of current control, scoped actor/legal capacity, recipient readiness and sender/receiver authorisation. Record exact source version, holder/recipient identity references, idempotency, cryptographic nonces/signatures as applicable, transaction reference and evidence. If the provider times out, **DO NOT** assume transfer failed or immediately retry with a new instrument number; reconcile before reissue.

## 4. Jurisdictional guardrails
UNCITRAL MLETR is a model-law reference, **not universally adopted law**. The existence of an eBL implementation, DCSA alignment or signed PDF does not prove enforceability in Uganda, South Africa, transit markets or under a specific carriage contract. Legal/scheme acceptance must be evaluated per jurisdiction, instrument, issuer, custody provider, title/control rules and operational acceptance. Track paper/electronic medium reconciliation and risk of duplicate originals.

## 5. Integration
DCSA eBL message types are protocol adapter details (ADR-TDOC-0010). TMS remains source of physical shipment and carriage execution; SCF may receive authorised pinned ETR status/encumbrance evidence, never control the instrument merely by querying it; ERP records financing/accounting consequences. IAM/CP authentication and relationship entitlement do not constitute exclusive legal control.

## 6. Security and reconciliation
Threats: duplicate electronic original, simultaneous transfers, forged holder/endorser, compromised registry credential, lost transfer ACK, stale revocation, unauthorised change of medium, secret disclosure and source disagreement. Use signed confirmation, strong provider/holder binding, idempotency and immutable attempt history. Refuse new transfer when exclusive control cannot be verified.

## 7. Implementation gates
| Gate | Evidence |
|---|---|
| TDOC-ETR-01 | Legal/scheme eligibility and capability matrix per instrument/corridor; documentary non-claims |
| TDOC-ETR-02 | Control/endorsement/transfer/surrender conceptual model and trust provenance fixtures |
| TDOC-ETR-03 | Simulated qualified-provider adapter, stale control and concurrency/duplicate-original tests |
| TDOC-ETR-04 | Strong credentials, signature/mandate, out-of-order and unknown-outcome reconciliation tests |
| TDOC-ETR-05 | DCSA or equivalent scheme-specific sandbox conformance and change-of-medium evidence |
| TDOC-ETR-06 | Independent legal acceptance and qualified live provider proof before any transferable-record production claim |

No ETR/eBL legal-control capability, licensed registry, electronically transferable title or financing collateral validity is deployed by this ADR.
## 8. Alternatives, traceability and follow-up

Reject direct replacement of immutable issued-version content, universal legal status inferred from a PDF/credential/hash, arbitrary tenant access from knowing a reference, external vendor as canonical Trade Docs authority, reuse of another engine's operational database and bypass of maker/checker or Regulations/Customs. Implement in separate bounded PRs with actual source and test fixtures, explicit capability/contract approval through Shared, and CP/EA-09 certification only after verified implementation. ADR-TDOC-0001/0002 remain Accepted and unchanged by this proposed extension.
