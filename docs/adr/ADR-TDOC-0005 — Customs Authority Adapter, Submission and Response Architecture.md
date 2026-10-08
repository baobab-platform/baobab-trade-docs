# ADR-TDOC-0005 — Customs Authority Adapter, Submission and Response Architecture

**Status:** Proposed — engine-local decision for architecture review; not accepted, implemented, certified or production-ready  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Precedence:** Accepted ADR-TDOC-0001 / ADR-TDOC-0002; Shared ADR-SHARED-019..026 as applicable, `contracts/trade-document/v2`, `cross-engine-reference/v1` and `regulatory-document-exchange/v1`  
**Runtime direction:** Headless, self-hosted; TDOC-TECH-01 (separate Proposed technology decision)  
**Platform authority:** Shared owns canonical cross-engine contracts/producer registry; Control Plane owns binding/activation; IAM authenticates; external competent authorities own legal acts.  

> **Maturity:** `.baobab/rtd-conformance.yaml` remains `ARCHITECTURE_ONLY`. This ADR creates design guidance and gates, not application code, published messages, lawfully issued instruments or operational customs capability.


## 1. Decision
Trade Docs owns provider-neutral **CustomsAuthorityPort** interfaces and authenticated submission/response orchestration. Each national customs administration, border agency or accredited intermediary is represented by an **adapter implementing only verified functions** under actual permissions. There is **no universally deployable Customs API** and no single authority schema that can be forced into all jurisdictions.

~~~mermaid
sequenceDiagram
  participant W as Trade Docs workflow
  participant O as Durable Outbox
  participant A as National Authority Adapter
  participant X as Authority endpoint
  W->>O: Commit exact declaration version + attempt
  O->>A: Submit stable request ID / digest
  A->>X: Authenticated national message
  X-->>A: Transport ACK / timeout
  A-->>W: Confirmed receipt OR UNKNOWN_OUTCOME
  X-->>A: Signed async decision
  A->>W: Authenticated, mapped response
  W->>W: Reconcile actual case projection
~~~

## 2. Adapter contracts
| Port | What it does | Proof required |
|---|---|---|
| `AuthorityProfilePort` | Discover supported procedure, message/schema revision, endpoint and environment | Verified national specification and partner mandate |
| `SubmitDeclarationPort` | Submit idempotent pinned payload, evidence refs and declarant authority | Credentials, payload digest, transport confidentiality |
| `SubmissionStatusPort` | Resolve an uncertain submission using external correlation | External receipt/outcome read, not guesses |
| `AuthorityMessageIngestPort` | Authenticate/parse acknowledgements, errors, queries, assessments and release notifications | Signatures/sender binding/replay protection |
| `AmendOrWithdrawPort` | Execute only authority-supported amendment, correction/withdrawal semantics | Specific national workflow documentation |
| `DutyAssessmentReadPort` | Project source-issued duty/tax assessment into case | Not a local tariff/duty-calculation authority |

## 3. Submission semantics
Distinct **prepared, locally queued, transmitted, delivery-acknowledged, technically accepted, substantively accepted, assessed, released and rejected** statuses. An HTTP 200 may acknowledge a gateway only. Store immutable request/version/digest/credential-scope audit with event times, attempt IDs, external reference, map version and reviewer consent. Every retry uses authority-specific idempotency or **status reconciliation before reissue** to prevent duplicate declarations.

A synchronous timeout followed by late agency acknowledgement is an **UNKNOWN_OUTCOME**, not FAILED. User may never press "resubmit" until an authorised workflow establishes safe retry or alternative procedure. A manual filing path remains auditable and must be explicitly marked MANUAL / NOT_VERIFIED unless the competent authority receipt is recorded.

## 4. Credential and legal controls
The responsible declarant (or licensed customs broker) and national API authorisation are prerequisites, not inferred from an IAM token or business registration. Keep partner secrets per tenant/legal entity, declarant, authority, market and environment in managed secrets with rotation. Protect from SSRF, callback impersonation, metadata poisoning and exfiltration. Record raw authority payload hashes/verification and optionally encrypted originals subject to retention/legal constraints.

## 5. Failure and reconciliation
Categorise credential revocation, rate limit, downtime, schema drift, unsupported procedure, source fact mismatch, authority hold/query, in-flight amendment, duplicates and disputed receipt. Quarantine unknown message types; do not silently convert messages to release. Reconcile after outages by authority-native IDs with operator review, preserving prior immutable facts.

## 6. Standards
WCO Data Model, UN/CEFACT and national EDI/XML/JSON profiles are mapping sources, not Trade Docs' canonical database. ADR-TDOC-0010 owns the standards mapping and conformance strategy; this ADR owns transport, side effects, retries, reconciliation and legal actor authority.

## 7. Independent implementation gates
| Gate | Evidence |
|---|---|
| TDOC-ADP-01 | Typed provider-neutral ports, API contracts, unknown-outcome taxonomy and auth/threat model |
| TDOC-ADP-02 | Synthetic authority adapter with deterministic signed acknowledgements and denial/hold fixtures |
| TDOC-ADP-03 | Outbox/inbox crash, idempotency, duplicate response and safe reissue tests |
| TDOC-ADP-04 | Per-provider credentials, revocation, forged callback and webhook replay rejection |
| TDOC-ADP-05 | Real jurisdiction specification, broker authority, mapping version and sandbox acceptance record |
| TDOC-ADP-06 | Scoped production authority and legal/operational sign-off; no universal customs capability claims |

No real customs credentials, authority response, certified integration or production market is established by this ADR.
## 8. Traceability and decision consequences

Implementation must provide code-path evidence, unit/integration/contract fixtures, explicit denied/unknown outcomes, security/tenant isolation proof, Shared contract lock and a documented provider/operator scope. Existing accepted TradeDocument v2 document/version/content/relationship semantics and Shared event producer authority remain unchanged. This local ADR does not define a canonical Shared event/key or move authority from Regulations, Trade, TMS, ERP, CP, IAM or the competent external issuer. **No gate passes by merging this documentation.**
