# TDOC-HYB-01 — Reproducible hybrid runtime scaffold

**Architecture:** Accepted TDOC-TECH-02. **Implementation status:** IN PROGRESS / CI PENDING, not a provider activation.

## Scope
- Python 3.14 Django 6 application with a private diagnostic route, **no public issuance endpoints**.
- Rust 1.90/PyO3 0.27 native extension built by maturin, loaded by Django.
- PostgreSQL 17 only, real migrations and DB connection gate.
- Codespaces/DevContainer and required GitHub Actions build/test gate.
- Existing `reference/` remains unchanged as independently tested Shared schema/issuer reference.

## Explicitly excluded
No canonical document models, immutable versions, storage adapters, outbox, live IAM/CP auth, document signing, issuer activation, Customs integration or regulatory evidence resolution. These belong to HYB-02 through HYB-07.

## Local startup
Open the repository in Codespaces using `.devcontainer/devcontainer.json`; from its terminal:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install 'maturin>=1.9,<2'
(cd rust-kernel && maturin build --release --interpreter python --out ../dist-wheels)
python -m pip install --no-index --find-links dist-wheels baobab-tdoc-kernel==0.1.0
python -m pip install 'Django>=6.0,<6.1' 'psycopg[binary]>=3.2,<3.4'
cd runtime
python manage.py check
python manage.py migrate --noinput
python manage.py test tests -v2
```

Environment credentials are local development only. Never run the development server publicly or promote a HYB-01 build to provider ACTIVE.

## Required exit evidence and remaining gaps
HYB-01 needs green CI for actual Python/Rust wheel import and PostgreSQL 17 migrations, cold DevContainer build verification, immutable dependency closure including Cargo.lock/Python lock and pinned base images/actions, a binary/SBOM vulnerability review and valid source/test conformance registration. This PR establishes the executable CI candidate; passing a pipeline alone does **not** prove all lock/security/development-container evidence. Until qualified keep HYB-01 PARTIAL and `ARCHITECTURE_ONLY`.
