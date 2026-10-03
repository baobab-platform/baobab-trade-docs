# ADR-TDOC-0002 — Canonical TradeDocument, Version, Content and Relationship Model

**Status:** Accepted — Foundational Trade Docs Domain Architecture  
**Date:** 2026-10-03  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Engine:** Baobab Trade Docs  
**Depends On:** ADR-TDOC-0001  
**Platform Contract Authority:** `baobab-platform/shared`  
**Capability Resolution Authority:** `baobab-platform/baobab-cp`  
**Canonical Organisation Authority:** `baobab-platform/baobab-cp`  
**Identity Authority:** `baobab-platform/baobab-iam`  
**Regulatory Decision Authority:** `baobab-platform/baobab-regulations`  
**Transport Execution Authority:** `baobab-platform/baobab-tms`  
**Financial Authority:** `baobab-platform/baobab-erp`  
**External Legal Authority:** Competent issuing authorities, carriers, banks, insurers, Customs administrations and other legally competent issuers  
**Decision Class:** TradeDocument / version / content / rendition / relationship / identity / provenance / lifecycle / transferability

---

# 1. Decision

Baobab Trade Docs SHALL adopt a canonical document architecture based on four independently identifiable layers:

```text id="i1afz7"
TRADE DOCUMENT
      │
      │ stable semantic identity
      ▼
DOCUMENT VERSION
      │
      │ immutable historical snapshot
      ▼
DOCUMENT CONTENT
      │
      │ one or more representations
      ▼
CONTENT ARTIFACT
      │
      ├── structured JSON
      ├── XML
      ├── PDF
      ├── EDI
      ├── image
      ├── signed credential
      └── authority-native representation
```

Document relationships SHALL form an explicit graph:

```text id="a43ht1"
TradeDocument A
      │
      ├── SUPPORTS ───────► TradeDocument B
      ├── REFERENCES ─────► TradeDocument C
      ├── SUPERSEDES ─────► TradeDocument D
      ├── DERIVED_FROM ───► TradeDocument E
      └── SUBMITTED_WITH ─► TradeDocument F
```

These layers SHALL NOT be collapsed into a single:

```text id="h5jvqe"
File {
    id
    filename
    url
    status
}
```

record.

---

# 2. Governing Principle

> **A TradeDocument is a durable semantic business object; a DocumentVersion is an immutable state of that object; DocumentContent is the information embodied by that version; and a ContentArtifact is one technical representation of that information.**

---

# 3. Why This Decision Is Required

The existing Shared:

```text id="ao0b10"
contracts/trade-document/v1
```

was intentionally minimal.

It currently models approximately:

```text id="baj7op"
TradeDocument
├── trade_document_id
├── tenant_id
├── document_type
├── status
├── related_shipment_id?
├── related_procurement_request_id?
├── issuing_party_reference
├── storage_reference?
├── issued_at?
├── superseded_by?
├── created_at
└── updated_at
```

That contract was appropriate as an initial cross-platform publication.

It is insufficient for a dedicated Trade Docs engine.

---

# 4. Existing Contract Limitations

The current Shared contract:

```text id="nd590x"
uses one storage_reference

uses one closed document-type enum

mixes document lifecycle with verification

models only one related shipment and procurement request

uses an unstructured issuing_party_reference

contains only one superseded_by pointer

contains no first-class versions

contains no content representations

contains no signatures

contains no external identifier schemes

contains no document relationship graph

contains no transferable-record semantics

contains no content integrity model
```

TDOC-0002 SHALL establish the richer canonical domain.

Shared SHALL later publish only the stable cross-engine subset.

---

# 5. Standards Direction

Baobab SHALL favour structured, interoperable and verifiable trade documents while retaining compatibility with legacy paper/PDF and authority-native formats.

UN/CEFACT's current **UN Verifiable Trade Documents (UNVTD)** work defines trade documents as structured, machine-readable data that may also be rendered for humans and cryptographically verified. Its current architecture uses JSON Schema, semantic mappings and verifiable credentials while remaining vendor-neutral.

UN/CEFACT's broader Reference Data Model approach likewise emphasises shared business semantics instead of tying interoperability to one static document/message representation.

Baobab SHALL align with these principles without requiring every external document to arrive as a UNVTD credential.

---

# 6. Electronic Transferable Records

Certain trade documents are legally different from ordinary informational documents.

Examples may include:

```text id="n7l9xp"
bill of lading

warehouse receipt

bill of exchange

promissory note
```

depending upon applicable law.

UNCITRAL's Model Law on Electronic Transferable Records distinguishes electronic transferable records by requiring reliable methods for identification, integrity and **control**, with control functioning as the electronic equivalent of possession.

Therefore:

> **Versioning and storage alone are insufficient for transferable documents.**

Baobab SHALL model transferability and control separately.

---

# 7. Fundamental Separations

The following SHALL remain non-negotiable:

```text id="6t90cw"
TradeDocument
    != File

TradeDocument
    != DocumentVersion

DocumentVersion
    != ContentArtifact

DocumentContent
    != Storage Location

Structured Data
    != PDF Rendering

Document Number
    != Canonical Document ID

External Authority ID
    != Canonical Document ID

Document Lifecycle
    != Verification State

Document Lifecycle
    != Validity State

Verification
    != Authenticity

Authenticity
    != Legal Validity

Legal Validity
    != Regulatory Sufficiency

Signature
    != Document

Signature Valid
    != Signatory Authorised

Document Relationship
    != Database Foreign Key

Document Version
    != Corrective Document

Amendment
    != Silent Mutation

Supersession
    != Deletion

Transfer of Control
    != Document Version Change

Document
    != Evidence

Evidence
    != Evidence Assessment
```

---

# 8. TradeDocument

`TradeDocument` SHALL be the durable semantic identity of a business/trade document.

It answers:

> **Which document is this?**

Conceptually:

```text id="j64g96"
TradeDocument
├── trade_document_id
├── tenant_context
├── document_type
├── document_family
├── issuer_reference
├── issuance_context
├── business_identifiers[]
├── subject_associations[]
├── lifecycle_state
├── current_version_id?
├── transferability_profile?
├── confidentiality_classification?
├── external_references[]
├── created_at
└── aggregate_version
```

---

# 9. Document Identity Survives Representation Changes

The same TradeDocument MAY have:

```text id="ruxscp"
JSON representation

XML representation

human-readable HTML

PDF rendering
```

without becoming four different TradeDocuments.

---

# 10. Document Identity May Survive Version Changes

Where the legal/document policy treats an amendment as revision of the same document:

```text id="j1m4fj"
TradeDocument TD-001
│
├── Version 1
├── Version 2
└── Version 3
```

SHALL be valid.

---

# 11. New Legal Instrument May Require New Document Identity

Some corrections SHALL instead create:

```text id="lo28k3"
TradeDocument TD-001
      │
      │ SUPERSEDED_BY
      ▼
TradeDocument TD-002
```

rather than:

```text id="46ci71"
TD-001 version 2
```

The applicable document policy SHALL determine which model applies.

---

# 12. Versioning Policy Is Document-Type Specific

This SHALL NOT be universal:

```text id="nkt06c"
every correction
=
new version
```

Nor:

```text id="mwev4h"
every correction
=
new document
```

Different legal/business documents permit different amendment models.

---

# 13. Canonical Document ID

Trade Docs SHALL mint its authoritative domain identifier.

Conceptually:

```text id="ziloxo"
tdoc_<opaque-id>
```

or another approved canonical format.

The identifier SHALL:

```text id="fk5oe1"
be opaque

be tenant-safe

not encode document type

not encode jurisdiction

not encode business meaning

not depend on provider IDs

remain durable
```

---

# 14. Correction to Existing Shared Contract

The existing Shared schema describes:

```text id="4gws4a"
trade_document_id
```

as a:

> Control Plane-minted opaque identifier.

That statement SHALL be superseded for Trade Docs domain identity.

The target architecture is:

```text id="5u6m81"
Trade Docs Provider
      │
      ▼
mints TradeDocument domain ID
```

while:

```text id="8nbeki"
Control Plane
```

continues to govern:

```text id="qwn1m2"
tenant context

canonical organisations

capability resolution

mappings

CanonicalEntity registration where applicable
```

---

# 15. No Synchronous CP Dependency for Document Creation

TradeDocument creation SHALL NOT normally require:

```text id="69j14b"
Trade Docs
   │
   ▼
Control Plane
   │
   ▼
please mint document ID
```

before local transaction commit.

That would unnecessarily couple document availability to Control Plane availability.

---

# 16. CanonicalEntity Registration Is Separate

Where a TradeDocument requires representation as a Control Plane:

```text id="wsykvq"
CanonicalEntity
```

