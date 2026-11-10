"""HYB-03 bounded PostgreSQL scaffold; draft and unverified records only."""
from django.db import migrations, models
import django.db.models.deletion


FORWARD_SQL = r"""
ALTER TABLE documentary_tradedocument
    ADD CONSTRAINT tdoc_opaque_id_chk CHECK (id ~ '^tdoc_[a-z0-9]+$' AND length(id) BETWEEN 8 AND 63),
    ADD CONSTRAINT tdoc_tenant_id_chk CHECK (tenant_id ~ '^tn_[a-z0-9]+$' AND length(tenant_id) BETWEEN 6 AND 63),
    ADD CONSTRAINT tdoc_type_chk CHECK (document_type ~ '^[A-Z][A-Z0-9_]{1,63}$'),
    ADD CONSTRAINT tdoc_draft_only_chk CHECK (lifecycle_state = 'DRAFT'),
    ADD CONSTRAINT tdoc_revision_chk CHECK (aggregate_version >= 1);

ALTER TABLE documentary_documentversion
    ADD CONSTRAINT tdoc_version_id_chk CHECK (id ~ '^tdocv_[a-z0-9]+$' AND length(id) BETWEEN 9 AND 63),
    ADD CONSTRAINT tdoc_version_seq_chk CHECK (version_sequence >= 1),
    ADD CONSTRAINT tdoc_version_draft_only_chk CHECK (lifecycle_snapshot = 'DRAFT'),
    ADD CONSTRAINT tdoc_version_not_self_chk CHECK (supersedes_version_id IS DISTINCT FROM id);

ALTER TABLE documentary_contentartifact
    ADD CONSTRAINT tdoc_artifact_id_chk CHECK (id ~ '^tdoca_[a-z0-9]+$' AND length(id) BETWEEN 9 AND 63),
    ADD CONSTRAINT tdoc_artifact_hash_chk CHECK (digest_algorithm = 'SHA-256' AND digest_value ~ '^[a-f0-9]{64}$'),
    ADD CONSTRAINT tdoc_artifact_unverified_chk CHECK (custody_state = 'UNVERIFIED');

ALTER TABLE documentary_documentrelationship
    ADD CONSTRAINT tdoc_relationship_id_chk CHECK (id ~ '^tdocr_[a-z0-9]+$' AND length(id) BETWEEN 9 AND 63),
    ADD CONSTRAINT tdoc_relationship_not_self_chk CHECK (source_document_id <> target_document_id);

CREATE FUNCTION tdoc_reject_immutable_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'TDOC_IMMUTABLE_ROW: %', TG_TABLE_NAME USING ERRCODE = '23514';
END;
$$;

CREATE TRIGGER tdoc_version_immutable
BEFORE UPDATE OR DELETE ON documentary_documentversion
FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE TRIGGER tdoc_artifact_immutable
BEFORE UPDATE OR DELETE ON documentary_contentartifact
FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE TRIGGER tdoc_relationship_immutable
BEFORE UPDATE OR DELETE ON documentary_documentrelationship
FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE FUNCTION tdoc_fence_document_tenant() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
        RAISE EXCEPTION 'TDOC_TENANT_REBIND_DENIED' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tdoc_document_tenant_fence
BEFORE UPDATE ON documentary_tradedocument
FOR EACH ROW EXECUTE FUNCTION tdoc_fence_document_tenant();

CREATE FUNCTION tdoc_enforce_version_lineage() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.supersedes_version_id IS NOT NULL AND
        NOT EXISTS (
            SELECT 1 FROM documentary_documentversion prior
            WHERE prior.id = NEW.supersedes_version_id
              AND prior.trade_document_id = NEW.trade_document_id
              AND prior.version_sequence < NEW.version_sequence
        )
    THEN
        RAISE EXCEPTION 'TDOC_VERSION_LINEAGE_DENIED' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tdoc_version_lineage_fence
BEFORE INSERT ON documentary_documentversion
FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_version_lineage();

CREATE FUNCTION tdoc_fence_relationship_tenant() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    source_tenant text;
    target_tenant text;
BEGIN
    SELECT tenant_id INTO source_tenant FROM documentary_tradedocument
      WHERE id = NEW.source_document_id FOR SHARE;
    SELECT tenant_id INTO target_tenant FROM documentary_tradedocument
      WHERE id = NEW.target_document_id FOR SHARE;
    IF source_tenant IS NULL OR target_tenant IS NULL OR source_tenant <> target_tenant THEN
        RAISE EXCEPTION 'TDOC_CROSS_TENANT_RELATIONSHIP_DENIED' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tdoc_relationship_scope_fence
BEFORE INSERT ON documentary_documentrelationship
FOR EACH ROW EXECUTE FUNCTION tdoc_fence_relationship_tenant();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS tdoc_relationship_scope_fence ON documentary_documentrelationship;
DROP TRIGGER IF EXISTS tdoc_version_lineage_fence ON documentary_documentversion;
DROP TRIGGER IF EXISTS tdoc_document_tenant_fence ON documentary_tradedocument;
DROP TRIGGER IF EXISTS tdoc_relationship_immutable ON documentary_documentrelationship;
DROP TRIGGER IF EXISTS tdoc_artifact_immutable ON documentary_contentartifact;
DROP TRIGGER IF EXISTS tdoc_version_immutable ON documentary_documentversion;
DROP FUNCTION IF EXISTS tdoc_fence_relationship_tenant();
DROP FUNCTION IF EXISTS tdoc_enforce_version_lineage();
DROP FUNCTION IF EXISTS tdoc_fence_document_tenant();
DROP FUNCTION IF EXISTS tdoc_reject_immutable_change();
ALTER TABLE documentary_documentrelationship DROP CONSTRAINT IF EXISTS tdoc_relationship_id_chk;
ALTER TABLE documentary_documentrelationship DROP CONSTRAINT IF EXISTS tdoc_relationship_not_self_chk;
ALTER TABLE documentary_contentartifact DROP CONSTRAINT IF EXISTS tdoc_artifact_id_chk;
ALTER TABLE documentary_contentartifact DROP CONSTRAINT IF EXISTS tdoc_artifact_hash_chk;
ALTER TABLE documentary_contentartifact DROP CONSTRAINT IF EXISTS tdoc_artifact_unverified_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_version_id_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_version_seq_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_version_draft_only_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_version_not_self_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_opaque_id_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_tenant_id_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_type_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_draft_only_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_revision_chk;
"""


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TradeDocument",
            fields=[
                ("id", models.CharField(max_length=63, primary_key=True, serialize=False)),
                ("tenant_id", models.CharField(db_index=True, max_length=63)),
                ("document_type", models.CharField(max_length=64)),
                ("document_family", models.CharField(max_length=32, choices=[(x, x.replace('_', ' ').title()) for x in (
                    "TRADE", "TRANSPORT", "CUSTOMS", "REGULATORY", "PROCUREMENT", "FINANCIAL",
                    "INSURANCE", "QUALITY", "WAREHOUSE", "PAYMENT", "CONTRACT",
                    "IDENTITY_SUPPORTING", "OTHER"
                )])),
                ("lifecycle_state", models.CharField(max_length=16, default="DRAFT", choices=[(x, x.replace('_', ' ').title()) for x in (
                    "DRAFT", "ISSUED", "SUPERSEDED", "VOIDED", "WITHDRAWN", "ARCHIVED"
                )])),
                ("aggregate_version", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"indexes": [models.Index(fields=["tenant_id", "created_at"], name="tdoc_tenant_created_idx")]},
        ),
        migrations.CreateModel(
            name="DocumentVersion",
            fields=[
                ("id", models.CharField(max_length=63, primary_key=True, serialize=False)),
                ("version_sequence", models.PositiveIntegerField()),
                ("lifecycle_snapshot", models.CharField(max_length=16, default="DRAFT", choices=[(x, x.replace('_', ' ').title()) for x in (
                    "DRAFT", "ISSUED", "SUPERSEDED", "VOIDED", "WITHDRAWN", "ARCHIVED"
                )])),
                ("medium_classification", models.CharField(max_length=24, choices=[(x, x.replace('_', ' ').title()) for x in (
                    "NATIVE_DIGITAL", "DIGITISED_PAPER", "PAPER_REFERENCE", "HYBRID"
                )])),
                ("provenance_kind", models.CharField(max_length=24, choices=[(x, x.replace('_', ' ').title()) for x in (
                    "EXTERNAL_INGESTED", "BAOBAB_GENERATED", "MIGRATED", "DERIVED"
                )])),
                ("provenance_recorded_at", models.DateTimeField()),
                ("created_by", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("trade_document", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="versions", to="documentary.tradedocument")),
                ("supersedes_version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="successors", to="documentary.documentversion")),
            ],
        ),
        migrations.CreateModel(
            name="ContentArtifact",
            fields=[
                ("id", models.CharField(max_length=63, primary_key=True, serialize=False)),
                ("artifact_role", models.CharField(max_length=40, choices=[(x, x.replace('_', ' ').title()) for x in (
                    "CANONICAL_STRUCTURED_CONTENT", "SOURCE_ORIGINAL", "HUMAN_RENDERING",
                    "AUTHORITY_NATIVE_MESSAGE", "SIGNED_ENVELOPE", "SCANNED_COPY",
                    "DERIVED_EXTRACTION", "ATTACHMENT_PART", "OTHER"
                )])),
                ("media_type", models.CharField(max_length=255)),
                ("storage_reference", models.TextField()),
                ("digest_algorithm", models.CharField(default="SHA-256", max_length=16)),
                ("digest_value", models.CharField(max_length=64)),
                ("byte_length", models.PositiveBigIntegerField(blank=True, null=True)),
                ("custody_state", models.CharField(default="UNVERIFIED", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("document_version", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="artifacts", to="documentary.documentversion")),
            ],
        ),
        migrations.CreateModel(
            name="DocumentRelationship",
            fields=[
                ("id", models.CharField(max_length=63, primary_key=True, serialize=False)),
                ("relationship_type", models.CharField(max_length=32, choices=[(x, x.replace('_', ' ').title()) for x in (
                    "SUPERSEDES", "SUPERSEDED_BY", "AMENDS", "AMENDED_BY", "CORRECTS",
                    "CORRECTED_BY", "REPLACES", "REPLACED_BY", "CANCELS", "CANCELLED_BY",
                    "SUPPORTS", "SUPPORTED_BY", "EVIDENCES", "EVIDENCED_BY", "REFERENCES",
                    "REFERENCED_BY", "DERIVED_FROM", "SOURCE_FOR", "GENERATED_FROM",
                    "GENERATES", "SUBMITTED_WITH", "RESPONDS_TO", "DUPLICATES"
                )])),
                ("created_by", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("source_document", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="outgoing_relationships", to="documentary.tradedocument")),
                ("target_document", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="incoming_relationships", to="documentary.tradedocument")),
            ],
        ),
        migrations.AddConstraint(
            model_name="documentversion",
            constraint=models.UniqueConstraint(
                fields=["trade_document", "version_sequence"], name="tdoc_document_sequence_unique"
            ),
        ),
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]
