# ADR-TDOC-0013 — Security, Audit and Privileged Customs Operations

**Status:** Proposed — architecture review only; not accepted/implemented/production-certified  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Normative precedence:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and canonical TradeDocument v2, RTD-05 cross-engine reference and RTD-06/07/08 interfaces  
**Technology:** Proposed TDOC-TECH-01 self-hosted headless direction; code choices and certification remain separately gated  

> **Design vs operation:** This document defines engineering obligations and independently testable implementation gates. It cannot activate a provider, issue a sovereign Customs decision, move another engine's ownership or turn Shared's event registration into an executable publisher.


## 1. Decision
Treat documentary issue, cancellation, signature, verification, Customs declaration submission/withdrawal, release decision ingest and cross-organisation disclosure as **high-consequence privileged actions**. Authentication is via IAM, context via CP, document/workflow authorisation via Trade Docs domain policy, and legal powers via independently established issuer/broker/authority mandate. Security control design must protect actual content, metadata, provenance and audit.

~~~mermaid
flowchart TD
  I["IAM token / workload identity"] --> C["CP caller-bound context"]
  C --> P["Resource / relationship / legal mandate policy"]
  P --> S["Maker/checker or strong action confirmation"]
  S --> O["Version-pinned command"]
  O --> A["Append-only audit + outbox"]
~~~

## 2. Privileged action matrix
| Operation | Mandatory additional guard |
|---|---|
| Issue/certify document | correct issuer capacity, exact content digest, version policy, reviewer approval when policy requires |
| Verify issuer/signature | authorised verifier and recorded trust method/policy version; reviewer cannot silently self-certify |
| Customs declaration submission | valid declarant/broker authority, country/procedure endpoint scope, approved declaration version |
| Amend/withdraw lodged declaration | legal workflow and authority-supported command; previous submission remains in history |
| Record official authority release | verified source/protocol mapping/decision reference; cannot be manual local "release" flag |
| Read protected content/PII | purpose, document-level permission, content-class permission and audit |
| Disclose to bank/carrier | exact recipient, legal purpose, pinned version, expiry, acknowledgement/revocation handling |
| Operate integration credentials | separately scoped secrets/incident rotation; no browser-side bearer secrets |
| Break-glass | explicit incident/legal basis, dual control, narrow time scope, immutable supervisor review |

Maker and checker cannot be the same effective actor when a dual-control policy applies; separate IAM account names are insufficient if they resolve to the same controlled human.

## 3. Threat model and countermeasures
- IDOR/tenant impersonation via document IDs, digest enumeration or open preview links: CP-bound access + document/content policies + denial tests.
- Forged issuer or broker mandate; stolen carrier/customs credentials: verify source/issuer trust, constrain per partner/legal entity/jurisdiction, revoke/rotate.
- XML/EDI and PDF injection, script-bearing SVG, zip bomb, malware or unsanitised HTML in renditions: parse sandboxing, allowlisted resources, malware scan, strict resource quotas.
- Callback spoof/replay/out-of-order sovereign messages: signature validation, issuer/audience, source message ID, signed timestamp, deduplication and exception queue.
- SSRF by remote artifact URL or rendering: allowlist external fetch, limit network egress, isolate renderer/OCR.
- Compromised AI parser hallucination/field leakage: quarantine provenance, confidence/human review and tenant-isolated input.
- Forged audit trail/delete issued evidence: append-oriented audit, separation of duty, tamper-evidence and offsite security review.
- Data exposure through analytics/metrics and test fixtures: structured redaction, synthetic non-real documents, access logs.

## 4. Authentication vs legal authority
IAM SSO or Keycloak federation grants a principal identity/credential assurance, not a licensed customs broker or competent authority position. In a multi-provider IAM environment, normalised assurance levels and source credential proof must be evaluated separately from business/legal mandate. Financial or regulatory truth remains external. Human workflow sign-off may be a required control but not an independent determination of statutory validity.

## 5. Tamper-evident audit
Record actor/workload, tenant, legal entity, purpose, source and pinned Version, command, before/after version refs, outcome, policy version, timestamp, hash-linked/event-correlation as designed, and privileged approval. A signature over an audit log does not create a universal non-repudiation legal guarantee. Audit must allow historical reconstruction without exposing raw secrets or other tenants' documents.

## 6. Credential custody
Use approved secret manager/KMS with environment-specific keys; short-lived/mTLS/workload credentials where available. Split source customs endpoint, signatory service and storage keys. Rotate/revoke on incident, disable adapter without rewriting documents, preserve safe pending operations and notify authorised owners. Direct credentials in GitHub secrets may support CI workflows but must not be embedded in code, images or emitted events.

## 7. Independent implementation gates
| Gate | Evidence |
|---|---|
| TDOC-SEC-01 | Threat model, privileged action RACI and document/Customs authority matrix |
| TDOC-SEC-02 | IAM/CP token/context wrong-audience, expired, revoked, impersonation and sibling-tenant tests |
| TDOC-SEC-03 | Issuer/broker mandate, maker/checker segregation and illegal release escalation tests |
| TDOC-SEC-04 | Object storage, format parsing, PDF renderer SSRF/malware/security test suite |
| TDOC-SEC-05 | External callback signature/replay/fraud and environment secret rotation tests |
| TDOC-SEC-06 | Audit replay/integrity, dependency SBOM, penetration review and high-severity remediation gate |

Passing architecture review is not a security audit, legal mandate or production acceptance.
## 8. Rejected alternatives and governance

Rejected: tenant identity from untrusted headers; file-as-document; document verified = requirement satisfied; Customs gateway HTTP success = released; mutable issued versions; global opaque vendor IDs as Baobab identity; new mandatory JVM/PHP operational suite; direct other-engine database sharing; self-certification from architecture. Canonical API/key/event changes must go through Shared, producer support through code and tests, CP capability activation through EA-09 and independent governance. Every gate requires a bounded PR with real source/test paths and explicit open issues.
