# ADR-TDOC-0001 — Baobab Trade Docs Mission, Authority, Executable Trade Document and Customs Workflow Boundary

**Status:** Accepted — Foundational Engine Charter  
**Date:** 2026-10-03  
**Amended:** 2026-10-05 — RTD-06/RTD-07 under ADR-SHARED-021/022/023; cross-engine exchange made executable and canonical `documents` event stewardship/producer authority assigned to `baobab-trade-docs`  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Engine:** Baobab Trade Docs  
**Engine Role:** Headless Executable Trade Document, Customs Workflow and Regulatory Evidence Capability Provider  
**Platform Contract Authority:** `baobab-platform/shared`  
**Capability Resolution Authority:** `baobab-platform/baobab-cp`  
**Regulatory Decision Authority:** `baobab-platform/baobab-regulations`  
**Transport Execution Authority:** `baobab-platform/baobab-tms`  
**Financial Authority:** `baobab-platform/baobab-erp`  
**Identity Authority:** `baobab-platform/baobab-iam`  
**External Legal Authority:** Competent customs/regulatory/document-issuing authorities  
**Initial Strategic Consumers:** Thamani, ZuriBeans and future cross-border Baobab tenants  
**Decision Class:** Engine mission / trade documents / customs workflow / declarations / document evidence / authority adapters / system-of-record boundary

---

# RTD-06 Normative Amendment — Regulatory Requirement and Documentary Evidence Exchange

ADR-SHARED-021 and ADR-SHARED-022 now govern the executable cross-engine reference and exchange semantics between Trade Docs and Regulations.

## A. Requirements arrive as pinned Regulations authority

Trade Docs consumes pinned references/projections for:

~~~text
DOCUMENT_REQUIREMENT
PERMIT_REQUIREMENT
EVIDENCE_REQUIREMENT
REGULATORY_DECISION
~~~

Trade Docs SHALL NOT rewrite, reinterpret or locally reproduce those requirements as legal truth.

## B. Trade Docs supplies documentary facts

The canonical cross-engine documentary projection is:

~~~text
DocumentEvidenceFactBundle
~~~

including:

~~~text
IDENTITY_PINNED DocumentVersion reference
document type/family
issuer claim
verification snapshot
temporal-validity snapshot
subject references
documentary assertions
content-artifact references
facts_observed_at
~~~

## C. Assertion origin is preserved

Every cross-engine documentary assertion distinguishes:

~~~text
ISSUER_ASSERTED
BAOBAB_EXTRACTED
BAOBAB_GENERATED
EXTERNAL_NORMALIZED
~~~

An OCR/extracted value SHALL NOT silently become an issuer assertion.

## D. Evidence offered is not evidence accepted

Trade Docs may state:

~~~text
these DocumentVersions were offered
against this Regulations requirement
~~~

It SHALL NOT state:

~~~text
the requirement is satisfied
~~~

Regulations owns requirement-satisfaction evaluation.

## E. Canonical synchronous surfaces

Trade Docs exposes:

~~~text
POST /v1/regulatory-document-evidence/resolve
~~~

for exact pinned DocumentVersion fact resolution.

An authorised workflow requests Regulations assessment through:

~~~text
POST /v1/documentary-evidence/assessments
~~~

The latter is a command and SHALL NOT be disguised as an event.

## F. Planned Trade Docs event

RTD-06 defines:

~~~text
com.baobab-platform.documents.regulatory-evidence.offered.v1
~~~

but does not activate it.

Producer activation remains RTD-07.

## G. Document changes can trigger reassessment

Once activated:

~~~text
document-version.verification-changed.v2
document-version.validity-changed.v2
~~~

may trigger Regulations reassessment where a linked requirement exists.

Those events do not themselves determine regulatory outcome.

## H. Historical replay

A consequential Regulations assessment cites the exact immutable DocumentVersion used.

Trade Docs SHALL NOT replace a historical version reference with the current TradeDocument/version.

## I. Tenant/context consistency

Every tenant-scoped reference returned through RTD-06 must match the tenant established by trusted Control Plane context and authorised caller.

Reference possession alone grants no document access.


# 1. Decision

Baobab Trade Docs SHALL be the Baobab Platform's reusable headless engine for:

