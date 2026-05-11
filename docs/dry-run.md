# Dry-run mode

**Version:** v1.1.0 (additive, no breaking change)
**Status:** stable
**Scope:** all outbound HTTP issued by `PantryClient`

## What & why

Dry-run mode short-circuits every outbound HTTP request at the client chokepoint
(`PantryClient._request_with_retry`), emits the would-be request as
OpenTelemetry telemetry (with a stdlib-`logging` fallback), and returns a
generic, schema-agnostic mock response. It exists so that buyers can demo,
debug, and record traces of MCP payloads against Claude Desktop / Cursor /
Windsurf **without** standing up the real backend API.

The feature is fully gated by `Settings.api.dry_run` and defaults to `False`.
A deployment that never opts in sees zero behavior change.

**When NOT to use it.** Dry-run is intended for discovery, integration testing,
and pre-sale demonstrations. Do not enable it in production or in any pipeline
that asserts on a *typed* response model from a Tool — the mock dict satisfies
`dict[str, Any]` but does not satisfy a stricter Pydantic schema. See §7.

## Quick start

```bash
# 1. Activate (env var, no config.toml edit required)
export PANTRY_API__DRY_RUN=true

# 2. Run the server as usual
uv run server

# 3. Trigger any Tool from your MCP client (Claude Desktop, Cursor, ...)
#    Inspect the captured request in Jaeger:
#    http://localhost:16686  →  service "pantry-mcp"  →  span "pantry.dry_run"
```

If telemetry is disabled (`PANTRY_TELEMETRY__ENABLED=false`) or no OTLP
endpoint is reachable, the same payload is emitted via the stdlib `logging`
module on the `src.pantry_client` logger at `INFO` level.

## Vertical use cases

The template is sold across five buyer verticals. Below are three concrete
walk-throughs showing how dry-run lets each vertical demo end-to-end without a
backend.

### 1. POD / e-commerce (Printify product create)

A buyer wrapping the Printify `POST /products.json` endpoint wants to demo the
`create_product` Tool to a prospect without exhausting their Printify sandbox
quota.

```bash
export PANTRY_API__DRY_RUN=true
uv run server
```

```python
# MCP client side (Cursor, Claude Desktop, custom Python client)
await client.call_tool(
    "create_product",
    {"title": "Mug — Mountain Sunrise", "blueprint_id": 384, "print_areas": [...]},
)
# → {"_dry_run": True, "_method": "POST", "_path": "/products.json",
#    "_payload_size": 612}
```

The full request — method, path, body preview (first 2048 bytes), scrubbed
headers — is recorded in the `pantry.dry_run` span. The prospect sees the
payload shape and OTel trace; the buyer never touches their Printify token.

### 2. RAG / embeddings (batch embedding submit)

A buyer wrapping an embeddings provider (Voyage, Cohere, OpenAI) needs to test
that the `submit_embeddings` Tool correctly batches 200 chunks of context
without burning real API credits during CI smoke tests.

```bash
export PANTRY_API__DRY_RUN=true
export PANTRY_API__DRY_RUN_PREVIEW_BYTES=4096   # widen preview for batched payloads
uv run pytest tests/integration -m smoke
```

```python
await client.call_tool(
    "submit_embeddings",
    {"model": "voyage-3-large", "input": ["chunk1", "chunk2", ..., "chunk200"]},
)
# → {"_dry_run": True, "_method": "POST", "_path": "/v1/embeddings",
#    "_payload_size": 18741}
```

The CI job asserts on `_payload_size > 0` and inspects the captured
`http.request.body.preview` for the expected batching shape — no provider
call is made.

### 3. Scrapers (URL list submit)

A buyer wrapping a scraping API (ScrapingBee, Apify, Bright Data) wants to
record a sample trace of a 500-URL batch submission to share with a security
reviewer, without paying for the run.

```bash
export PANTRY_API__DRY_RUN=true
uv run server
```

```python
await client.call_tool(
    "submit_scrape_batch",
    {"urls": ["https://example.com/...", ...], "render_js": True},
)
# → {"_dry_run": True, "_method": "POST", "_path": "/v1/scrape/batch",
#    "_payload_size": 24108}
```

The reviewer opens the Jaeger UI, navigates to the `pantry.dry_run` span, and
reads `http.request.body.preview` to verify that no credentials or PII leak
out of the Tool input — all sensitive headers are redacted by default
(see §6).

## Configuration reference

All four fields live on `APIConfig` in `src/config.py`. They are declared with
`extra="forbid"`, so a typo surfaces immediately at startup.

| Field | Type | Default | Env var | Purpose |
|-------|------|---------|---------|---------|
| `dry_run` | `bool` | `False` | `PANTRY_API__DRY_RUN` | Master switch. When `True`, every request through `PantryClient` is short-circuited unless the path matches `dry_run_bypass_paths`. |
| `dry_run_preview_bytes` | `int` | `2048` | `PANTRY_API__DRY_RUN_PREVIEW_BYTES` | Maximum number of UTF-8 bytes of the request body captured in `http.request.body.preview`. Bytes, not characters — matches OTel semconv `http.request.body.size`. |
| `dry_run_bypass_paths` | `str` (regex) | `"^/health\|^/ping"` | `PANTRY_API__DRY_RUN_BYPASS_PATHS` | `re.search`-style regex of request paths that bypass dry-run (i.e. still hit the real backend). Compiled lazily on first use. |
| `dry_run_extra_scrub_headers` | `str` (CSV) | `""` | `PANTRY_API__DRY_RUN_EXTRA_SCRUB_HEADERS` | Additional header names (case-insensitive) to redact, in addition to the hardcoded list. Comma-separated. |

