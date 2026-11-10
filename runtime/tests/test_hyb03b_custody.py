"""HYB-03B real PostgreSQL and bounded S3-contract negative tests.

The fake S3 transport exercises S3 SDK request/response semantics, not a live
provider. Protected S3/KMS/Object Lock qualification remains a separate gate.
"""
from __future__ import annotations

import hashlib
import io
from datetime import timedelta
from uuid import uuid4

from django.db import DatabaseError, connection, transaction
from django.test import TestCase, SimpleTestCase
from django.utils import timezone

from documentary.custody import CustodyFailure, PrivateS3Store
from documentary.custody_service import stage_artifact, reconcile_artifact, inspect_orphans
from documentary.models import (
    ArtifactRole, ContentArtifact, CustodyAttempt, CustodyObservation,
    DocumentFamily, DocumentRelationship, DocumentTemporalValidityObservation,
    DocumentVerificationObservation, DocumentVersion, Medium, OrphanObservation,
    ProvenanceKind, RelationshipType, TemporalValidityState, TradeDocument,
    VerificationState,
)
from documentary.wire import (
    DocumentaryWireError, artifact_v2, document_version_v2, relationship_v2,
    trade_document_v2, validity_v2, verification_v2,
)


class FakeNotFound(Exception):
    response = {"Error": {"Code": "NoSuchKey"}}


class FakeS3:
    def __init__(self):
        self.objects = {}
        self.put_calls = 0
        self.fail_after_put = False
        self.put_options = []
        self.lock_mode = "COMPLIANCE"
        self.encryption = "aws:kms"

    def put_object(self, **kw):
        self.put_calls += 1
        self.put_options.append(kw.copy())
        version = "version_" + str(self.put_calls)
        self.objects[(kw["Key"], version)] = {
            "body": kw["Body"], "sha": hashlib.sha256(kw["Body"]).hexdigest(),
            "size": len(kw["Body"]), "key": kw["SSEKMSKeyId"],
            "retention": kw["ObjectLockRetainUntilDate"],
        }
        if self.fail_after_put:
            raise TimeoutError("simulated lost PUT response")
        return {"VersionId": version}

    def head_object(self, **kw):
        v = self.objects.get((kw["Key"], kw["VersionId"]))
        if v is None:
            raise FakeNotFound()
        return {
            "ContentLength": v["size"], "VersionId": kw["VersionId"],
            "ServerSideEncryption": self.encryption,
            "SSEKMSKeyId": v["key"],
            "ObjectLockMode": self.lock_mode,
            "ObjectLockRetainUntilDate": v["retention"],
        }

    def get_object(self, **kw):
        v = self.objects.get((kw["Key"], kw["VersionId"]))
        if v is None:
            raise FakeNotFound()
        return {"Body": io.BytesIO(v["body"])}

    def list_object_versions(self, **kw):
        versions = [
            {"Key": key, "VersionId": version}
            for (key, version) in self.objects
            if key.startswith(kw["Prefix"])
        ]
        return {"Versions": versions, "IsTruncated": len(versions) > kw.get("MaxKeys", 1000)}

    def list_objects_v2(self, **kw):
        keys = list(dict.fromkeys(
            key for key, _ in self.objects if key.startswith(kw["Prefix"])
        ))
        limit = kw["MaxKeys"]
        return {"Contents": [{"Key": key} for key in keys[:limit]],
                "IsTruncated": len(keys) > limit}


class CleanTestScanner:
    def scan(self, data, media_type):
        return "CLEAN"


class BadTestScanner:
    def scan(self, data, media_type):
        return "UNSAFE"