that registration/mapping SHALL be a separate platform concern.

Therefore:

```text id="e80s76"
TradeDocument domain ID
    !=
Control Plane CanonicalEntity ID
```

unless platform architecture explicitly establishes identity equivalence.

---

# 17. Business Document Number

A document MAY carry one or more business identifiers.

Example:

```text id="ccrv3v"
Canonical ID:
tdoc_01...

Business identifier:
INV-ZA-2026-004188
```

Both SHALL be retained.

---

# 18. Business Identifier Model

Conceptually:

```text id="yaflmy"
DocumentIdentifier
├── value
├── scheme
├── issuer
├── jurisdiction?
├── scope?
├── issued_at?
├── valid_from?
├── valid_to?
└── external_system?
```

---

# 19. One Document Can Have Several Identifiers

Example:

```text id="58r6yj"
TradeDocument
├── Carrier B/L number
├── Customs reference
├── internal Thamani reference
└── external platform document reference
```

No one external identifier SHALL replace canonical identity.

---

# 20. Document Type

`document_type` SHALL identify document semantics explicitly.

It SHALL NOT be inferred from:

```text id="h6jg5o"
filename

file extension

folder

issuer

template name
```

---

# 21. Closed Enum Is Insufficient

The current Shared enum contains only:

```text id="9vu5o6"
COMMERCIAL_INVOICE

PACKING_LIST

BILL_OF_LADING

AIRWAY_BILL

CERTIFICATE_OF_ORIGIN

CUSTOMS_DECLARATION

INSPECTION_CERTIFICATE

PROOF_OF_DELIVERY

INSURANCE_CERTIFICATE
```

A production trade-document engine requires far more document classes.

The canonical type system SHALL therefore become extensible and governed.

---

# 22. Document Type Registry

Trade Docs SHOULD establish or consume a canonical:

```text id="taoy0k"
DocumentTypeRegistry
```

Conceptually:

```text id="86fwt2"
DocumentType
├── type_code
├── family
├── name
├── description
├── transferable_capability
├── lifecycle_policy
├── amendment_policy
├── issuer_roles[]
├── possible_subject_types[]
├── schema_refs[]
├── semantic_context_refs[]
├── authority_profile?
├── effective_from
├── effective_to?
└── version
```

---

# 23. Document Families

Initial high-level families MAY include:

```text id="38d4dn"
TRADE

TRANSPORT

CUSTOMS

REGULATORY

PROCUREMENT

FINANCIAL

INSURANCE

QUALITY

WAREHOUSE

PAYMENT

CONTRACT

IDENTITY_SUPPORTING

OTHER
```

A family SHALL NOT itself determine legal authority.

---

# 24. UNVTD Compatibility

Current UNVTD coverage includes document classes across trade, transport, financial and regulatory categories such as commercial invoices, packing lists, bills of lading, air waybills, road consignment notes, warehouse receipts, insurance certificates, letters of credit, certificates of origin and Customs declarations.

The Baobab type registry SHOULD maintain explicit mappings where relevant.

---

# 25. DocumentVersion

`DocumentVersion` SHALL represent one immutable semantic state of a TradeDocument.

Conceptually:

```text id="b1frfd"
DocumentVersion
├── document_version_id
├── trade_document_id
├── version_sequence
├── external_revision_label?
├── lifecycle_snapshot
├── semantic_payload_ref?
├── source_snapshot_ref?
├── content_set_id
├── created_at
├── created_by
├── issued_at?
├── effective_from?
├── effective_to?
├── change_reason?
├── supersedes_version_id?
└── integrity_metadata
```

---

# 26. Version ID

Each version SHALL have its own durable identifier.

Example:

```text id="in7l77"
TradeDocument:
tdoc_A

Versions:
tdocv_A_001
tdocv_A_002
tdocv_A_003
```

Exact format remains implementation-specific.

---

# 27. Version Sequence

A monotonic:

```text id="gi7ffj"
version_sequence
```

MAY provide local ordering.

It SHALL NOT be assumed to be an external document revision number.

---

# 28. External Revision Label

External issuers may provide:

```text id="fra09d"
Rev A

Version 3

Amendment 2
```

Such values SHALL be retained separately.

---

# 29. Issued Version Is Immutable

Once a version has been:

```text id="z16us0"
issued

submitted

signed

accepted by external authority

or otherwise committed
```

according to document policy, its semantic content SHALL be immutable.

---

# 30. Draft Version

A DRAFT version MAY evolve internally before commitment.

However, if draft history matters for:

```text id="cvtqrw"
approval

audit

regulated preparation

collaboration
```

the implementation MAY preserve draft revisions separately.

---

# 31. No Silent Mutation

This SHALL be prohibited:

```text id="s814qg"
UPDATE document_content
SET amount = 52000
WHERE version = issued_version
```

after issue.

---

# 32. Correction by New Version

Where policy permits:

```text id="t5dixa"
Version 1
    │
    ▼
Correction
    │
    ▼
Version 2
```

SHALL preserve:

```text id="8hns71"
Version 1

reason

actor

time

relationship
```

---

# 33. Correction by New Document

Where the legal instrument requires replacement:

```text id="z26im9"
Document A
   │
   │ REPLACED_BY
   ▼
Document B
```

SHALL be used instead.

---

# 34. DocumentVersion Is Not ContentArtifact

A version is the semantic state.

A ContentArtifact is a technical representation.

One version MAY have:

```text id="zz4f8b"
JSON

PDF

XML

EDI
```

representations simultaneously.

---

# 35. DocumentContentSet

A `DocumentContentSet` SHALL group the content representations belonging to one version.

Conceptually:

```text id="8r8ba5"
DocumentContentSet
├── content_set_id
├── document_version_id
├── semantic_payload_ref?
├── artifacts[]
└── created_at
```

---

# 36. ContentArtifact

Conceptually:

```text id="h5mh1h"
ContentArtifact
├── artifact_id
├── document_version_id
├── artifact_role
├── media_type
├── syntax?
├── schema_ref?
├── semantic_context_ref?
├── language?
├── character_encoding?
├── storage_reference
├── byte_length?
├── digest_algorithm
├── digest_value
├── generated_at?
├── generated_by?
├── renderer_version?
└── source_artifact_id?
```

---

# 37. Artifact Roles

Initial semantic roles MAY include:

```text id="aupdkl"
CANONICAL_STRUCTURED_CONTENT

SOURCE_ORIGINAL

HUMAN_RENDERING

AUTHORITY_NATIVE_MESSAGE

SIGNED_ENVELOPE

SCANNED_COPY

DERIVED_EXTRACTION

ATTACHMENT_PART

OTHER
```

---

# 38. Canonical Structured Content

Where Baobab generates a native digital document, the preferred architecture SHOULD be:

```text id="zaa11g"
structured semantic data
        │
        ├── machine processing
        ├── validation
        ├── signing
        └── human rendering
```

rather than:

```text id="o6j6ar"
PDF first
    ↓
extract data later
```

---

# 39. UNVTD Structured-First Alignment

UNVTD's current approach treats the structured trade document as data capable of:

```text id="ei9grz"
machine processing

human rendering

cryptographic signing

inter-system exchange
```

rather than treating PDF as the primary information model.

Trade Docs SHOULD remain compatible with this direction.

---

# 40. PDF Remains Supported

Structured-first architecture SHALL NOT imply:

```text id="6w7s77"
PDF prohibited
```

Many authorities and counterparties still require:

```text id="o42kt1"
PDF

scan

image

paper-originated artifact
```

Trade Docs SHALL support them with explicit provenance.

---

# 41. Source Original

When receiving an external document:

```text id="ogee1x"
source original
```

SHALL be preserved where required.

Example:

```text id="6p2cba"
External certificate PDF
        │
        ▼
SOURCE_ORIGINAL artifact
```

---

# 42. Derived Extraction

If Trade Docs extracts structured data from a PDF:

```text id="bfcfrd"
Source PDF
       │
       ▼
Extraction Activity
       │
       ▼
Structured Representation
```

the derived representation SHALL retain provenance.

It SHALL NOT silently replace the source original.

---

# 43. OCR / Extraction Is Not Authority

This remains:

```text id="swkt2r"
Extracted Value
    !=
Issuer's authoritative structured assertion
```

unless independently verified.

---

# 44. Integrity

Every material content artifact SHOULD carry a cryptographic digest.

Conceptually:

```text id="9n8c43"
digest_algorithm

digest_value
```

The digest SHALL apply to an explicitly defined byte representation.

---

# 45. Integrity Is Not Authenticity

This SHALL remain:

```text id="pfcg44"
hash matches
    !=
issuer authenticated
```

A hash proves integrity relative to a known hash value.

It does not itself establish who issued the content.

---

# 46. Authenticity