Nested overrides use the double-underscore delimiter declared on `Settings`
(`env_nested_delimiter="__"`). Example:

```bash
PANTRY_API__DRY_RUN=true \
PANTRY_API__DRY_RUN_PREVIEW_BYTES=4096 \
PANTRY_API__DRY_RUN_BYPASS_PATHS="^/health|^/ping|^/metrics" \
PANTRY_API__DRY_RUN_EXTRA_SCRUB_HEADERS="X-Tenant-Token,X-Signature" \
uv run server
```

## Telemetry contract

When dry-run intercepts a request, `PantryClient._emit_dry_run_telemetry`
opens a manual span (the auto-instrumented `httpx.request` span never fires
because no real HTTP is issued) and attaches one event.

| Surface | Name | Notes |
|---------|------|-------|
| Span | `pantry.dry_run` | New span name. Add a Jaeger / Tempo filter if your dashboards group by span name. |
| Span attribute | `mcp.dry_run` = `True` | Custom `mcp.*` namespace, declared in `docs/decisions.md`. |
| Event | `dry_run.request` | Single event per intercepted request. |

The event carries five attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `http.method` | `str` | HTTP verb (`GET`, `POST`, `PUT`, ...). |
| `http.url.path` | `str` | Request path as passed to the client. |
| `http.request.body.size` | `int` | Byte length of the serialized request body. |
| `http.request.body.preview` | `str` | First `dry_run_preview_bytes` of the body, UTF-8 decoded with `errors="replace"`. |
| `http.request.headers.scrubbed` | `str` (JSON) | JSON-encoded dict of the merged client + per-request headers after scrubbing. |

**Fallback.** When the active tracer provider is the default no-op
(`PANTRY_TELEMETRY__ENABLED=false`, no OTLP endpoint reachable, or
`span.is_recording()` returns `False`), the same five attributes are emitted
as an `INFO` record on the `src.pantry_client` logger via the standard library
`logging` module. No third-party dependency (no `structlog`) is required.

**Failure mode.** Telemetry emission is wrapped in `try / except` and downgrades
to a `WARNING` log entry on the same logger. A broken tracer never prevents
the mock response from being returned.

## Security model

Dry-run is designed to be safe to enable on a workstation that has real API
credentials in its environment. Two guarantees:

1. **Hardcoded header scrubbing, non-disablable.** The following headers are
   always redacted to `"<redacted>"` before being attached to the span event
   or the log record. The set is `frozenset` and lives in
   `src/pantry_client.py`:

   ```
   authorization, cookie, set-cookie,
   x-api-key, x-auth-token, proxy-authorization
   ```

   Match is case-insensitive. The header *key* is preserved; only the value
   is replaced. This is intentional — observability tools and security
   reviewers should see that an `Authorization` header was *present*, just
   not what it contained.

2. **Extension via env var.** Buyers wrapping APIs that use non-standard
   authentication header names (`X-Tenant-Token`, `X-Signature`,
   `X-Printify-Hmac`, ...) extend the scrub set without code changes:

   ```bash
   PANTRY_API__DRY_RUN_EXTRA_SCRUB_HEADERS="X-Tenant-Token,X-Signature"
   ```

**Why non-disablable.** This template is sold as a commercial asset. A buyer
shipping a fork that accidentally leaks credentials to Jaeger because they
"turned off scrubbing for debugging" is a foreseeable failure mode. The
hardcoded list cannot be turned off; only extended. Aligns with the existing
`_mask_auth_header` philosophy in `src/telemetry.py`.

**Body preview.** No automatic scrubbing is applied to the body preview. If
your request bodies carry secrets (e.g. an OAuth `client_secret` in a token
request), either disable dry-run for those paths via `dry_run_bypass_paths`,
or set `dry_run_preview_bytes=0` to suppress the preview entirely.

## Limitations & roadmap

**Generic mock shape.** The returned dict has the shape
`{"_dry_run": True, "_method": str, "_path": str, "_payload_size": int}`.
This satisfies `dict[str, Any]` but does not satisfy a strict Pydantic
response model. If your Tool validates its return against a typed model,
either:

- Accept the breakage and document dry-run as "demo-only" for that Tool, or
- Wait for the v1.2.0 per-tool typed override extension point (see below).

**No replay.** Captured payloads are emitted as telemetry; they are not
persisted to disk by the template. Export from Jaeger / Tempo / Honeycomb
or pipe stdout to a file if you need durable capture.

**No recording-to-disk.** Same reasoning: out of scope for the chokepoint
implementation. A recipe using a stdout `logging.FileHandler` is one
possible workaround.

**HTTP method coverage.** `PantryClient` exposes `get`, `post`, and `put` in
v1.1.0. New verbs (`delete`, `patch`) are covered automatically the moment
they land — the dry-run branch lives in `_request_with_retry`, which is the
single chokepoint for all verbs.

**v1.2.0 — per-tool typed override.** A registration hook on `PantryClient`
will let a buyer plug a per-path mock factory:

```python
# v1.2.0 sketch — not yet shipped
client.register_dry_run_mock(
    method="POST",
    path_regex=r"^/products\.json$",
    factory=lambda req: PrintifyProductResponse(id="mock-123", title=req["title"]),
)
```

Until then, buyers needing a typed mock can subclass `PantryClient` and
override `_request_with_retry` — the dry-run branch is intentionally small
and copy-friendly.

## See also

- `docs/runbook.md` → "Dry-run troubleshooting" — symptom → cause → fix
- `docs/decisions.md` → ADR for the chokepoint placement
- `.superpowers/specs/2026-05-11-dry-run-mode-design.md` — full design rationale
- `src/pantry_client.py` — implementation
- `tests/unit/test_dry_run.py` — T1–T4 unit tests
