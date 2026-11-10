# TDOC-HYB-03B — Canonical documentary domain and private custody increment

**Governing architecture:** TDOC-TECH-02 (Accepted); compatible TDOC-TECH-01 persistence/adapter guidance; ADR-TDOC-0001/0002/0020; pinned Shared trade-document/v2.  
**Scope:** Development scaffold; no document issuer, producer activation, CP provider, production readiness or protected storage acceptance.  
**Stacking:** PR #25 builds on draft PR #24 (HYB-03A). No changes to Shared contracts or to RTD-10 maturity.

## Implemented domain model

HYB-03A's separate Document, Version, Artifact and Relationship tables remain authoritative.
HYB-03B adds these *persisted* contract fields:

| Shared v2 type | Additional attributes |
|---|---|
| TradeDocument | issuer_claim, business_identifiers, subject_associations, current_version_id |
| DocumentVersion | external_revision_label, semantic/source snapshot refs, signature_references, issued/effective times, change_reason, complete provenance source refs |
| ContentArtifact | syntax, schema/semantic context, language, character encoding, generation/renderer metadata, source artifact |
| DocumentRelationship | source/target pinned versions, reason, provenance |
| Verification/Temporal Validity | **separate append-only observations**, not document lifecycle or Regulations outcomes |

The internal `documentary/wire.py` projects each of the six type families against exact,
SHA-256-verified Shared v2 schemas with offline JSON Schema Draft 2020-12 resolution.
Issuer assertions remain **claims**, not CP-mandate proof. PostgreSQL constraints refuse
cross-document references, cross-tenant relationships, positive verification or temporal
validity without an accepted authority transition; the DRAFT and UNVERIFIED fences from
HYB-03A remain intact.

## Private S3-compatible custody adapter

`documentary/custody.py` uses the pinned boto3 SDK and accepts only the caller's **private
bucket**, explicit KMS key ARN, region and TLS endpoint; runtime credentials must be acquired
through the standard AWS credential chain. No public ACL, unauthenticated URL or browser
direct upload is supported. Object keys use only opaque documentary artifact IDs.

The adapter submits a bounded SHA-256-checked payload with:
- S3 versioning/VersionId required; AWS SDK checksum headers used;
- SSE-KMS, exact expected KMS key; Object Lock **COMPLIANCE** mode and explicit retention;
- exact-VersionId HEAD and streamed GET readback with byte-count and independently
  recomputed SHA-256; a successful PUT or ETag alone is **not** proof;
- no optimistic fallback if the provider omits lock/encryption/retention/version evidence.

**Operators must configure** a dedicated private, versioned, Object-Lock-enabled bucket with
KMS, restricted write/read/list privileges, denial of object-lock bypass, audit and retention.
Provider-specific retention, SSE-KMS compatibility, bucket policies, key rotation,
legal holds and recovery must be proven before a real provider becomes eligible.

## Durable custody and recovery

`CustodyAttempt` persists artifact, tenant, exact digest/length, scoped bucket/key and
retention *before* any object-store call. `CustodyObservation` is append-only; it records
request, version-pinned upload, verified readback, missing object or quarantine. The mutable
attempt state is **not** itself an immutable certificate.

`stage_artifact()` refuses absent/unqualified scanner, cross-tenant artifact, wrong digest,
wrong reference or bad retention before PUT. A lost PUT response produces
`RECHECK_REQUIRED` and no authoritative result; `reconcile_artifact()` never PUTs or
deletes during recovery. It binds an observed VersionId or selects a unique existing
version, fails closed on ambiguity, and independently repeats lock/KMS/retention/content
readback before writing an append-only receipt. Concurrent repair is generation-fenced.
`inspect_orphans()` produces bounded append-only observations only—**never deletion**.

This is **technical custody evidence**, not document issuance, malware-certification proof,
legal original control or electronic transferable-record authority. Object storage and
PostgreSQL cannot share a transaction; the journal explicitly handles their failure gap.

## Verification and gaps

- PostgreSQL integration tests: direct SQL mutation refusal, tenant/version/source fences,
  immutable evidence, draft-only lifecycle, and no unqualified positive projections.
- Storage-contract tests: exact version, SHA-256, KMS, Object Lock, retention, loss recovery,
  ambiguous version quarantine, missing objects, scanner refusal and orphan inventory.
- HYB-01 cold Python 3.14/Rust/PostgreSQL 17 CI unchanged, with migration-drift checks.
- Hash-locked boto3/JSON Schema stack; no unlocked dependency exception.

**Not yet qualified:** live S3/KMS/Object Lock provider tests against approved storage,
qualified malware scanner, restricted DB-role and concurrent crash/restart test harness,
live CP/IAM mandate (HYB-04), native issuance API, audit/outbox and Regulations exchange
(HYB-05), or protected production/staging approval. The internal stage helper must
not be exposed as a public route until those gates exist.

## Suggested connected qualification

1. Create an isolated test bucket with Object Lock enabled at creation, versioning,
   SSE-KMS and least-privilege dedicated credentials; no public access.
2. Install an approved malware scanner adapter; refuse missing scan verdicts.
3. Upload a real controlled test artifact; independently inspect HeadObject/Object Lock
   retention, GET exact version, digest, private access policy, ciphertext protection.
4. Kill the worker before/after PUT, before/after observation commit and during GET;
   replay `reconcile_artifact`, verify zero duplicate issuance/ambiguous version acceptance.
5. Prove orphan inventory and restricted DB-account direct SQL denials.
6. Independently approve storage/data residency and legal retention under applicable
   corridor policies; then qualify HYB-03 before considering HYB-04.

The accepted architectural decision remains unchanged. RTD-10 remains ARCHITECTURE_ONLY.
