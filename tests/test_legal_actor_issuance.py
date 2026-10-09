"""LA-05F fail-closed documentary issuance acceptance corpus."""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from reference.legal_actor_issuance import (
    DocumentIssuanceDenied, IssuanceOperation,
    issue_with_legal_actor, require_current_document_actor,
)

NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
OP = IssuanceOperation(
    context_id="0199a1b2-c3d4-7e8f-9a0b-1c2d3e4f5a6b",
    tenant_id="tn_test_operating", operating_organisation_id="0199a1b2-c3d4-7e8f-9a0b-1c2d3e4f5a6c",
    document_family="COMMERCIAL_INVOICE",
    subject_reference="order/synthetic-123", activity="B2B_COFFEE_EXPORT",
    market="ZA", capability="documents.trade-document.issue",
    operation_reference="document/synthetic-123",
    expected_responsible_legal_entity_id="LE-VERIFIED-TEST",
)


def good():
    return {
        "context_id": OP.context_id,
        "operation_reference": OP.operation_reference,
        "provider_permissions_granted": False,
        "legal_actor_resolution": {
            "outcome": "AUTHORIZED", "policy_reference": "ADR-BCP-027",
            "mandate_id": "0199a1b2-c3d4-7e8f-9a0b-1c2d3e4f5a6d",
            "responsible_legal_entity_id": "LE-VERIFIED-TEST",
            "evidence_references": ["synthetic/verified-company"],
            "evaluated_at": NOW.isoformat(),
            "valid_until": (NOW + timedelta(seconds=10)).isoformat(),
        },
    }


class Assessor:
    def __init__(self, result):
        self.result, self.calls = result, 0

    def assess(self, request):
        self.calls += 1
        assert request == {
            "context_id": OP.context_id, "role": "INVOICE_ISSUER",
            "activity": OP.activity, "market": OP.market,
            "capability": OP.capability, "operation_reference": OP.operation_reference,
        }
        return self.result


class Issuer:
    def __init__(self, allowed):
        self.allowed, self.calls = allowed, 0

    def check_issuance_ready(self, operation, mandate):
        self.calls += 1
        assert operation == OP
        assert mandate == good()["legal_actor_resolution"]["mandate_id"]
        return self.allowed


class TestDocumentIssuerGate(unittest.TestCase):
    def test_private_request_never_supplies_actor_tenant_or_mandate(self):
        request = OP.assessment_request()
        for name in ("tenant_id", "operating_organisation_id", "responsible_legal_entity_id", "mandate_id", "effective_at"):
            self.assertNotIn(name, request)

    def test_allows_proved_invoice_issuer_and_provider_each_attempt(self):
        caller, provider, attempts = Assessor(good()), Issuer(True), []
        for _ in range(2):
            result = issue_with_legal_actor(OP, caller, provider,
                lambda: attempts.append("issued") or "document/v1", now=lambda: NOW)
            self.assertEqual(result, "document/v1")
        self.assertEqual((caller.calls, provider.calls, len(attempts)), (2, 2, 2))

    def test_deny_revoked_actor_mismatch_provisioning_and_expired(self):
        denied = [
            {"context_id": "other-context"},
            {"operation_reference": "other-document"},
            {"provider_permissions_granted": True},
            {"legal_actor_resolution": {**good()["legal_actor_resolution"], "outcome": "REVOKED_OR_EXPIRED"}},
            {"legal_actor_resolution": {**good()["legal_actor_resolution"], "responsible_legal_entity_id": "LE-OTHER"}},
            {"legal_actor_resolution": {**good()["legal_actor_resolution"], "valid_until": (NOW-timedelta(seconds=1)).isoformat()}},
            {"legal_actor_resolution": {**good()["legal_actor_resolution"], "evaluated_at": (NOW-timedelta(minutes=1)).isoformat()}},
        ]
        for change in denied:
            with self.subTest(change=change):
                assessor, provider, touched = Assessor({**good(), **change}), Issuer(True), []
                with self.assertRaises(DocumentIssuanceDenied):
                    issue_with_legal_actor(OP, assessor, provider,
                        lambda: touched.append("issued"), now=lambda: NOW)
                self.assertEqual(touched, [])
                self.assertEqual(provider.calls, 0)

    def test_provider_deny_stops_issuance_even_when_cp_authorised(self):
        touched = []
        with self.assertRaises(DocumentIssuanceDenied):
            issue_with_legal_actor(OP, Assessor(good()), Issuer(False),
                lambda: touched.append("issued"), now=lambda: NOW)
        self.assertEqual(touched, [])

    def test_unsupported_official_certificates_are_not_self_authorised(self):
        for family in ("OFFICIAL_CERTIFICATE", "CERTIFICATE_OF_ORIGIN", "CUSTOMS_RELEASE"):
            with self.subTest(family=family):
                with self.assertRaises(DocumentIssuanceDenied):
                    replace(OP, document_family=family).assessment_request()

    def test_no_implicit_issuer_from_parent_company_or_default_legal_entity(self):
        with self.assertRaises(DocumentIssuanceDenied):
            replace(OP, expected_responsible_legal_entity_id="").assessment_request()

    def test_current_decision_is_fact_not_external_signing_grant(self):
        self.assertEqual(require_current_document_actor(OP, good(), NOW),
            good()["legal_actor_resolution"]["mandate_id"])


if __name__ == "__main__":
    unittest.main()
