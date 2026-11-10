"""Canonical Shared v2 projections of *draft* documentary records.

These representations are schema-validated offline. They are not signed, issued,
verified or authorised simply because they satisfy a JSON Schema.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

SCHEMA_BASE = Path(__file__).resolve().parents[2] / "reference/shared_contracts/data"
DOMAIN_URI = "https://contracts.baobab-platform.com/trade-document/v2/domain.schema.json"


class DocumentaryWireError(ValueError):
    pass


@lru_cache(maxsize=1)
def _registry() -> Registry:
    manifest = json.loads((SCHEMA_BASE / "provenance.json").read_bytes())
    registry = Registry()
    for relative, digest in manifest["files"].items():
        raw = (SCHEMA_BASE / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise RuntimeError("Pinned Shared contract digest mismatch")
        if relative.endswith(".schema.json"):
            schema = json.loads(raw)
            Draft202012Validator.check_schema(schema)
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def _validate(definition: str, value: dict) -> dict:
    validator = Draft202012Validator(
        {"$ref": f"{DOMAIN_URI}#/$defs/{definition}"},
        registry=_registry(),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    try:
        validator.validate(value)
    except ValidationError:
        raise DocumentaryWireError("SHARED_V2_WIRE_SHAPE_REFUSED") from None
    return value


def _date(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise DocumentaryWireError("NAIVE_TIMESTAMP_REFUSED")
    return value.isoformat()


def trade_document_v2(doc) -> dict:
    if doc.current_version_id is not None:
        if doc.current_version.trade_document_id != doc.pk:
            raise DocumentaryWireError("CROSS_DOCUMENT_CURRENT_VERSION")
    if doc.issuer_claim is None:
        raise DocumentaryWireError("ISSUER_CLAIM_REQUIRED")
    return _validate("tradeDocument", {
        "trade_document_id": doc.pk,
        "tenant_id": doc.tenant_id,
        "document_type": doc.document_type,
        "document_family": doc.document_family,
        "issuer_claim": doc.issuer_claim,
        "lifecycle_state": doc.lifecycle_state,
        "current_version_id": doc.current_version_id,
        "business_identifiers": doc.business_identifiers,
        "subject_associations": doc.subject_associations,
        "aggregate_version": doc.aggregate_version,
        "created_at": _date(doc.created_at),
        "updated_at": _date(doc.updated_at),
    })


def artifact_v2(artifact) -> dict:
    if artifact.source_artifact_id and (
        artifact.source_artifact.document_version.trade_document_id
        != artifact.document_version.trade_document_id
    ):
        raise DocumentaryWireError("CROSS_DOCUMENT_DERIVED_ARTIFACT")
    return _validate("contentArtifact", {
        "artifact_id": artifact.pk,
        "document_version_id": artifact.document_version_id,
        "artifact_role": artifact.artifact_role,
        "media_type": artifact.media_type,
        "syntax": artifact.syntax,
        "schema_reference": artifact.schema_reference,
        "semantic_context_reference": artifact.semantic_context_reference,
        "language": artifact.language,
        "character_encoding": artifact.character_encoding,
        "storage_reference": artifact.storage_reference,
        "byte_length": artifact.byte_length,
        "digest_algorithm": artifact.digest_algorithm,
        "digest_value": artifact.digest_value,
        "generated_at": _date(artifact.generated_at),
        "generated_by": artifact.generated_by,
        "renderer_version": artifact.renderer_version,
        "source_artifact_id": artifact.source_artifact_id,
    })


def document_version_v2(version) -> dict:
    if version.supersedes_version_id and version.supersedes_version.trade_document_id != version.trade_document_id:
        raise DocumentaryWireError("CROSS_DOCUMENT_VERSION_LINEAGE")
    return _validate("documentVersion", {
        "document_version_id": version.pk,
        "trade_document_id": version.trade_document_id,
        "version_sequence": version.version_sequence,
        "external_revision_label": version.external_revision_label,
        "lifecycle_snapshot": version.lifecycle_snapshot,
        "medium_classification": version.medium_classification,
        "semantic_payload_reference": version.semantic_payload_reference,
        "source_snapshot_reference": version.source_snapshot_reference,
        "content_artifacts": [artifact_v2(a) for a in version.artifacts.order_by("pk")],
        "signature_references": version.signature_references,
        "issued_at": _date(version.issued_at),
        "effective_from": _date(version.effective_from),
        "effective_to": _date(version.effective_to),
        "change_reason": version.change_reason,
        "supersedes_version_id": version.supersedes_version_id,
        "created_at": _date(version.created_at),
        "created_by": version.created_by,
        "provenance": {
            "source_kind": version.provenance_kind,
            "source_reference": version.provenance_source_reference,
            "supplied_by_reference": version.provenance_supplied_by_reference,
            "source_system": version.provenance_source_system,
            "recorded_at": _date(version.provenance_recorded_at),
        },
    })


def relationship_v2(relationship) -> dict:
    if relationship.source_version_id and relationship.source_version.trade_document_id != relationship.source_document_id:
        raise DocumentaryWireError("CROSS_DOCUMENT_SOURCE_VERSION")
    if relationship.target_version_id and relationship.target_version.trade_document_id != relationship.target_document_id:
        raise DocumentaryWireError("CROSS_DOCUMENT_TARGET_VERSION")
    return _validate("documentRelationship", {
        "relationship_id": relationship.pk,
        "source_document_id": relationship.source_document_id,
        "target_document_id": relationship.target_document_id,
        "relationship_type": relationship.relationship_type,
        "source_version_id": relationship.source_version_id,
        "target_version_id": relationship.target_version_id,
        "reason": relationship.reason,
        "created_at": _date(relationship.created_at),
        "created_by": relationship.created_by,
        "provenance": relationship.provenance,
    })


def verification_v2(observation) -> dict:
    if observation.document_version.trade_document_id != observation.trade_document_id:
        raise DocumentaryWireError("CROSS_DOCUMENT_VERIFICATION")
    return _validate("documentVerificationProjection", {
        "trade_document_id": observation.trade_document_id,
        "document_version_id": observation.document_version_id,
        "verification_state": observation.verification_state,
        "reason_code": observation.reason_code,
        "verifier_reference": observation.verifier_reference,
        "observed_at": _date(observation.observed_at),
    })


def validity_v2(observation) -> dict:
    if observation.document_version.trade_document_id != observation.trade_document_id:
        raise DocumentaryWireError("CROSS_DOCUMENT_VALIDITY")
    return _validate("documentTemporalValidityProjection", {
        "trade_document_id": observation.trade_document_id,
        "document_version_id": observation.document_version_id,
        "temporal_validity_state": observation.temporal_validity_state,
        "authority_reference": observation.authority_reference,
        "basis_reference": observation.basis_reference,
        "observed_at": _date(observation.observed_at),
    })
