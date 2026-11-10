"""HYB-03B PostgreSQL fences beyond ORM protections; no issuer activation."""
from django.db import migrations


FORWARD = r"""
ALTER TABLE documentary_tradedocument
  ADD CONSTRAINT tdoc_issuer_json_chk CHECK (issuer_claim IS NULL OR jsonb_typeof(issuer_claim) = 'object'),
  ADD CONSTRAINT tdoc_identifiers_json_chk CHECK (jsonb_typeof(business_identifiers) = 'array'),
  ADD CONSTRAINT tdoc_subjects_json_chk CHECK (jsonb_typeof(subject_associations) = 'array');

ALTER TABLE documentary_documentversion
  ADD CONSTRAINT tdoc_signatures_json_chk CHECK (jsonb_typeof(signature_references) = 'array'),
  ADD CONSTRAINT tdoc_version_effective_range_chk CHECK (
    effective_from IS NULL OR effective_to IS NULL OR effective_from <= effective_to
  );

ALTER TABLE documentary_custodyattempt
  ADD CONSTRAINT tdoc_attempt_digest_chk CHECK (expected_digest ~ '^[a-f0-9]{64}$'),
  ADD CONSTRAINT tdoc_attempt_size_chk CHECK (expected_size > 0 AND expected_size <= 16777216),
  ADD CONSTRAINT tdoc_attempt_key_chk CHECK (object_key ~ '^documentary/staging/tdoca_[a-z0-9]+$'),
  ADD CONSTRAINT tdoc_attempt_state_chk CHECK (
    state IN ('PENDING', 'RECHECK_REQUIRED', 'VERIFIED', 'MISSING', 'QUARANTINED')
  );

ALTER TABLE documentary_custodyobservation
  ADD CONSTRAINT tdoc_observation_kind_chk CHECK (
    kind IN ('STAGE_REQUESTED', 'UPLOAD_OBSERVED', 'READBACK_VERIFIED',
             'CHECK_FAILED', 'OBJECT_MISSING', 'QUARANTINED')
  );

ALTER TABLE documentary_documentverificationobservation
  ADD CONSTRAINT tdoc_verification_no_positive_chk CHECK (
    verification_state IN ('UNVERIFIED', 'PENDING', 'FAILED', 'DISPUTED', 'UNKNOWN')
  );

ALTER TABLE documentary_documenttemporalvalidityobservation
  ADD CONSTRAINT tdoc_validity_unknown_only_chk CHECK (temporal_validity_state = 'UNKNOWN');

CREATE TRIGGER tdoc_custody_evidence_append_only
  BEFORE UPDATE OR DELETE ON documentary_custodyobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE TRIGGER tdoc_orphan_evidence_append_only
  BEFORE UPDATE OR DELETE ON documentary_orphanobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE TRIGGER tdoc_verification_append_only
  BEFORE UPDATE OR DELETE ON documentary_documentverificationobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE TRIGGER tdoc_validity_append_only
  BEFORE UPDATE OR DELETE ON documentary_documenttemporalvalidityobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_reject_immutable_change();

CREATE FUNCTION tdoc_enforce_current_version() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.current_version_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM documentary_documentversion v
    WHERE v.id = NEW.current_version_id AND v.trade_document_id = NEW.id
  ) THEN
    RAISE EXCEPTION 'TDOC_CURRENT_VERSION_CROSS_DOCUMENT' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_current_version_scope
  BEFORE INSERT OR UPDATE ON documentary_tradedocument
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_current_version();

CREATE FUNCTION tdoc_enforce_reference_lineage() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.source_version_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM documentary_documentversion
    WHERE id=NEW.source_version_id AND trade_document_id=NEW.source_document_id
  ) THEN
    RAISE EXCEPTION 'TDOC_SOURCE_VERSION_SCOPE' USING ERRCODE = '23514';
  END IF;
  IF NEW.target_version_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM documentary_documentversion
    WHERE id=NEW.target_version_id AND trade_document_id=NEW.target_document_id
  ) THEN
    RAISE EXCEPTION 'TDOC_TARGET_VERSION_SCOPE' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_relationship_version_scope
  BEFORE INSERT ON documentary_documentrelationship
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_reference_lineage();

CREATE FUNCTION tdoc_enforce_artifact_source() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.source_artifact_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM documentary_contentartifact s
    JOIN documentary_documentversion v ON v.id=s.document_version_id
    JOIN documentary_documentversion n ON n.id=NEW.document_version_id
    WHERE s.id=NEW.source_artifact_id
      AND s.id <> NEW.id
      AND v.trade_document_id=n.trade_document_id
  ) THEN
    RAISE EXCEPTION 'TDOC_SOURCE_ARTIFACT_SCOPE' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_artifact_source_scope
  BEFORE INSERT ON documentary_contentartifact
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_artifact_source();

CREATE FUNCTION tdoc_enforce_observation_scope() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM documentary_documentversion v
    WHERE v.id=NEW.document_version_id AND v.trade_document_id=NEW.trade_document_id
  ) THEN
    RAISE EXCEPTION 'TDOC_OBSERVATION_CROSS_DOCUMENT' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_verification_version_scope
  BEFORE INSERT ON documentary_documentverificationobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_observation_scope();
CREATE TRIGGER tdoc_validity_version_scope
  BEFORE INSERT ON documentary_documenttemporalvalidityobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_observation_scope();

CREATE FUNCTION tdoc_enforce_attempt_binding() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  expected_tenant text;
  expected_hash text;
  expected_bytes bigint;
  expected_ref text;
BEGIN
  IF TG_OP='UPDATE' AND (
    NEW.tenant_id IS DISTINCT FROM OLD.tenant_id OR
    NEW.artifact_id IS DISTINCT FROM OLD.artifact_id OR
    NEW.bucket IS DISTINCT FROM OLD.bucket OR
    NEW.object_key IS DISTINCT FROM OLD.object_key OR
    NEW.expected_digest IS DISTINCT FROM OLD.expected_digest OR
    NEW.expected_size IS DISTINCT FROM OLD.expected_size OR
    NEW.required_retention_until IS DISTINCT FROM OLD.required_retention_until
  ) THEN
    RAISE EXCEPTION 'TDOC_ATTEMPT_IMMUTABLE_BINDING' USING ERRCODE = '23514';
  END IF;
  SELECT d.tenant_id, a.digest_value, a.byte_length, a.storage_reference
    INTO expected_tenant, expected_hash, expected_bytes, expected_ref
  FROM documentary_contentartifact a
  JOIN documentary_documentversion v ON a.document_version_id=v.id
  JOIN documentary_tradedocument d ON v.trade_document_id=d.id
  WHERE a.id=NEW.artifact_id;
  IF expected_tenant IS NULL OR NEW.tenant_id <> expected_tenant OR
     NEW.expected_digest <> expected_hash OR NEW.expected_size IS DISTINCT FROM expected_bytes OR
     expected_ref <> ('s3://' || NEW.bucket || '/' || NEW.object_key) THEN
    RAISE EXCEPTION 'TDOC_ATTEMPT_SCOPE_OR_MANIFEST' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_attempt_binding_fence
  BEFORE INSERT OR UPDATE ON documentary_custodyattempt
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_attempt_binding();

CREATE FUNCTION tdoc_enforce_custody_receipt() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  expected_hash text;
  expected_bytes bigint;
  required_until timestamptz;
BEGIN
  IF NEW.kind='READBACK_VERIFIED' THEN
    SELECT expected_digest, expected_size, required_retention_until
      INTO expected_hash, expected_bytes, required_until
    FROM documentary_custodyattempt WHERE id=NEW.attempt_id;
    IF expected_hash IS NULL OR NEW.provider_version_id IS NULL OR
       NEW.provider_version_id IN ('', 'null') OR
       NEW.observed_sha256 IS DISTINCT FROM expected_hash OR
       NEW.observed_length IS DISTINCT FROM expected_bytes OR
       NEW.encryption_algorithm IS DISTINCT FROM 'aws:kms' OR
       NEW.encryption_key_id IS NULL OR
       NEW.retention_mode IS DISTINCT FROM 'COMPLIANCE' OR
       NEW.retain_until IS NULL OR NEW.retain_until < required_until THEN
      RAISE EXCEPTION 'TDOC_RECEIPT_INCOMPLETE' USING ERRCODE='23514';
    END IF;
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER tdoc_custody_receipt_complete
  BEFORE INSERT ON documentary_custodyobservation
  FOR EACH ROW EXECUTE FUNCTION tdoc_enforce_custody_receipt();
"""

