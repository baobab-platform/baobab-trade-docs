# LA-05F — Document Issuer / Declarant Legal-Actor Enforcement Reference

**Authority:** Accepted ADR-BCP-027 LA-05, ADR-TDOC-0001/0002, Shared v2 Trade Document contracts and Shared LA-05A #261 / CP #299.

The reference PEP `reference/legal_actor_issuance.py` provides a **real, unittest-exercised fail-closed issuer policy**, independent of a deployed server. Each issue/sign/file attempt must fresh-assess the *specific* CP context-owned operating business and one of these roles:

| Family | CP legal actor role |
|---|---|
| COMMERCIAL_INVOICE | INVOICE_ISSUER |
| TRADE_CONTRACT | CONTRACTING_PARTY |
| IMPORT_DECLARATION | IMPORTER_OF_RECORD |
| EXPORT_DECLARATION | EXPORTER_OF_RECORD |

All other document families, including certificates of origin, official certificates and customs release, are **NOT** privately authorized through this reference: an official external competent authority remains required.

A real Trade Docs implementation MUST:
1. Authenticate an active purpose-specific Trade Docs workload with `context:resolve` and explicitly enrolled `legal-actor:assess`; context ownership/expiry is verified by CP.
2. Bind each exact operation to a pinned canonical TradeDocument/DocumentVersion (immutable external references under Shared RTD-04/05). The operation reference must match the CP assessment response; no raw document identifier is a bearer authorization.
3. Reassess CP `AUTHORIZED` on every issue/sign/file/retry, verify the responsible LegalEntity is the **intended** issuer/importer/exporter/contractor, and cap decision lease to 30 seconds.
4. Independently prove document issuer delegation, qualified signing certificate and signatures, current market/regulatory pack, customs gateway role and competence of external issuer; CP corporate mandate alone is never a customs or public official certificate.
5. Persist versioned documentary evidence and immutable signing proof, publish only Trade Docs-owned events, and preserve Regulations authority for sufficiency and assessments.
6. Deny if CP/issuer/provider or source version unavailable, invalid, revoked or ambiguous.

**Readiness:** this repository's runtime remains `ARCHITECTURE_ONLY` and has no deployed document issuer, database outbox, signing adapter or regulatory gateway. Reference code and CI are **NOT** product production readiness. Do not advertise `documents.*` provider-supported or issue a real invoice/declaration until the complete versioned issuance path is implemented and staging proven.

No Nabhold, ZuriBeans, Equator or Thamani legal role is inferred. LA-06 founding-group activation will follow PEO-02/03.
