#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
python --version
rustc --version
cargo --version
pg_isready -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER:-tdoc}" -d "${POSTGRES_DB:-tdoc}"
python -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check uv==0.13.5
# The lock is hash pinned; do not resolve new transitive versions at bootstrap.
uv pip sync --python .venv/bin/python runtime/requirements.lock
(cd rust-kernel && cargo test --locked && maturin build --locked --release --interpreter ../.venv/bin/python --out ../dist-wheels)
python -m pip install --no-index --no-deps --find-links dist-wheels baobab-tdoc-kernel==0.1.0
(cd runtime && ../.venv/bin/python manage.py check && ../.venv/bin/python manage.py migrate --noinput && ../.venv/bin/python manage.py test tests -v2)
