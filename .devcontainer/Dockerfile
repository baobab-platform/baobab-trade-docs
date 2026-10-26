FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm
ARG RUST_VERSION=1.90.0
RUN apt-get update && apt-get install -y --no-install-recommends build-essential pkg-config libpq-dev postgresql-client ca-certificates curl && rm -rf /var/lib/apt/lists/*
USER vscode
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain "${RUST_VERSION}" --profile minimal
ENV PATH="/home/vscode/.cargo/bin:${PATH}"
