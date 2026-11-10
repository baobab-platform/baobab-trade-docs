"""Private S3-compatible HYB-03B custody adapter.

This module never issues trade documents or treats object custody as issuer,
Regulations or Customs authority. Calls are internal until HYB-04 IAM/CP gates.
"""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as datetime_timezone
from typing import Protocol

from django.conf import settings
from django.utils import timezone


MAX_CONTENT_BYTES = 16 * 1024 * 1024
READ_CHUNK_BYTES = 65536
OBJECT_PREFIX = "documentary/staging/"


class CustodyFailure(Exception):
    """A stable, non-sensitive refusal reason."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class ContentScanner(Protocol):
    def scan(self, content: bytes, media_type: str) -> str:
        """Return CLEAN only for a *qualified* malware/format scan."""


@dataclass(frozen=True)
class Readback:
    version_id: str
    digest: str
    size: int
    encryption: str
    encryption_key_id: str
    lock_mode: str
    retain_until: datetime


class PrivateS3Store:
    """One scoped bucket/key namespace. Never uses public ACLs or presigned writes."""

    def __init__(self, client, *, bucket: str, kms_key_id: str):
        if not bucket or not kms_key_id:
            raise CustodyFailure("STORAGE_CONFIGURATION_MISSING")
        self.client = client
        self.bucket = bucket
        self.kms_key_id = kms_key_id

    @classmethod
    def from_environment(cls):
        """Build a production SDK client from the standard, rotating AWS credential chain."""
        import boto3
        from botocore.config import Config

        bucket = os.environ.get("TDOC_S3_BUCKET", "")
        kms_key = os.environ.get("TDOC_S3_KMS_KEY_ARN", "")
        region = os.environ.get("TDOC_S3_REGION", "")
        endpoint = os.environ.get("TDOC_S3_ENDPOINT_URL") or None
        if not region or (endpoint and not endpoint.startswith("https://")):
            # No plain-HTTP fallback: local MinIO tests inject an in-memory client.
            raise CustodyFailure("STORAGE_ENDPOINT_NOT_PRIVATE_TLS")
        client = boto3.session.Session().client(
            "s3", region_name=region, endpoint_url=endpoint,
            config=Config(signature_version="s3v4", retries={"max_attempts": 2, "mode": "standard"}),
        )
        return cls(client, bucket=bucket, kms_key_id=kms_key)

    @staticmethod
    def object_key(artifact_id: str) -> str:
        if not artifact_id.startswith("tdoca_") or not artifact_id[6:].isalnum():
            raise CustodyFailure("INVALID_ARTIFACT_ID")
        return OBJECT_PREFIX + artifact_id

    def storage_reference(self, artifact_id: str) -> str:
        return f"s3://{self.bucket}/{self.object_key(artifact_id)}"

    def put(self, artifact_id: str, payload: bytes, media_type: str, retain_until: datetime) -> str:
        if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_CONTENT_BYTES:
            raise CustodyFailure("CONTENT_SIZE_REFUSED")
        if timezone.is_naive(retain_until) or retain_until <= timezone.now() + timedelta(hours=1):
            raise CustodyFailure("RETENTION_NOT_APPROVED")
        checksum = base64.b64encode(hashlib.sha256(payload).digest()).decode("ascii")
        response = self.client.put_object(
            Bucket=self.bucket,
            Key=self.object_key(artifact_id),
            Body=payload,
            ContentType=media_type,
            ChecksumSHA256=checksum,
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=self.kms_key_id,
            ObjectLockMode="COMPLIANCE",
            ObjectLockRetainUntilDate=retain_until,
            Metadata={"sha256": hashlib.sha256(payload).hexdigest()},
        )
        version_id = response.get("VersionId")
        if not version_id or version_id == "null":
            raise CustodyFailure("OBJECT_VERSION_UNCONFIRMED")
        return str(version_id)

    def recover_version(self, artifact_id: str) -> str:
        """Never substitute an unpinned latest object if multiple versions exist."""
        response = self.client.list_object_versions(
            Bucket=self.bucket, Prefix=self.object_key(artifact_id), MaxKeys=20,
        )
        if response.get("IsTruncated"):
            raise CustodyFailure("OBJECT_VERSION_AMBIGUOUS")
        matches = [v.get("VersionId") for v in response.get("Versions", [])
                   if v.get("Key") == self.object_key(artifact_id)]
        if not matches:
            raise CustodyFailure("OBJECT_NOT_FOUND")
        if len(matches) != 1 or not matches[0] or matches[0] == "null":
            raise CustodyFailure("OBJECT_VERSION_AMBIGUOUS")
        return str(matches[0])

    def verify(
        self, artifact_id: str, version_id: str, *,
        expected_sha256: str, expected_size: int, required_retention_until: datetime,
    ) -> Readback:
        if not version_id or version_id == "null":
            raise CustodyFailure("OBJECT_VERSION_UNCONFIRMED")
        args = {"Bucket": self.bucket, "Key": self.object_key(artifact_id), "VersionId": version_id}
        try:
            head = self.client.head_object(**args)
        except Exception as exc:
            if _is_not_found(exc):
                raise CustodyFailure("OBJECT_NOT_FOUND") from None
            raise CustodyFailure("OBJECT_READBACK_UNKNOWN") from None
        if int(head.get("ContentLength", -1)) != expected_size:
            raise CustodyFailure("OBJECT_LENGTH_MISMATCH")
        if head.get("VersionId") != version_id:
            raise CustodyFailure("OBJECT_VERSION_MISMATCH")
        if head.get("ServerSideEncryption") != "aws:kms":
            raise CustodyFailure("ENCRYPTION_UNVERIFIED")
        if head.get("SSEKMSKeyId") != self.kms_key_id:
            raise CustodyFailure("KMS_KEY_MISMATCH")
        if head.get("ObjectLockMode") != "COMPLIANCE":
            raise CustodyFailure("OBJECT_LOCK_UNVERIFIED")
        until = head.get("ObjectLockRetainUntilDate")
        if not isinstance(until, datetime) or timezone.is_naive(until):
            raise CustodyFailure("RETENTION_UNVERIFIED")
        if until < required_retention_until:
            raise CustodyFailure("RETENTION_TOO_SHORT")
        try:
            obj = self.client.get_object(**args)
        except Exception as exc:
            if _is_not_found(exc):
                raise CustodyFailure("OBJECT_NOT_FOUND") from None
            raise CustodyFailure("OBJECT_READBACK_UNKNOWN") from None
        stream = obj["Body"]
        digest = hashlib.sha256()
        count = 0
        try:
            while True:
                chunk = stream.read(READ_CHUNK_BYTES)
                if not chunk:
                    break
                count += len(chunk)
                if count > MAX_CONTENT_BYTES or count > expected_size:
                    raise CustodyFailure("OBJECT_LENGTH_MISMATCH")
                digest.update(chunk)
        except CustodyFailure:
            raise
        except Exception:
            raise CustodyFailure("OBJECT_READBACK_UNKNOWN") from None
        finally:
            stream.close()
        if count != expected_size or digest.hexdigest() != expected_sha256:
            raise CustodyFailure("OBJECT_DIGEST_MISMATCH")
        return Readback(
            version_id=version_id,
            digest=digest.hexdigest(), size=count, encryption="aws:kms",
            encryption_key_id=self.kms_key_id, lock_mode="COMPLIANCE", retain_until=until,
        )

    def list_staging_keys(self, *, max_keys: int = 100) -> tuple[list[str], bool]:
        if not 1 <= max_keys <= 1000:
            raise CustodyFailure("LIST_LIMIT_DENIED")
        response = self.client.list_objects_v2(
            Bucket=self.bucket, Prefix=OBJECT_PREFIX, MaxKeys=max_keys,
        )
        keys = [x["Key"] for x in response.get("Contents", [])
                if x.get("Key", "").startswith(OBJECT_PREFIX)]
        return keys, bool(response.get("IsTruncated"))


def _is_not_found(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    return bool(isinstance(response, dict) and
                str(response.get("Error", {}).get("Code")) in
                {"NoSuchKey", "NoSuchVersion", "404", "NotFound"})