```text
executable digital trade documents

trade-document lifecycle

document dossiers

document requirements execution

customs cases

customs declarations

customs submissions

authority responses

transit-document workflows

permit/certificate workflow references

document provenance

regulated-document evidence
```

It SHALL provide document and Customs-workflow capabilities to any entitled Baobab tenant.

It SHALL NOT be Thamani-specific.

---

# 2. Engine Mission

The engine SHALL answer questions such as:

```text
Which trade documents belong to this transaction?

Which document version is current?

Who issued the document?

Which authoritative source supplied its business data?

What evidence supports it?

Which documents are required for this Customs case?

Which are missing?

Which declaration version was prepared?

Which declaration was actually submitted?

Who authorised submission?

Which authority received it?

What acknowledgement was received?

Was the declaration accepted or rejected?

Did the authority request more information?

Was an inspection ordered?

Was a hold issued?

Was a release received?

Which transit documentation and guarantees apply?
```

---

# 3. What Trade Docs Does Not Answer

The engine SHALL NOT independently answer:

```text
Is import legally permitted?

Which HS classification is legally correct?

Which SPS rule applies?

Which transport route should be used?

Where is the truck now?

What is the final customer sell price?

What is the GL posting?

Has a user authenticated?

Did Customs legally make a decision
that no authority response evidences?
```

---

# 4. Standards Basis

The WCO Data Model provides an internationally standardised semantic framework for Customs and other cross-border regulatory data. Version 4.3.0, published in 2026, expanded support for JSON-oriented implementations and digital supporting-document types. Trade Docs SHOULD treat the WCO Data Model as an important adapter/interoperability standard, not as its persistence schema.

UN/CEFACT's Cross-Border Management Reference Data Model is expressly designed to link supply-chain, multimodal transport and regulatory/customs information models, reinforcing the decision to keep Trade Docs interoperable with—not merged into—TMS, Trade or Regulations.

UN/CEFACT also positions its broader reference-data models as interoperable foundations from which specific exchange structures can be built, supporting Baobab's adapter-oriented architecture.

---

# 5. Core Architectural Principle

> **Baobab Trade Docs owns the executable lifecycle of trade and Customs documents; it does not own every business fact contained inside those documents and it never replaces the competent authority that gives a document or Customs decision legal effect.**

---

# 6. Headless Engine

Trade Docs SHALL be headless.

It SHALL expose:

```text
APIs

commands

queries

events

workflow operations

authority adapters
```

without owning a mandatory user-facing Digital Estate.

---

# 7. Capability Provider

Trade Docs is expected to implement capabilities within:

```text
documents
```

and:

```text
customs
```

canonical domains.

Exact capability keys require Shared approval.

Potential capability concepts include:

```text
documents.trade-document.manage

documents.dossier.manage

documents.document.verify

customs.case.manage

customs.declaration.manage

customs.declaration.submit

customs.transit.manage

customs.authority-status.query
```

These names are candidates rather than automatically registered capabilities.

---

# 8. Provider Neutrality

This remains:

```text
documents.trade-document.manage
        │
        ▼
Capability Provider
        │
        ▼
baobab-trade-docs
```

not:

```text
baobab-trade-docs
=
documents capability identity
```

---

# 9. Initial Consumers

Potential consumers include:

```text
Thamani

ZuriBeans

Baobab Trade

Baobab TMS

ERP workflows

future importers/exporters

external freight forwarders

external brokers

other Baobab tenants
```

---

# 10. TradeDocument

Trade Docs SHALL own canonical lifecycle semantics for:

```text
TradeDocument
```

Conceptually:

```text
TradeDocument
├── canonical_document_id
├── document_type
├── issuer
├── subject/context references
├── lifecycle_state
├── issue_time
├── effective_time?
├── expiry_time?
├── version
├── content_references[]
├── signatures[]
├── evidence_references[]
├── external_identifiers[]
├── provenance
└── relationships[]
```

---

# 11. Document Is Not File

This SHALL remain:

```text
TradeDocument
    !=
PDF
```

A document is a semantic object.

Content MAY be represented in:

```text
PDF
XML
JSON
EDI
image
structured credential
other governed format
```

---

# 12. File Storage Boundary

The existing Shared TradeDocument contract states that artifact storage is a hosting estate's decision.

The creation of a dedicated Trade Docs engine makes that assumption incomplete.

This ADR therefore requires a later Trade Docs storage ADR.

The target principle is:

