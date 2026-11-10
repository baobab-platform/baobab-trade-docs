"""Internal HYB-03 persistence skeleton. NOT a document issuer or public wire API.

Shared trade-document/v2 owns all wire semantics. Rows inserted by development
fixtures are untrusted until IAM/CP issuance and artifact custody are qualified.
"""
from django.db import models


class DocumentFamily(models.TextChoices):
    TRADE = "TRADE"
    TRANSPORT = "TRANSPORT"
    CUSTOMS = "CUSTOMS"
    REGULATORY = "REGULATORY"
    PROCUREMENT = "PROCUREMENT"
    FINANCIAL = "FINANCIAL"
    INSURANCE = "INSURANCE"
    QUALITY = "QUALITY"
    WAREHOUSE = "WAREHOUSE"
    PAYMENT = "PAYMENT"
    CONTRACT = "CONTRACT"
    IDENTITY_SUPPORTING = "IDENTITY_SUPPORTING"
    OTHER = "OTHER"


class Lifecycle(models.TextChoices):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    SUPERSEDED = "SUPERSEDED"
    VOIDED = "VOIDED"
    WITHDRAWN = "WITHDRAWN"
    ARCHIVED = "ARCHIVED"


class Medium(models.TextChoices):
    NATIVE_DIGITAL = "NATIVE_DIGITAL"
    DIGITISED_PAPER = "DIGITISED_PAPER"
    PAPER_REFERENCE = "PAPER_REFERENCE"
    HYBRID = "HYBRID"


class ProvenanceKind(models.TextChoices):
    EXTERNAL_INGESTED = "EXTERNAL_INGESTED"
    BAOBAB_GENERATED = "BAOBAB_GENERATED"
    MIGRATED = "MIGRATED"
    DERIVED = "DERIVED"


class ArtifactRole(models.TextChoices):
    CANONICAL_STRUCTURED_CONTENT = "CANONICAL_STRUCTURED_CONTENT"
    SOURCE_ORIGINAL = "SOURCE_ORIGINAL"
    HUMAN_RENDERING = "HUMAN_RENDERING"
    AUTHORITY_NATIVE_MESSAGE = "AUTHORITY_NATIVE_MESSAGE"
    SIGNED_ENVELOPE = "SIGNED_ENVELOPE"
    SCANNED_COPY = "SCANNED_COPY"
    DERIVED_EXTRACTION = "DERIVED_EXTRACTION"
    ATTACHMENT_PART = "ATTACHMENT_PART"
    OTHER = "OTHER"


class RelationshipType(models.TextChoices):
    SUPERSEDES = "SUPERSEDES"
    SUPERSEDED_BY = "SUPERSEDED_BY"
    AMENDS = "AMENDS"
    AMENDED_BY = "AMENDED_BY"
    CORRECTS = "CORRECTS"
    CORRECTED_BY = "CORRECTED_BY"
    REPLACES = "REPLACES"
    REPLACED_BY = "REPLACED_BY"
    CANCELS = "CANCELS"
    CANCELLED_BY = "CANCELLED_BY"
    SUPPORTS = "SUPPORTS"
    SUPPORTED_BY = "SUPPORTED_BY"
    EVIDENCES = "EVIDENCES"
    EVIDENCED_BY = "EVIDENCED_BY"
    REFERENCES = "REFERENCES"
    REFERENCED_BY = "REFERENCED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    SOURCE_FOR = "SOURCE_FOR"
    GENERATED_FROM = "GENERATED_FROM"
    GENERATES = "GENERATES"
    SUBMITTED_WITH = "SUBMITTED_WITH"
    RESPONDS_TO = "RESPONDS_TO"
    DUPLICATES = "DUPLICATES"


class TradeDocument(models.Model):
    # Trade Docs-minted opaque ID, distinct from CP canonical entity identifiers.
    id = models.CharField(primary_key=True, max_length=63)
    tenant_id = models.CharField(max_length=63, db_index=True)
    document_type = models.CharField(max_length=64)
    document_family = models.CharField(max_length=32, choices=DocumentFamily.choices)
    lifecycle_state = models.CharField(max_length=16, choices=Lifecycle.choices, default=Lifecycle.DRAFT)
    aggregate_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["tenant_id", "created_at"], name="tdoc_tenant_created_idx")]


class DocumentVersion(models.Model):
    id = models.CharField(primary_key=True, max_length=63)
    trade_document = models.ForeignKey(TradeDocument, on_delete=models.PROTECT, related_name="versions")
    version_sequence = models.PositiveIntegerField()
    lifecycle_snapshot = models.CharField(max_length=16, choices=Lifecycle.choices, default=Lifecycle.DRAFT)
    medium_classification = models.CharField(max_length=24, choices=Medium.choices)
    provenance_kind = models.CharField(max_length=24, choices=ProvenanceKind.choices)
    provenance_recorded_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    supersedes_version = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="successors")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trade_document", "version_sequence"],
                name="tdoc_document_sequence_unique",
            ),
        ]


class ContentArtifact(models.Model):
    id = models.CharField(primary_key=True, max_length=63)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT, related_name="artifacts")
    artifact_role = models.CharField(max_length=40, choices=ArtifactRole.choices)
    media_type = models.CharField(max_length=255)
    storage_reference = models.TextField()
    digest_algorithm = models.CharField(max_length=16, default="SHA-256")
    digest_value = models.CharField(max_length=64)
    byte_length = models.PositiveBigIntegerField(null=True, blank=True)
    # Strictly no verified artifact claims until custody adapter is qualified.
    custody_state = models.CharField(max_length=32, default="UNVERIFIED")
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentRelationship(models.Model):
    id = models.CharField(primary_key=True, max_length=63)
    source_document = models.ForeignKey(
        TradeDocument, on_delete=models.PROTECT, related_name="outgoing_relationships"
    )
    target_document = models.ForeignKey(
        TradeDocument, on_delete=models.PROTECT, related_name="incoming_relationships"
    )
    relationship_type = models.CharField(max_length=32, choices=RelationshipType.choices)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