class DomainFixtures:
    def make_doc(self, id="tdoc_abcdef", tenant="tn_alpha", **kwargs):
        return TradeDocument.objects.create(
            id=id, tenant_id=tenant, document_type="COMMERCIAL_INVOICE",
            document_family=DocumentFamily.TRADE, **kwargs,
        )

    def make_version(self, doc, id="tdocv_abcdef", seq=1):
        return DocumentVersion.objects.create(
            id=id, trade_document=doc, version_sequence=seq,
            medium_classification=Medium.NATIVE_DIGITAL,
            provenance_kind=ProvenanceKind.BAOBAB_GENERATED,
            provenance_recorded_at=timezone.now(), created_by="fixture-only",
        )

    def make_artifact(self, doc, version, store, payload=b"%PDF-1.7 fixture data\n", id="tdoca_abcdef"):
        return ContentArtifact.objects.create(
            id=id, document_version=version, artifact_role=ArtifactRole.SOURCE_ORIGINAL,
            media_type="application/pdf", storage_reference=store.storage_reference(id),
            byte_length=len(payload), digest_value=hashlib.sha256(payload).hexdigest(),
        )


class DocumentaryWireTests(DomainFixtures, TestCase):
    def test_full_shared_v2_draft_projections_match_pinned_schemas(self):
        issuer = {"party_reference": "org_issuer", "issuer_role": "SELLER"}
        identifiers = [{"value": "INV-2026-0001", "scheme": "INVOICE_NUMBER"}]
        subjects = [{"subject_context": "trade", "subject_type": "ORDER",
                     "subject_reference": "ord_123", "role": "SOURCE"}]
        d1 = self.make_doc(issuer_claim=issuer, business_identifiers=identifiers,
                           subject_associations=subjects)
        v1 = self.make_version(d1)
        a1 = ContentArtifact.objects.create(
            id="tdoca_abcdef", document_version=v1,
            artifact_role=ArtifactRole.SOURCE_ORIGINAL,
            media_type="application/pdf", storage_reference="urn:private:fixture:abcdef",
            digest_value="a" * 64, byte_length=5,
            syntax="PDF", language="en", schema_reference="urn:example:pdf",
        )
        d1.current_version = v1
        d1.save(update_fields=["current_version", "updated_at"])
        doc_wire = trade_document_v2(d1)
        ver_wire = document_version_v2(v1)
        self.assertEqual(doc_wire["current_version_id"], v1.pk)
        self.assertEqual(doc_wire["issuer_claim"], issuer)
        self.assertEqual(ver_wire["content_artifacts"][0]["artifact_id"], a1.pk)
        self.assertEqual(artifact_v2(a1)["syntax"], "PDF")

        d2 = self.make_doc(id="tdoc_ghijkl", issuer_claim=issuer)
        relation = DocumentRelationship.objects.create(
            id="tdocr_abcdef", source_document=d1, target_document=d2,
            relationship_type=RelationshipType.REFERENCES, source_version=v1,
            created_by="fixture-only",
        )
        self.assertEqual(relationship_v2(relation)["source_version_id"], v1.pk)

        verify = DocumentVerificationObservation.objects.create(
            trade_document=d1, document_version=v1,
            verification_state=VerificationState.UNVERIFIED, observed_at=timezone.now(),
        )
        valid = DocumentTemporalValidityObservation.objects.create(
            trade_document=d1, document_version=v1,
            temporal_validity_state=TemporalValidityState.UNKNOWN, observed_at=timezone.now(),
        )
        self.assertEqual(verification_v2(verify)["verification_state"], "UNVERIFIED")
        self.assertEqual(validity_v2(valid)["temporal_validity_state"], "UNKNOWN")

    def test_missing_or_forged_claim_cannot_be_projected(self):
        doc = self.make_doc()
        with self.assertRaises(DocumentaryWireError):
            trade_document_v2(doc)
        doc.issuer_claim = {"party_reference": "org_a", "issuer_role": "not-legal"}
        with self.assertRaises(DocumentaryWireError):
            trade_document_v2(doc)

    def test_foreign_current_version_and_positive_unqualified_observations_denied_in_sql(self):
        first = self.make_doc()
        second = self.make_doc(id="tdoc_ghijkl")
        other_version = self.make_version(second)
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as c:
                    c.execute("UPDATE documentary_tradedocument SET current_version_id=%s WHERE id=%s",
                              [other_version.pk, first.pk])
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                DocumentVerificationObservation.objects.create(
                    trade_document=first, document_version=other_version,
                    verification_state=VerificationState.UNKNOWN, observed_at=timezone.now())
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                DocumentVerificationObservation.objects.create(
                    trade_document=second, document_version=other_version,
                    verification_state=VerificationState.VERIFIED, observed_at=timezone.now())
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                DocumentTemporalValidityObservation.objects.create(
                    trade_document=second, document_version=other_version,
                    temporal_validity_state=TemporalValidityState.CURRENTLY_VALID,
                    observed_at=timezone.now())

    def test_observations_append_only_and_cross_version_link_fenced(self):
        first = self.make_doc()
        first_version = self.make_version(first)
        second = self.make_doc(id="tdoc_ghijkl")
        second_version = self.make_version(second, id="tdocv_ghijkl")
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                DocumentRelationship.objects.create(
                    id="tdocr_abcdef", source_document=first, target_document=first,
                    source_version=second_version, relationship_type=RelationshipType.REFERENCES,
                    created_by="fixture-only")
        obs = DocumentVerificationObservation.objects.create(
            trade_document=first, document_version=first_version,
            verification_state=VerificationState.UNVERIFIED, observed_at=timezone.now())
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as c:
                    c.execute("DELETE FROM documentary_documentverificationobservation WHERE id=%s", [obs.pk])


