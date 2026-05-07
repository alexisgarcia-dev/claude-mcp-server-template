# Roadmap

This roadmap reflects MCP spec evolution and production-survival priorities.
Sourced from MCP 2026 official roadmap (March 2026), MCP 2025-11-25 specification, and production deployment feedback.

## v0.1.0 — Production-survival foundation (May 2026, current)

The version that doesn't die in production.

- 4 demo tools, 1 demo resource, 1 demo prompt (PantryAPI)
- Streamable HTTP transport (mandatory for remote deployment, MCP spec 2026)
- Static bearer token authentication (preview/dev — `StaticTokenVerifier`)
- OpenTelemetry observability pipeline (custom exporter, OTLP HTTP)
- Pinned dependencies + `uv.lock` committed
- Docker compose with Python httpx upstream healthcheck (no curl dependency)
- e2e quickstart validated on clean environment

## v0.2.0 — Auth maturation (target end May 2026)

For internet-exposed deployments.

- OAuth 2.1 + PKCE flow (FastMCP `JWTVerifier` + `OAuthProvider`)
- Reference integrations: Auth0, WorkOS, Azure Entra ID
- JWKS rotation handling
- Migration guide from `StaticTokenVerifier` (1-line change)
- Cookiecutter template generator (reduces fork-and-customize friction)

## v0.3.0 — Audit-ready & async maturity (target end June 2026)

For enterprise observability and long-running operations.

- Structured audit log (tool invocation tracing with parameters + results)
- Full SEP-1686 Tasks primitive RPC compliance: `tasks/get`, `tasks/result`, `tasks/list`, `tasks/cancel`, `notifications/tasks/status`
- Tool versioning support (mcp 1.28+ metadata `version` field)
- Migration path from `@mcp.tool(task=True)` async pattern to SEP-1686 RPC

## v0.4.0 — Horizontal scale (target end July 2026)

For multi-instance deployment.

- Stateless session mode (`stateless_http=True` + external state store)
- `.well-known/mcp-server-metadata.json` discovery endpoint (MCP Server Cards)
- Load-balancer-ready deployment patterns
- Reference Kubernetes manifest

## v0.5.0 — Multi-agent ready (target October 2026)

For agent-to-agent coordination.

- A2A protocol bridge (when Linux Foundation AAIF spec stabilizes Q3 2026)
- MCP Registry publishable manifest
- Server-as-agent capability (when MCP roadmap recursive servers ships)

---

## Versioning policy

- Backward compatibility within minor versions
- Migration guide for breaking changes between minor versions
- Deprecation window: 1 minor version minimum

## How to influence this roadmap

Open a GitHub issue with the label `roadmap` and a use case. Real-world deployment feedback weighs more than feature requests.