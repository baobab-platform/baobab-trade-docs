# TDOC-HYB-03A — Draft-only documentary persistence scaffold

**Decision:** Accepted TDOC-TECH-02, retaining compatible TDOC-TECH-01 persistence guidance and ADR-TDOC-0001/0002/0020. **Status: IMPLEMENTED SOURCE; NOT HYB-03 QUALIFIED.**

## Scope delivered

- A private Django `documentary` app with distinct `TradeDocument`, `DocumentVersion`, `ContentArtifact` manifest and `DocumentRelationship` aggregates.
- PostgreSQL 17 constraints for Shared v2 opaque IDs, tenant ID, type code and monotonically positive revision/sequence.
- SQL-level append-only enforcement for versions, artifacts and relationships, and a tenant-rebinding fence on documents.
- Cross-tenant document relationship rejection, same-document earlier-version lineage checks and uniqueness of version sequence.
- Explicit **draft-only document/version** and **unverified-only artifact** database constraints. These prevent a development fixture from being mistaken for an issued or custody-verified document.
- Negative Django/PostgreSQL tests exercising direct SQL rather than trusting `save()` overrides; enum parity checks with pinned Shared v2.

## Not yet implemented

This is **not** complete HYB-03. There is no CP-verified tenant context, IAM principal or mandate, issuer claimant validation, governed document-type policy, original artifact upload, object-store immutability, cryptographic custody validation, malware scanning, evidence escrow, maker/checker command, audit ledger, transactional outbox, event publisher, external API or Customs adapter. There is no production runtime or activated capability provider.

Shared v2 attributes such as issuer claims, typed subjects, external identifiers, semantic payload, signature references, verification and temporal-validity observations, and current-version projection remain future model iterations. Do **not** serialize these partial ORM classes directly as canonical Shared v2 objects.

A future governed migration must deliberately lift `DRAFT` and `UNVERIFIED` fences only as the corresponding IAM/CP, custody, audit/outbox and issuance acceptance gates become evidenced. There is no migration that does so in this PR.

## Verification

Run in the pinned Python 3.14 / Rust / PostgreSQL 17 environment:

```bash
cd runtime
../.venv/bin/python manage.py check
../.venv/bin/python manage.py makemigrations --check --dry-run
../.venv/bin/python manage.py migrate --noinput
../.venv/bin/python manage.py test tests -v2
```

The existing HYB-01 workflow exercises the migration and tests on actual PostgreSQL 17, x86_64 and aarch64. Passing the scaffold CI does **not** establish real protected custody or business issuance.

## Next steps to qualify HYB-03

1. Complete type-safe Shared v2 mapping (including issuer, subject, provenance and independent verification/validity axes), and integrate qualified Rust validation.
2. Implement private S3-compatible artifact staging/finalisation with malware, digest, encryption, retention, loss and orphan recovery proofs.
3. Implement immutable custody evidence and tenant-isolation tests under restricted **application** DB roles (not merely test-owner privileges); test concurrent creation and recovery.
4. Then take HYB-04 live IAM/CP issuer and capability fencing and HYB-05 atomic audit/outbox through independent connected qualification.

The conformance file remains `ARCHITECTURE_ONLY`, and no provider manifest is activated.