```text
Trade Docs owns document/content lifecycle semantics

Binary/object storage
may be implemented through a pluggable
storage capability/provider
```

Trade Docs SHALL NOT require every consuming Digital Estate to invent its own document-storage architecture.

---

# 13. Content Authority

Trade Docs owning a document does not mean it owns every field contained in it.

Examples:

```text
Commercial Invoice amount
    authoritative source → ERP / commercial domain

Shipment details
    authoritative source → TMS

HS classification
    authoritative source → Regulations

Organisation identity
    authoritative source → Control Plane

Customs authority release
    authoritative source → Customs authority
```

---

# 14. Source Snapshot

When generating or submitting a regulated document, Trade Docs SHALL preserve the values used at that time.

Therefore:

```text
Source master data
       │
       ▼
Document Draft
       │
       ▼
Issued / Submitted Snapshot
```

Later master-data changes SHALL NOT rewrite historical document content.

---

# 15. Document Versioning

Material changes SHALL produce explicit versions.

This SHALL be prohibited:

```text
overwrite old document
and lose submitted version
```

---

# 16. Document Lifecycle

Generic states MAY include:

```text
DRAFT

DATA_REQUIRED

READY_FOR_REVIEW

APPROVED

ISSUED

SUBMITTED

ACKNOWLEDGED

VERIFIED

REJECTED

EXPIRED

REVOKED

SUPERSEDED
```

Not every document uses every state.

---

# 17. Document Type Determines Lifecycle

A:

```text
Packing List
```

and a:

```text
Customs Declaration
```

do not necessarily share identical lifecycle rules.

The engine SHALL support:

```text
common lifecycle primitives
+
document-type-specific workflow
```

---

# 18. Document Dossier

Trade Docs SHALL own:

```text
DocumentDossier
```

for grouping documents required for a regulated or operational purpose.

Conceptually:

```text
DocumentDossier
├── dossier_id
├── subject references
├── requirement references[]
├── document references[]
├── missing requirements[]
├── verification states[]
├── status
└── version
```

---

# 19. Requirement Is Not Document

This remains:

```text
DocumentRequirement
    !=
TradeDocument
```

A regulatory requirement says:

```text
Certificate X required
```

A document instance attempts to satisfy that requirement.

---

# 20. Regulations Boundary

Baobab Regulations SHALL determine regulatory meaning.

Example:

```text
Regulations:
Phytosanitary certificate REQUIRED
```

Trade Docs SHALL execute:

```text
required-document workflow
```

---

# 21. Trade Docs Must Not Interpret Law Independently

This SHALL be prohibited:

```text
if country == X
and product == Y:
    require permit Z
```

inside Trade Docs unless the rule is merely implementing an authoritative Regulations decision or explicit external-authority protocol.

---

# 22. PDP / PEP Boundary

The architecture SHALL follow:

```text
Baobab Regulations
         │
         │ RegulatoryDecision
         ▼
Baobab Trade Docs
         │
         │ document/customs enforcement
         ▼
Workflow
```

---

# 23. CustomsCase

Trade Docs SHALL own the Baobab operational aggregate:

```text
CustomsCase
```

for orchestrating a Customs interaction.

Conceptually:

```text
CustomsCase
├── case_id
├── tenant/legal entity
├── customs territory
├── authority
├── procedure
├── declarant
├── represented party?
├── customs broker?
├── shipment/consignment references[]
├── declaration references[]
├── document dossier
├── regulatory decision references[]
├── authority messages[]
├── status projection
└── external references[]
```

---

# 24. CustomsCase Is Not Shipment

A Shipment may produce:

```text
Export Customs Case

Transit Case

Import Customs Case
```

Therefore:

```text
Shipment
    !=
CustomsCase
```

---

# 25. TMS Boundary

TMS SHALL own physical movement.

Trade Docs SHALL own documentary/Customs workflow.

Conceptually:

```text
TMS
Transport Movement
       │
       │ correlation
       ▼
Trade Docs
Customs Case
```

---

# 26. Border Crossing Is Not Customs Case

This remains:

```text
physical border node
    → TMS

customs procedure
    → Trade Docs
```

---

# 27. Customs Declaration

Trade Docs SHALL own the operational declaration aggregate.

Conceptually:

