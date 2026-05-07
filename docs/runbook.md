# PantryMCP — Bug-Fix Runbook

> Triage by symptom. 3-5 min lookup. If insufficient, escalate to design-v0.1.0.md cross-reference.

## Server won't start

### Symptom: ImportError on BaseSettings
**Cause**: `from pydantic import BaseSettings` (Pydantic v1 path)
**Fix**: `from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource`
**See**: design §2, ADR-002

### Symptom: ImportError on TomlConfigSettingsSource
**Cause**: pydantic-settings <2.0 OR Python <3.11 (tomllib stdlib required)
**Fix**: `uv add 'pydantic-settings>=2.0'` + verify Python 3.11+
**See**: design §2 pre-flight smoke test

### Symptom: Server starts but config.toml ignored
**Cause**: `settings_customise_sources` override missing
**Fix**: Add classmethod returning `(init_settings, env_settings, dotenv_settings, TomlConfigSettingsSource(settings_cls), file_secret_settings)`
**See**: design §2 fix 2

### Symptom: Server starts but ENV vars not overriding nested config
**Cause**: Single underscore in ENV var name
**Fix**: Double underscore for nested: `PANTRY_API__API_KEY` not `PANTRY_API_API_KEY`
**See**: design §2 fix 3

### Symptom: ValueError "api.api_key is required"
**Cause**: Production mode without api_key set
**Fix**: Set `PANTRY_API__API_KEY` in .env OR set `dev_mode=true` in config.toml (LOCAL ONLY)
**See**: design §5

### Symptom: ValueError "oauth.enabled=true is configured but v0.1.0 ships API key only"
**Cause**: Buyer enabled OAuth prematurely
**Fix**: Set `oauth.enabled=false` in config.toml until v0.2.0
**See**: ADR-009

## Tools fail with errors

### Symptom: 404 FileNotFoundError on get_recipe
**Cause**: Resource doesn't exist (by design, agent-actionable error)
**Fix**: Verify recipe_id is correct, use search_recipes first
**See**: error_messages.py RESOURCE_NOT_FOUND

### Symptom: 401/403 PermissionError on all tools
**Cause**: API key invalid or revoked
**Fix**: Verify PANTRY_API__API_KEY in .env, check API dashboard
**See**: error_messages.py AUTH_EXPIRED

### Symptom: 5xx errors after 3 retries
**Cause**: Upstream PantryAPI down or intermittent
**Fix**: Check pantry-api healthcheck status, verify upstream service
**See**: design §3 tenacity retry config

### Symptom: 429 rate limit, retries exhausted
**Cause**: Exponential backoff insufficient for upstream rate limit
**Fix**: v0.1.1 will add Retry-After header parsing. Workaround: increase max_retries in config.toml
**See**: ADR-003 + v0.1.1 roadmap

### Symptom: Tool parameter validation fails with cryptic message
**Cause**: Field constraint syntax wrong (using Field as default instead of Annotated)
**Fix**: `param: Annotated[int, Field(ge=1, le=100)] = 20` not `param: int = Field(default=20, ge=1, le=100)`
**See**: design §4 BLOCKING fix 2

### Symptom: Bulk update payload rejected with 422
**Cause**: Enum serialization leaks instance instead of string
**Fix**: `model_dump(mode="json")` not `model_dump()`
**See**: design §4 BLOCKING fix 3

## Resource and Prompt issues

### Symptom: Resource doesn't render markdown in Claude Desktop
**Cause**: mime_type missing in resource registration
**Fix**: `@mcp.resource(uri, mime_type="text/markdown")`
**See**: design §4 refinement 5

### Symptom: PromptMessage ValidationError "role must be user or assistant"
**Cause**: Used `role="system"` (rejected by mcp 1.27)
**Fix**: Pack system context in first user message
**See**: design §4 refinement 6 + sources.md mcp 1.27 verification

## Telemetry and observability

### Symptom: Spans appear in Jaeger with status UNSET
**Cause**: Validation raises inside span scope
**Fix**: Move validation BEFORE `with tracer.start_as_current_span()`
**See**: design §4 refinement 7

### Symptom: Authorization header visible in Jaeger UI
**Cause**: OTel httpx auto-instrumentation captures headers
**Fix**: Verify _mask_sensitive_headers_request hook registered in setup_telemetry
**See**: design §5 Blocking Fix 2