Document authenticity MAY depend on:

```text id="vgl93n"
cryptographic signature

issuer verification

authority lookup

external registry

trusted delivery channel

manual verification
```

depending on document type.

Detailed verification architecture belongs to ADR-TDOC-0008.

---

# 47. Signature Attachment

A cryptographic signature SHALL bind to:

```text id="azojzw"
specific DocumentVersion

specific ContentArtifact

or specific canonical signed payload
```

—not merely the mutable TradeDocument root.

---

# 48. Signature Does Not Float Across Versions

This SHALL be prohibited:

```text id="jep85e"
Signature on Version 1
automatically considered
signature on Version 2
```

unless the signature mechanism explicitly signs both.

---

# 49. Semantic Payload

A native structured document SHOULD maintain a semantic payload separate from its presentation.

Conceptually:

```text id="xgp71n"
DocumentVersion
      │
      ▼
Semantic Payload
      │
      ├── JSON
      ├── semantic context
      └── schema version
             │
             ▼
        Renderer
        ├── HTML
        └── PDF
```

---

# 50. Schema Versioning

Every structured representation SHALL identify the applicable schema version where required.

Example:

```text id="rds7l8"
schema:
UNVTD CommercialInvoice vX

or

DCSA TransportDocument 3.0
```

External schema identity SHALL remain independent from Baobab canonical document identity.

---

# 51. Semantic Vocabulary

Baobab SHOULD map structured document terms to governed semantic vocabularies where useful.

The current UN/CEFACT Web Vocabulary specifically supports linking JSON document properties to shared definitions via technologies such as JSON-LD.

---

# 52. Content Storage

`storage_reference` SHALL move from being a property of TradeDocument to being a property of an individual ContentArtifact.

This permits:

```text id="sbxevh"
Version 1 PDF
    → Storage Object A

Version 1 JSON
    → Storage Object B

Version 2 PDF
    → Storage Object C
```

without ambiguity.

---

# 53. Storage Reference Is Opaque

Trade Docs SHALL NOT expose storage implementation as domain semantics.

A content artifact MAY ultimately reside in:

```text id="0b199h"
object storage

content-addressed store

external authority store

document management service

cold archive
```

A later ADR defines storage.

---

# 54. Storage Location Is Not Document Identity

This remains:

```text id="4imf1l"
s3://bucket/a.pdf
    !=
TradeDocument ID
```

Changing storage provider SHALL not change canonical document identity.

---

# 55. Content Migration

Content MAY move:

```text id="acmk4p"
hot storage
   ↓
archive storage
```

without creating a new DocumentVersion if bytes/semantic content did not change.

---

# 56. Renderer Change

Re-rendering the same semantic Version using:

```text id="7odsfh"
Renderer v1
    ↓
Renderer v2
```

MAY create a new `HUMAN_RENDERING` ContentArtifact without creating a new DocumentVersion if document semantics are unchanged.

---

# 57. Semantic Change Requires Version Decision

Changing:

```text id="21a5iv"
invoice amount

consignee

cargo quantity

document terms
```

is not merely rendering.

It SHALL require a new version or new TradeDocument according to document policy.

---

# 58. TradeDocument Lifecycle

The engine SHALL not use one overloaded `status` field for every concern.

Document state SHALL be decomposed.

At minimum:

```text id="2dft84"
DocumentLifecycleState

VerificationState

TemporalValidityState

TransferControlState where applicable

Submission/AuthorityState where applicable
```

---

# 59. Lifecycle State

A generic document lifecycle MAY include:

```text id="qoztxi"
DRAFT

ISSUED

SUPERSEDED

VOIDED

WITHDRAWN

ARCHIVED
```

Not every document type needs every state.

---

# 60. Verification Is Not Lifecycle

The existing Shared contract includes:

```text id="dyqydj"
VERIFIED

REJECTED
```

inside `tradeDocumentStatus`.

This SHALL be superseded.

These states concern verification or workflow outcome, not intrinsic document lifecycle.

---

# 61. Verification State

A separate projection MAY include:

```text id="gdjv0c"
UNVERIFIED

PENDING

VERIFIED

FAILED

DISPUTED

UNKNOWN
```

Detailed semantics belong to TDOC-0008.

---

# 62. Temporal Validity

Documents may independently be:

```text id="xle7z2"
NOT_YET_EFFECTIVE

CURRENTLY_VALID

EXPIRED

REVOKED

UNKNOWN
```

depending upon issuer/authority semantics.

---

# 63. Expiry Is Not Deletion

An expired certificate remains a TradeDocument.

It SHALL not be deleted merely because:

```text id="6imszg"
valid_to < now
```

---

# 64. Revocation Is Not Content Mutation

If an issuer revokes a certificate:

```text id="g0urtk"
original certificate content
```

SHALL remain historically available.

A revocation fact changes its validity state.

---

# 65. Authority Submission State

For documents submitted to external authorities, another axis MAY include:

```text id="95ut0m"
NOT_SUBMITTED

SUBMISSION_PENDING

SUBMITTED

ACKNOWLEDGED

ACCEPTED

REJECTED

AMENDMENT_REQUIRED
```

Detailed Customs workflow belongs to TDOC-0004/0005.

---

# 66. One Document Can Have Several Submission Contexts

A document MAY be:

```text id="hktav7"
submitted to Customs Authority A

submitted to Bank B

shared with Customer C
```

These interactions SHALL not be represented as one universal `submission_status`.

---

# 67. Issuer

Every TradeDocument SHALL have a determinable issuer claim.

Conceptually:

```text id="bnm92o"
DocumentIssuer
├── party_reference
├── issuer_role
├── source_identity?
├── authority_context?
└── verification_state?
```

---

# 68. Issuer Reference

Where the issuer is known in Baobab:

```text id="cfhltf"
canonical_organisation_id
```

SHOULD be referenced.

For unresolved external issuers, an external party reference MAY exist temporarily.

---

# 69. Do Not Create Duplicate Organisations

Trade Docs SHALL attempt canonical organisation resolution before minting or persisting local organisation copies.

It SHALL NOT create:

```text id="tu1qsu"
"Maersk in Trade Docs"

"SARS in Trade Docs"

"URA in Trade Docs"
```

as competing canonical organisation identities.

---

# 70. Issuer Claim Is Not Issuer Verification

This remains:

```text id="96uq5d"
document says
issuer = Authority X

    !=

Baobab verified
issuer = Authority X
```

Verification belongs to separate trust/evidence processing.

---

# 71. Recipient

A document MAY identify one or more:

```text id="x0jtsr"
recipient

consignee

applicant

beneficiary

holder

endorsee
```

depending on document semantics.

These SHALL NOT be collapsed into one generic recipient field when legal meaning differs.

---

# 72. Subject Associations

TradeDocument SHALL relate to domain objects through explicit typed associations.

Conceptually:

```text id="kmi271"
DocumentSubjectAssociation
├── trade_document_id
├── subject_context
├── subject_type
├── subject_reference
├── role
├── effective_from?
└── effective_to?
```

---

# 73. Subject Types

Possible subjects include:

```text id="gwlrt9"
TradeShipment

LogisticsShipment

Consignment

TransportMovement

TransportEquipment

CustomsCase

CustomsDeclaration

Order

Invoice

Payment

Contract

WarehouseReceipt

InventoryLot

Product

Organisation

ProviderQualification

RegulatoryAssessment
```

The set SHALL remain extensible.

---

# 74. No One-Off Foreign-Key Explosion

This architecture SHALL avoid:

```text id="77bzyx"
related_shipment_id

related_procurement_request_id

related_invoice_id

related_payment_id

related_customs_case_id

related_everything_id
```

on `TradeDocument`.

Typed subject associations are preferred.

---

# 75. Existing Shared Related Fields

Current Shared:

```text id="0il2mo"
related_shipment_id
related_procurement_request_id
```

SHALL be migrated toward typed associations.

They MAY remain temporarily for compatibility.

---

# 76. DocumentRelationship

Document-to-document semantics SHALL use a first-class relationship.

Conceptually:

```text id="lym2s2"
DocumentRelationship
├── relationship_id
├── source_document_id
├── target_document_id
├── relationship_type
├── source_version_id?
├── target_version_id?
├── reason?
├── created_at
├── created_by
└── provenance?
```

---

# 77. Relationship Vocabulary

Initial relationship semantics SHOULD support:

```text id="5qvywg"
SUPERSEDES

SUPERSEDED_BY

AMENDS

AMENDED_BY

CORRECTS

CORRECTED_BY

REPLACES

REPLACED_BY

CANCELS

CANCELLED_BY

SUPPORTS

SUPPORTED_BY

EVIDENCES

EVIDENCED_BY

REFERENCES

REFERENCED_BY

DERIVED_FROM

SOURCE_FOR

GENERATED_FROM

GENERATES

SUBMITTED_WITH

RESPONDS_TO

FULFILS_REQUIREMENT

DUPLICATES
```