```text
CustomsDeclaration
├── declaration_id
├── customs_case_id
├── authority
├── procedure
├── declarant
├── declaration_type
├── goods items
├── classifications references
├── origin references
├── value references
├── document references
├── version
├── state
├── submitted snapshot
├── authority reference?
└── provenance
```

---

# 28. Declaration Is Not Regulatory Assessment

This SHALL remain:

```text
CustomsDeclaration
    !=
RegulatoryDecision
```

Trade Docs composes validated regulatory facts into a declaration.

It SHALL not become their semantic owner.

---

# 29. Declaration Is Not Authority Decision

Likewise:

```text
Declaration
    !=
Customs Release
```

---

# 30. Customs Authority Boundary

Competent Customs administrations remain legally authoritative for:

```text
acceptance

rejection

assessment

inspection

hold

release

amendment approval

transit acquittal
```

where applicable.

Baobab SHALL not fabricate those outcomes.

---

# 31. Submission Is Not Acceptance

This SHALL remain:

```text
message transmitted successfully
    !=
declaration accepted
```

---

# 32. Acceptance Is Not Release

Likewise:

```text
declaration accepted
    !=
goods released
```

---

# 33. Release Is Not Delivery

This remains:

```text
customs release
    !=
physical delivery
```

Delivery remains TMS execution.

---

# 34. Authority Message

Trade Docs SHALL preserve authority interactions.

Conceptually:

```text
AuthorityMessage
├── message_id
├── authority
├── adapter
├── external correlation
├── sent_or_received
├── occurred_at
├── received_at
├── raw content reference
├── normalized meaning
├── mapping version
└── checksum/provenance
```

---

# 35. Raw Evidence and Projection

A normalized:

```text
RELEASED
```

state SHALL not replace the original authority response.

Both SHALL be retained according to policy.

---

# 36. Customs Authority Adapters

Trade Docs SHALL support independently versioned authority adapters.

Potential interfaces include:

```text
REST / JSON

SOAP / XML

UN/EDIFACT

national EDI

ASYCUDA

Single Window

secure file exchange

controlled human workflow
```

---

# 37. No Universal Customs API Assumption

The engine SHALL NOT assume every Customs administration exposes:

```text
modern REST API
```

African and global Customs integrations require protocol diversity.

---

# 38. WCO Data Model Adapter

Trade Docs SHOULD implement mappings to relevant WCO Data Model structures where appropriate.

The WCO Data Model exists to standardise the data requirements of Customs and other cross-border regulatory agencies and is actively evolving.

Mappings SHALL be versioned.

---

# 39. UN/CEFACT Adapter

UN/CEFACT cross-border and supply-chain models SHOULD inform:

```text
document semantics

party semantics

goods semantics

transport references

regulatory information exchange
```

without forcing Trade Docs to duplicate the entire UN semantic library internally.

---

# 40. Authority Adapter Is Not Authority

This remains:

```text
SARS Adapter
    !=
SARS

ASYCUDA Adapter
    !=
Customs Authority
```

---

# 41. Transit

Trade Docs SHALL support regulated Customs transit workflows.

Conceptually:

```text
TransitCase
├── procedure/regime
├── departure authority
├── transit authorities
├── destination authority
├── cargo references
├── transport references
├── declarations
├── guarantees
├── seals
├── control events
├── authority messages
└── acquittal
```

---

# 42. Transit Is Not Transport Movement

This remains:

```text
TransitCase
    !=
TMS TransportMovement
```

The first is a Customs/regulatory procedure.

The second is physical execution.

---

# 43. Transit Guarantee

Trade Docs MAY own workflow/reference semantics around:

```text
TransitGuarantee
```

but SHALL NOT become:

```text
bank

insurer

guarantor

Customs authority
```

---

# 44. Financial Boundary

Actual financial liabilities arising from:

```text
duties

taxes

broker charges

guarantee fees

customs fees
```

SHALL be posted/reconciled through ERP.

---

# 45. Expected Duty vs Authority Assessment

The engine SHALL distinguish:

```text
Regulations / calculation expectation

Customs authority assessment

ERP financial posting
```

These are independent facts.

---

# 46. Customs Namespace

Shared currently defines:

```text
customs
```

to include:

```text
declaration
duty/import-tax calculation
clearance
```

This description predates the fuller Regulations/ERP decomposition.

A Shared reconciliation SHALL refine ownership so that:

