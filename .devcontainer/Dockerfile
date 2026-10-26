# Pinned multi-architecture image manifest; vetted 2026-10-26 from Microsoft Artifact Registry.
FROM mcr.microsoft.com/devcontainers/python:dev-3.14-bookworm@sha256:4a146bbf4b85b374c9d094f839cb377bd6dbd8f15a498a3bd39e4cec264294f3
ARG RUST_VERSION=1.90.0
RUN apt-get update && apt-get install -y --no-install-recommends build-essential pkg-config libpq-dev postgresql-client ca-certificates curl && rm -rf /var/lib/apt/lists/*
USER vscode
# Bootstrap uses TLS and an explicitly selected Rust release; toolchain and Cargo.lock are
# checked again in CI. rustup bootstrap provenance must be reviewed on updates.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain "${RUST_VERSION}" --profile minimal
ENV PATH="/home/vscode/.cargo/bin:${PATH}"
