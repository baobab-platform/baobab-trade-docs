# Baobab Trade Docs Architecture Decision Records

This directory is the engine-local ADR canon for
`baobab-platform/baobab-trade-docs`.

Cross-engine authority and canonical wire-contract decisions remain governed
by `baobab-platform/shared/docs/adr/`.

## Precedence relevant to Trade Docs

1. **ADR-SHARED-019** governs the platform-level Regulations ↔ Trade Docs ↔
   Pulse authority boundary.
2. **ADR-SHARED-020** governs the Shared TradeDocument v2 contract
   reconciliation.
3. **ADR-SHARED-021** governs portable cross-engine object references.
4. **ADR-SHARED-022** governs Regulations ↔ Trade Docs requirement/evidence
   choreography and the RTD-06 API/event surfaces.
5. **ADR-TDOC-0001** governs this engine's mission and system boundary.
6. **ADR-TDOC-0002** governs TradeDocument, DocumentVersion, content and
   relationship semantics.

If a local implementation conflicts with an accepted Shared cross-engine
contract or boundary, the conflict must be reconciled architecturally. It must
not be hidden through copied schemas, direct database access or undocumented
adapters.

## ADR register

| ADR | Status | Decision |
|---|---|---|
| ADR-TDOC-0001 | Accepted | Baobab Trade Docs Mission, Authority, Executable Trade Document and Customs Workflow Boundary |
| ADR-TDOC-0002 | Accepted | Canonical TradeDocument, Version, Content and Relationship Model |

## RTD-04 / RTD-05 / RTD-06 contract result

The canonical Shared foundation is:

```text
contracts/trade-document/v2
```

The old v1 package is compatibility history, not the implementation target.

Future local ADRs should build from the v2 foundation and must not reintroduce:

- Control Plane-minted TradeDocument IDs;
- file-as-document identity;
- mutable issued document versions;
- lifecycle/verification conflation;
- regulatory requirement logic inside document type definitions;
- direct cross-engine database ownership.
