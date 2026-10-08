# ADR-TDOC-0019 — Document Extraction, Semantic Normalisation and AI-Assisted Validation

**Status:** Proposed — additional architecture decision, pending formal review; not code or production approval  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Programme note:** ADR-TDOC-0016..0019 are **extensions to the original ADR-TDOC-0001 charter programme**, which previously ended at ADR-TDOC-0015. Numbering/scope remain Proposed.  
**Inherited authority:** Accepted ADR-TDOC-0001/0002, Shared ADR-SHARED-019..026 and TradeDocument v2/RTD-05/06/07/08 governance, CP/IAM and competent external legal/issuer authority  
**Technology:** Headless self-hosting; TDOC-TECH-01 is separate Proposed technology strategy.  

> **Non-claim:** No new canonical Shared key, event, version contract, capability activation, legal authority, self-hosted integration or production readiness results from writing or merging this ADR.


## 1. Rationale and decision
Trade Docs must ingest scanned paper, PDF, XML, EDI, JSON and photos without allowing parsers, OCR, ML or generative AI to transform guesses into **issuer-certified or regulatory truth**. This ADR defines an optional, provider-neutral **DocumentExtractionPort** and **SemanticNormalisationPort**, with human review and deterministic verification rules. Trade Docs remains semantic document/evidence authority; Pulse provides optional intelligence assistance, not issuer or documentary legal authority.

~~~mermaid
flowchart TD
  S["Original PDF/Image/XML/EDI"] --> Q["Quarantine / malware / integrity check"]
  Q --> P["Deterministic parser or OCR/ML adapter"]
  P --> A["Attributed extraction assertions"]
  A --> C["Schema, subject and source consistency checks"]
  C --> R["Authorised human review if needed"]
  R --> V["Versioned documentary facts / evidence observations"]
  V --> G["Regulations legal requirement assessment"]
~~~

## 2. Extraction state and provenance
| Concept | Meaning | Invariant |
|---|---|---|
| ExtractionJob | job_id, tenant, exact ContentArtifact/version, adapter, request digest, status | no implicit issuer authority |
| ExtractionRun | parser/model ID+version, configuration, locale/language, start/end and confidence | reproducible and auditable where possible |
| ExtractedAssertion | source page/region/path, proposed field and value, unit/currency, uncertainty/confidence, transformation | always `BAOBAB_EXTRACTED` |
| SourceAssertion | original structured/issuer assertion and provenance where verified | must not be overwritten by extraction |
| NormalisationObservation | mapped semantic field, dictionary/code-list and mapper version; original remains accessible | `EXTERNAL_NORMALIZED` is not issuer claim |
| HumanReviewDecision | reviewer, source excerpts, corrected value, reason, outcome, provenance and timestamp | review outcome is not competent authority authentication |
| ConsistencyCheck | deterministic rules vs cross-engine pinned facts, rule version, mismatch/gaps | flags discrepancies, does not change ERP/TMS/Trade |
| VerificationObservation | hash, signature/source method, confidence, validity and explicit limitations | verification != legal sufficiency |

## 3. Workflow and trust controls
1. Ingest immutable original ContentArtifact after malware/size/MIME and privacy controls (ADR-0009).
2. Determine authorised type/profile and explicit source (ADR-0016), without pretending OCR can issue a certificate.
3. Extract text/fields into a separate **non-authoritative candidate** with exact artifact reference, model/parser version, coordinate/location and transformation provenance.
4. Validate units, dates, invoice lines, issuer identifiers, codes and referential consistency. Compare to pinned ERP/Trade/TMS/Regulations facts through authorised APIs, without direct foreign database writes.
5. If confidence/consistency below the reviewed threshold, require human review; human may accept that extraction matches visible source, not confer issuer/legal authority.
6. Generate structured documentary assertions with source type retained; create new DocumentVersion only via the document-type's authorised issuance/version policy, not a background autonomous model action.
7. Supply exact documentary fact bundle to Regulations via RTD-06, keeping **BAOBAB_EXTRACTED != ISSUER_ASSERTED**.

## 4. AI and Pulse boundary
Pulse may propose anomalies or extraction enrichment through a narrow authorised adapter using minimal necessary artefacts; it must not become the document issuer, version owner, independent Regulations decision maker or legal verifier. Self-hosted deterministic parsers are baseline candidates; optional OCR/ML models must pass data classification, model licence, isolation, cost, dataset governance and accuracy evaluation before use.

No confidential documents or personal data may be sent to an external LLM/OCR provider without approved data processor terms, residency, purpose, contractual authority and explicit tenant-level permission. Redact secrets and minimise prompts/logs. Model hallucination, prompt injection inside source PDFs/EDI, training-data memorisation and misleading confidence are explicit threat cases.

## 5. Deterministic and nondeterministic outputs
A model may be nondeterministic; never promise byte-identical inference results without tested configuration/seed guarantees. Persist input hash, model/adapter version, prompt/config digest, locale, reviewer changes, result digest and known error rates; keep source artifacts immutable. Hallucinated fields should be marked unsupported, not turned into null-free "complete" invoices. Distinguish extraction confidence from source trust and from Regulations sufficiency.

## 6. Example test journeys
- UG→ZA commercial invoice: original PDF invoice and ERP source amount disagree; show discrepancy with independent reviewer and preserve both.
- Packing list from image: parcel count/weight uncertain; mark LOW_CONFIDENCE, block auto-verified issue.
- Carrier-issued B/L: model extracts vessel and bill number but cannot establish issuer signature or legal control without issuer/registry evidence.
- Customs form: parser observes an apparent release stamp, but CustomsCase remains unreleased pending verified sovereign source.
- Malicious document embeds instructions to exfiltrate tenant records; extraction adapter treats all document text as data and cannot invoke privileged tools.

## 7. Implementation gates
| Gate | Evidence |
|---|---|
| TDOC-EXT-01 | Parser/extractor port, typed attributed assertions and complete provenance schema |
| TDOC-EXT-02 | Deterministic XML/JSON and scanned-PDF reference extraction fixtures with confidence/error benchmarks |
| TDOC-EXT-03 | Wrong-issuer, mismatched ERP values, invalid quantities and human review/override tests |
| TDOC-EXT-04 | Prompt injection, PII isolation, external network egress, licence and model/data governance review |
| TDOC-EXT-05 | RTD-06 evidence bundle source-attribution conformance and verification/lifecycle separation |
| TDOC-EXT-06 | Production deployment only after model monitoring, human control and measured market/document-type accuracy |

No AI model, OCR tool, issuer verification, production extraction accuracy or regulatory compliance is asserted to exist by this ADR.
## 8. Alternatives, traceability and follow-up

Reject direct replacement of immutable issued-version content, universal legal status inferred from a PDF/credential/hash, arbitrary tenant access from knowing a reference, external vendor as canonical Trade Docs authority, reuse of another engine's operational database and bypass of maker/checker or Regulations/Customs. Implement in separate bounded PRs with actual source and test fixtures, explicit capability/contract approval through Shared, and CP/EA-09 certification only after verified implementation. ADR-TDOC-0001/0002 remain Accepted and unchanged by this proposed extension.
