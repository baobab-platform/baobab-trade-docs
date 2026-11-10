"""PostgreSQL-level HYB-03 negative tests; not issuer conformance or certification."""
import json
from pathlib import Path

from django.db import DatabaseError, connection, transaction
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from documentary.models import (
    ArtifactRole, ContentArtifact, DocumentFamily, DocumentRelationship,
    DocumentVersion, Lifecycle, Medium, ProvenanceKind, RelationshipType,
    TradeDocument,
)


class SharedV2EnumParity(SimpleTestCase):
    """Choices mirror the *pinned* owner schema, not an invented local wire API."""

    def test_closed_shared_enums_are_exact(self):
        root = Path(__file__).resolve().parents[2]
        schema = json.loads(
            (root / "reference/shared_contracts/data/trade-document/v2/domain.schema.json").read_text()
        )
        mapping = {
            "documentFamily": DocumentFamily,
            "documentLifecycleState": Lifecycle,
            "mediumClassification": Medium,
            "artifactRole": ArtifactRole,
            "relationshipType": RelationshipType,
        }
        for key, enum in mapping.items():
            with self.subTest(schema_def=key):
                self.assertEqual(
                    {value for value, _ in enum.choices},
                    set(schema["$defs"][key]["enum"]),
                )
        self.assertEqual(
            {value for value, _ in ProvenanceKind.choices},
            set(schema["$defs"]["provenance"]["properties"]["source_kind"]["enum"]),
        )


class PersistenceGuards(TestCase):
    def make_doc(self, identifier, tenant="tn_alpha"):
        return TradeDocument.objects.create(
            id=identifier, tenant_id=tenant,
            document_type="COMMERCIAL_INVOICE", document_family=DocumentFamily.TRADE,
        )

    def make_version(self, doc, identifier="tdocv_alpha1", seq=1, supersedes=None, lifecycle="DRAFT"):
        return DocumentVersion.objects.create(
            id=identifier, trade_document=doc, version_sequence=seq,
            lifecycle_snapshot=lifecycle, medium_classification=Medium.NATIVE_DIGITAL,
            provenance_kind=ProvenanceKind.BAOBAB_GENERATED,
            provenance_recorded_at=timezone.now(), created_by="test-fixture-only",
            supersedes_version=supersedes,
        )

    def reject_sql(self, statement, params=()):
        # A savepoint is essential after an expected PostgreSQL exception.
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(statement, params)

    def test_opaque_id_and_draft_only_are_enforced_by_database(self):
        self.reject_sql(
            "INSERT INTO documentary_tradedocument "
            "(id, tenant_id, document_type, document_family, lifecycle_state, "
            "aggregate_version, created_at, updated_at) "
            "VALUES ('ce_123', 'tn_alpha', 'COMMERCIAL_INVOICE', 'TRADE', "
            "'DRAFT', 1, now(), now())"
        )
        doc = self.make_doc("tdoc_alpha1")
        self.reject_sql(
            "UPDATE documentary_tradedocument SET lifecycle_state = 'ISSUED' WHERE id = %s",
            [doc.pk],
        )
        self.reject_sql(
            "UPDATE documentary_tradedocument SET tenant_id = 'tn_other' WHERE id = %s",
            [doc.pk],
        )
        self.assertEqual(TradeDocument.objects.get(pk=doc.pk).lifecycle_state, Lifecycle.DRAFT)

    def test_version_is_immutable_even_under_direct_sql(self):
        doc = self.make_doc("tdoc_alpha1")
        version = self.make_version(doc)
        self.reject_sql(
            "UPDATE documentary_documentversion SET created_by = 'forged' WHERE id = %s",
            [version.pk],
        )
        self.reject_sql("DELETE FROM documentary_documentversion WHERE id = %s", [version.pk])
        self.assertEqual(DocumentVersion.objects.get(pk=version.pk).created_by, "test-fixture-only")

    def test_versions_are_unique_and_lineage_is_document_local(self):
        first = self.make_doc("tdoc_alpha1")
        second = self.make_doc("tdoc_alpha2")
        prior = self.make_version(first)
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                self.make_version(first, "tdocv_duplicate", seq=1)
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                self.make_version(second, "tdocv_foreign", seq=2, supersedes=prior)
        allowed = self.make_version(first, "tdocv_alpha2", seq=2, supersedes=prior)
        self.assertEqual(allowed.supersedes_version_id, prior.pk)
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                self.make_version(first, "tdocv_issued", seq=3, lifecycle="ISSUED")

    def test_artifact_manifest_is_unverified_and_append_only(self):
        doc = self.make_doc("tdoc_alpha1")
        version = self.make_version(doc)
        artifact = ContentArtifact.objects.create(
            id="tdoca_alpha1", document_version=version,
            artifact_role=ArtifactRole.SOURCE_ORIGINAL, media_type="application/pdf",
            storage_reference="urn:tdoc:unverified:alpha1",
            digest_value="a" * 64, byte_length=128,
        )
        self.assertEqual(artifact.custody_state, "UNVERIFIED")
        self.reject_sql(
            "UPDATE documentary_contentartifact SET digest_value = %s WHERE id = %s",
            ["b" * 64, artifact.pk],
        )
        self.reject_sql(
            "UPDATE documentary_contentartifact SET custody_state = 'VERIFIED' WHERE id = %s",
            [artifact.pk],
        )
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                ContentArtifact.objects.create(
                    id="tdoca_forged", document_version=version,
                    artifact_role=ArtifactRole.HUMAN_RENDERING,
                    media_type="application/pdf", storage_reference="urn:tdoc:unverified:forged",
                    digest_value="b" * 64, custody_state="VERIFIED",
                )
        self.assertEqual(ContentArtifact.objects.get(pk=artifact.pk).digest_value, "a" * 64)

    def test_relationship_cannot_cross_tenant_or_mutate(self):
        first = self.make_doc("tdoc_alpha1", "tn_alpha")
        second = self.make_doc("tdoc_alpha2", "tn_alpha")
        outsider = self.make_doc("tdoc_omega1", "tn_omega")
        rel = DocumentRelationship.objects.create(
            id="tdocr_alpha1", source_document=first, target_document=second,
            relationship_type=RelationshipType.REFERENCES, created_by="test-fixture-only",
        )
        with self.assertRaises(DatabaseError):
            with transaction.atomic():
                DocumentRelationship.objects.create(
                    id="tdocr_cross1", source_document=first, target_document=outsider,
                    relationship_type=RelationshipType.REFERENCES,
                    created_by="test-fixture-only",
                )
        self.reject_sql(
            "UPDATE documentary_documentrelationship SET target_document_id = %s WHERE id = %s",
            [outsider.pk, rel.pk],
        )
        self.reject_sql(
            "DELETE FROM documentary_documentrelationship WHERE id = %s", [rel.pk]
        )
        self.assertEqual(
            DocumentRelationship.objects.get(pk=rel.pk).target_document_id, second.pk
        )

    def test_no_public_documentary_routes_registered(self):
        from django.urls import get_resolver
        routes = [str(p.pattern) for p in get_resolver().url_patterns]
        self.assertEqual(routes, ["_internal/health"])
