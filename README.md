# baobab-trade-docs

> **Status:** architecture established; runtime implementation has not started.

Baobab Trade Docs is the Baobab Platform engine for **executable trade-document
and Customs-workflow state**. Its accepted architecture is defined by
ADR-TDOC-0001 and ADR-TDOC-0002 and is bounded by the platform-level
ADR-SHARED-019 relationship with Baobab Regulations and Baobab Pulse.

## Role

Trade Docs owns the reusable platform semantics for:

- durable `TradeDocument` identity;
- immutable `DocumentVersion`;
- document content/artifact association;
- document lifecycle;
- documentary verification workflow;
- document relationships and provenance;
- future document dossiers;
- future Customs cases, declaration/submission workflows and authority
  responses.

It does **not** become authoritative for every fact contained in a document.

Examples:

```text
commercial invoice financial value
    → ERP / commercial authority

shipment movement
    → TMS / logistics authority

HS classification / regulatory requirement
    → Baobab Regulations

organisation identity
    → Control Plane

Customs release
    → competent Customs authority
```

## Foundational separations

```text
TradeDocument != File
TradeDocument != DocumentVersion
DocumentVersion != ContentArtifact

Document Lifecycle != Verification State
Verification != Regulatory Sufficiency

Document Requirement != TradeDocument

TradeDocument ID != Control Plane CanonicalEntity ID
```

Trade Docs owns the documentary side of these boundaries. Baobab Regulations
owns document/permit/evidence requirements and requirement-satisfaction
decisions.

## Shared contract authority

The canonical Shared document foundation is:

```text
baobab-platform/shared/contracts/trade-document/v2
```

governed by ADR-SHARED-020 / RTD-04.

The older Shared `trade-document/v1` package is a preserved pre-Trade-Docs
compatibility scaffold. New implementation must not target its overloaded
`status`, root-level `storage_reference`, Control Plane-minted document ID,
or proposed `trade-document.verified/rejected.v1` events.

The v2 package establishes:

- Trade Docs-minted opaque document IDs;
- extensible document type codes;
- first-class immutable versions;
- ContentArtifact storage and digest semantics;
- separate lifecycle / verification / temporal-validity axes;
- issuer claims;
- typed subject associations;
- document-to-document relationships;
- proposed `documents.*.v2` event facts.

Producer activation is intentionally separate from RTD-04. Until Shared event
governance assigns an authorised producer, the v2 event types remain
`PROPOSED`.

## Cross-engine relationship

```text
               CONTROL PLANE
          context / capability binding
                    │
                    ▼
            BAOBAB REGULATIONS
     requirements / applicability / decision
                    │
          requirements / decision refs
                    ▼
             BAOBAB TRADE DOCS
      documents / versions / workflow facts
                    │
          documentary evidence refs
                    ▼
            BAOBAB REGULATIONS
        requirement satisfaction / decision
                    │
             operational disposition
                    ▼
             Trade / TMS / ERP
```

Pulse may consume Regulations and Trade Docs facts asynchronously for
risk, opportunity, forecasting and research. Pulse is not part of the
synchronous documentary/regulatory enforcement path.

## Contract dependencies

Current architectural dependencies:

| Contract / decision | Role |
|---|---|
| Shared ADR-SHARED-019 | Cross-engine Regulations ↔ Trade Docs ↔ Pulse authority boundary |
| Shared ADR-SHARED-020 | TradeDocument v2 contract reconciliation |
| Shared `trade-document/v2` | Canonical document/version/content/relationship wire semantics |
| Shared event envelope | Cross-engine event metadata |
| Control Plane contracts | Tenant/platform context and canonical identity boundaries |
| Future RTD-05 contract | Portable cross-engine canonical object references |
| Future RTD-06 contracts | Regulations ↔ Trade Docs requirement/evidence choreography |

Canonical contracts remain in `baobab-platform/shared`; this repository must
consume them through a pinned contract lock once implementation begins. They
must not be copied or forked locally.

## ADR programme

- ADR-TDOC-0001 — Baobab Trade Docs Mission, Authority, Executable Trade
  Document and Customs Workflow Boundary.
- ADR-TDOC-0002 — Canonical TradeDocument, Version, Content and Relationship
  Model.

Later ADRs are expected to cover dossier, Customs case/declaration workflows,
authority adapters, verification/trust, transferable records, retention and
other implementation domains.

## Implementation status

No production application runtime is present yet.

Before runtime implementation begins, the repository must activate its real
language/runtime declaration, devcontainer and Foundation CI rather than
leaving template `.example` workflow/environment files as the execution
surface.

The implementation must start from Shared v2 semantics rather than reproducing
the old v1 model locally.