### Symptom: Tasks primitive doesn't report progress
**Cause**: ctx parameter missing or not passed
**Fix**: Add `ctx: Context | None = None` to tool signature, call `await ctx.report_progress(...)`
**See**: design §4 refinement 8

## Security incidents

### Symptom: Suspicious request from unknown origin to MCP server
**Cause**: Possible DNS rebinding attempt OR misconfigured client
**Action**: 
1. Verify FastMCP host="127.0.0.1" (default since CVE-2025-66416 fix)
2. If 0.0.0.0 binding: configure TransportSecuritySettings allowed_hosts
3. Review server logs for Origin header anomalies
**See**: ADR-010 + CVE-2025-66416 sources.md

### Symptom: Secret leaked in logs/traces
**Cause**: SecretStr field used as plain str OR get_secret_value() called and logged
**Fix**: 
1. Audit code for `.get_secret_value()` usage in logged contexts
2. Verify SecretStr fields on api_key, client_secret in config.py
3. Verify OTel httpx masking hooks active
**See**: design §5 Blocking Fix 2

### Symptom: dev_mode=true in production
**Action**: Loud warning should appear at startup. If missed, immediate fix:
1. Set `dev_mode=false` in config.toml
2. Set `PANTRY_API__API_KEY` env var
3. Restart server
**See**: design §5 refinement 4

## Docker / Deployment

### Symptom: Docker compose up fails with healthcheck timeout
**Cause**: Healthcheck uses curl which isn't in Python slim image
**Fix**: Use Python httpx healthcheck pattern
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8001/health', timeout=3.0).raise_for_status()"]
  start_period: 30s
```
**See**: design §6 fix A

### Symptom: mcp service starts before pantry-api ready
**Cause**: depends_on without condition: service_healthy
**Fix**: Verify `depends_on: pantry-api: condition: service_healthy` in docker-compose.yml
**See**: design §6

### Symptom: Jaeger UI not accessible at http://localhost:16686
**Cause**: Port mapping or service not started
**Fix**: 
1. `docker-compose ps` verify jaeger service up
2. Check port mapping: `127.0.0.1:16686:16686`
3. Verify `COLLECTOR_OTLP_ENABLED=true` env var set
**See**: design §6

## Testing failures

### Symptom: pytest fails with "async fixture must use pytest_asyncio.fixture"
**Cause**: pytest_asyncio strict mode + @pytest.fixture on async fixture
**Fix**: `@pytest_asyncio.fixture` not `@pytest.fixture`
**See**: design §10 testing strategy

### Symptom: Coverage <70% on src/tools/
**Cause**: Per-file floor enforcement
**Fix**: Add unit tests for uncovered branches OR justify exclusion in .coveragerc
**See**: design §10

### Symptom: test_http_transport.py fails connection
**Cause**: Server not started OR port conflict
**Fix**: Use fastmcp.utilities.tests.run_server_async fixture (handles ephemeral port)
**See**: design §10

## Pre-flight (J13 9h05) failures

### Symptom: uv add fastmcp[tasks] fails — extras not available
**Action**: Pivot fallback. Use `fastmcp>=3.0` without [tasks] extras + manual pydocket integration. Document workaround in design doc + revisit v0.1.1.
**See**: design §7 red flag 1

### Symptom: Smoke test imports fail Python version check
**Action**: Verify Python 3.11+ active. uv venv with explicit `--python 3.14`.
**See**: design §7 pre-flight

## Quick reference paths

- **Architecture**: design-v0.1.0.md §1
- **Config**: design-v0.1.0.md §2 + config.py + config.toml + .env.example
- **HTTP retry**: design-v0.1.0.md §3 + pantry_client.py + tenacity docs
- **Primitives**: design-v0.1.0.md §4 + src/tools/* + src/resources/* + src/prompts/*
- **Security**: design-v0.1.0.md §5 + auth/oauth_middleware.py + .gitignore
- **Deployment**: design-v0.1.0.md §6 + docker-compose.yml + Dockerfile
- **Sprint history**: design-v0.1.0.md §7 + STATE.md
- **All ADRs**: docs/decisions.md
- **All sources**: docs/sources.md (re-verify if older than 30 days)