```text
customs
    execution/workflow facts

regulations
    regulatory meaning and assessment

finance/tax
    financial/accounting consequences
```

remain distinct.

---

# 47. Current Customs Event Stewardship

Shared currently assigns:

```text
customs
```

event-context stewardship to:

```text
baobab-trade
```

based on older Trade ADR-0021.

This charter does NOT silently transfer that stewardship.

A Shared migration ADR/change SHALL explicitly move applicable Customs-workflow event ownership to Trade Docs while preserving any genuine Trade enforcement facts.

---

# 48. Documents Event Stewardship

ADR-SHARED-023 / RTD-07 now assigns:

```text
documents
    status = ACTIVE
    steward = baobab-trade-docs
```

and activates `baobab-trade-docs` as canonical producer for the reconciled
TradeDocument v2 fact family.

This includes TradeDocument, DocumentVersion, ContentArtifact,
DocumentRelationship, documentary verification and documentary
temporal-validity facts.

RTD-07 also activates the RTD-06 document-side fact:

```text
com.baobab-platform.documents.regulatory-evidence.offered.v1
```

Trade Docs remains prohibited from publishing Regulations-owned
requirement-satisfaction or RegulatoryDecision facts.

The assignment is semantic producer authority. It does not claim a Trade Docs
runtime, broker or transactional outbox has already been deployed.

---

# 49. Existing TradeDocument Contract

The existing:

```text
contracts/trade-document/v1
```

SHALL be treated as architectural input.

It currently defines:

```text
TradeDocument metadata

issue

verify

reject
```

events.

It is insufficient as the complete Trade Docs engine contract.

---

# 50. Contract Reconciliation Required

The existing TradeDocument contract SHALL be reviewed for:

```text
document lifecycle expansion

versioning

issuer authority

signatures

content storage

dossiers

requirements

Customs cases

declarations

authority messages

transit

evidence/provenance
```

before production engine implementation.

---

# 51. Trade Docs vs Evidence

Trade Docs SHALL reference the Baobab evidence architecture.

This remains:

```text
TradeDocument
    !=
Evidence
```

A document may constitute or reference evidence.

Evidence has its own provenance and verification semantics.

---

# 52. Document Verification

Document verification MAY establish:

```text
issuer authenticity

signature validity

external authority status

expiry

data consistency
```

depending on document type.

Verification SHALL remain explainable.

---

# 53. Applicant Cannot Self-Verify

A provider/customer MAY:

```text
upload

assert

submit
```

a document.

That SHALL NOT automatically make the document:

```text
VERIFIED
```

---

# 54. Signature

The engine SHALL support pluggable signature semantics for documents requiring:

```text
human signature

organisation signature

workload signature

PKI signature

external authority signature
```

according to document type and jurisdiction.

---

# 55. Signature Does Not Create Legal Authority Automatically

This remains:

```text
cryptographically valid signature
    !=
legally authorised signatory
```

Authorisation must be separately established.

---

# 56. IAM Boundary

IAM SHALL authenticate:

```text
brokers

reviewers

signatories

provider staff

service workloads
```

Trade Docs SHALL enforce domain-specific authority such as:

```text
may prepare declaration

may approve submission

may submit to authority

may amend declaration
```

---

# 57. Machine-to-Machine Credentials

Government-system credentials SHALL use controlled service/workload identity where possible.

They SHALL NOT be:

```text
stored in browser localStorage

embedded in source code

shared across unrelated tenants
```

---

# 58. Credential Scope

Customs/authority credentials SHOULD be scoped by:

```text
legal entity

declarant/broker

authority

jurisdiction

environment

procedure
```

where applicable.

---

# 59. Maker / Checker

Trade Docs SHALL support separation of duties where organisational or regulatory policy requires:

```text
preparer
    !=
submission approver
```

---

# 60. TMS Integration

Trade Docs SHALL consume TMS facts such as:

```text
shipment reference

consignment reference

route

transport means

equipment

carrier

movement
```

where declarations/documents require them.

It SHALL not duplicate TMS execution authority.

---

# 61. Route Change

A TMS route change MAY invalidate or change:

```text
transit documents

jurisdiction requirements

Customs procedures

permit requirements
```

Trade Docs SHALL support reassessment workflows rather than assuming previously generated documents remain valid.

---

# 62. Regulations Integration

