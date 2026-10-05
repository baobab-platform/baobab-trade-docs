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
  - proposed `documents.*.v2` event definitions
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

## Producer status

RTD-04 does not activate event production.

Even though Trade Docs is the accepted target authority for the `documents`
context, Shared v2 event entries remain `PROPOSED` until the later event
governance/producer-activation step.

This repository therefore must not claim to emit canonical `documents.*.v2`
events until that activation is merged in Shared.

## Future contracts

Do not invent local permanent substitutes for work explicitly deferred by the
RTD programme:

- RTD-05 — `CrossEngineObjectReference`;
- RTD-06 — Regulations ↔ Trade Docs requirement/evidence contracts;
- later Trade Docs dossier/CustomsCase/CustomsDeclaration/authority-response
  contracts.

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