Not all inverse relations need to be persisted separately.

---

# 78. Relationship Direction

Relationship semantics SHALL have defined direction.

Example:

```text id="jjf85q"
Document B
SUPERSEDES
Document A
```

must not be ambiguously interpreted as the reverse.

---

# 79. Supersession Graph Is Acyclic

Relationships such as:

```text id="b36k8y"
SUPERSEDES

REPLACES
```

SHALL be validated to prevent cycles.

This SHALL be invalid:

```text id="29q9a6"
A supersedes B

B supersedes A
```

---

# 80. Supporting Documents

A Customs declaration may be associated with:

```text id="3284vj"
commercial invoice

packing list

certificate of origin

permit

transport document
```

through:

```text id="c7e49s"
SUPPORTS
```

or:

```text id="00t5hz"
SUBMITTED_WITH
```

relationships rather than file attachments alone.

---

# 81. Supporting Document Is Still Independent

A commercial invoice submitted with a Customs declaration SHALL retain its own:

```text id="wrc4lc"
TradeDocument identity

issuer

version

authority

lifecycle
```

It SHALL not become a binary child blob of the declaration.

---

# 82. Annex / Content Part

A true annex that is legally part of the same document MAY instead belong to the same DocumentVersion's content set.

The engine SHALL distinguish:

```text id="hctfu7"
Document relationship
```

from:

```text id="50e5aa"
content part relationship
```

---

# 83. Derived Documents

A document may be generated from source business records.

Example:

```text id="kqevhq"
ERP Invoice
      │
      ▼
TradeDocument
COMMERCIAL_INVOICE
```

That does not make:

```text id="cfj2xy"
ERP invoice record
=
TradeDocument
```

The TradeDocument is the governed documentary representation.

---

# 84. Generated From Business Record

Business-record provenance SHOULD use:

```text id="59pofp"
source associations / provenance
```

rather than pretending the source business record is another TradeDocument.

---

# 85. Document-to-Document Derivation

By contrast:

```text id="l6v5lx"
Certificate A
      │
      ▼
Derived summary / translation B
```

may use:

```text id="i4f757"
DERIVED_FROM
```

between TradeDocuments.

---

# 86. Translation

A translated document MAY be:

```text id="bke24o"
another content representation
```

or:

```text id="rkcsg0"
a derived TradeDocument
```

depending on whether the translation has independent:

```text id="327thh"
issuer

certification

legal effect

lifecycle
```

---

# 87. Copy vs New Document

Creating a copy of an artifact SHALL NOT create a new TradeDocument.

Example:

```text id="ch99vg"
same PDF
downloaded twice
```

remains one content artifact unless independent provenance requires otherwise.

---

# 88. Duplicate Detection

Trade Docs MAY detect possible duplicates based on:

```text id="ewat1o"
content hash

issuer

document number

document type

issue date

subject associations
```

A duplicate candidate SHALL NOT be automatically merged without governed rules.

---

# 89. Document Authority

Trade Docs owns:

```text id="ziqujw"
canonical TradeDocument identity

document versioning

content association

document relationships

document lifecycle

document provenance
```

It does not necessarily own the underlying business truth.

---

# 90. Document-Specific Business Authority

Examples:

```text id="bm0ibv"
Commercial invoice financial values
    → ERP

Bill of lading issuance facts
    → issuing carrier

Customs declaration authority response
    → Customs authority

Certificate of origin
    → competent issuer

POD physical-delivery fact
    → TMS / delivery provider
```

Trade Docs governs their documentary representation.

---

# 91. Legal Authority

This SHALL remain:

```text id="erq821"
Trade Docs stores/records document
    !=
Trade Docs is legal issuer
```

---

# 92. Externally Issued Document

Conceptually:

```text id="1qk2st"
External Issuer
      │
      ▼
Source Document
      │
      ▼
Trade Docs Ingestion
      │
      ├── canonical identity
      ├── source artifact
      ├── provenance
      └── verification state
```

---

# 93. Baobab-Generated Document

Conceptually:

```text id="15n0k9"
Authoritative Business Facts
       │
       ▼
Trade Docs Generator
       │
       ▼
DocumentVersion
       │
       ├── Structured Content
       ├── PDF Rendering
       └── Signature
```

---

# 94. Issuing Party Still Governs Issuance

Trade Docs generating a document for:

```text id="hutolb"
Thamani

ZuriBeans

another tenant
```

does not make:

```text id="2rce2h"
Baobab Trade Docs
```

the business/legal issuer.

The tenant/legal entity acts through the engine.

---

# 95. TransferabilityProfile

A TradeDocument MAY carry a transferability classification.

Conceptually:

```text id="beqjzg"
TransferabilityProfile
├── class
├── legal_regime_ref?
├── jurisdiction_ref?
├── transferable_record_scheme?
├── control_method_ref?
└── status
```

---

# 96. Transferability Classes

At minimum the model SHOULD distinguish conceptually:

```text id="z3rw2f"
NON_TRANSFERABLE

POTENTIALLY_TRANSFERABLE

ELECTRONIC_TRANSFERABLE_RECORD

PAPER_TRANSFERABLE_INSTRUMENT_REFERENCE

UNKNOWN
```

Exact canonical vocabulary requires legal/regulatory review.

---

# 97. Transferability Must Not Be Inferred From Type Alone

This SHALL be prohibited:

```text id="2vtoyp"
if document_type == BILL_OF_LADING:
    transferable = true
```

because:

```text id="59msl7"
sea waybill

straight bill

order bill

jurisdiction

governing law

issuance terms
```

may materially affect legal character.

---

# 98. MLETR Control

For an electronic transferable record where applicable law recognises such treatment, the engine SHALL be capable of representing:

```text id="7dcrfc"
control

controller

transfer of control

surrender

integrity

record identity
```

consistent with the functional-equivalence principles of MLETR.

---

# 99. Control Is Not Ordinary Permission

This SHALL remain:

```text id="v13lmt"
MLETR-style control
    !=
IAM permission
```

IAM may authenticate the person exercising an action.

It does not itself establish legal control over a transferable record.

---

# 100. Control Is Not Ownership of Goods Automatically

Likewise:

```text id="gthxyn"
control of electronic transferable record
    !=
universal proof of title to goods
```

Legal consequences depend on applicable substantive law.

---

# 101. Control State Is Separate From Document Version

An endorsement or transfer MAY change:

```text id="s42qyt"
controller
```

without changing the document's substantive content.

Therefore:

```text id="3gv9oq"
ControlTransfer
    !=
DocumentVersion
```

---

# 102. Transfer Control Model

Conceptually:

```text id="3j2myq"
TransferableRecordControl
├── trade_document_id
├── document_version_id
├── controller
├── control_method
├── established_at
├── ended_at?
├── source_system
├── legal_regime_ref?
├── evidence_ref
└── audit_reference?
```

---

# 103. Control Transfer

Conceptually:

```text id="eec7rq"
Controller A
     │
     ▼
Transfer / Endorsement
     │
     ▼
Controller B
```

The transfer history SHALL be reconstructable.

---

# 104. DCSA eBL Alignment

DCSA's current eBL architecture includes issuance, amendment/surrender and endorsement-chain processes for electronic bills of lading. Its endorsement-chain module explicitly records actions including transfer, blank endorsement, endorsement to order and surrender, together with audit references.

Trade Docs SHALL support adapters for those semantics without making DCSA's ocean-specific model universal.

---

# 105. DCSA Amendment Example

Current DCSA eBL technical guidance includes a flow in which an original transport document may be voided and an amended document issued.

This supports Baobab's distinction between:

```text id="v2k36h"
new version
```

and:

```text id="7stj0m"
new legal document replacing old document
```

according to applicable document policy.

---

# 106. Endorsement Chain Is Not Relationship Graph

This distinction SHALL remain:

```text id="nkpjvk"
DocumentRelationship graph
    !=
Transferable-document endorsement/control chain
```

The first relates documents.

The second represents control/title-transfer actions relevant to a transferable instrument.

---

# 107. Electronic vs Paper

Trade Docs SHALL support:

```text id="gkqxhz"
NATIVE_DIGITAL

DIGITISED_PAPER

PAPER_REFERENCE

HYBRID
```

or equivalent medium classifications.

---

# 108. Scanned Paper Is Not Native Electronic Record

This SHALL remain:

```text id="y9rwwf"
scan of paper B/L
    !=
electronic transferable record
```

merely because the scan is a PDF.

---

# 109. Change of Medium

Where supported by legal regime and document type, the engine MAY need to represent:

