# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-05-10

**Stable reference release. Frozen-by-design.** Maintenance community-driven from this point forward — see [ROADMAP.md](./ROADMAP.md) Future directions.

### Added

- `SECURITY.md` — vulnerability disclosure policy + GitHub Security Advisory pointer
- `CONTRIBUTING.md` — conventional commits + DCO + uv-based dev setup
- `.dockerignore` — Python + IDE + secrets + .github + .claude exclusions
- `.env.example` — sample env vars (MCP_TRANSPORT/HOST/PORT, PANTRY_*, OTEL_*, LOG_LEVEL)
- `.github/workflows/ci.yml` — uv matrix Python 3.11/3.12/3.13 + ruff lint + format check + pytest
- `.github/workflows/codeql.yml` — Python security scanning weekly Monday
- `.github/workflows/bandit.yml` — Python static analysis weekly Wednesday + SARIF upload Security tab
- `.github/dependabot.yml` — pip + github-actions + docker weekly security updates
- `.github/PULL_REQUEST_TEMPLATE.md` — structured PR template
- `.pre-commit-config.yaml` — ruff 0.15.12 + bandit 1.7.10 + check-yaml + detect-private-key + trailing-whitespace + end-of-file-fixer
- `docs/images/jaeger-ui.png` — screenshot from Layer 4 e2e validation (post-push)
- Container hardening: `security_opt: no-new-privileges:true` + `cap_drop: ALL` on `mcp-server` and `pantry-mock` services in `docker-compose.yml`
- Native `HEALTHCHECK` directives in `Dockerfile` and `Dockerfile.pantry-mock`
- Defensive entries in `.gitignore` (`*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.crt`, `*.cer`, `id_rsa*`, `id_ed25519*`, `.aws/`, `.kube/config`, `.npmrc`, `.netrc`)

### Changed

- Bump version `0.1.0` → `1.0.0` (SemVer first stable public API release)
- `pyproject.toml` description updated from placeholder to factual neutral
- `pyproject.toml` `[dependency-groups] dev` now includes `pytest-cov >= 7.1.0`
- `pyproject.toml` `[tool.pytest.ini_options]` now includes `addopts = ["--cov=src", "--cov-report=xml", "--cov-report=term"]`
- `ROADMAP.md` repositioned community-driven (sections "Stable as-is" / "Future directions, contributions welcome" / "Out of scope by design"), removed dated personal commitments
- `README.md` hero block: badges enriched (CI + CodeQL + Python matrix), Jaeger UI screenshot inserted, Pillar wording made honest about healthcheck scope (no longer claims upstream API validation), Authentication section gained alarm-level warning about demo tokens
- Healthcheck `start_period` bumped from 30s to 45s in `docker-compose.yml` to mitigate Jaeger 1.62 cold-start race
- `pantry_mock_api.py` mock contract aligned with tool expectations: 3 seed recipes now include required `instructions` field, GET /recipes returns SearchResult-shaped response, POST /pantry/bulk endpoint matches update_pantry.py contract with success/failures envelope, defensive name/quantity validation per-item
- `healthcheck.py` logic now correctly returns exit 1 on JSON-RPC error responses (previously masked as success), docstring made honest about scope (validates auth + transport + tool registration, not upstream connectivity)
- `CLAUDE.md` version reference updated `v0.1.0` → `v1.0.0`

### Removed

- Obsolete `POST /pantry` endpoint in `pantry_mock_api.py` (unused, replaced by `POST /pantry/bulk`)

### Security

- Container hardening per OWASP Container Security 2026 guidance (services applicatifs only, jaeger keeps default capabilities for OTLP receiver)
- CodeQL Python scanning enabled (weekly + on PR)
- Bandit static analysis enabled with SARIF upload to GitHub Security tab
- Dependabot security updates enabled for pip, github-actions, docker

### Tests

- 58 tests passing (unit + deselected integration). Test:code ratio 1.46.

### Notes

- Per-tool scope enforcement (e.g., gating `update_pantry` behind `write:pantry`) is not implemented in v1.0.0 — both demo tokens carry `read:pantry`. See ROADMAP.md "Future directions / Per-tool scope guards".
- Healthcheck does not validate upstream PantryAPI connectivity in v1.0.0 — `tools/list` is served from in-process registry. See ROADMAP.md Future directions.

