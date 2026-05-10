# Multi-stage build for the MCP server.
# Stage 1: build deps with uv (cached layer, --locked for reproducibility)
# Stage 2: runtime slim image (no build tools)

# syntax=docker/dockerfile:1.6

FROM python:3.14-slim AS builder

# Install uv 0.11.8 pinned (matches pyproject.toml-aligned tooling)
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

WORKDIR /app

# Copy lockfile and project metadata first (Docker layer cache deps separately from src)
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Install deps to a venv at /app/.venv (reproducible via uv.lock)
RUN uv sync --locked --no-dev

# ---------------------------------------------------------------------------
# Stage 2: runtime
# ---------------------------------------------------------------------------
FROM python:3.14-slim

WORKDIR /app

# Copy venv + source + runtime configs from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY config.toml ./
COPY healthcheck.py ./

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

EXPOSE 8000

# Non-root user (security hardening, OWASP recommendation for container images)
RUN useradd --create-home --shell /bin/bash --uid 1000 mcp \
    && chown -R mcp:mcp /app
USER mcp

# Healthcheck: httpx-based MCP tools/list call (no curl dependency, production-realistic)
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]

CMD ["python", "-m", "src.server"]
