# ADR-TDOC-0009 — Document Content Storage, Encryption and Integrity Architecture

**Status:** Proposed — architecture decision for review, not runtime implementation/acceptance  
**Date:** 2026-10-08  
**Repository:** `baobab-platform/baobab-trade-docs`  
**Authority:** Accepted ADR-TDOC-0001/0002; Shared ADR-SHARED-019..026 and pinned canonical v2/RTD-05/06/07 contracts  
**Technology:** TDOC-TECH-01 separate Proposed headless/self-hosted Python/Django/PostgreSQL direction; no new mandatory platform stack  

> Source facts, documentary verification, legal authority and runtime capability certification are different. This is an **ARCHITECTURE_ONLY** proposal; no real issuer validation, secure object store, signed legal document or production provider is represented as deployed.


## 1. Decision
Trade Docs owns **semantic document identity and immutable version/content metadata** in its own PostgreSQL 17 database; binary **ContentArtifact** payloads are stored in encrypted private **self-hosted or infrastructure-approved S3-compatible object storage**, subject to TDOC-TECH-01 selection gates. Object storage is a content persistence adapter, not the owner of TradeDocument IDs, versions, issuer identities or lifecycle states.

~~~mermaid
flowchart TD
  C["Authenticated content ingest"] --> S["Validate MIME, limits, malware, quotas"]
  S --> H["Content digest + immutable artifact manifest"]
  H --> O["Private object storage, encrypted and versioned"]
  H --> P["Trade Docs PostgreSQL: DocumentVersion / ContentArtifact"]
  P --> A["Authorised short-lived content delivery"]
  A --> R["Entitled recipient; audited access"]
~~~

## 2. Four-layer separation
DocumentType / TradeDocument / DocumentVersion / DocumentContentSet/ContentArtifact must not collapse into one URL. One immutable DocumentVersion may contain original XML, JSON structured semantics, attached PDF, human-readable rendition and source scan, each with separate artifact IDs, media type, role, digest, byte length, storage pointer, metadata and integrity verification. A content digest does **not** replace document version identity, prove authorship or license cross-tenant deduplication.

## 3. Immutability and concurrency
- Issued DocumentVersion is write-once semantically and historically; revisions create new version records or separate legal instruments per type policy, with supersession graph and explicit temporal provenance.
- Store source digest and artifact encryption/key versions. Encryption rewrap, storage relocation and backend replacement must preserve logical artifact identity, content digest, verification history and audit.
- Content uploads are staged/quarantined until antivirus/format/size/decompression protections pass and database commit associates exact digest/manifest. Orphan cleanup must not delete an artifact under legal hold or active reference.
- Use transactional database issuance and idempotent **artifact finalisation workflow**; database and object storage are not distributed ACID. Recover from partial object written / DB failed, or DB committed / object temporarily unavailable without falsely claiming issued content ready.
- Concurrent issue/upload/version updates use optimistic revisions, stable idempotency digest, tenant scope and checked source of authority.
- Per-tenant dedupe is permitted only under approved privacy/encryption/threat policy. Never publicly reveal existence of another tenant's file through hash or metadata.

## 4. Security controls
Private buckets, encryption at rest and in transit, key rotation, strict KMS/secret manager, malware scanning, MIME magic checking, content-type policy, archive expansion limits, signed access tokens with expiration and purpose, and read audit. Disallow public S3 ACLs, arbitrary URI fetch/SSRF, MIME-only trust and direct customer access to bucket credentials. Driver/receiver signature and protected commercial information require data classification and retention rules.

Authenticated proxy/short-lived URL options must respect provider capabilities and prevent leaked URL reuse. A reference in a dossier or cross-engine object is **not** permission to read content.

## 5. Renditions and large objects
PDF generator is an optional **out-of-process** rendition adapter, not core storage authority. Generated rendition has parent pinned DocumentVersion plus deterministic renderer/template/config version and separate digest; it must not silently replace issuer-native originals. Streaming upload/download with quotas and backpressure, malware check timeouts, retry queues, corruption alarms and object integrity checks prevent memory pressure.

## 6. Retention, residency and disaster recovery
Map document/legal hold, consent, privacy, market, issuer and Customs audit obligations to defensible retention rules. Separate logical document validity expiry from deletion eligibility; purge only with approved policy and verifiable non-legal-hold status. Region and encryption-key residency reviewed per legal entity/market. Backups must restore **database and artifacts coherently**, including key access and digests; test loss of object while metadata remains.

## 7. Independent implementation gates
| Gate | Evidence |
|---|---|
| TDOC-STO-01 | Storage vendor fit-gap, self-host footprint, licence, object-lock/KMS feasibility and ADR-TECH alignment |
| TDOC-STO-02 | Multi-artifact immutable version, content digest and tamper detection tests |
| TDOC-STO-03 | Quarantine/malware/MIME/size/zip-bomb and interrupted upload recovery |
| TDOC-STO-04 | Authorisation, wrong-tenant hash guessing, expired download, encryption/rotation tests |
| TDOC-STO-05 | Database+object-store restore, legal hold and retention/erasure conflict tests |
| TDOC-STO-06 | Measured scaling/security/availability only after live configured storage, no premature readiness |

No storage instance, KMS or legally compliant retention policy is provisioned by this document.
## 8. Rejected alternatives and governance

Reject file-as-document or one overloaded status, mutable issued DocumentVersion, direct foreign DB writes, vendor account/ID as canonical TradeDocument, universal regulatory validity inferred from a PDF or digital signature, tenant/market hard-coding, and candidate capabilities/events called active. A conflicting cross-engine change belongs first in Shared. Each numbered gate needs a bounded implementation PR with source/test/evidence references and honest unsupported-operation reporting.
