# P0-04A — Trade Docs reference contract convergence

Date: 13 October 2026. Governing authority: Accepted ADR-BCP-026/027,
ADR-TDOC-0001/0002, Shared ADR-SHARED-019..024 and LA-05A. Consulted issuer
ADR-TDOC-0007 and API ADR-TDOC-0012 plus TDOC-TECH-01; these remain Proposed.
This increment neither accepts those proposals nor starts the production runtime.

## Audit and bounded implementation

Trade Docs main `04a51f38d22c05b7232de4dc4c08f3506a1ebd38` had no open PRs and
only the main branch at audit. Shared main is
`a9c53087d63caa356edf54ec8037ba1713c4827f`; CP programme baseline is
`afeab1114cdbeb375b57230f0894b826e78c076a`. Earlier ERP/Payments/Subscriptions
consumer convergence is recorded in the CP completion plan.

LA-05F had a tested policy reference but no consumer lock and manual response
validation accepted a 36-character non-UUID mandate, omitted policy references,
unknown fields and some schema-invalid times. The new lock declares all twelve
paths in its complete reference closure and architectural RTD dependencies.
Immutable Git blobs are packaged without modification; provenance pins hashes
and three owned entry points. RTD profile and consumer lock use the same pin,
while RTD maturity remains ARCHITECTURE_ONLY. Reference source/test evidence is
now listed explicitly, not represented as a deployed issuer.

Both initial and final legal-actor responses must satisfy Shared's exact schema
before operation/issuer/freshness binding. Malformed requests deny before assessor
or provider contact. Negative resolutions are schema-valid facts that still deny
issuance. UUID and RFC3339 date-time formats are asserted; startup refuses a
missing checker. No schema retrieval, data coercion, unknown-property removal,
actor selection or default legal entity is permitted.

The existing thirty-second lease, intended issuer check, independent provider
readiness and final fresh mandate equality remain in force. Private assessment
requests still contain no caller-selected tenant, Organisation, actor, mandate
or decision time. Reference packaging does not grant external signing authority.

## Maintenance and verification

1. Review changed Shared schemas, every relative reference and workload vocabulary.
2. Check out the exact full lock SHA; update both locks only in an explicit PR.
3. Install `requirements-conformance.txt` with Python 3.14.
4. Run `python scripts/sync_contracts.py --shared-checkout /path/to/shared`.
5. Run the same command with `--check`; generated resources are replaced wholesale.
6. Run `SHARED_CHECKOUT=/path/to/shared python -m unittest discover -s tests -v`.
7. Build with `python -c "from setuptools.build_meta import build_wheel; build_wheel('dist')"`.
   CI installs this wheel into a separate environment and runs
   `scripts/verify_packaged_reference.py` outside the checkout against the saved vectors.

Fourteen unit/conformance tests include 45 independently owner-validated synthetic
wire vectors, initial/final malformed response denial, invalid request non-contact,
schema-valid denial, foreign/stale authority, revocation/replacement during provider
I/O and repeated issuance attempts. Installed-wheel checks assert original file
bytes, complete inventory and executable validators without Shared, issuer, database
or source-tree imports. Local checks use available Python 3.12; hosted CI must prove
the declared Python 3.14 baseline before merge. Fixtures are synthetic wire proof,
not corporate/legal/provider acceptance evidence.

## Remaining gates

The dedicated staging workload remains PROVISIONED with CP audience,
`context:resolve` and `legal-actor:assess`; no admission changes are made.
No document issuer service, authenticated CP transport, stored context redemption,
Django API, PostgreSQL immutable versions/outbox, signer, Customs gateway or
provider-supported capability exists. Future transport must enforce active IAM
identity/scope, current context ownership, TLS, bounded reads/deadlines, redirect
refusal and strict duplicate-member JSON rejection before reference validation.

P0-04B must implement the real context-bound, immutable, versioned issuance path,
provider/issuer proof, signing and atomic history/outbox with native bypass tests.
Genuine P0-03 records and mandates plus protected deployment/qualification remain
independently outstanding. No capability/whole-tenant production promotion follows
from P0-04A or a passing reference wheel.