class CustodyServiceTests(DomainFixtures, TestCase):
    def setUp(self):
        self.client = FakeS3()
        self.store = PrivateS3Store(self.client, bucket="tdoc-private-test", kms_key_id="arn:aws:kms:example:key/fixture")
        self.doc = self.make_doc()
        self.version = self.make_version(self.doc)
        self.raw = b"%PDF-1.7 fixture data\n"
        self.artifact = self.make_artifact(self.doc, self.version, self.store, self.raw)
        self.until = timezone.now() + timedelta(days=30)

    def stage(self, **kwargs):
        return stage_artifact(
            artifact_id=self.artifact.pk, tenant_id="tn_alpha",
            payload=self.raw, store=self.store, scanner=CleanTestScanner(),
            retain_until=self.until, **kwargs,
        )

    def test_private_versioned_lock_and_digest_attestation(self):
        attempt = self.stage()
        self.assertEqual(attempt.state, CustodyAttempt.State.VERIFIED)
        self.assertEqual(self.artifact.custody_state, "UNVERIFIED")
        receipt = attempt.observations.get(kind=CustodyObservation.Kind.READBACK_VERIFIED)
        self.assertEqual(receipt.observed_sha256, hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(receipt.observed_length, len(self.raw))
        self.assertEqual(receipt.retention_mode, "COMPLIANCE")
        opts = self.client.put_options[0]
        self.assertEqual(opts["ServerSideEncryption"], "aws:kms")
        self.assertEqual(opts["ObjectLockMode"], "COMPLIANCE")
        self.assertNotIn("ACL", opts)
        self.assertEqual(opts["Bucket"], "tdoc-private-test")
        self.assertTrue(opts["Key"].startswith("documentary/staging/"))
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as c:
                    c.execute("UPDATE documentary_custodyobservation SET error_code='forged' WHERE id=%s",
                              [str(receipt.pk)])
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as c:
                    c.execute("UPDATE documentary_custodyattempt SET tenant_id='tn_other' WHERE id=%s",
                              [str(attempt.pk)])

    def test_missing_or_unqualified_scanner_fails_closed(self):
        with self.assertRaisesRegex(CustodyFailure, "SCAN_REFUSED"):
            stage_artifact(
                artifact_id=self.artifact.pk, tenant_id="tn_alpha",
                payload=self.raw, store=self.store, scanner=BadTestScanner(),
                retain_until=self.until)
        self.assertEqual(self.client.put_calls, 0)
        self.assertEqual(CustodyAttempt.objects.get(artifact=self.artifact).state, CustodyAttempt.State.QUARANTINED)

    def test_rejected_cross_tenant_and_checksum_before_upload(self):
        with self.assertRaisesRegex(CustodyFailure, "ARTIFACT_NOT_AVAILABLE"):
            stage_artifact(
                artifact_id=self.artifact.pk, tenant_id="tn_other",
                payload=self.raw, store=self.store, scanner=CleanTestScanner(),
                retain_until=self.until)
        with self.assertRaisesRegex(CustodyFailure, "CONTENT_MANIFEST_MISMATCH"):
            stage_artifact(
                artifact_id=self.artifact.pk, tenant_id="tn_alpha",
                payload=b"incorrect", store=self.store, scanner=CleanTestScanner(),
                retain_until=self.until)
        self.assertEqual(self.client.put_calls, 0)

    def test_direct_sql_cannot_mark_custody_verified_without_receipt(self):
        # Raw SQL must not bypass evidence custody, even with a valid manifest.
        attempt = self._create_only_unobserved_attempt()
        self.assertEqual(CustodyAttempt.objects.get(pk=attempt.pk).state, "PENDING")

    def _create_only_unobserved_attempt(self):
        from documentary.models import CustodyAttempt
        attempt = CustodyAttempt.objects.create(
            artifact=self.artifact, tenant_id="tn_alpha", bucket=self.store.bucket,
            object_key=self.store.object_key(self.artifact.pk),
            expected_digest=self.artifact.digest_value, expected_size=len(self.raw),
            required_retention_until=self.until,
        )
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as c:
                    c.execute(
                        "UPDATE documentary_custodyattempt SET state='VERIFIED' WHERE id=%s",
                        [str(attempt.pk)],
                    )
        return attempt

    def test_lost_upload_result_recovers_only_one_exact_version(self):
        self.client.fail_after_put = True
        with self.assertRaisesRegex(CustodyFailure, "UPLOAD_UNKNOWN"):
            self.stage()
        attempt = CustodyAttempt.objects.get(artifact=self.artifact)
        self.assertEqual(attempt.state, CustodyAttempt.State.RECHECK_REQUIRED)
        self.client.fail_after_put = False
        result = reconcile_artifact(attempt_id=attempt.pk, tenant_id="tn_alpha", store=self.store)
        self.assertEqual(result.state, CustodyAttempt.State.VERIFIED)
        self.assertEqual(self.client.put_calls, 1)
        self.assertEqual(result.observations.filter(kind="READBACK_VERIFIED").count(), 1)

    def test_ambiguous_versions_quarantine_instead_of_picking_latest(self):
        self.client.fail_after_put = True
        with self.assertRaises(CustodyFailure):
            self.stage()
        self.client.fail_after_put = False
        self.store.put(self.artifact.pk, self.raw, self.artifact.media_type, self.until)
        attempt = CustodyAttempt.objects.get(artifact=self.artifact)
        result = reconcile_artifact(attempt_id=attempt.pk, tenant_id="tn_alpha", store=self.store)
        self.assertEqual(result.state, CustodyAttempt.State.QUARANTINED)
        self.assertEqual(result.observations.filter(kind="READBACK_VERIFIED").count(), 0)

    def test_missing_object_never_implies_verified(self):
        self.client.fail_after_put = True
        with self.assertRaises(CustodyFailure):
            self.stage()
        self.client.objects.clear()
        attempt = CustodyAttempt.objects.get(artifact=self.artifact)
        result = reconcile_artifact(attempt_id=attempt.pk, tenant_id="tn_alpha", store=self.store)
        self.assertEqual(result.state, CustodyAttempt.State.MISSING)
        self.assertEqual(result.observations.filter(kind="READBACK_VERIFIED").count(), 0)

    def test_missing_object_lock_blocks_proof(self):
        self.client.lock_mode = "GOVERNANCE"
        with self.assertRaisesRegex(CustodyFailure, "OBJECT_LOCK_UNVERIFIED"):
            self.stage()
        self.assertEqual(CustodyAttempt.objects.get(artifact=self.artifact).state,
                         CustodyAttempt.State.RECHECK_REQUIRED)

    def test_orphan_detection_is_bounded_and_non_destructive(self):
        self.client.put_object(
            Bucket=self.store.bucket, Key="documentary/staging/tdoca_orphan1",
            Body=b"orphan", SSEKMSKeyId=self.store.kms_key_id,
            ObjectLockRetainUntilDate=self.until,
        )
        count, truncated = inspect_orphans(store=self.store)
        self.assertEqual((count, truncated), (1, False))
        self.assertEqual(OrphanObservation.objects.count(), 1)
        self.assertEqual(self.client.put_calls, 1)
        self.assertEqual(len(self.client.objects), 1)