```text id="piuhvh"
paper → electronic

electronic → paper
```

conversion.

UNCITRAL MLETR expressly addresses change of medium as part of its framework.

Detailed transferable-record architecture SHALL be defined in a later ADR.

---

# 110. Verifiable Credentials

Trade Docs SHOULD support verifiable-credential representations where appropriate.

UNVTD currently uses W3C Verifiable Credentials as a portable cryptographic envelope for structured trade documents.

Baobab SHALL not require VC technology for every document.

---

# 111. Cryptographic Verification Is Not Trust Decision

UNVTD's architecture itself distinguishes cryptographic verification from the broader decision whether the issuer should be trusted.

Baobab SHALL preserve:

```text id="gr50te"
Signature Valid
    !=
Issuer Trusted

Issuer Trusted
    !=
Document Sufficient

Document Sufficient
    !=
Regulatory Requirement Satisfied
```

---

# 112. Evidence Boundary

A TradeDocument MAY be used as evidence.

This SHALL remain:

```text id="86caaa"
TradeDocument
    !=
Evidence
```

Evidence associations SHALL be first-class but distinct.

---

# 113. Evidence Relationship

Conceptually:

```text id="lkunn1"
TradeDocument
       │
       ▼
Evidence Record
       │
       ▼
Evidence Assessment
       │
       ▼
Decision / Requirement
```

ADR-REG-0014 reinforces the distinction between evidence, evidence assessment, evidentiary sufficiency, provenance and decision trace.

---

# 114. Provenance

Every critical TradeDocument SHALL preserve provenance sufficient to establish:

```text id="p8d8ha"
where it came from

who supplied it

who claims to have issued it

how it entered Baobab

which content was received

which transformations occurred

which version exists

which verification occurred
```

---

# 115. Provenance Is Not Audit Log

This remains:

```text id="yp5ib4"
provenance
    !=
audit log
```

Both are required for different purposes.

---

# 116. Transformation Provenance

Derived artifacts SHALL record the activity that created them.

Example:

```text id="f8jh0q"
Authority XML
      │
      ▼
Mapper v2.3
      │
      ▼
Canonical JSON
      │
      ▼
Renderer v1.8
      │
      ▼
PDF
```

---

# 117. Source Snapshot

When generating a document from business systems, Trade Docs SHALL preserve sufficient source lineage.

Conceptually:

```text id="5oqgne"
SourceSnapshot
├── source_context
├── source_entity_refs[]
├── source_versions[]
├── extracted_values/hash?
├── snapshot_time
└── generation_policy_version
```

---

# 118. Later Source Changes

If ERP later changes an invoice record:

```text id="4yi5mz"
ERP Invoice v2
```

Trade Docs SHALL NOT silently rewrite:

```text id="7npkhc"
Commercial Invoice Document v1
```

that was previously issued.

---

# 119. Re-generation

A source change MAY cause:

```text id="pou6te"
new DocumentVersion
```

or:

```text id="217v3i"
new TradeDocument
```

according to document policy.

---

# 120. Document Relationships Across Engines

Cross-engine references SHALL use canonical identifiers.

Example:

```text id="hbk7dq"
TradeDocument
   │
   ├── LogisticsShipmentRef → TMS
   ├── InvoiceRef           → ERP
   ├── RegulatoryDecisionRef → Regulations
   └── CustomsCaseRef       → Trade Docs
```

No direct database foreign keys across engine databases SHALL be required.

---

# 121. Deleted Source Records

A document SHALL remain historically interpretable even where its source business object is later:

```text id="9l8nss"
closed

archived

retired
```

according to retention policy.

---

# 122. No Hard Deletion of Material Issued Versions

Material issued/submitted/signed versions SHALL not ordinarily be hard-deleted while retention or audit requirements remain.

Deletion and retention policies belong to TDOC-0011.

---

# 123. Document Relationships Are Temporal Facts

A relationship MAY have:

```text id="h8yplm"
created_at

effective_at

ended_at
```

where relationships change over time.

---

# 124. Relationships Are Auditable

Creation/removal of material relationships such as:

```text id="q20grv"
SUPERSEDES

SUPPORTS

FULFILS_REQUIREMENT
```

SHALL be auditable.

---

# 125. Relationship Does Not Transfer Authority

This remains:

```text id="qg6jdj"
Document A supports Document B
    !=
Document A owns Document B
```

---

# 126. Content Language

Content artifacts SHOULD preserve:

```text id="j65l7h"
language

script

locale
```

where relevant.

One DocumentVersion MAY have several human-language renderings.

---

# 127. Translation Integrity

An unofficial translation SHALL remain distinguishable from:

```text id="t786bs"
certified translation
```

or the authoritative-language document.

---

# 128. Document Confidentiality

TradeDocument MAY carry an access classification such as:

```text id="hdkgb5"
PUBLIC

INTERNAL

CONFIDENTIAL

RESTRICTED

REGULATED
```

according to future security governance.

The classification SHALL not replace per-tenant authorisation.

---

# 129. Document Access

Authorisation SHOULD consider:

```text id="37j2dn"
tenant

legal entity

document role

subject relationship

issuer relationship

recipient relationship

case assignment

confidentiality

actor authority
```

---

# 130. Content Access Can Differ From Metadata Access

The engine MAY permit a user to know:

```text id="8nci1s"
Commercial Invoice exists
```

without permitting access to:

```text id="2ezr6i"
invoice content
```

where policy requires.

---

# 131. Content Integrity Through Storage Changes

Storage migration SHALL preserve:

```text id="ysftr8"
artifact digest

artifact identity

version relationship

provenance
```

so that integrity can still be demonstrated.

---

# 132. Mime Type Is Not Semantic Type

This remains:

```text id="wuq2bd"
application/pdf
    !=
COMMERCIAL_INVOICE
```

A PDF can represent many semantic document types.

---

# 133. Schema Is Not Document Type Either

A schema describes structure.

Document type describes business/legal semantics.

One semantic document type MAY have several schema mappings.

---

# 134. Template Is Not Document

This remains:

```text id="d27wln"
Commercial Invoice Template
    !=
Commercial Invoice TradeDocument
```

Templates belong to generation configuration/content infrastructure.

---

# 135. Document Bundle

A convenience:

```text id="zk65uv"
DocumentBundle
```

MAY group documents for exchange.

Example:

```text id="e6k61j"
Customs submission bundle
```

A bundle SHALL NOT erase individual document identities.

---

# 136. Bundle vs Dossier

A:

```text id="6rfq5i"
DocumentDossier
```

is a governed set of documents fulfilling a business/regulatory purpose.

A:

```text id="st0xfy"
DocumentBundle
```

is an exchange/packaging construct.

They SHALL remain conceptually distinct.

Detailed dossier architecture belongs to TDOC-0003.

---

# 137. Document Requirement

Trade Docs SHALL eventually associate documents with:

```text id="2v4sp5"
DocumentRequirement
```

without embedding requirement semantics in the TradeDocument itself.

Example:

```text id="8qegnf"
Requirement:
Valid certificate of origin

Document:
COO-2026-12345
```

---

# 138. Document Can Fulfil Multiple Requirements

Where policy permits:

```text id="65ldfv"
TradeDocument A
       │
       ├── fulfils Requirement 1
       └── fulfils Requirement 2
```

SHALL be representable.

---

# 139. Requirement Can Need Multiple Documents

Likewise:

```text id="ssgjg1"
Requirement X
      │
      ├── Document A
      └── Document B
```

may be valid.

---

# 140. Relationship to CustomsDeclaration

A CustomsDeclaration MAY itself be represented as a TradeDocument.

But the operational:

```text id="j1gwf4"
CustomsDeclaration aggregate
```

in TDOC-0004 SHALL remain distinct from its documentary representation.

---

# 141. Declaration Aggregate vs Document

Conceptually:

```text id="1c71bo"
CustomsDeclaration
    workflow / business aggregate
        │
        ▼
TradeDocument
    issued/submitted documentary representation
```

---

# 142. Same Pattern for Commercial Invoice

ERP owns:

```text id="u3pxtb"
Invoice transaction
```

Trade Docs owns:

```text id="jtbs7o"
CommercialInvoice document
```

They are related, not identical.

---

# 143. Same Pattern for POD

TMS owns:

```text id="7seixz"
Delivery fact
```

Trade Docs may own:

```text id="9m4fjc"
ProofOfDelivery document
```

The document evidences the event.

It does not create the physical event.

---

# 144. Same Pattern for Transport Documents

A carrier may issue:

```text id="dqxy4l"
Bill of Lading
```

Trade Docs owns its Baobab documentary identity and lifecycle.

TMS references it in transport execution.

The issuing carrier remains document issuer.

---

