# claude-mcp-server-template

> Production-survival MCP server template — for servers that don't die in production.

[![MCP Spec 2025-11-25](https://img.shields.io/badge/MCP%20Spec-2025--11--25-blue)](https://modelcontextprotocol.io/specification/2025-11-25)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.x](https://img.shields.io/badge/FastMCP-3.x-green.svg)](https://gofastmcp.com)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python MCP server template built around the patterns that distinguish 9% healthy from 52% dead MCP servers in production (April 2026 community scan, 2,181 endpoints).

## Why this template

Most MCP server templates ship the spec primitives. This one ships the production-survival foundation:

1. **Streamable HTTP transport** — mandatory for remote deployment per 2026 spec, not stdio
2. **Bearer token authentication** — `StaticTokenVerifier` for preview, migration path to `JWTVerifier` documented
3. **OpenTelemetry observability** — OTLP exporter wired in `lifespan`, MCP semantic conventions
4. **Pinned dependencies + `uv.lock`** — reproducible across dev, staging, production
5. **Upstream healthcheck** — Docker `HEALTHCHECK` validates the upstream API connectivity, not just the process

If `git clone && docker compose up && curl` doesn't work on a fresh machine, this template has failed its primary contract.

## Quickstart

```bash
git clone https://github.com/alexisgarcia-dev/claude-mcp-server-template.git
cd claude-mcp-server-template
docker compose up
```

The server is now reachable at `http://localhost:8000/mcp/` with Streamable HTTP transport.

Test a tool call (token = `demo-readwrite` for full access):

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Authorization: Bearer demo-readwrite" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

OpenTelemetry traces are visible at `http://localhost:16686` (Jaeger UI).

## What's inside

| Primitive | Count | Notes |
|---|---|---|
| Tools | 4 | `get_recipe`, `search_recipes`, `update_pantry`, `generate_meal_plan` (async with progress) |
| Resources | 1 | `recipe_resource` (MIME-typed) |
| Prompts | 1 | `weekly_planner` (role-restricted per MCP 1.27) |

The demo wraps a fake SaaS (`PantryAPI`, included as `pantry_mock_api.py`) so you can see end-to-end wiring without external accounts.

## Authentication

`v0.1.0` ships `StaticTokenVerifier` with two demo tokens:

```python
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

verifier = StaticTokenVerifier(
    tokens={
        "demo-readonly":  {"client_id": "ro", "scopes": ["read:pantry"]},
        "demo-readwrite": {"client_id": "rw", "scopes": ["read:pantry", "write:pantry"]},
    },
    required_scopes=["read:pantry"],
)
```

This is **preview/dev authentication**. For internet-exposed production deployments, wait for `v0.2.0` or use behind a gateway.

`v0.2.0` will ship full OAuth 2.1 + PKCE with reference integrations for Auth0, WorkOS, and Azure Entra ID. Migration is a one-line change (`StaticTokenVerifier` → `JWTVerifier(jwks_uri=..., issuer=..., audience=...)`).

See [ROADMAP.md](ROADMAP.md) for the full versioning plan.

## Customizing for your API

Replace `PantryAPI` with your own:

1. Update `src/config.py` with your API base URL, auth, timeouts
2. Replace tool implementations in `src/tools/` with calls to your API
3. Update healthcheck in `src/server.py` `/ready` endpoint to ping your upstream

The retry logic (`tenacity AsyncRetrying`), secret masking (`SecretStr`), and OTel masking hooks are configured once in `src/pantry_client.py` and reused.

## Stack

- Python 3.14
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- [`mcp`](https://pypi.org/project/mcp/) 1.27 official SDK
- [`fastmcp`](https://gofastmcp.com) 3.2 framework
- `pytest`, `ruff`, `mypy` for the test/lint/type pipeline
- Docker compose with Jaeger for local observability

Exact pins in `pyproject.toml` and `uv.lock`.

## Tests

```bash
uv run pytest -q
```

48 tests passing (last run J14, 2026-05-08).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for v0.2 → v0.5 trajectory.

Current: `v0.1.0` production-survival foundation. Next: `v0.2.0` OAuth 2.1 (target end May 2026).

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues with the label `roadmap` carry weight. Real production feedback over speculative features.
