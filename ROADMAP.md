# Roadmap

**Status: v1.0.0 is the stable reference release.** Maintenance is community-driven from this point forward — pull requests, forks, and discussion welcome.

This roadmap reflects MCP spec evolution and production-survival priorities, sourced from the MCP 2026 official roadmap, the MCP 2025-11-25 specification, and production deployment feedback.

## v1.0.0 — Production-survival foundation (current, May 2026)

The version that doesn't die in production.

- 4 demo tools, 1 demo resource, 1 demo prompt (PantryAPI placeholder)
- Streamable HTTP transport (mandatory for remote deployment, MCP spec 2026)
- Static bearer token authentication (preview/dev — `StaticTokenVerifier`)
- OpenTelemetry observability pipeline (custom exporter, OTLP HTTP)
- Pinned dependencies + `uv.lock` committed
- Docker compose with Python httpx upstream healthcheck (no curl dependency)
- Container hardening (`no-new-privileges`, `cap_drop: ALL` services applicatifs)
- GitHub Actions CI matrix Python 3.11/3.12/3.13 + CodeQL + Bandit + Dependabot
- 10 ADR-light decisions documented in [`docs/decisions.md`](./docs/decisions.md)
- End-to-end quickstart validated empirically pre-push and post-push (Layer 4 clone fresh from GitHub)

## Future directions (contributions welcome)

These are areas where the template could grow. The maintainer is not committing to ship these — pull requests and forks are welcome. Open a GitHub issue with the label `roadmap` and a use case to discuss.

### v1.1.x line — conditional release target

**Trigger conditions** (any one suffices):
- MCP specification publishes a revision later than `2025-11-25` with breaking changes that affect tool/resource/prompt registration, transport, or auth surface.
- FastMCP ships a `4.x` major with non-trivial migration friction from `3.2.x`.
- A community PR ships a substantial production-pattern improvement (e.g., OAuth 2.1 + PKCE reference integration, structured audit log) with maintainer-grade test coverage.

**Tentative window**: Q4 2026 evaluation if any trigger fires before then. No commitment otherwise — `v1.0.x` remains the stable reference until then.

**What `v1.1.x` would NOT change**:
- The five production-survival pillars list (those are the project's identity).
- Pinned-version philosophy for reproducibility (only the pins move).
- "Out of scope by design" boundaries.

### Authentication maturation

- **OAuth 2.1 + PKCE** flow via FastMCP `JWTVerifier` + `OAuthProvider`, with reference integrations for Auth0, WorkOS, Azure Entra ID
- **JWKS rotation handling**
- **Migration guide** from `StaticTokenVerifier` (single-line change pattern)
- **Per-tool scope guards** (currently both demo tokens carry `read:pantry`; production deployments would gate `update_pantry` etc. behind `write:pantry`)
- **Cookiecutter template generator** to reduce fork-and-customize friction

### Audit-ready & async maturity

- **Structured audit log** (tool invocation tracing with parameters and results)
- **Full SEP-1686 Tasks primitive RPC compliance**: `tasks/get`, `tasks/result`, `tasks/list`, `tasks/cancel`, `notifications/tasks/status` (when MCP spec stabilizes this proposal)
- **Tool versioning support** (mcp 1.28+ metadata `version` field)

### Horizontal scale

- **Stateless session mode** (`stateless_http=True` + external state store)
- **`.well-known/mcp-server-metadata.json`** discovery endpoint (MCP Server Cards)
- **Reference Kubernetes manifest**

### Multi-agent ready

- **A2A protocol bridge** when the Linux Foundation AAIF specification stabilizes
- **MCP Registry publishable manifest**

## Out of scope by design

These are intentionally not part of this template's scope. Other projects address them well:

- **Multi-tenant session stores at scale** — see [IBM ContextForge](https://github.com/IBM/mcp-context-forge) for a gateway-grade solution
- **Plugin system / Admin UI** — gateway-class needs are not the focus of a lightweight template
- **Rate limiting middleware** — recommended pattern is to put nginx, Caddy, or Traefik in front of this server
- **Production-grade Identity Provider** — drop in your own (Keycloak, Authentik, Auth0, Okta). The template provides the integration surface, not the IdP itself.

## How to contribute

If you'd like to ship one of the future directions: open an issue first to discuss the approach, then submit a PR linked to the issue. See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Versioning policy (frozen v1.0.0)

This is the stable reference release. Future major versions, if any, would follow SemVer with documented breaking changes and migration guides.