# 145. DCSA eBL Adapter

For container shipping, DCSA's Bill of Lading standard SHALL be treated as an interoperability adapter.

DCSA currently standardises machine-processable B/L data and processes, including issuance, amendment/surrender and endorsement-chain interoperability.

It SHALL NOT define Trade Docs' universal core model.

---

# 146. WCO Adapter

WCO Data Model document types and supporting-document semantics SHALL similarly be mapped at the Customs boundary.

WCO Data Model 4.3.0 now supports a broader range of digital supporting-document types and JSON tags for web implementation.

---

# 147. WCO Model Does Not Become Storage Schema

This remains:

```text id="ahbdvx"
WCO Data Model
    !=
Trade Docs persistence schema
```

---

# 148. UNVTD Adapter

Trade Docs SHOULD aim for interoperability with UNVTD schemas and conformance tooling where document types overlap.

UNVTD is explicitly designed for portable, vendor-neutral digitally verifiable trade documents.

---

# 149. Adapter Versioning

Every external document standard mapping SHALL preserve:

```text id="cnnkfg"
standard

major/minor version

mapping version

effective period

conformance status
```

---

# 150. No Universal External Schema

This SHALL be rejected:

```text id="dz5vwj"
all TradeDocuments
must conform to DCSA
```

or:

```text id="e2tzsv"
all TradeDocuments
must conform to WCO
```

or:

```text id="80ac1s"
all TradeDocuments
must be UNVTD credentials
```

Different standards serve different purposes.

---

# 151. Domain Commands

Candidate commands MAY include:

```text id="0oj8hb"
CreateTradeDocument

CreateDocumentVersion

GenerateDocumentVersion

AttachContentArtifact

IssueDocument

SupersedeDocument

VoidDocument

RelateDocuments

AssociateDocumentSubject

RecordExternalIdentifier

RegisterSourceOriginal
```

Detailed APIs remain for later ADRs.

---

# 152. Commands vs Events

This remains:

```text id="9lv9nt"
Command:
IssueDocument

Event:
TradeDocumentIssued
```

A command requests an operation.

An event records a committed fact.

---

# 153. Candidate Document Events

Future canonical `documents.*` events MAY include:

```text id="1kfqed"
documents.trade-document.created

documents.trade-document.issued

documents.trade-document.superseded

documents.trade-document.voided

documents.document-version.created

documents.document-version.issued

documents.document-relationship.created

documents.content-artifact.registered
```

Exact names require Shared governance.

---

# 154. Existing Shared Events

Current Shared defines proposed events corresponding to:

```text id="nyq8tc"
trade document issued

trade document verified

trade document rejected
```

Producer authority has not yet been assigned.

---

# 155. Existing Events Shall Be Reconciled

Acceptance of TDOC-0001 and TDOC-0002 SHOULD lead Shared to:

```text id="9xe7j4"
assign Trade Docs producer authority where appropriate

separate lifecycle events from verification events

expand version/content events where cross-engine useful

preserve compatibility where contracts have consumers
```

---

# 156. No Event for Every Internal Change

Not every:

```text id="44wjf2"
field update

rendering

cache update

internal workflow transition
```

needs a platform event.

Only meaningful cross-domain facts SHOULD be registered.

---

# 157. Existing `storage_reference`

The current Shared:

```text id="mqzrii"
storage_reference
```

SHALL become a compatibility projection to:

```text id="99hyak"
current/preferred ContentArtifact.storage_reference
```

during migration.

It SHALL not remain canonical document storage architecture.

---

# 158. Existing `superseded_by`

Current:

```text id="ehvn25"
superseded_by
```

SHALL migrate toward:

```text id="mza1ta"
DocumentRelationship
    SUPERSEDED_BY
```

---

# 159. Existing Status Migration

Current:

```text id="tcc0jh"
DRAFT
ISSUED
VERIFIED
REJECTED
SUPERSEDED
```

SHALL be decomposed approximately into:

```text id="ixs27i"
Lifecycle:
DRAFT
ISSUED
SUPERSEDED

Verification:
VERIFIED
FAILED / REJECTED
```

Final semantics require migration review.

---

# 160. Current Document Type Migration

Existing closed enum values SHALL map into the new DocumentType registry.

No existing canonical semantic value SHALL be silently reinterpreted.

---

# 161. Business Identifier Migration

Any current:

```text id="krd335"
document number
provider document ID
authority ID
```

SHALL become explicit `DocumentIdentifier` / ExternalReference records.

---

# 162. Issuer Migration

Current plain:

```text id="skof0f"
issuing_party_reference
```

SHALL migrate to a structured issuer relation.

Historical unresolved strings MAY remain as provenance until canonical resolution is possible.

---

# 163. Migration Does Not Require Immediate Rewrite

TDOC-0002 defines target architecture.

Existing `trade-document/v1` consumers MAY continue temporarily through compatibility views/adapters.

---

# 164. Consumer-First Shared Migration

Preferred sequence:

```text id="8m8oai"
1. publish new compatible contract

2. update consumers

3. activate Trade Docs producer

4. migrate document creation

5. migrate historical records

6. deprecate old surfaces

7. retire only after replay/retention window
```

---

# 165. Import Existing Historical Documents

Historical documents SHALL be imported preserving:

```text id="oe8e26"
original identifiers

source system

source content

known issue time

known status

checksum where possible

original storage reference

relationship context
```

Unknown metadata SHALL remain:

```text id="d0a5nx"
UNKNOWN
```

rather than invented.

---

# 166. Do Not Fabricate Versions

If historical data contains only one artifact and no revision history:

```text id="ip30bs"
Imported Version 1
```

MAY be created.

Trade Docs SHALL not invent nonexistent past revisions.

---

# 167. Historical Hash

Where original content exists, ingestion SHOULD calculate an integrity digest.

That digest proves integrity from ingestion onward.

It SHALL NOT be represented as proof that the bytes were unchanged before Baobab received them.

---

# 168. Current Version

TradeDocument MAY expose:

```text id="89aifn"
current_version_id
```

as a convenience projection.

Historical consumers SHALL reference explicit version IDs when the exact issued/submitted version matters.

---

# 169. “Latest” Is Contextual

This SHALL be avoided:

```text id="tbmxmc"
getLatestDocument()
```

for regulated decisions where one needs:

```text id="8o00k6"
version submitted to Customs

version effective at date X

version signed by party Y
```

---

# 170. Temporal Querying

Trade Docs SHOULD eventually support:

```text id="xcn3kv"
Document as known at time T

Document version effective at time T

Document version submitted in Case C
```

where regulatory/audit use cases require it.

---

# 171. Transferable Records Require Stronger Semantics

A generic:

```text id="j76i7b"
current_version_id
```

is not sufficient to represent:

```text id="xb87dq"
who controls an eBL

whether the chain of control is valid

whether it has been surrendered
```

These SHALL remain separate domain concerns.

---

# 172. Legal Regime Awareness

A document MAY reference:

```text id="yiqo8n"
governing law

legal regime

jurisdiction

authority scheme
```

where needed.

Trade Docs SHALL NOT infer enforceability solely from technical conformance.

---

# 173. MLETR Is Not Universal Law

UNCITRAL MLETR is a model law; adoption and exact legal effect depend on jurisdiction-specific legislation. UNCITRAL's current status page lists a limited set of jurisdictions with legislation based on or influenced by the model.

Therefore Trade Docs SHALL NOT assume:

```text id="kydxdm"
MLETR-compliant technology
=
legally valid transferable electronic record everywhere
```

---

# 174. Regulations Integration

Baobab Regulations SHOULD determine or inform:

```text id="9iyb9e"
document legally required

document validity requirements

acceptable issuer

signature requirement

required retention

transferability/legal regime

jurisdiction-specific document rules
```

where its regulatory packs cover those questions.

---

# 175. Trade Docs Enforces, Regulations Decides

The pattern remains:

```text id="q3w994"
Regulations
     │
     ▼
Document requirement / policy
     │
     ▼
Trade Docs
     │
     ▼
Document workflow
```

---

# 176. No Regulatory Logic Hidden in Type Registry

DocumentType MAY define structural/default workflow policy.

It SHALL NOT become a substitute regulatory rule engine containing jurisdiction-specific legal requirements.

---

# 177. Authority-Defined Schemas

An external authority may require a precise message schema.

Trade Docs SHALL preserve that requirement in the corresponding adapter.

It SHALL not contaminate the generic TradeDocument domain.

---

# 178. Human-Readable Rendering

Every structured document that must be reviewed by humans SHOULD support a deterministic human-readable rendering where practical.

The rendering SHOULD identify:

```text id="04q6vp"
document type

document identity

version

issuer

issue date

key business data

verification information where appropriate
```

---

