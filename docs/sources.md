# PantryMCP — Sources Verified

> Sources used during brainstorm with verification dates. Re-verify if used after 30 days.

## MCP Protocol Specification
- **modelcontextprotocol.io/specification/2025-11-25** (verified 2026-05-07)
  - Streamable HTTP Origin header MUST validate
  - Localhost binding 127.0.0.1 SHOULD default
  - Auth required for exposed endpoints

## CVE Database
- **CVE-2025-49596** (CVSS 9.4 Critical, June 2025)
  - Anthropic MCP Inspector RCE via DNS rebinding
  - Fix: Inspector v0.14.1 + allowed origins verification
  - URL: oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596

- **CVE-2025-66416** (December 2025)
  - Python MCP SDK no DNS rebinding protection by default
  - Fix: FastMCP() with host="127.0.0.1" or "localhost" auto-activates protection
  - URL: advisories.gitlab.com/pkg/pypi/mcp/CVE-2025-66416/

## Pydantic v2 / Pydantic-settings
- **pydantic-settings issue #259** — TomlConfigSettingsSource needs explicit registration via settings_customise_sources
- **pydantic-settings issue #413** — toml_file path override pattern
- **Settings Management official docs** — env_nested_delimiter required for nested model overrides
- **Verified runtime 2026-05-07**: model_dump() default leaks Enum instance, mode='json' returns plain string

## FastMCP 3.2.4 Installed Package Introspection (2026-05-07)
- `Context.report_progress(progress: float, total: float|None, message: str|None)` — exists, async, works in foreground (MCP progress notifications) and background (Docket task) contexts
- Native `@mcp.tool(task=True)` available, in-process pydocket worker
- DNS rebinding protection auto-active when host=127.0.0.1 or localhost (CVE-2025-66416 fix)
- TransportSecuritySettings explicit configuration required for 0.0.0.0 binding

## mcp 1.27 Schema Verification (2026-05-07)
- `PromptMessage.role` enum: `["user", "assistant"]` ONLY
- `role="system"` raises ValidationError at runtime
- Pattern: pack system context in first user message

## httpx Retry Behavior (verified docs 2026)
- `AsyncHTTPTransport(retries=N)` retries ONLY on `httpx.ConnectError` (TCP-level)
- Does NOT retry on 429, 5xx, ReadTimeout, HTTPStatusError
- httpx team explicitly declined to add status-code retry (issue tracked since 2023)
- 2026 standard for status-code retry: tenacity 9.0+ (100M+ downloads/month)

## OpenTelemetry Python
- `opentelemetry-exporter-otlp-proto-http>=1.20.0` — HTTP exporter (firewall-friendly vs gRPC)
- Jaeger 1.62+ accepts both gRPC and HTTP via COLLECTOR_OTLP_ENABLED=true
- `opentelemetry-instrumentation-httpx>=0.50b0` — auto-instrumentation with header masking hooks (request_hook, response_hook)
- `TraceIdRatioBased(sampling_ratio)` — production sampling, default 1.0 dev / 0.1 prod

## Upwork Freelance Strategy 2026
- Talib MCP template reference pricing: $350 / $500 / $2500
- Top Rated qualifying: 16 weeks JSS visible
- Direct Contracts target 5% fee (Freelancer Plus subscription, P2+ evaluation)
- Anti-AI marker checklist for proposals: no em dash, no "It's not just X it's Y", no "delve/harness/unleash/tapestry/leverage/In today's"

## Last Verification Pass
- Date: 2026-05-07 (J13 AM)
- Method: live introspection via claude-code-mcp + web_search
- Re-verify if used after: 2026-06-07
