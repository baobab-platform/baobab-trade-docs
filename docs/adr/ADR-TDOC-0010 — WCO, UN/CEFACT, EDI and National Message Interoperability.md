# ADR-TDOC-0010 — WCO, UN/CEFACT, EDI and National Message Interoperability

**Status:** Proposed — architecture decision for review, not runtime implementation/acceptance  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Authority:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and pinned canonical v2/RTD-05/06/07 contracts  
**Technology:** TDOC-TECH-01 separate Proposed headless/self-hosted Python/Django/PostgreSQL direction; no new mandatory platform stack  

> Source facts, documentary verification, legal authority and runtime capability certification are different. This is an **ARCHITECTURE_ONLY** proposal; no real issuer validation, secure object store, signed legal document or production provider is represented as deployed.


## 1. Decision
Trade Docs maintains **canonical document identity, version, structure, provenance and customs workflow**; external standards are implemented in **versioned anti-corruption adapters**. WCO Data Model, UN/CEFACT semantic components, DCSA transport-document profiles, GS1 vocabulary, national customs specifications and EDI/XML/JSON forms do **not** become the internal TradeDocument object schema.

~~~mermaid
flowchart LR
  A["Baobab canonical TradeDocument v2"] --> P["Typed standards adapter port"]
  P --> W["WCO / national Customs profile"]
  P --> U["UN/CEFACT / UNVTD profile"]
  P --> D["DCSA transport document profile"]
  P --> E["EDIFACT / partner-native message"]
  W --> X["External competent gateway"]
  U --> X
  D --> X
  E --> X
~~~

## 2. Source and mapping registry
| Concept | Policy |
|---|---|
| ExternalMessageProfile | standard/body, standard-version, jurisdiction, procedure, issuer/gateway, namespace/schema digest |
| MappingVersion | canonical-source/destination paths, converters, effective dates, provenance, fixture set |
| CodeListReference | national commodity/country/unit/procedure/document/currency code lists, owner/effective revision |
| NativePayloadReference | immutable raw external payload digest and secured artifact ref where lawful |
| TranslationObservation | conversion timestamp, mapper version, lost/unmapped/ambiguous fields, confidence and validator |
| ConformanceEvidence | exact fixture, national sandbox receipt, supported operation and schema-validation version |

Do not assume equivalent field names convey equivalent law. A cargo package unit, commodity tariff code, importer identifier, valuation basis or guarantee reference may vary by procedure and source; require explicit semantic mapping and policy source.

## 3. Mapping rules
- Every adapter documents which canonical fields it reads/writes, the originating engine of source business truth, allowed data transformations, and whether a field is issuer-asserted, Baobab-generated or external-normalized.
- Unknown required external field blocks submission; unknown optional field remains explicit extension/quarantined metadata with provenance, not dropped silently.
- Round-trip tests must identify **lossy transformations** and preserve source-native identifiers as ExternalReference.
- Format validation is distinct from regulatory applicability and statutory documentary sufficiency (Regulations) and from actual authority acceptance (competent external gateway).
- A DCSA eBL or IATA air waybill may have its own issuance/control rules; Trade Docs does not become transferable-record controller merely by generating standards-aligned JSON.
- Local standards mapper has no power to modify Shared canonical event schema; propose any platform contract evolution through Shared governance.

## 4. National customs profiles
A national-adapter profile must pin customs administration/approved intermediary, procedure, schema release, code-list version, endpoint environment, identity/credential requirements and official source/receipt semantics. Uganda and South Africa are **initial scenarios**, not one uniform national API; other transit countries may require additional profiles. Source specification and date are mandatory for each mapping proof.

## 5. Validation hierarchy
Layered validation: transport payload framing -> syntactic XML/JSON/EDI parse -> source schema and allowed code lists -> canonical semantic/subject consistency -> approved actor/representation -> Regulations eligibility where relevant -> gateway submission -> actual competent authority decision. Passing any previous layer never implies success of a later layer.

## 6. Operational change management
Version compatibility, dual-mapping shadow tests, deprecated national schema dates, adapter emergency disable, correlation IDs and callback mapping support. National code-list drift may require case revalidation; do not rewrite immutable previously submitted declaration payloads.

## 7. Independent implementation gates
| Gate | Objective evidence |
|---|---|
| TDOC-STD-01 | Standards/procedure scope matrix with pinned licences/spec versions and source-of-truth mapping |
| TDOC-STD-02 | UN/CEFACT structured commercial invoice reference fixture with no copied ERP financial authority |
| TDOC-STD-03 | WCO/national synthetic declaration mapping, missing-field and lossy-transform tests |
| TDOC-STD-04 | DCSA transport-document mapping with issuer and eBL-transferability separation |
| TDOC-STD-05 | EDI/native parser security, malformed payload, unknown code-list and schema drift tests |
| TDOC-STD-06 | Authority-specific sandbox/partner conformance and changed-version migration sign-off |

No actual national Customs connectivity, DCSA certification or cross-jurisdiction interoperability guarantee arises from this ADR.
## 8. Rejected alternatives and governance

Reject file-as-document or one overloaded status, mutable issued DocumentVersion, direct foreign DB writes, vendor account/ID as canonical TradeDocument, universal regulatory validity inferred from a PDF or digital signature, tenant/market hard-coding, and candidate capabilities/events called active. A conflicting cross-engine change belongs first in Shared. Each numbered gate needs a bounded implementation PR with source/test/evidence references and honest unsupported-operation reporting.