REVERSE = r"""
DROP TRIGGER IF EXISTS tdoc_custody_receipt_complete ON documentary_custodyobservation;
DROP TRIGGER IF EXISTS tdoc_attempt_binding_fence ON documentary_custodyattempt;
DROP TRIGGER IF EXISTS tdoc_validity_version_scope ON documentary_documenttemporalvalidityobservation;
DROP TRIGGER IF EXISTS tdoc_verification_version_scope ON documentary_documentverificationobservation;
DROP TRIGGER IF EXISTS tdoc_artifact_source_scope ON documentary_contentartifact;
DROP TRIGGER IF EXISTS tdoc_relationship_version_scope ON documentary_documentrelationship;
DROP TRIGGER IF EXISTS tdoc_current_version_scope ON documentary_tradedocument;
DROP TRIGGER IF EXISTS tdoc_validity_append_only ON documentary_documenttemporalvalidityobservation;
DROP TRIGGER IF EXISTS tdoc_verification_append_only ON documentary_documentverificationobservation;
DROP TRIGGER IF EXISTS tdoc_orphan_evidence_append_only ON documentary_orphanobservation;
DROP TRIGGER IF EXISTS tdoc_custody_evidence_append_only ON documentary_custodyobservation;
DROP FUNCTION IF EXISTS tdoc_enforce_custody_receipt();
DROP FUNCTION IF EXISTS tdoc_enforce_attempt_binding();
DROP FUNCTION IF EXISTS tdoc_enforce_observation_scope();
DROP FUNCTION IF EXISTS tdoc_enforce_artifact_source();
DROP FUNCTION IF EXISTS tdoc_enforce_reference_lineage();
DROP FUNCTION IF EXISTS tdoc_enforce_current_version();
ALTER TABLE documentary_documenttemporalvalidityobservation DROP CONSTRAINT IF EXISTS tdoc_validity_unknown_only_chk;
ALTER TABLE documentary_documentverificationobservation DROP CONSTRAINT IF EXISTS tdoc_verification_no_positive_chk;
ALTER TABLE documentary_custodyobservation DROP CONSTRAINT IF EXISTS tdoc_observation_kind_chk;
ALTER TABLE documentary_custodyattempt DROP CONSTRAINT IF EXISTS tdoc_attempt_state_chk;
ALTER TABLE documentary_custodyattempt DROP CONSTRAINT IF EXISTS tdoc_attempt_key_chk;
ALTER TABLE documentary_custodyattempt DROP CONSTRAINT IF EXISTS tdoc_attempt_size_chk;
ALTER TABLE documentary_custodyattempt DROP CONSTRAINT IF EXISTS tdoc_attempt_digest_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_version_effective_range_chk;
ALTER TABLE documentary_documentversion DROP CONSTRAINT IF EXISTS tdoc_signatures_json_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_subjects_json_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_identifiers_json_chk;
ALTER TABLE documentary_tradedocument DROP CONSTRAINT IF EXISTS tdoc_issuer_json_chk;
"""


class Migration(migrations.Migration):
    dependencies = [("documentary", "0002_orphanobservation_contentartifact_character_encoding_and_more")]
    operations = [migrations.RunSQL(sql=FORWARD, reverse_sql=REVERSE)]