Trade Docs SHALL consume Regulations-owned decisions/requirements through
ADR-SHARED-021 pinned references and ADR-SHARED-022 projections.

Relevant semantics include:

```text
classification

DocumentRequirement

PermitRequirement

EvidenceRequirement

origin requirements

SPS requirements

prohibition/conditionality

applicability

RegulatoryDecision
```

Trade Docs SHALL execute documentary workflow from those requirements without
becoming their legal authority.

Trade Docs supplies documentary facts back through
`DocumentEvidenceFactBundle`; Regulations owns the resulting legal
sufficiency assessment.

---

# 63. Stale Regulatory Decision

A document/customs workflow SHALL NOT reuse a regulatory decision if material context changed without proving its continued applicability.

---

# 64. ERP Integration

Trade Docs SHALL consume authoritative commercial/financial facts needed to generate documents.

Examples:

```text
invoice value

currency

seller

buyer

tax values

commercial invoice reference
```

It SHALL not become the accounting authority.

---

# 65. Document Generation

Trade Docs MAY generate:

```text
rendered PDF

structured XML

structured JSON

EDI representation
```

from authoritative source data.

Generation SHALL preserve:

```text
template/schema version

source references

generated time

document version
```

---

# 66. Rendered Document vs Canonical Document

This remains:

```text
PDF rendering
    !=
canonical document object
```

Several renderings/formats may represent one document version.

---

# 67. Customer-Supplied Document

Trade Docs SHALL support documents originating externally.

Example:

```text
customer uploads certificate
```

The engine SHALL preserve:

```text
external origin

uploader

issuer claim

verification state
```

rather than treating it as internally issued.

---

# 68. Authority-Issued Document

Similarly:

```text
Customs release notice
```

SHALL retain the Customs authority as issuer/source.

Baobab merely records it.

---

# 69. Document Relationships

The engine SHOULD support relationships such as:

```text
SUPPORTS

SUPERSEDES

AMENDS

REPLACES

DERIVED_FROM

SUBMITTED_WITH

EVIDENCES

RESPONDS_TO
```

according to later domain ADRs.

---

# 70. Data Discrepancy

When source systems disagree, Trade Docs SHALL NOT silently resolve the conflict.

It SHOULD create:

```text
DATA_DISCREPANCY
```

or an equivalent review workflow.

---

# 71. Validation Layers

The engine SHALL distinguish:

```text
SCHEMA VALID

DOMAIN VALID

DOCUMENT COMPLETE

REGULATORY REQUIREMENTS SATISFIED

SUBMISSION ACCEPTED

AUTHORITY RELEASED
```

These are not synonyms.

---

# 72. Manual Workflow

Where no machine interface exists, Trade Docs MAY support governed human execution.

Conceptually:

```text
Trade Docs Task
       │
       ▼
Authorised Operator
       │
       ▼
External Authority Portal
       │
       ▼
Evidence / Reference Captured
```

---

# 73. Manual Does Not Mean Uncontrolled

Manual tasks SHALL remain:

```text
assigned

authorised

auditable

time-stamped

evidence-backed
```

---

# 74. Browser Automation

RPA/browser automation MAY exist behind an adapter where unavoidable.

It SHALL NOT become the canonical architecture for government integrations.

---

# 75. Idempotency

Submission operations SHALL use:

```text
idempotency

correlation

authority identifiers

reconciliation
```

to reduce duplicate declarations/documents caused by retries.

---

# 76. Unknown Outcome

If authority submission outcome cannot be determined:

```text
UNKNOWN
```

or:

```text
RECONCILIATION_REQUIRED
```

SHALL be used.

The engine SHALL NOT assume success.

---

# 77. Fail Closed

This is prohibited:

```text
authority unavailable
    therefore
CUSTOMS_RELEASED
```

Likewise:

```text
Regulations unavailable
    therefore
document requirement satisfied
```

---

# 78. Persistence

A later ADR SHALL define:

```text
metadata store

document-content storage

immutable/versioned content

large-object handling

encryption

retention

search/indexing
```

This foundational ADR intentionally does not prescribe storage technology.

---

# 79. No Shared Database

Trade Docs SHALL NOT read/write:

```text
TMS database

ERP database

Regulations database

Thamani database
```

directly.

Use governed APIs/events/contracts.

---

# 80. Multi-Tenancy

