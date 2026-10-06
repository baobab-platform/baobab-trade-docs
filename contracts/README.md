# Shared contract consumption

This repository does **not** define canonical cross-engine contracts locally.

Canonical schemas live in:

```text
baobab-platform/shared
```

and must be consumed through the platform contract-lock/pinning mechanism when
runtime implementation begins.

## RTD-04 canonical document contract

Trade Docs is the semantic authority behind:

```text
contracts/trade-document/v2
```

in Shared, governed by ADR-SHARED-020.

The package currently contains:

- `domain.schema.json`
  - TradeDocument
  - DocumentVersion
  - ContentArtifact
  - DocumentIdentifier
  - IssuerClaim
  - SubjectAssociation
  - DocumentRelationship
  - separate lifecycle, verification and temporal-validity states
- `events.schema.json`
  - minimal document/version/artifact/relationship fact payloads
- `asyncapi.yaml`
  - ACTIVE `documents.*.v2` event definitions produced by `baobab-trade-docs` under ADR-SHARED-023
- examples validated in Shared CI.

## v1 compatibility rule

`contracts/trade-document/v1` is **not** the implementation target.

It is preserved because accepted architecture forbids silently mutating that
shape. In particular, this engine must not implement:

```text
Control Plane-minted trade_document_id
one overloaded TradeDocument.status
TradeDocument.storage_reference
related_shipment_id / related_procurement_request_id
trade-document.verified.v1 as a lifecycle event
trade-document.rejected.v1 as a lifecycle event
```

as the canonical Trade Docs domain.

## Producer status — RTD-07

ADR-SHARED-023 / RTD-07 assigns:

```text
documents steward = baobab-trade-docs
canonical producer = baobab-trade-docs
```

for the reconciled TradeDocument v2 event family.

The Shared event registry now marks those v2 events `ACTIVE`.

The legacy v1:

```text
trade-document.issued.v1
trade-document.verified.v1
trade-document.rejected.v1
```

remain `PROPOSED` and producerless. They are compatibility history and must
not be implemented as the new runtime event target.

`ACTIVE` here grants canonical producer authority. It does **not** claim
that this repository already contains a deployed application runtime,
transactional outbox, relay or broker integration.

## RTD-05 cross-engine references

RTD-05 is now defined by:

```text
contracts/cross-engine-reference/v1
```

under ADR-SHARED-021.

Cross-engine references preserve owner, object type, object identity, tenant
scope and historical pinning without copying foreign aggregates.

## RTD-06 Regulations ↔ Trade Docs exchange

RTD-06 is now defined by:

```text
contracts/regulatory-document-exchange/v1
```

under ADR-SHARED-022.

Trade Docs is responsible for the documentary side of the exchange:

```text
DocumentVersion
document type/family
issuer claim
verification snapshot
temporal-validity snapshot
subject references
documentary assertions
content-artifact references
```

The canonical Trade Docs query surface is:

```text
POST /v1/regulatory-document-evidence/resolve
```

RTD-07 activates the document-side RTD-06 fact:

```text
com.baobab-platform.documents.regulatory-evidence.offered.v1
```

with `baobab-trade-docs` as the canonical producer.

Its AsyncAPI publication contract lives in Shared under:

```text
contracts/regulatory-document-evidence/v1
```

Trade Docs SHALL NOT emit:

```text
requirement_satisfied = true
compliant = true
```

as documentary facts. Regulations owns those conclusions.

## Future contracts

Do not invent local permanent substitutes for later Trade Docs
dossier/CustomsCase/CustomsDeclaration/authority-response contracts.

Prototype types may exist behind local ports only if they are clearly
non-canonical and replaceable.

## Enforcement location

There is no runtime code yet.

When implementation starts, this file must be extended to identify:

- the exact pinned Shared revision/tag;
- generated or hand-maintained binding location;
- schema validation entry points;
- event producer/consumer adapters;
- conformance tests proving local types match Shared.