## [0.1.0] - 2026-05-09

Production-survival foundation. Initial release.

### Added

- 4 demo Tools: `get_recipe`, `search_recipes`, `update_pantry`, `generate_meal_plan` (async with progress notifications via FastMCP `task=True`)
- 1 demo Resource: `recipe_resource` (URI scheme `recipe://{recipe_id}`, MIME type `application/json`)
- 1 demo Prompt: `weekly_planner` (role-restricted per MCP 1.27 schema, packs system context in first user message)
- Streamable HTTP transport support via `MCP_TRANSPORT=streamable-http` env var (mandatory for remote deployment per MCP 2026 spec)
- OpenTelemetry observability pipeline: custom OTLP HTTP exporter + auto-instrumentation httpx + manual pedagogical spans on Tool #2 (`search_recipes`) and Tool #4 (`generate_meal_plan`)
- Docker compose 3-service demo stack: `pantry-mock` (FastAPI seed) + `mcp-server` + `jaeger:1.62` (pinned per ADR-005)
- Production-realistic healthcheck: `healthcheck.py` httpx-based MCP `tools/list` JSON-RPC validation (no `curl` dependency)
- Hierarchical configuration (Pydantic-settings Pattern C): `ENV > .env > config.toml > Docker secrets > defaults`
- Pinned dependencies via `uv.lock` (committed for reproducibility)
- 58 tests passing (unit `httpx.MockTransport` + integration tests behind `integration` marker, deselected by default)
- 10 ADR-light decisions in `docs/decisions.md` covering architecture, retry strategy, OAuth scope, DNS rebinding mitigation
- `pantry_mock_api.py` standalone FastAPI mock with 3 seed recipes (Italian, Asian, Greek cuisines) for plug-and-play self-validation

### Security

- DNS rebinding mitigation: FastMCP `host=127.0.0.1` default activates protection (CVE-2025-66416 fix per `docs/sources.md`). Docker `0.0.0.0` documented as production-behind-proxy pattern only (ADR-010).
- Bearer token authentication via `StaticTokenVerifier` with 2 demo tokens: `demo-readonly` (`read:pantry` scope) and `demo-readwrite` (`read:pantry` + `write:pantry` scopes)
- `SecretStr` for all credentials (Pydantic-settings) — no leak in `__repr__` or logs
- OpenTelemetry header masking hooks (request_hook + response_hook) prevent `Authorization` / `Cookie` leaks in spans
- API key stored in `.env` (gitignored), structure-only in `config.toml` (committed)
- `dev_mode=true` triggers explicit stderr warning at boot
- `oauth.enabled=true` raises clearly at boot (v0.1.0 ships API key + `StaticTokenVerifier` only; OAuth 2.1 lands in v0.2.0)

### Documentation

- README with quickstart, architecture overview, and customization guide
- ROADMAP through v0.5.0 (versioned feature plan tied to MCP spec evolution)
- `docs/design-v0.1.0.md` full architecture rationale
- `docs/runbook.md` bug-fix triage by symptom
- `docs/sources.md` verified sources with dates (re-verify after 30 days)
- `CLAUDE.md` navigation map for AI-augmented contributors
- `.github/ISSUE_TEMPLATE/` bug report and feature request forms

### Known Limitations (v0.2.0+ targets)

- OAuth 2.1 + PKCE flow currently absent (`StaticTokenVerifier` is preview/dev only — internet-exposed deployments should wait for v0.2.0; cf ADR-009)
- Full SEP-1686 Tasks primitive RPC compliance not implemented (currently uses FastMCP `task=True` framework abstraction; `tasks/get`, `tasks/result`, `tasks/list`, `tasks/cancel`, `notifications/tasks/status` ship in v0.3.0; cf ADR-012)

[Unreleased]: https://github.com/alexisgarcia-dev/claude-mcp-server-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/alexisgarcia-dev/claude-mcp-server-template/releases/tag/v1.0.0
[0.1.0]: https://github.com/alexisgarcia-dev/claude-mcp-server-template/releases/tag/v0.1.0