# 179. Rendering Determinism

Where legal/audit significance attaches to a rendering, the engine SHOULD retain:

```text id="8qmhbh"
renderer version

template version

structured input digest

rendered artifact digest
```

---

# 180. Visual Layout Is Not Semantic Authority

A changed logo or pagination SHALL not necessarily create a new semantic DocumentVersion.

The distinction depends on whether business/legal meaning changed.

---

# 181. Accessibility

Human renderings SHOULD be generated with accessibility and machine extraction in mind where technically feasible.

Scanned-image-only PDFs SHOULD not be the preferred output for Baobab-generated documents.

---

# 182. Content Validation

Structured content MAY undergo:

```text id="4fa8sg"
schema validation

semantic validation

domain validation

regulatory validation
```

These are separate layers.

---

# 183. Schema Valid Does Not Mean Document Valid

This SHALL remain:

```text id="u94j8j"
JSON Schema valid
    !=
legally valid invoice
```

---

# 184. Document Completeness

A document MAY be syntactically valid yet incomplete for a particular requirement.

Completeness belongs to dossier/requirement evaluation in TDOC-0003.

---

# 185. Document Immutability and Storage

Issued-version immutability SHALL be enforced at the domain level even if underlying object storage technically permits overwrite.

Storage technology is not the authority defining immutability.

---

# 186. Content-Addressed Storage

A future storage implementation MAY use:

```text id="c7wdb0"
content-addressing
```

or immutable object versions.

TDOC-0002 does not require a specific storage technology.

---

# 187. Encryption

Content encryption architecture belongs to TDOC-0009.

Encryption SHALL not change TradeDocument identity.

---

# 188. Key Rotation

Likewise:

```text id="cs2onq"
re-encrypt same artifact
```

SHALL not require a new DocumentVersion if the semantic/document bytes represented to the business remain unchanged.

---

# 189. Search

Search indexes MAY include:

```text id="4xc381"
document number

type

issuer

subject references

dates

extracted fields
```

Search indexes SHALL remain projections.

---

# 190. Search Result Is Not Document Authority

This remains:

```text id="52jesb"
Search index record
    !=
TradeDocument
```

---

# 191. Audit

Material operations SHALL be auditable, including:

```text id="9qfyd9"
TradeDocument created

Version created

content attached

issuer changed during draft

document issued

document voided

document superseded

relationship created

external identifier added

content regenerated

signature attached

control transferred

document imported
```

---

# 192. Audit Is Append-Oriented

Historical audit records SHALL not be rewritten to match current state.

---

# 193. Multi-Tenancy

TradeDocument, versions, content artifacts and relationships SHALL remain tenant-scoped according to platform context.

Cross-tenant document sharing SHALL require explicit governed semantics.

---

# 194. Cross-Tenant Exchange

A document issued by Tenant A and received by Tenant B SHALL NOT automatically become:

```text id="ul3ecx"
two unrelated canonical TradeDocuments
```

nor SHALL one tenant automatically gain write authority over the other's canonical record.

The exchange model requires a later architecture decision.

---

# 195. External Portable Document

For portable digitally verifiable documents, a recipient MAY ingest the externally issued credential as its own governed received-document record while preserving issuer identity and original portable-document identity.

Canonical cross-tenant identity reconciliation SHALL be separately governed.

---

# 196. Security

Access to document content SHALL be least-privilege and may differ from access to document metadata.

Sensitive document classes include:

```text id="dqv74j"
commercial invoices

bank guarantees

letters of credit

insurance

identity evidence

Customs declarations

regulated certificates
```

---

# 197. No Secret Leakage Through Metadata

Even metadata MAY be sensitive.

Examples:

```text id="euvvyf"
document exists

bank name

invoice value

cargo nature

authority case number
```

Security policy SHALL consider metadata exposure.

---

# 198. API Design Implication

Public APIs SHOULD address specific resources:

```text id="xo8tht"
/trade-documents/{id}

/trade-documents/{id}/versions/{versionId}

/document-versions/{id}/contents

/document-relationships
```

rather than expose raw storage URLs as the principal API.

Exact REST/API shape remains a later decision.

---

# 199. Current Shared Contract Compatibility

During migration Trade Docs MAY expose a compatibility projection resembling current:

```text id="yq37jt"
TradeDocument {
  trade_document_id
  tenant_id
  document_type
  status
  issuing_party_reference
  storage_reference
}
```

while internally using the richer canonical model.

---

# 200. Compatibility Status Mapping

Compatibility mapping SHALL be explicit and potentially lossy.

Example:

```text id="mybxdw"
New:
Lifecycle = ISSUED
Verification = VERIFIED

Old projection:
status = VERIFIED
```

Consumers SHALL be migrated away from this ambiguity.

---

# 201. Required Shared Reconciliation

Following this ADR, `baobab-platform/shared` SHOULD eventually revise:

```text id="nk5kck"
trade-document/v1
```

or introduce:

```text id="mwqsjo"
trade-document/v2
```

rather than making breaking semantic changes silently.

---

# 202. Shared v2 Candidate Surfaces

Likely cross-engine surfaces include:

```text id="hjawlx"
TradeDocumentReference

DocumentVersionReference

DocumentType

DocumentIdentifier

DocumentSubjectAssociation

DocumentRelationship

ContentArtifactReference

DocumentLifecycleState

VerificationState
```

Only provider-neutral stable fields SHALL be promoted.

---

# 203. Shared Should Not Export TMS/ERP Internals

Document associations SHALL use:

```text id="3vnr6j"
context

type

canonical reference
```

instead of importing entire source-domain schemas.

---

# 204. Event Migration

Current proposed:

```text id="vwxg6s"
TradeDocumentIssued

TradeDocumentVerified

TradeDocumentRejected
```

events SHOULD be reviewed.

Likely target separation:

```text id="u3u7mg"
documents.trade-document.issued

documents.trade-document.superseded

documents.trade-document.voided

documents.document-verification.completed
```

subject to Shared governance.

---

# 205. Producer Authority

Once Shared contracts are reconciled and Trade Docs implementation is certified:

```text id="dbd8ao"
baobab-trade-docs
```

SHOULD become the principal authorised producer for canonical TradeDocument lifecycle events.

---

# 206. External Issuer Is Not Event Producer

This distinction remains:

```text id="xsf4jj"
External Carrier
    legally issues B/L

Trade Docs
    emits Baobab canonical
    document-ingested / issued-projection event
```

The Baobab event describes Baobab's authoritative documentary state.

---

# 207. Implementation Gates

Implementation SHOULD proceed in controlled stages.

## TDOC-DOM-00 — Legacy Contract Audit

Audit:

```text id="by92hj"
Shared trade-document/v1

Trade ADR-0025

Trade document consumers

current files/storage

current document IDs

current event consumers
```

Classify:

```text id="zb7o8v"
KEEP

MAP

SUPERSEDE

DEPRECATE

MIGRATE
```

---

## TDOC-DOM-01 — TradeDocument Identity

Implement:

```text id="31ah03"
provider-minted canonical document ID

tenant context

document type

issuer

external identifiers
```

---

## TDOC-DOM-02 — Type Registry

Establish extensible:

```text id="5w2apc"
DocumentType

DocumentFamily

lifecycle policy

versioning policy
```

without embedding jurisdictional law.

---

## TDOC-DOM-03 — DocumentVersion

Implement immutable:

```text id="9d6j5u"
DocumentVersion

version sequencing

issue snapshot

supersession lineage
```

---

## TDOC-DOM-04 — Content Model

Implement:

```text id="hvv0sn"
DocumentContentSet

ContentArtifact

artifact role

media type

storage reference

digest
```

---

## TDOC-DOM-05 — Structured Document Spine

Support native:

```text id="uvl1vs"
JSON

JSON Schema

semantic context
```

as a first-class document representation.

---

## TDOC-DOM-06 — Rendering

Support deterministic:

```text id="u4tx6z"
HTML/PDF
```

rendering from structured content.

---

## TDOC-DOM-07 — External Document Ingestion

Support:

```text id="rzxb7f"
PDF

XML

JSON

EDI

image
```

source originals with provenance.

---

## TDOC-DOM-08 — Subject Associations

Replace one-off:

```text id="rml3te"
related_shipment_id
```

style fields with typed domain associations.

---

## TDOC-DOM-09 — Relationship Graph

Implement:

```text id="4mkxl0"
SUPERSEDES

AMENDS

SUPPORTS

EVIDENCES

REFERENCES

DERIVED_FROM

SUBMITTED_WITH
```

with validation.

---

## TDOC-DOM-10 — Multi-Axis Status

Separate:

```text id="1o2lc3"
lifecycle

verification

validity

submission
```

states.

---

## TDOC-DOM-11 — Integrity

