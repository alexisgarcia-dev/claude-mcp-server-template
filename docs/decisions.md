# PantryMCP — Decisions Log (ADR-light)

> One-line ADRs. For full rationale, see docs/design-v0.1.0.md cross-references.

## ADR-001 — Hybrid Pattern B: One-File-Per-Tool + Shared Client Middleware
**Date**: 2026-05-06 (J12 PM brainstorm)
**Status**: Locked v0.1.0
**Context**: Choose project layout for 6 primitives. Options: Flat Registry, Config-Driven Auto-Discovery, Hybrid B.
**Decision**: Hybrid B. Each primitive has its own file. Shared client (`pantry_client.py`) centralizes auth/retry/error mapping.
**Consequences**: Buyer can copy individual primitive files. Shared middleware = production differentiator vs Fiverr templates.
**See**: design-v0.1.0.md §1

## ADR-002 — Pydantic-settings Pattern C (Hierarchical Override)
**Date**: 2026-05-06
**Status**: Locked
**Decision**: Priority order ENV > .env > config.toml > Docker secrets > defaults. Use BaseSettings with explicit `settings_customise_sources` override.
**Consequences**: 12-factor compliant. Docker secrets free upgrade for production buyers.
**See**: design-v0.1.0.md §2

## ADR-003 — tenacity for async retry, not httpx native
**Date**: 2026-05-07 (J13 AM brainstorm)
**Status**: Locked
**Context**: httpx 0.28 AsyncHTTPTransport(retries=N) only retries on ConnectError, not 429/5xx (verified docs).
**Decision**: tenacity AsyncRetrying with wait_random_exponential (jitter anti-thundering-herd).
**Consequences**: +50KB dependency. 2026 standard async retry. Replaces ~100 lines custom buggy retry.
**See**: design-v0.1.0.md §3

## ADR-004 — Native FastMCP Tasks primitive (task=True), not custom backend
**Date**: 2026-05-06
**Status**: Locked v0.1.0
**Decision**: `@mcp.tool(task=True)` with FastMCP 3.0+ in-process pydocket worker. Zero infra externe.
**Consequences**: Native demonstration of Tasks spec 2025-11-25. Caveat: Claude Desktop client-side consumption non vérifié end-to-end.
**See**: design-v0.1.0.md §4 (Tool #4)

## ADR-005 — Hybrid OpenTelemetry (auto + manual spans pédagogiques)
**Date**: 2026-05-06
**Status**: Locked
**Decision**: Auto-instrumentation httpx + manual spans on Tool #2 (search_recipes) pédagogique + Tool #4 (generate_meal_plan) différenciateur. OTLP HTTP exporter (port 4318), Jaeger 1.62 pinned.
**Consequences**: Production observability out-of-box. Tier $2400 differentiator.
**See**: design-v0.1.0.md §6 + Section 4 Tool #2/#4

## ADR-006 — Test Strategy Hybrid C (Unit MockTransport + Integration native MCP utilities)
**Date**: 2026-05-06
**Status**: Locked
**Decision**: tests/unit/ httpx.MockTransport (6 files). tests/integration/ memory transport + http transport + tasks smoke. Coverage 70% per-file floor on src/tools/, src/resources/, src/prompts/.
**Consequences**: pytest_asyncio.fixture mandatory in strict mode. .coveragerc per-file enforcement.
**See**: design-v0.1.0.md §10

## ADR-007 — Hard stop J15 EOD, never cut Tool #4
**Date**: 2026-05-06
**Status**: Locked
**Decision**: Cut sequence if pressure: Prompt #6 → Resource #5 → never Tool #4 (the differentiator).
**Consequences**: README v0.1.1 transparent disclosure if any cut. v0.1.1 ETA "within 2 weeks".
**See**: design-v0.1.0.md §7

## ADR-008 — Pricing humble first project ($400/$900/$2400)
**Date**: 2026-05-07
**Status**: Locked v0.1.0 → revisit J90+ post-reviews
**Context**: First MCP project, zero accumulated reviews. Premium pricing without social proof = 0 buyers.
**Decision**: $400 Starter / $900 Standard / $2400 Advanced. Aligned market median (Talib reference $350/$500/$2500).
**Consequences**: Strategic priority J0-J60 = review accumulation, not revenue maximization. 5 Standard sales = 5 reviews + Top Rated qualifying trajectory J90+.
**See**: design-v0.1.0.md §1

## ADR-009 — Honest OAuth scope v0.1.0 (API key only, OAuth stub for v0.2.0)
**Date**: 2026-05-07
**Status**: Locked
**Decision**: API key auth only v0.1.0. ClientCredentialsProvider stub raises clearly. oauth.enabled=true validated AT BOOT (not at runtime).
**Consequences**: Buyer Segment B audit reads honest scope = trust+. v0.2.0 upgrade path documented.
**See**: design-v0.1.0.md §5

## ADR-010 — DNS rebinding mitigation via FastMCP host="127.0.0.1" default
**Date**: 2026-05-07
**Status**: Locked
**Context**: MCP spec 2025-11-25 MUST validate Origin. CVE-2025-49596 (RCE 9.4) + CVE-2025-66416 (Python SDK default).
**Decision**: Bind 127.0.0.1 default. FastMCP auto-activates DNS rebinding protection. README documents 0.0.0.0 production behind reverse proxy pattern.
**Consequences**: OWASP-baseline compliance. Differentiator vs 95% MCP templates 2026.
**See**: design-v0.1.0.md §5
