# ADR-TDOC-0007 — Issuer, Signature, Credential and Representative Authority

**Status:** Proposed — architecture decision for review, not runtime implementation/acceptance  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Authority:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and pinned canonical v2/RTD-05/06/07 contracts  
**Technology:** TDOC-TECH-01 separate Proposed headless/self-hosted Python/Django/PostgreSQL direction; no new mandatory platform stack  

> Source facts, documentary verification, legal authority and runtime capability certification are different. This is an **ARCHITECTURE_ONLY** proposal; no real issuer validation, secure object store, signed legal document or production provider is represented as deployed.


## 1. Decision
Distinguish the **document issuer**, **submitter**, **signer**, **authorised representative**, **credential issuer**, **external relying party** and **Baobab IAM principal**. A signature proves a specific cryptographic or witnessed action only to the extent demonstrated; it does **not** automatically prove identity, representative capacity, legitimate issuance, statutory validity, transferable-record control or Customs release.

~~~mermaid
flowchart LR
 I["Canonical organisation & principal refs (CP/IAM)"] --> R["Representative authority grant"]
 E["Competent external issuer"] --> C["IssuerClaim on DocumentVersion"]
 R --> S["SignatureIntent / evidence"]
 C --> V["DocumentVersion"]
 S --> V
 V --> T["Verification observations"]
 T --> A["Contextual trust and legal decision elsewhere"]
~~~

## 2. Identity and trust dimensions
| Concept | Proposed records | Trust authority |
|---|---|---|
| IssuerClaim | issuer ref, original source, asserted issuer role, document type, issue time, evidence | external issuer statement; claim ≠ verified |
| SignatureEvidence | signature value/ref, signed content digest, signing time, certificate or witness, algorithm/policy | cryptographic verifier and recognised trust scheme |
| RepresentativeMandate | principal, acting-for organisation, document/procedure powers, market, scope, effective dates, delegation chain | CP relationships and externally valid appointment/legal capacity |
| CredentialEvidence | credential issuer, subject, scope, expiry, revocation/status check, validator version | external trust registry or qualified credential issuer |
| VerificationObservation | checks performed, results, time, trust anchors, source policy version, limitations | Trade Docs checks, not sovereign authenticity declaration |
| IssuanceAuthorisation | maker/checker, competent document issuer or approved delegated party, signatory and exact DocumentVersion | governed issuer/procedure policy |

Canonical organisation/actor identities must be resolved through CP/IAM. Do not duplicate the global organisation registry. A foreign shipping line, laboratory or bank may be an external issuer even if it is **not** a Baobab tenant or CapabilityProvider.

## 3. Signature and representative workflow
Candidate workflow: draft -> determine issuer/capacity -> bind approved content digest -> maker/checker approval where applicable -> request signature/issuer action -> verify signature evidence and signer identity/capacity -> issue immutable DocumentVersion -> preserve verification observations. Signatures on content revised later must be re-evaluated; stale certificates and changed mandates invalidate assumptions for new operations, not prior historical facts without proper time analysis.

A human with IAM login and generic corporate admin role is not automatically a customs broker, bank officer, insurer, competent inspector, carrier signatory or documentary issuer. Where legal mandates cannot be verified, operation returns AUTHORITY_UNKNOWN/PENDING_REVIEW and does not claim legally valid issuance.

## 4. Security and legal portability
- Trust anchors, certificate status checks, recognised signature standards and national e-sign law vary by country/instrument; record jurisdiction, policy and limitations rather than making universal legal pronouncements.
- Private signing keys stay with approved HSM/KMS/provider or authorised signer; Trade Docs stores only permitted references and tamper-evident evidence. No shared unencrypted signature password in the engine database.
- Separate **issuer authentication**, **representative mandate**, **cryptographic integrity**, **certificate validity at signing time**, **non-repudiation evidence** and **legal effect** in read projections.
- A detached signature, typed name, scanned wet signature and qualified electronic signature have different evidence semantics; never convert one into another by casting a flag.
- For eBL/transferable records, legal control is governed by ADR-TDOC-0017, not inferred from signing alone.

## 5. Provider strategy
Headless signature/verification ports permit software/provider replacement. An optional self-hosted signing product may be evaluated, but **no JVM/Node signing platform is a baseline dependency** under TDOC-TECH-01. Preserve cryptographic implementation version, trust roots, network revocation evidence and signature-envelope digest. Supplier/partner portals remain estate-owned.

## 6. Negative cases
Forged issuer, expired mandate, signer mismatch, content changed after signature, unknown trust root, cross-tenant representative, delegated power outside document type, broken certificate chain, revoked credential, invalid archived timestamp and unavailable revocation authority must return explicit evidence state, not "verified".

## 7. Independent implementation gates
| Gate | Evidence |
|---|---|
| TDOC-SIG-01 | Issuer/claim/signer/mandate distinct model and policy matrix by instrument |
| TDOC-SIG-02 | Cryptographic digest and verification adapter contract with altered-content and trust-root tests |
| TDOC-SIG-03 | CP/IAM actor+representative authority, expiry/revocation and wrong-tenant negative tests |
| TDOC-SIG-04 | Signed issued-version immutable replay and historical signing-time validation |
| TDOC-SIG-05 | Optional signing provider licence/threat/rotation and approved test-trust fixtures |
| TDOC-SIG-06 | Legal/jurisdictional issuer and representative validation before any claim of legally effective signing |

No electronic transferable-record provider or universal legal signature guarantee is authorised.
## 8. Rejected alternatives and governance

Reject file-as-document or one overloaded status, mutable issued DocumentVersion, direct foreign DB writes, vendor account/ID as canonical TradeDocument, universal regulatory validity inferred from a PDF or digital signature, tenant/market hard-coding, and candidate capabilities/events called active. A conflicting cross-engine change belongs first in Shared. Each numbered gate needs a bounded implementation PR with source/test/evidence references and honest unsupported-operation reporting.
