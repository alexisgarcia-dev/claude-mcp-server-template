# v1.0.0 — Initial stable release (frozen-by-design)

> Production-survival Python MCP server template — five sourced patterns + PantryAPI demo + ten ADR-light decisions documented.

## Why this template

A community scan published by Apigene in April 2026 surveyed 2,181 public MCP server endpoints: roughly 9 percent healthy and responding correctly, 52 percent dead or unreachable. The protocol is solid — the failure mode is downstream production patterns templates don't ship.

This template ships them.

## What v1.0.0 ships

Five pillars, validated end-to-end on every push and post-push:

1. **MCP primitives complete** — Tools + Resources + Prompts demonstrated end-to-end. Top ~4% of public MCP servers per [digitalapplied.com](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2025) 2026 stats.
2. **JSON-RPC healthcheck** — `HEALTHCHECK` runs the full MCP session lifecycle (`initialize` → `notifications/initialized` → `tools/list`) validating bearer auth + Streamable HTTP transport + session handshake + tool registration in one round-trip.
3. **OpenTelemetry + Jaeger 1.62.0 observability** — OTLP exporter wired in `lifespan`, Jaeger UI included in `docker-compose.yml`. Trace your MCP tool calls at `http://localhost:16686`.
4. **ADR-light architectural decisions** — ten decisions documented in [`docs/decisions.md`](./docs/decisions.md) with verified tier-2 sources.
5. **End-to-end validated quickstart** — `git clone && docker compose up && fastmcp Client list_tools()` works on a fresh machine. Pre-push and post-push (Layer 4 clone fresh from this public GitHub URL) empirical validation.

## Quickstart

```bash
git clone https://github.com/alexisgarcia-dev/claude-mcp-server-template.git
cd claude-mcp-server-template
docker compose up -d
```

Then in Python:

```python
from fastmcp import Client
import asyncio

async def main():
    async with Client(
        "http://127.0.0.1:8000/mcp",
        headers={"Authorization": "Bearer demo-readonly"},
    ) as client:
        tools = await client.list_tools()
        for t in tools:
            print(f"  {t.name}: {t.description}")

asyncio.run(main())
```

Open Jaeger UI at <http://localhost:16686> to inspect traces. For raw `curl` / PowerShell debugging, see [docs/manual-http-handshake.md](./docs/manual-http-handshake.md).

## What's inside

- 4 Tools (`list_pantry`, `suggest_recipes`, `add_to_pantry`, `swap_ingredients`)
- 1 Resource (`recipe_resource` MIME-typed)
- 1 Prompt (`weekly_planner`)
- Streamable HTTP transport + `StaticTokenVerifier` auth (demo-readonly / demo-readwrite — preview only, do NOT deploy with defaults)
- OpenTelemetry pipeline + Jaeger 1.62.0 UI
- Docker Compose 3-service stack (mcp-server + pantry-mock + jaeger)
- Non-root containers (mcp uid=1000 / pantry uid=1001)
- Container hardening (`no-new-privileges` + `cap_drop: ALL` on application services)
- GitHub Actions CI (uv matrix Python 3.11/3.12/3.13: ruff lint + format + pytest)
- CodeQL Python security scanning + Bandit weekly + Dependabot weekly
- 58 tests passing (unit + integration deselected by default)
- SECURITY.md + CONTRIBUTING.md + .dockerignore + .env.example + PR template + pre-commit hooks

## Replace PantryAPI with your domain

PantryAPI is a placeholder demonstrating the upstream-API + MCP-wrapper pattern. Swap for your real API in about 30 minutes — see the "Customizing for your API" section in the README.

## Pinned stack

Python 3.11+ | uv 0.11.8 | mcp 1.27.0 | fastmcp 3.2.4 | pytest 9.0.3 | jaeger 1.62.0

## Status

**Stable reference release. Maintenance community-driven from this point forward.** See [ROADMAP.md](./ROADMAP.md) for explicit future directions (OAuth 2.1 + PKCE, per-tool scope guards, structured audit log, horizontal scale) marked as "contributions welcome", and "out of scope by design" boundaries.

## Audit pre-ship

- Opus 4.7 manual security review: HIGH=0 on `src/server.py`, HIGH=0 on Docker stack
- Code-review bug-detector audit: identified and fixed 4 mock contract drift bugs invisible to unit tests, plus 1 healthcheck false-success masking bug — see commits in this release
- Verified tier-2 sources for every defensible claim (see [`docs/sources.md`](./docs/sources.md))

## Sourcing

- Apigene Blog 2026 — *Host MCP Server Deployment Guide* community scan (9%/52% stats)
- digitalapplied.com 2026 — *MCP Adoption Statistics* (top ~4% Tools+Prompts)
- modelcontextprotocol/python-sdk — official Python SDK and `mcp.server.auth` reference
- gofastmcp.com — FastMCP 3.2.4 documentation
- OWASP Container Security 2026 — hardening recommendations
- pydevtools handbook 2026 — *Setting up GitHub Actions with uv*

## Docs

- [README.md](./README.md)
- [ROADMAP.md](./ROADMAP.md) — community-driven future directions
- [docs/decisions.md](./docs/decisions.md) — 10 ADR-light decisions
- [docs/manual-http-handshake.md](./docs/manual-http-handshake.md) — raw HTTP debugging
- [docs/sources.md](./docs/sources.md) — verified tier-2 sources
- [docs/runbook.md](./docs/runbook.md) — bug-fix triage by symptom
- [SECURITY.md](./SECURITY.md) — vulnerability disclosure
- [CONTRIBUTING.md](./CONTRIBUTING.md) — contribution guide
