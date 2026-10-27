"""Owner-pinned positive/negative nested Shared v2 vectors (ADR-TDOC-0020).

Vectors use actual Shared $defs, including nested artifacts, provenance and
cross-schema references. These are wire-shape checks, never issuance authority.
"""
import copy
import json
import os
import subprocess
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from reference.shared_contracts import PROVENANCE

ROOT = Path(__file__).resolve().parents[1]
SHARED = Path(os.environ.get("SHARED_CHECKOUT", ROOT.parent / "shared"))
STAMP = "2026-10-26T10:00:00Z"
DOC = "tdoc_abc"
VERSION = "tdocv_abc"
ARTIFACT = "tdoca_abc"
REL = "tdocr_abc"
TENANT = "tn_synthetic1"
PROVENANCE_RECORD = {"source_kind": "BAOBAB_GENERATED", "recorded_at": STAMP}
ARTIFACT_RECORD = {
    "artifact_id": ARTIFACT, "document_version_id": VERSION,
    "artifact_role": "SOURCE_ORIGINAL", "media_type": "application/pdf",
    "storage_reference": "https://example.invalid/artifacts/abc",
    "digest_algorithm": "SHA-256", "digest_value": "a" * 64,
}
VERSION_RECORD = {
    "document_version_id": VERSION, "trade_document_id": DOC,
    "version_sequence": 1, "lifecycle_snapshot": "ISSUED",
    "medium_classification": "NATIVE_DIGITAL",
    "content_artifacts": [ARTIFACT_RECORD],
    "created_at": STAMP, "created_by": "synthetic-test-actor",
    "provenance": PROVENANCE_RECORD,
}
REL_RECORD = {
    "relationship_id": REL, "source_document_id": DOC,
    "target_document_id": "tdoc_def", "relationship_type": "SUPERSEDES",
    "created_at": STAMP, "created_by": "synthetic-test-actor",
}
DOCUMENT_RECORD = {
    "trade_document_id": DOC, "tenant_id": TENANT,
    "document_type": "COMMERCIAL_INVOICE", "document_family": "TRADE",
    "issuer_claim": {"party_reference": "synthetic-org", "issuer_role": "SELLER"},
    "lifecycle_state": "ISSUED", "current_version_id": VERSION,
    "business_identifiers": [{"value": "INV-1", "scheme": "INVOICE_NUMBER"}],
    "subject_associations": [{"subject_context": "trade", "subject_type": "ORDER",
                               "subject_reference": "order-1", "role": "EVIDENCES"}],
    "aggregate_version": 1, "created_at": STAMP, "updated_at": STAMP,
}
EVENT_RECORD = {
    "trade_document_id": DOC, "document_version_id": VERSION,
    "artifact_id": ARTIFACT, "tenant_id": TENANT,
    "artifact_role": "SOURCE_ORIGINAL", "media_type": "application/pdf",
    "digest_algorithm": "SHA-256", "digest_value": "a" * 64,
    "registered_at": STAMP,
}
VECTORS = (
    ("trade-document/v2/domain.schema.json", "contentArtifact", ARTIFACT_RECORD, ("digest_value", "short")),
    ("trade-document/v2/domain.schema.json", "documentVersion", VERSION_RECORD, ("version_sequence", 0)),
    ("trade-document/v2/domain.schema.json", "documentRelationship", REL_RECORD, ("relationship_type", "UNAUTHORISED")),
    ("trade-document/v2/domain.schema.json", "tradeDocument", DOCUMENT_RECORD, ("lifecycle_state", "INVALID")),
    ("trade-document/v2/events.schema.json", "contentArtifactRegisteredEventData", EVENT_RECORD, ("artifact_role", "INVALID")),
)

class NestedContractVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()
        cls.schemas = {}
        for path in PROVENANCE["files"]:
            if not path.endswith(".schema.json"):
                continue
            raw = subprocess.check_output([
                "git", "-C", str(SHARED), "show",
                f"{PROVENANCE['commit']}:contracts/{path}",
            ])
            schema = json.loads(raw)
            cls.schemas[path] = schema
            cls.registry = cls.registry.with_resource(schema["$id"], Resource.from_contents(schema))

    def test_owner_pinned_nested_positive_and_negative_vectors(self):
        for path, definition, positive, (bad_key, bad_value) in VECTORS:
            uri = self.schemas[path]["$id"] + "#/$defs/" + definition
            validator = Draft202012Validator({"$ref": uri}, registry=self.registry,
                format_checker=Draft202012Validator.FORMAT_CHECKER)
            with self.subTest(path=path, definition=definition, case="positive"):
                self.assertTrue(validator.is_valid(positive), list(validator.iter_errors(positive)))
            negative = copy.deepcopy(positive)
            negative[bad_key] = bad_value
            with self.subTest(path=path, definition=definition, case="negative"):
                self.assertFalse(validator.is_valid(negative))
            nested_negative = copy.deepcopy(positive)
            if definition == "documentVersion":
                nested_negative["content_artifacts"][0]["digest_value"] = "bad"
            elif definition == "tradeDocument":
                nested_negative["issuer_claim"]["issuer_role"] = "bad"
            else:
                continue
            with self.subTest(path=path, definition=definition, case="nested-negative"):
                self.assertFalse(validator.is_valid(nested_negative))
