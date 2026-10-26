#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
python --version
rustc --version
cargo --version
pg_isready -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER:-tdoc}" -d "${POSTGRES_DB:-tdoc}"
# Codespaces and mounted GitHub Actions repositories may be read-only for vscode.
# Keep all temporary build outputs in the user's home, not the checked-out tree.
TDOC_BUILD_ROOT="${TDOC_BUILD_ROOT:-$HOME/.cache/baobab-tdoc}"
mkdir -p "$TDOC_BUILD_ROOT/wheels"
export CARGO_TARGET_DIR="$TDOC_BUILD_ROOT/cargo-target"
VENV="$TDOC_BUILD_ROOT/venv"
python -m venv "$TDOC_BUILD_ROOT/tooling"
"$TDOC_BUILD_ROOT/tooling/bin/python" -m pip install --disable-pip-version-check uv==0.13.5
UV="$TDOC_BUILD_ROOT/tooling/bin/uv"
python -m venv "$VENV"
"$UV" pip sync --python "$VENV/bin/python" --require-hashes runtime/requirements.lock
(cd rust-kernel && cargo test --locked && "$VENV/bin/maturin" build --locked --release --interpreter "$VENV/bin/python" --out "$TDOC_BUILD_ROOT/wheels")
"$UV" pip install --python "$VENV/bin/python" --no-index --no-deps --find-links "$TDOC_BUILD_ROOT/wheels" baobab-tdoc-kernel==0.1.0
(cd runtime && "$VENV/bin/python" manage.py check && "$VENV/bin/python" manage.py migrate --noinput && "$VENV/bin/python" manage.py test tests -v2)
