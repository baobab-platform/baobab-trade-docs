# ADR-TDOC-0018 — Cross-Organisation Document Exchange, Disclosure and Consent Architecture

**Status:** Proposed — additional architecture decision, pending formal review; not code or production approval  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Programme note:** ADR-TDOC-0016..0019 are **extensions to the original ADR-TDOC-0001 charter programme**, which previously ended at ADR-TDOC-0015. Numbering/scope remain Proposed.  
**Inherited authority:** Accepted ADR-TDOC-0001/0002, Shared ADR-SHARED-019..026 and TradeDocument v2/RTD-05/06/07/08 governance, CP/IAM and competent external legal/issuer authority  
**Technology:** Headless self-hosting; TDOC-TECH-01 is separate Proposed technology strategy.  

> **Non-claim:** No new canonical Shared key, event, version contract, capability activation, legal authority, self-hosted integration or production readiness results from writing or merging this ADR.


## 1. Rationale and decision
A trade transaction may involve independent buyer, supplier, carrier, customs broker, insurer, bank/funder, inspection body and competent authority. Sharing one tenant account or leaking an object-store URL is **not** an acceptable exchange mechanism. A document can remain owned by its original Trade Docs tenant/issuer while another independently authorised party receives **purpose-limited, revocable access** to an exact DocumentVersion or documentary fact projection.

Introduce **DocumentDisclosure**, **ExchangeInvitation**, **RecipientEntitlement**, **AccessGrant**, **DeliveryReceipt**, **DisclosureRevocation**, **ExchangeAudit** and **DisclosurePolicyReference** as Trade Docs operational constructs. CP/IAM provide trusted actor/organisation context, while actual legal disclosure capacity may require contract, consent, regulatory authority or data-protection basis.

~~~mermaid
flowchart TD
  O["Owning tenant / Trade Docs document version"] --> P["Purpose and entitlement evaluation"]
  P --> G["Disclosure grant + pinned version"]
  G --> B["Buyer"]
  G --> C["Carrier / customs broker"]
  G --> F["Funder / insurer"]
  G --> A["Competent authority"]
  B --> L["Audited delivery/access receipt"]
  C --> L
  F --> L
  A --> L
~~~

## 2. Model and policy
| Concept | Scope | Non-equivalence |
|---|---|---|
| ExchangeInvitation | intended recipient, independent organisation ref, purpose, delivery channel, expiry | new tenant account or user entitlement |
| RecipientEntitlement | verified recipient identity, role, relationship and permitted document fields | possession of URL/doc ID |
| DocumentDisclosure | grantor, exact DocumentVersion, content/artifact or facts permitted, legal basis, operation, market/time | legal issuer ownership transfer |
| AccessGrant | scoped read/verify/download/submit permission, expiry/revocation, channel, maximum scope | electronic transferable-record control |
| DeliveryReceipt | authenticated delivered/accessed/acknowledged evidence with timestamps and subject | substantive document acceptance |
| DisclosureRevocation | stop further access or circulation through controlled channel as technically possible | erasure of already downloaded copy |
| ExchangeAudit | access and grant decisions, recipient, purpose, version, denial, external delivery correlation | public availability or universal traceability |

Metadata access differs from content access. A bank may require documentary fact summaries but not customer PII; a broker may require the declaration PDF but not financial buy-rate data; regulators may have lawful compelled access beyond ordinary consent subject to appropriate verification.

## 3. Exchange workflow
Grant request -> verify legal purpose/source authority -> resolve recipient identity and independent legal entity -> check relevant document/version/disclosure-class policy -> maker/checker for high-risk export where required -> issue narrowly scoped grant -> serve authorised redacted or original artifact securely -> record recipient receipt -> optionally revoke **future** access. A disclosure references immutable version; later document supersession **does not silently replace** the disclosed record.

Direct inter-tenant access via CP must use explicit cross-entity relationship and permitted resource projection. A parent Nabhold company has no blanket access to ZuriBeans or Thamani tenant documents by virtue of shareholding.

## 4. Information security and privacy
Prefer auth-bound short-lived tokens/capability access, not publicly cached presigned URLs. Signed URLs if used must be short-lived, audience/purpose-scoped as technically supported and never indexed or logged. Malware, sensitive commercial data, KYC, driver/receiver signatures, bank details and Customs declarations require access classification and minimised projections. Record cross-border transfer legal basis and storage/recipient location constraints under ADR-TDOC-0011.

No claim of retracting a recipient's already downloaded/printed evidence. Repudiation/dispute evidence and statutory retention must survive access-grant expiration where required.

## 5. Events and audit
Internal grant/delivery events may be produced for auditable operations but **no canonical shared exchange key/event is approved** by this ADR. External delivery, SMTP/provider ACK and recipient acknowledgement have different meanings; "email sent" is not "document received" and neither implies document verified or requirement satisfied. Use durable idempotent jobs and a receipt reconciliation queue.

## 6. Failure and abuse
Wrong tenant, leaked token, forged recipient, non-matching organisation/case, expired consent, incorrect document version, stale content classification, cross-market data transfer restriction, bulk enumeration, ineligible broker, revoked mandate or gateway timeout must be denied/quarantined. Log at least who attempted which action, why rejected, what was shared and exact artifact/version.

## 7. Implementation gates
| Gate | Testable deliverables |
|---|---|
| TDOC-EXC-01 | Disclosure/recipient/grant/receipt model and distinct ownership/control/authorisation state axes |
| TDOC-EXC-02 | CP/IAM tenant-to-external-party proof and case/relationship authorisation negative tests |
| TDOC-EXC-03 | Field-level/redacted and full-content permissions, expiry/revocation and non-enumeration tests |
| TDOC-EXC-04 | ZuriBeans→bank and Thamani→broker synthetic multi-organisation exchange flows |
| TDOC-EXC-05 | Privacy/legal basis, residency, consent, maker/checker and audit receipt verification |
| TDOC-EXC-06 | Shared contract approval and real partner channel acceptance before production exposure |

No universal document-sharing API, external recipient contractual authority or cross-border transfer compliance is certified by this ADR.
## 8. Alternatives, traceability and follow-up

Reject direct replacement of immutable issued-version content, universal legal status inferred from a PDF/credential/hash, arbitrary tenant access from knowing a reference, external vendor as canonical Trade Docs authority, reuse of another engine's operational database and bypass of maker/checker or Regulations/Customs. Implement in separate bounded PRs with actual source and test fixtures, explicit capability/contract approval through Shared, and CP/EA-09 certification only after verified implementation. ADR-TDOC-0001/0002 remain Accepted and unchanged by this proposed extension.
