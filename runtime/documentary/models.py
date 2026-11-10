"""Internal HYB-03 persistence skeleton. NOT a document issuer or public wire API.

Shared trade-document/v2 owns all wire semantics. Rows inserted by development
fixtures are untrusted until IAM/CP issuance and artifact custody are qualified.
"""
import uuid
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
    # Assertions are documentary facts, NOT CP/IAM grants.
    issuer_claim = models.JSONField(null=True, blank=True)
    business_identifiers = models.JSONField(default=list)
    subject_associations = models.JSONField(default=list)
    current_version = models.ForeignKey(
        "DocumentVersion", null=True, blank=True, on_delete=models.PROTECT, related_name="+",
    )
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
    external_revision_label = models.CharField(max_length=128, null=True, blank=True)
    semantic_payload_reference = models.CharField(max_length=512, null=True, blank=True)
    source_snapshot_reference = models.CharField(max_length=512, null=True, blank=True)
    signature_references = models.JSONField(default=list)
    issued_at = models.DateTimeField(null=True, blank=True)
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_to = models.DateTimeField(null=True, blank=True)
    change_reason = models.CharField(max_length=1000, null=True, blank=True)
    provenance_source_reference = models.CharField(max_length=512, null=True, blank=True)
    provenance_supplied_by_reference = models.CharField(max_length=256, null=True, blank=True)
    provenance_source_system = models.CharField(max_length=128, null=True, blank=True)
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
    syntax = models.CharField(max_length=128, null=True, blank=True)
    schema_reference = models.CharField(max_length=512, null=True, blank=True)
    semantic_context_reference = models.CharField(max_length=512, null=True, blank=True)
    language = models.CharField(max_length=35, null=True, blank=True)
    character_encoding = models.CharField(max_length=64, null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.CharField(max_length=256, null=True, blank=True)
    renderer_version = models.CharField(max_length=128, null=True, blank=True)
    source_artifact = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT,
        related_name="derived_artifacts",
    )
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
    source_version = models.ForeignKey(
        DocumentVersion, null=True, blank=True, on_delete=models.PROTECT,
        related_name="outgoing_document_relationships",
    )
    target_version = models.ForeignKey(
        DocumentVersion, null=True, blank=True, on_delete=models.PROTECT,
        related_name="incoming_document_relationships",
    )
    reason = models.CharField(max_length=1000, null=True, blank=True)
    provenance = models.JSONField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)



class VerificationState(models.TextChoices):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class TemporalValidityState(models.TextChoices):
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    CURRENTLY_VALID = "CURRENTLY_VALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class DocumentVerificationObservation(models.Model):
    """Append-only observed documentary status; not Regulations satisfaction."""
    trade_document = models.ForeignKey(TradeDocument, on_delete=models.PROTECT)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT)
    verification_state = models.CharField(max_length=16, choices=VerificationState.choices)
    reason_code = models.CharField(max_length=128, null=True, blank=True)
    verifier_reference = models.CharField(max_length=256, null=True, blank=True)
    observed_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["trade_document", "observed_at"], name="tdoc_verify_observed_idx")]


class DocumentTemporalValidityObservation(models.Model):
    """Independent validity observation; never asserted from an OCR result."""
    trade_document = models.ForeignKey(TradeDocument, on_delete=models.PROTECT)
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT)
    temporal_validity_state = models.CharField(max_length=24, choices=TemporalValidityState.choices)
    authority_reference = models.CharField(max_length=256, null=True, blank=True)
    basis_reference = models.CharField(max_length=512, null=True, blank=True)
    observed_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["trade_document", "observed_at"], name="tdoc_valid_observed_idx")]


class CustodyAttempt(models.Model):
    """Durable, recoverable storage attempt; mutable state is not custody evidence."""
    class State(models.TextChoices):
        PENDING = "PENDING"
        RECHECK_REQUIRED = "RECHECK_REQUIRED"
        VERIFIED = "VERIFIED"
        MISSING = "MISSING"
        QUARANTINED = "QUARANTINED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artifact = models.OneToOneField(ContentArtifact, on_delete=models.PROTECT, related_name="custody_attempt")
    tenant_id = models.CharField(max_length=63)
    bucket = models.CharField(max_length=255)
    object_key = models.CharField(max_length=512, unique=True)
    expected_digest = models.CharField(max_length=64)
    expected_size = models.PositiveBigIntegerField()
    required_retention_until = models.DateTimeField()
    state = models.CharField(max_length=32, choices=State.choices, default=State.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    last_error_code = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["state", "updated_at"], name="tdoc_custody_recovery_idx")]


class CustodyObservation(models.Model):
    """Append-only technical observation; never a legal issuance certificate."""
    class Kind(models.TextChoices):
        STAGE_REQUESTED = "STAGE_REQUESTED"
        UPLOAD_OBSERVED = "UPLOAD_OBSERVED"
        READBACK_VERIFIED = "READBACK_VERIFIED"
        CHECK_FAILED = "CHECK_FAILED"
        OBJECT_MISSING = "OBJECT_MISSING"
        QUARANTINED = "QUARANTINED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(CustodyAttempt, on_delete=models.PROTECT, related_name="observations")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    provider_version_id = models.CharField(max_length=255, null=True, blank=True)
    observed_sha256 = models.CharField(max_length=64, null=True, blank=True)
    observed_length = models.PositiveBigIntegerField(null=True, blank=True)
    encryption_algorithm = models.CharField(max_length=48, null=True, blank=True)
    encryption_key_id = models.CharField(max_length=512, null=True, blank=True)
    retention_mode = models.CharField(max_length=32, null=True, blank=True)
    retain_until = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, null=True, blank=True)
    observed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["attempt", "observed_at"], name="tdoc_custody_evidence_idx")]


class OrphanObservation(models.Model):
    """Non-destructive listing evidence; never authorises object deletion."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bucket = models.CharField(max_length=255)
    object_key = models.CharField(max_length=512)
    provider_version_id = models.CharField(max_length=255, null=True, blank=True)
    observed_at = models.DateTimeField(auto_now_add=True)