Implement artifact digests and immutable issued-version semantics.

---

## TDOC-DOM-12 — Transferability Seam

Introduce:

```text id="ycw3o1"
TransferabilityProfile

TransferControl reference
```

without yet implementing full eBL/control workflows.

---

## TDOC-DOM-13 — UNVTD Reference Slice

Implement one structured document, preferably:

```text id="cdbd03"
Commercial Invoice
```

against a standards-aligned structured representation.

---

## TDOC-DOM-14 — DCSA B/L Reference Slice

Map a DCSA transport document into canonical TradeDocument semantics while preserving provider-native representation.

---

## TDOC-DOM-15 — ERP Integration

Prove:

```text id="4z4w3r"
ERP invoice
      │
      ▼
TradeDocument
Commercial Invoice
```

without duplicating financial authority.

---

## TDOC-DOM-16 — TMS Integration

Prove:

```text id="25b0hc"
TMS delivery event
      │
      ▼
ProofOfDelivery document/evidence reference
```

without making the document the delivery authority.

---

## TDOC-DOM-17 — Shared v2 Proposal

Publish provider-neutral cross-engine document/reference contracts.

---

## TDOC-DOM-18 — Event Reconciliation

Assign `documents.*` producer authority and migrate old proposed lifecycle semantics.

---

## TDOC-DOM-19 — Production Hardening

Verify:

```text id="6rgtr3"
tenant isolation

version immutability

content integrity

concurrent revision

duplicate detection

relationship cycles

provider outage

storage outage

source provenance

external identifier collisions

audit

backup/recovery

migration
```

---

# 208. Rejected Alternatives

## Alternative A — File-Centric Model

```text id="mjtqgu"
File + URL + Type
```

**Rejected.**

It cannot express identity, versions, legal lifecycle, provenance or relationships.

---

## Alternative B — One Document Row Per File

**Rejected.**

One document version may have several representations.

---

## Alternative C — One Mutable Document Record

**Rejected.**

Issued/submitted history must remain reproducible.

---

## Alternative D — Version Equals PDF Revision

**Rejected.**

Document versions represent semantic state, not merely rendering revisions.

---

## Alternative E — Every Correction Is a Version

**Rejected.**

Some legal documents require a new instrument.

---

## Alternative F — Every Correction Is a New Document

**Rejected.**

Some document types explicitly support revisions/amendments.

---

## Alternative G — Verification Inside Lifecycle Status

**Rejected.**

A document can simultaneously be:

```text id="0t07xw"
ISSUED
+
UNVERIFIED
```

or:

```text id="jd1qpg"
ISSUED
+
VERIFIED
```

---

## Alternative H — Closed Document-Type Enum

**Rejected.**

The international trade-document universe is too broad and evolves.

---

## Alternative I — CP Mints Every Document ID Synchronously

**Rejected.**

It unnecessarily couples domain transaction availability to Control Plane availability.

---

## Alternative J — Provider Document Number as Canonical ID

**Rejected.**

External identifiers can change, collide or have issuer-specific scope.

---

## Alternative K — PDF as Canonical Content

**Rejected as universal architecture.**

Structured-native documents should be supported.

---

## Alternative L — Structured-Only Documents

**Rejected.**

Existing authorities and counterparties still rely on legacy representations.

---

## Alternative M — DCSA as Universal Document Model

**Rejected.**

It primarily addresses container-shipping documents.

---

## Alternative N — WCO Data Model as Universal Document Model

**Rejected.**

It addresses Customs and border-regulatory interoperability.

---

## Alternative O — UNVTD as Mandatory Internal Model

**Rejected.**

It is highly relevant for interoperability but SHALL remain an external/open standard mapping rather than the only possible internal representation.

---

## Alternative P — Control Transfer as Document Versioning

**Rejected.**

Transferable-record control changes and content changes are different dimensions.

---

# 209. Architectural Invariants

The following SHALL remain non-negotiable:

```text id="dzlqp9"
TradeDocument
    != File

TradeDocument
    != DocumentVersion

DocumentVersion
    != ContentArtifact

ContentArtifact
    != Storage Location

Document Type
    != MIME Type

Document Type
    != Filename

Document ID
    != Document Number

Canonical ID
    != External Authority ID

TradeDocument domain ID
    != Control Plane CanonicalEntity ID automatically

Version Sequence
    != External Revision Number

Issued Version
    must not be silently mutated

Renderer Change
    != Semantic Version Change automatically

Storage Migration
    != Document Version Change

Verification
    != Lifecycle

Validity
    != Verification

Signature Validity
    != Issuer Trust

Issuer Trust
    != Document Sufficiency

Document
    != Evidence

Evidence
    != Evidence Assessment

Document Requirement
    != Document

Source Business Record
    != TradeDocument

ERP Invoice
    != Commercial Invoice TradeDocument

TMS Delivery
    != POD TradeDocument

CustomsDeclaration aggregate
    != declaration document representation

Supporting Document
    retains independent identity

Document Relationship
    != Content Attachment

Supersession
    != Deletion

Relationship Graph
    must preserve direction

Supersession Graph
    must not contain cycles

Transfer Control
    != IAM Permission

Transfer Control
    != Document Version

Electronic PDF
    != Electronic Transferable Record automatically

Cryptographic Signature
    != Legal Enforceability automatically

External Standard Schema
    != Baobab persistence schema

Structured Representation
    must preserve schema/version provenance

Derived Representation
    must preserve source provenance

Historical issued content
    must remain reconstructable
```

---

# 210. Canonical Domain Diagram

```text id="b2xijx"
                         TRADE DOCUMENT
                     stable semantic identity
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
          Identifiers       Subjects       Relationships
              │               │                │
              │               │          ┌─────┴─────────┐
              │               │          ▼               ▼
              │               │      SUPPORTS       SUPERSEDES
              │               │
              └───────────────┼──────────────────────┐
                              ▼                      │
                       DOCUMENT VERSION              │
                    immutable semantic state         │
                              │                      │
                  ┌───────────┼────────────┐         │
                  ▼           ▼            ▼         │
              Source      Semantic      Integrity    │
             Snapshot      Payload        Data       │
                              │                      │
                              ▼                      │
                       CONTENT SET                   │
                 ┌────────────┼─────────────┐        │
                 ▼            ▼             ▼        │
           Structured      Human         Source      │
             JSON          PDF           Original    │
                 │            │             │        │
                 └────────────┼─────────────┘        │
                              ▼                      │
                      CONTENT ARTIFACTS              │
                      hash + storage ref             │
                                                     │
                Transferable documents only          │
                              │                      │
                              ▼                      │
                       CONTROL STATE                 │
                              │                      │
                  ┌───────────┼────────────┐         │
                  ▼           ▼            ▼         │
              Controller   Endorsement   Surrender   │
                                                     │
                              └───────────────────────┘
```

---

# 211. Final Decision

Baobab Trade Docs SHALL establish `TradeDocument` as the stable canonical documentary identity and SHALL model all material document history through explicit immutable versions, content artifacts and relationships.

The canonical hierarchy SHALL be:

```text id="v7l8yj"
TradeDocument
      │
      ▼
DocumentVersion
      │
      ▼
DocumentContentSet
      │
      ├── Structured Content
      ├── Source Original
      ├── Human Rendering
      ├── Authority-Native Representation
      └── Signed / Verifiable Representation
```

with independent relationships:

```text id="rpvtas"
TradeDocument
      │
      ├── subject associations
      ├── business identifiers
      ├── external references
      ├── document relationships
      ├── evidence relationships
      └── transfer-control state where applicable
```

The defining identity principle is:

> **A document's canonical identity shall not depend on its filename, storage URI, PDF, business document number, provider identifier or current version.**

The defining version principle is:

> **Every materially committed document state shall remain historically reconstructable; issued, submitted or signed versions shall never be silently overwritten.**

The defining content principle is:

> **One document version may have several machine- and human-readable representations, all tied to the same semantic version through explicit integrity and provenance metadata.**

The defining relationship principle is:

> **Documents shall form an explicit typed graph rather than an expanding collection of ad-hoc foreign-key fields and file attachments.**

The defining authority principle is:

> **Trade Docs owns document identity, lifecycle, versions, content associations and documentary provenance; the authoritative business system or external institution continues to own the underlying business or legal fact represented by the document.**

The defining digital-trade principle is:

> **Baobab shall favour structured, interoperable and verifiable trade documents while remaining capable of governing legacy PDFs, scans, EDI and authority-native formats without confusing digitisation with legal validity.**

And the defining transferable-record principle is:

> **Where a document is legally transferable, Trade Docs shall model identity, integrity and control separately from ordinary versioning; transfer of control is a legal-operational history, not merely another document edit.**