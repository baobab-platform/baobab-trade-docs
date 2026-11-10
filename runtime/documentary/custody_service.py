"""Internal HYB-03B custody coordination with durable replay/recovery.

No public API, document issuance, CP authority bypass, or legal attestation.
Never treat a storage observation as a valid document-issue command.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from uuid import UUID

from django.db import IntegrityError, transaction
from django.utils import timezone

from documentary.custody import (
    MAX_CONTENT_BYTES, CustodyFailure, ContentScanner, PrivateS3Store, Readback,
)
from documentary.models import (
    ContentArtifact, CustodyAttempt, CustodyObservation, OrphanObservation,
)


def _owned_artifact(artifact_id: str, tenant_id: str) -> ContentArtifact:
    try:
        artifact = ContentArtifact.objects.select_related(
            "document_version__trade_document"
        ).get(pk=artifact_id)
    except ContentArtifact.DoesNotExist:
        raise CustodyFailure("ARTIFACT_NOT_AVAILABLE") from None
    if artifact.document_version.trade_document.tenant_id != tenant_id:
        # No cross-tenant artifact discovery via status or error detail.
        raise CustodyFailure("ARTIFACT_NOT_AVAILABLE")
    return artifact


def _record(attempt_id: UUID, generation: int, kind: str, state: str | None,
            *, version_id: str | None = None, receipt: Readback | None = None,
            error_code: str | None = None) -> bool:
    """Commit state and immutable evidence under a generation fence."""
    with transaction.atomic():
        attempt = CustodyAttempt.objects.select_for_update().get(pk=attempt_id)
        if attempt.attempts != generation:
            return False
        if state is not None:
            attempt.state = state
            attempt.last_error_code = error_code
            attempt.save(update_fields=["state", "last_error_code", "updated_at"])
        CustodyObservation.objects.create(
            attempt=attempt, kind=kind,
            provider_version_id=receipt.version_id if receipt else version_id,
            observed_sha256=receipt.digest if receipt else None,
            observed_length=receipt.size if receipt else None,
            encryption_algorithm=receipt.encryption if receipt else None,
            encryption_key_id=receipt.encryption_key_id if receipt else None,
            retention_mode=receipt.lock_mode if receipt else None,
            retain_until=receipt.retain_until if receipt else None,
            error_code=error_code,
        )
    return True


def _claim(attempt_id: UUID) -> int | None:
    """No DB transaction is kept open while calling a remote object store."""
    with transaction.atomic():
        attempt = CustodyAttempt.objects.select_for_update().get(pk=attempt_id)
        if attempt.state in {CustodyAttempt.State.VERIFIED, CustodyAttempt.State.QUARANTINED}:
            return None
        attempt.attempts += 1
        attempt.save(update_fields=["attempts", "updated_at"])
        return attempt.attempts


def stage_artifact(
    *, artifact_id: str, tenant_id: str, payload: bytes, store: PrivateS3Store,
    scanner: ContentScanner, retain_until: datetime,
) -> CustodyAttempt:
    """Private test/operator path. HYB-04 must provide live IAM/CP authorisation."""
    artifact = _owned_artifact(artifact_id, tenant_id)
    if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_CONTENT_BYTES:
        raise CustodyFailure("CONTENT_SIZE_REFUSED")
    if artifact.byte_length != len(payload) or artifact.digest_value != hashlib.sha256(payload).hexdigest():
        raise CustodyFailure("CONTENT_MANIFEST_MISMATCH")
    if artifact.storage_reference != store.storage_reference(artifact_id):
        raise CustodyFailure("STORAGE_REFERENCE_MISMATCH")
    if artifact.custody_state != "UNVERIFIED":
        raise CustodyFailure("ARTIFACT_NOT_UNVERIFIED")
    if timezone.is_naive(retain_until) or retain_until <= timezone.now():
        raise CustodyFailure("RETENTION_NOT_APPROVED")

    # A journal entry commits before any network call; no DB+object-store ACID is claimed.
    with transaction.atomic():
        try:
            attempt = CustodyAttempt.objects.create(
                artifact=artifact, tenant_id=tenant_id, bucket=store.bucket,
                object_key=store.object_key(artifact_id),
                expected_digest=artifact.digest_value, expected_size=len(payload),
                required_retention_until=retain_until,
            )
        except IntegrityError:
            raise CustodyFailure("STAGE_ALREADY_EXISTS") from None
        CustodyObservation.objects.create(
            attempt=attempt, kind=CustodyObservation.Kind.STAGE_REQUESTED,
        )

    generation = _claim(attempt.id)
    assert generation is not None
    try:
        if scanner is None or scanner.scan(payload, artifact.media_type) != "CLEAN":
            _record(attempt.id, generation, CustodyObservation.Kind.QUARANTINED,
                    CustodyAttempt.State.QUARANTINED, error_code="SCAN_REFUSED")
            raise CustodyFailure("SCAN_REFUSED")
    except CustodyFailure:
        raise
    except Exception:
        _record(attempt.id, generation, CustodyObservation.Kind.QUARANTINED,
                CustodyAttempt.State.QUARANTINED, error_code="SCAN_UNAVAILABLE")
        raise CustodyFailure("SCAN_UNAVAILABLE") from None

    try:
        version_id = store.put(artifact_id, payload, artifact.media_type, retain_until)
    except Exception:
        # Upload may have committed remotely before response loss. Never immediately retry PUT.
        _record(attempt.id, generation, CustodyObservation.Kind.CHECK_FAILED,
                CustodyAttempt.State.RECHECK_REQUIRED, error_code="UPLOAD_UNKNOWN")
        raise CustodyFailure("UPLOAD_UNKNOWN") from None
    _record(attempt.id, generation, CustodyObservation.Kind.UPLOAD_OBSERVED,
            None, version_id=version_id)
    try:
        receipt = store.verify(
            artifact_id, version_id, expected_sha256=artifact.digest_value,
            expected_size=len(payload), required_retention_until=retain_until,
        )
    except CustodyFailure as exc:
        _record(attempt.id, generation, CustodyObservation.Kind.CHECK_FAILED,
                CustodyAttempt.State.RECHECK_REQUIRED, version_id=version_id,
                error_code=exc.code)
        raise
    except Exception:
        _record(attempt.id, generation, CustodyObservation.Kind.CHECK_FAILED,
                CustodyAttempt.State.RECHECK_REQUIRED, version_id=version_id,
                error_code="READBACK_UNKNOWN")
        raise CustodyFailure("READBACK_UNKNOWN") from None
    if not _record(attempt.id, generation, CustodyObservation.Kind.READBACK_VERIFIED,
                   CustodyAttempt.State.VERIFIED, receipt=receipt):
        raise CustodyFailure("STALE_CUSTODY_GENERATION")
    return CustodyAttempt.objects.get(pk=attempt.id)


def reconcile_artifact(
    *, attempt_id: UUID, tenant_id: str, store: PrivateS3Store,
) -> CustodyAttempt:
    """Readback only. Does not put, delete or select an ambiguous 'latest' version."""
    try:
        attempt = CustodyAttempt.objects.select_related(
            "artifact__document_version__trade_document"
        ).get(pk=attempt_id)
    except CustodyAttempt.DoesNotExist:
        raise CustodyFailure("ARTIFACT_NOT_AVAILABLE") from None
    if (attempt.tenant_id != tenant_id or
            attempt.artifact.document_version.trade_document.tenant_id != tenant_id or
            attempt.bucket != store.bucket):
        raise CustodyFailure("ARTIFACT_NOT_AVAILABLE")
    generation = _claim(attempt.id)
    if generation is None:
        return CustodyAttempt.objects.get(pk=attempt.id)
    history = attempt.observations.filter(
        kind__in=[CustodyObservation.Kind.UPLOAD_OBSERVED,
                  CustodyObservation.Kind.CHECK_FAILED],
        provider_version_id__isnull=False,
    ).order_by("-observed_at", "-pk").first()
    version_id = history.provider_version_id if history else None
    try:
        if not version_id:
            version_id = store.recover_version(attempt.artifact_id)
        receipt = store.verify(
            attempt.artifact_id, version_id,
            expected_sha256=attempt.expected_digest, expected_size=attempt.expected_size,
            required_retention_until=attempt.required_retention_until,
        )
    except CustodyFailure as exc:
        state = (CustodyAttempt.State.MISSING if exc.code == "OBJECT_NOT_FOUND" else
                 CustodyAttempt.State.QUARANTINED if exc.code in {
                     "OBJECT_VERSION_AMBIGUOUS", "OBJECT_DIGEST_MISMATCH",
                     "ENCRYPTION_UNVERIFIED", "OBJECT_LOCK_UNVERIFIED",
                     "RETENTION_TOO_SHORT", "KMS_KEY_MISMATCH",
                 } else CustodyAttempt.State.RECHECK_REQUIRED)
        kind = (CustodyObservation.Kind.OBJECT_MISSING if state == CustodyAttempt.State.MISSING
                else CustodyObservation.Kind.QUARANTINED if state == CustodyAttempt.State.QUARANTINED
                else CustodyObservation.Kind.CHECK_FAILED)
        _record(attempt.id, generation, kind, state, version_id=version_id, error_code=exc.code)
    except Exception:
        _record(attempt.id, generation, CustodyObservation.Kind.CHECK_FAILED,
                CustodyAttempt.State.RECHECK_REQUIRED, version_id=version_id,
                error_code="READBACK_UNKNOWN")
    else:
        _record(attempt.id, generation, CustodyObservation.Kind.READBACK_VERIFIED,
                CustodyAttempt.State.VERIFIED, receipt=receipt)
    return CustodyAttempt.objects.get(pk=attempt.id)


def inspect_orphans(*, store: PrivateS3Store, max_keys: int = 100) -> tuple[int, bool]:
    """Bounded non-destructive inventory; never delete or reclassify an unknown object."""
    keys, truncated = store.list_staging_keys(max_keys=max_keys)
    known = set(CustodyAttempt.objects.filter(
        bucket=store.bucket, object_key__in=keys,
    ).values_list("object_key", flat=True))
    with transaction.atomic():
        for key in keys:
            if key not in known:
                OrphanObservation.objects.create(bucket=store.bucket, object_key=key)
    return len(keys) - len(known), truncated
