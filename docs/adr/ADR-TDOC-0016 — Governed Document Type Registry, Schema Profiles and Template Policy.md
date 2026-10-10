# ADR-TDOC-0016 — Governed Document Type Registry, Schema Profiles and Template Policy

**Status:** Proposed — additional architecture decision, pending formal review; not code or production approval  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Programme note:** ADR-TDOC-0016..0019 are **extensions to the original ADR-TDOC-0001 charter programme**, which previously ended at ADR-TDOC-0015. Numbering/scope remain Proposed.  
**Inherited authority:** Accepted ADR-TDOC-0001/0002, Shared ADR-SHARED-019..026 and TradeDocument v2/RTD-05/06/07/08 governance, CP/IAM and competent external legal/issuer authority  
**Technology:** Headless self-hosting; TDOC-TECH-01 is separate Proposed technology strategy.  

> **Non-claim:** No new canonical Shared key, event, version contract, capability activation, legal authority, self-hosted integration or production readiness results from writing or merging this ADR.


## 1. Rationale and decision
Accepted ADR-TDOC-0002 makes `document_type` an extensible governed code and separates **DocumentType**, **DocumentFamily**, a legal requirement and a rendered template. This ADR defines how Trade Docs will govern type metadata and executable **technical document profile policy** without embedding jurisdictional regulatory requirements inside the registry.

Establish a versioned **DocumentTypeRegistry** with distinct **DocumentTypeDefinition**, **DocumentFamily**, **SchemaProfile**, **IssuerPolicyReference**, **LifecyclePolicy**, **VersioningPolicy**, **RenditionTemplateBinding** and **ProfileChangeRecord**. Profiles are **configuration of document-domain validation**, not laws or a universal assertion of compliance.

~~~mermaid
flowchart TD
  R["DocumentTypeRegistry"] --> F["DocumentFamily"]
  R --> T["DocumentTypeDefinition + effective version"]
  T --> S["Structured SchemaProfile"]
  T --> L["Lifecycle / Versioning Policy"]
  T --> I["Issuer PolicyReference"]
  T --> P["Optional RenditionTemplateBinding"]
  X["Regulations RequirementSet"] --> D["Dossier / completeness, not registry"]
  T --> D
~~~

## 2. Entity model and precedence
| Component | Responsible content | Forbidden assumption |
|---|---|---|
| DocumentFamily | Commercial, Transport, Origin/Certification, Customs, Delivery, Finance etc. | legal sufficiency for all markets |
| DocumentTypeDefinition | portable type code, semantic purpose, family, version, aliases/deprecation, valid use contexts | closed enum requiring new base domain schema |
| SchemaProfile | JSON/XML/EDI structured shape, media constraints, code-list revisions, validation outcome | proof source has legal authority |
| IssuerPolicyReference | issuer roles/mandates and external credential requirement | technical admin is issuing authority |
| LifecyclePolicy | allowed draft/issued/superseded/revoked/corrected operations | verifier/regulator outcome is lifecycle |
| VersioningPolicy | immutability/reissuance/amendment/translation/correction constraints | original content may be overwritten |
| RenditionTemplateBinding | template source/version, renderer config, output formats, accessibility and provenance | PDF layout is semantic authority |
| DocumentTypeAssignment | pinned profile/version on TradeDocument and DocumentVersion | type upgrade silently rewrites old issued documents |

## 3. Profile authoring and approval
Technical document profiles can be defined by authorised Trade Docs governance, but their **legal scope and mandatory requirements** are resolved by Regulations or competent issuing authorities. A document profile cannot override TradeDocument v2 canonical properties or local issuer/certification mandates. Governance flow: PROPOSED -> TECHNICALLY_VALIDATED -> REVIEWED -> ACTIVE_FOR_NAMED_USE -> DEPRECATED / RETIRED. Each change carries actor, source, effective time, backwards compatibility, migration guidance, maker/checker when appropriate and exact schema/template digest.

Document-version issue pins the effective profile plus source content and proof. Updating the registry **does not mutate previously issued DocumentVersions**, retroactively change historic completeness assessments or invalidate issued legal instruments by itself. Supersession requires explicit policy/evidence.

## 4. Initial reference profiles
| Family | Proposed representative profile | Ownership boundary |
|---|---|---|
| Commercial | Commercial Invoice / Pro Forma Invoice / Packing List | ERP/Trade authoritative quantities and prices; document representation in Trade Docs |
| Transport | Bill of Lading / Air Waybill / road consignment note | TMS physical facts; issuer/carrier legal claim and eBL control separate |
| Origin | Certificate of Origin | recognised chamber/authority issuance, not platform self-assertion |
| Customs | Declaration rendition / supporting schedule | CustomsCase and national authority adapter, not Regulations policy copy |
| Delivery | Proof of Delivery | TMS delivery event vs documentary issuer/recipient evidence |
| Finance | Bank/Funder letter or financing evidence | SCF request/ERP finance facts, external bank remains issuer |

Use an **open code registry**, not a globally closed enum. Mappings from UN/CEFACT, DCSA and national code lists are adapter metadata under ADR-TDOC-0010, not canonical truth.

## 5. Failure and compatibility
Conflicting code, profile removed during pending issue, expired issuer credentials, schema change after issuance, cross-tenant type override, template mismatch, document type with no legally authorised issuer, deprecated version and unresolved law must generate explicit error/unknown outcomes. Permit domain type extension but never runtime unreviewed code execution inside templates.

## 6. Implementation gates
| Gate | Objective acceptance proof |
|---|---|
| TDOC-TYP-01 | Domain and registry schema with immutable profile/version snapshots and separation from Regulations |
| TDOC-TYP-02 | Technical profile validation, open code pattern, collision and alias/deprecation tests |
| TDOC-TYP-03 | Maker/checker approval, issuer constraints, permission and wrong-tenant tests |
| TDOC-TYP-04 | Historical version remains unchanged after schema/template update, deterministic rendering proof |
| TDOC-TYP-05 | Commercial Invoice / POD / origin-certificate reference fixtures and source authority conformance |
| TDOC-TYP-06 | Exact Shared v2 contract fit and consumer compatibility before canonical type publication |

## 7. Alternatives and consequence
Reject hard-coded closed document-type enum, template-as-TradeDocument, embedding UG/ZA legal policy in type JSON, or changing history when a technical profile is updated. Registry publication alone is not production issuance authority or legal document validation.
## 8. Alternatives, traceability and follow-up

Reject direct replacement of immutable issued-version content, universal legal status inferred from a PDF/credential/hash, arbitrary tenant access from knowing a reference, external vendor as canonical Trade Docs authority, reuse of another engine's operational database and bypass of maker/checker or Regulations/Customs. Implement in separate bounded PRs with actual source and test fixtures, explicit capability/contract approval through Shared, and CP/EA-09 certification only after verified implementation. ADR-TDOC-0001/0002 remain Accepted and unchanged by this proposed extension.
