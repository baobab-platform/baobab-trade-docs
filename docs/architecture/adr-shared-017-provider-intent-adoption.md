# ADR-SHARED-017 — Trade Docs source declaration adoption

**Baseline:** Trade Docs main `d622f541cbf545230ab000e3321f5870bc954fa9`; Shared `2a2ac16a` reviewed 10 November 2026.

## Source finding

The root `.baobab/` folder supplied only a generic `capability-provider.yaml.example` from the engine-template. It did not declare actual, typed engine-owned capability intent. ADR-SHARED-017's candidate-only path is appropriate because Trade Docs' README explicitly records that HYB-01 is a development scaffold with **no production document issuance provider**.

## Implementation

- Add `.baobab/capability-provider.yaml` with exactly two **CANDIDATE** proposed operations, backed by accepted ADR-TDOC-0002 but **not** promoted to canonical Shared capabilities.
- Do **not** claim a provider, `IMPLEMENTED` support, certification, registered instance, approved document issuance, tenant grant, active event publisher or legal-document approval.
- Add source CI validating the declaration against the **immutable existing Trade Docs Shared pin** from `contracts.lock.yaml`. The file only references future intent and does not mint a Shared capability key.
- Retain the existing generic `.example` as a teaching template; the engine's real declaration is independently validated.

## Qualification still required

Contract owner reviews, future Shared capability census/contract admission, actual provider implementation and evidence, EA-09 certification, CP/IAM authority, controlled production activation, durable versioned document storage, event/outbox publisher, documentary evidence/rule separation, cross-tenant and replay negatives. None is supplied by a planned capability.

**Regression intent:** if this repository begins claiming a provider or promotes a candidate to CONTRACTED/IMPLEMENTED, the candidate-only gate refuses until the capability registration/activation process is updated explicitly.