Every Trade Docs object SHALL carry or resolve correct:

```text
tenant

legal entity

organisation context

jurisdiction

authority context
```

where applicable.

---

# 81. Data Isolation

The engine SHALL isolate:

```text
document metadata

document contents

Customs cases

authority credentials

submission history

search indexes

caches

background jobs
```

between tenants/legal entities as required.

---

# 82. Data Residency

Regulated documents MAY have residency or jurisdictional constraints.

Trade Docs SHALL integrate with Control Plane resolution/isolation policy rather than hard-code one global storage location.

---

# 83. Sensitive Data

Trade documents may contain:

```text
commercial prices

banking information

personal data

cargo details

supplier/customer data

government references

identity numbers

route data
```

Access SHALL follow least privilege.

---

# 84. Audit

Material actions SHALL be auditable:

```text
document created

document generated

document uploaded

document reviewed

document signed

document issued

document superseded

declaration prepared

declaration approved

declaration submitted

authority response received

declaration amended

hold recorded

release recorded

manual override

credential use
```

---

# 85. Historical Reproducibility

The engine SHALL support reconstruction of:

```text
what data was used

which document version existed

which rule/requirement applied

who approved it

what exactly was submitted

which adapter version was used

what the authority replied

what changed later
```

---

# 86. Engine Does Not Own Commerce Documents' Business Truth

For example:

```text
Commercial Invoice
```

may have its financial content generated from ERP.

Trade Docs owns its:

```text
document identity

representation

version

submission/evidence lifecycle
```

not the underlying ledger transaction.

---

# 87. Engine Does Not Own Transport Documents' Physical Truth

A:

```text
Bill of Lading

Air Waybill

Road Consignment Note
```

may evidence transport obligations.

TMS remains physical-execution authority.

Issuing carrier/party remains authoritative for externally issued transport documents.

---

# 88. Executable Document Definition

An **Executable Trade Document** SHALL mean:

> A semantically identified, versioned and provenance-preserving document object capable of participating in automated or human-governed business, Customs and regulatory workflows.

It SHALL NOT mean:

> Any file that Baobab has stored.

---

# 89. Current Repository State

At acceptance:

```text
baobab-trade-docs
```

is a Foundation-0 scaffold.

This ADR defines the target boundary.

It does not claim working document or Customs capabilities already exist.

---

# 90. Foundation Activation

Before substantive application implementation, the repository SHALL:

```text
replace placeholder README

remove template scaffolding after activation

establish ownership

select runtime deliberately

activate .baobab metadata

declare dev environment

activate Foundation CI

establish provider declaration

pin Shared contracts

establish security posture
```

---

# 91. Shared Changes Required

The charter's Shared dependencies now stand as:

```text
TradeDocument contract evolution
    → completed by RTD-04 / ADR-SHARED-020

cross-engine reference contracts
    → completed by RTD-05 / ADR-SHARED-021

Regulations ↔ Trade Docs requirement/evidence exchange
    → completed by RTD-06 / ADR-SHARED-022

documents event producer authority
    → completed by RTD-07 / ADR-SHARED-023

customs event stewardship migration
    → still outstanding

customs capability refinement
    → still outstanding

Trade Docs provider registration
    → still outstanding

Regulations namespace convergence
    → still outstanding
```

---

# 92. Existing Event Migration

RTD-07 resolves the TradeDocument producer ambiguity.

The reconciled v2 family is now:

```text
lifecycle = ACTIVE
producer = baobab-trade-docs
```

The pre-Trade-Docs v1 family remains:

```text
trade-document.issued.v1
trade-document.verified.v1
trade-document.rejected.v1

lifecycle = PROPOSED
producer = none
```

The v1 family SHALL NOT be implemented as the new runtime target because its
verification/rejection semantics predate the lifecycle/version decomposition.

Existing Customs event semantics associated with Trade remain separate and
SHALL be migrated consumer-first only through a dedicated stewardship change.

Historical events SHALL not be rewritten.

---

# 93. Initial ADR Programme

Following this charter, the recommended sequence is:

```text
ADR-TDOC-0002
Canonical TradeDocument, Version,
Content and Relationship Model

ADR-TDOC-0003
Document Dossier, Requirement
and Completeness Architecture

ADR-TDOC-0004
Customs Case, Declaration and
Authority Decision Projection Model

ADR-TDOC-0005
Customs Authority Adapter,
Submission and Response Architecture

ADR-TDOC-0006
Transit, Guarantee, Seal and
Acquittal Architecture

ADR-TDOC-0007
Issuer, Signature, Credential
and Representative Authority

ADR-TDOC-0008
Evidence, Provenance,
Verification and Discrepancy Architecture

ADR-TDOC-0009
Document Content Storage,
Encryption and Integrity Architecture

ADR-TDOC-0010
WCO, UN/CEFACT, EDI and
National Message Interoperability

ADR-TDOC-0011
Tenant, Isolation, Residency
and Retention Architecture

ADR-TDOC-0012
API, Events, Idempotency
and Durable Workflow Architecture

ADR-TDOC-0013
Security, Audit and
Privileged Customs Operations

ADR-TDOC-0014
Observability, Authority Outage,
Reconciliation and DR

ADR-TDOC-0015
Production Readiness,
Capability Certification and Migration
```

---

# 94. Alternatives Rejected

**Keep document/customs execution inside Baobab Trade.**  
Rejected because commerce is only one consumer.

**Put Trade Docs inside TMS.**  
Rejected because transport and document/Customs workflows have independent authorities and lifecycles.

**Put Trade Docs inside Regulations.**  
Rejected because regulatory decision and operational document execution are separate.

**Let Digital Estates own their own trade-document architecture.**  
Rejected because it creates repeated and inconsistent customs/document capabilities.

**Treat files as documents.**  
Rejected because semantic identity, versioning and provenance are required.

**Treat Trade Docs as Customs authority.**  
Rejected because sovereign legal authority remains external.

---

# 95. Architectural Invariants

```text
Trade Docs
    != Digital Estate

Trade Docs
    != TMS

Trade Docs
    != Regulations

Trade Docs
    != ERP

Trade Docs
    != Customs Authority

TradeDocument
    != File

Document Requirement
    != Document

Document
    != Evidence

Evidence
    != Verification

Declaration Draft
    != Declaration Submitted

Submitted
    != Accepted

Accepted
    != Released

Released
    != Delivered

Customs Case
    != Shipment

Transit Case
    != Transport Movement

Customs Procedure
    != Physical Route

HS Classification
    comes from Regulations

Physical movement
    comes from TMS

Financial posting
    comes from ERP

Canonical organisation
    comes from Control Plane

Authentication
    comes from IAM

External authority reference
    != Canonical Baobab ID

Authority adapter
    != Authority

Successful transport
    != Customs compliance automatically

Successful submission
    != Customs acceptance

Regulatory PASS
    != Customs release

Document content
    must preserve provenance

Submitted values
    must remain historically reproducible

Capability identity
    must remain provider-neutral
```

---

# 96. Final Decision

Baobab Trade Docs SHALL become the reusable Baobab authority for **executable trade-document and Customs workflow state**, while preserving the authority of the systems and institutions that provide the underlying business, regulatory and legal facts.

Its conceptual architecture is:

```text
                  SOURCE BUSINESS FACTS
             ┌────────┬────────┬─────────┐
             ▼        ▼        ▼         ▼
            ERP      TMS   Regulations   CP
             │        │        │         │
             └────────┴────────┼─────────┘
                               ▼
                     BAOBAB TRADE DOCS
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
            Documents        Dossiers     Customs Cases
                 │             │             │
                 ├─────────────┼─────────────┤
                               ▼
                         Declarations
                               │
                               ▼
                       Authority Adapter
                               │
                               ▼
                  CUSTOMS / REGULATORY SYSTEM
                               │
                               ▼
                    Authority Responses
                               │
                               ▼
                   Normalised Baobab Facts
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
                 TMS         Thamani       ERP
             enforcement      UX        financial effects
```

The defining documentary principle is:

> **Baobab Trade Docs shall own document identity, lifecycle, version, provenance and executable workflow without usurping the authority of the business system or institution that supplies the document's authoritative facts.**

The defining Customs principle is:

> **Trade Docs may prepare, validate, submit, track and evidence Customs transactions, but only the competent Customs administration may exercise sovereign authority to assess, reject, hold or release goods.**

And the defining platform principle is:

> **Trade-document and Customs capabilities shall be reusable Baobab capabilities, not hidden implementation details of Trade, TMS or any individual Digital Estate.**