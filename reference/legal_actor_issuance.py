"""LA-05F: executable *reference* PEP for Trade Docs issuance.

This repository is still ARCHITECTURE_ONLY, with NO deployed Trade Docs
runtime. This reference is intended to be imported by the proposed Django
service once its execution boundary is implemented; it cannot itself issue
any canonical TradeDocument or customs declaration.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Protocol, TypeVar

T = TypeVar("T")
MAX_LEASE = timedelta(seconds=30)

# Authorities belong to the explicit legal act, NOT to a document title.
# External official certificates require a different competent authority
# proof; a corporate CP mandate alone never licenses their issuance.
LEGAL_ROLE_BY_DOCUMENT: dict[str, str] = {
    "COMMERCIAL_INVOICE": "INVOICE_ISSUER",
    "TRADE_CONTRACT": "CONTRACTING_PARTY",
    "IMPORT_DECLARATION": "IMPORTER_OF_RECORD",
    "EXPORT_DECLARATION": "EXPORTER_OF_RECORD",
}


class DocumentIssuanceDenied(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class IssuanceOperation:
    context_id: str                 # issued to authenticated engine workload
    tenant_id: str
    operating_organisation_id: str
    document_family: str
    subject_reference: str           # pinned transaction/document aggregate
    activity: str
    market: str                      # ISO country
    capability: str
    operation_reference: str
    expected_responsible_legal_entity_id: str

    def assessment_request(self) -> dict[str, str]:
        role = LEGAL_ROLE_BY_DOCUMENT.get(self.document_family)
        if (role is None or not all((
                self.context_id, self.tenant_id, self.operating_organisation_id,
                self.subject_reference, self.activity, self.capability,
                self.operation_reference, self.expected_responsible_legal_entity_id
            )) or len(self.market) != 2 or not self.market.isascii() or not self.market.isupper()):
            raise DocumentIssuanceDenied("unsupported document family or missing scoped legal responsibility")
        return {
            "context_id": self.context_id, "role": role,
            "activity": self.activity, "market": self.market,
            "capability": self.capability,
            "operation_reference": self.operation_reference,
        }


class LegalActorAssessor(Protocol):
    def assess(self, request: Mapping[str, str]) -> Mapping[str, Any]: ...


class DocumentIssuerProvider(Protocol):
    def check_issuance_ready(self, operation: IssuanceOperation, mandate_id: str) -> bool: ...


def require_current_document_actor(
    operation: IssuanceOperation, decision: Mapping[str, Any],
    now: datetime,
) -> str:
    operation.assessment_request()
    if (decision.get("context_id") != operation.context_id
        or decision.get("operation_reference") != operation.operation_reference
        or decision.get("provider_permissions_granted") is not False):
        raise DocumentIssuanceDenied("CP response not bound to this documentary operation")
    legal = decision.get("legal_actor_resolution")
    if not isinstance(legal, Mapping) or legal.get("outcome") != "AUTHORIZED":
        raise DocumentIssuanceDenied("document legal responsibility denied")
    mandate = legal.get("mandate_id")
    entity = legal.get("responsible_legal_entity_id")
    references = legal.get("evidence_references")
    if (not isinstance(mandate, str) or len(mandate) != 36 or
        entity != operation.expected_responsible_legal_entity_id or
        not isinstance(references, list) or not references or
        any(not isinstance(x, str) or not x for x in references)):
        raise DocumentIssuanceDenied("legal actor verification mismatch")
    try:
        at = datetime.fromisoformat(str(legal["evaluated_at"]).replace("Z", "+00:00"))
        until = datetime.fromisoformat(str(legal["valid_until"]).replace("Z", "+00:00"))
    except (ValueError, TypeError, KeyError) as exc:
        raise DocumentIssuanceDenied("missing decision validity proof") from exc
    if (now.tzinfo is None or at.tzinfo is None or until.tzinfo is None
        or at > now + timedelta(seconds=1)
        or now - at > MAX_LEASE or until <= now
        or until > at + MAX_LEASE + timedelta(seconds=1)):
        raise DocumentIssuanceDenied("stale document issuer authority")
    return mandate


def issue_with_legal_actor(
    operation: IssuanceOperation, assessor: LegalActorAssessor,
    provider: DocumentIssuerProvider, issue: Callable[[], T],
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> T:
    """Reassess immediately before issuing/signing/filing, on EACH retry.

    External issuer evidence, legal signature delegation, documents'
    immutable artifact integrity, Regulations requirements, customs gateway
    authority and official licences belong to provider-specific enforcement.
    """
    request = operation.assessment_request()
    if assessor is None or provider is None or issue is None:
        raise DocumentIssuanceDenied("current CP and issuance readiness required")
    response = assessor.assess(request)  # fail closed if CP unavailable
    if not isinstance(response, Mapping):
        raise DocumentIssuanceDenied("CP response unavailable")
    mandate_id = require_current_document_actor(operation, response, now())
    if provider.check_issuance_ready(operation, mandate_id) is not True:
        raise DocumentIssuanceDenied("document issuer provider not ready")
    return issue()
