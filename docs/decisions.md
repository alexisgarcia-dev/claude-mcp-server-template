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

---

## ADR-011 — Strategic pivot: prospection volume → differentiating asset (J11–J12)

**Date** : 2026-05-05 (J11) → 2026-05-06 (J12)
**Status** : Accepted
**Type** : Strategic (not technical)

### Context

Phase P1 freelance Upwork started J0 (2026-04-24). Cohort J0–J8: 10 proposals sent, 1 viewed, 0 interviews, 0 hires. L99 debrief J8 (v3.2) decomposed root causes:

- Discipline pré-tri off-criteria: 25–45% (median 35%)
- Timing outside 15–60 min sweet spot: 15–35% (median 25%)
- 0-review structural barrier: 15–25% (median 20%) — non-repairable J9–J18
- Style AI-flag residual: 5–15% (median 12%)

The 0-review barrier (median 20%) is the only factor non-addressable by behavioral changes within J9–J18 timeframe. It requires a differentiating proof artifact.

### Decision

Pivot from "prospection volume + grille triage 5/5 + alertes timing" to "build differentiating MCP server template asset, ship as Upwork Project Catalog + dev.to article + repo public, use as proof in cover letters."

Formal Upwork bid-ratio checkpoint J13 (originally 2026-05-07) **deliberately deferred** to allow asset construction priority.

### Consequences

**Positive:**
- Compensates 0-review structural barrier (median 20% obstacle) with technical proof artifact
- Reusable across multiple cover letters (single asset, multiple opportunities)
- Reduces dependency on Upwork algorithm Best Match ranking (anti-fragile)
- Creates ROADMAP-versioned IP that scales beyond Upwork (Gumroad bolt-on J60+)

**Negative:**
- Defers first € target window (J10–J18 cible MIN, P50)
- Risks compounding "no revenue" pressure if asset doesn't yield contracts by J30
- Ship deadline self-imposed = stress factor

**Neutral:**
- Skill investment carries forward regardless of asset commercial outcome

### Revalidation criteria — J20 (2026-05-19, Tuesday)

Five bids minimum sent post-ship using asset as proof. Tracked metrics:

- **Interview rate** ≥ 2% (1+ interviews / 5 bids) → asset producing differentiation, continue path
- **Interview rate** < 2% on 10+ bids → asset insufficient, fallback Plan B
- **Bid-ratio drop after asset shipped vs J0–J8 baseline** → asset hurting positioning (overclaim?), fallback Plan C

### Plan B (if J20 inconclusive)

Return to prospection grille v3.2 (FREELANCE_OPERATIONS §4) + Loom proof artifact (60-90 min) + Project Catalog Standard tier listing. Asset becomes background, not primary differentiator.

### Plan C (if J30 still no €)

Reposition entirely or pivot platform (Wellfound after Top Rated qualifying, post-J60+).

### Sources

- L99 debrief J8 v3.2 (Project Files `L99-debrief-J8-axes-amelioration-20260502-v32.md`)
- GigRadar Upwork algorithm 2026, SnipeWork 92-profile experiment
- TIMELINE.md ancrage J0 = 2026-04-24

---

## ADR-012 — Cut "Tasks primitive 2025-11-25" claim from v0.1.0 marketing scope

**Date** : 2026-05-07 (J13) — pre-J15 ship
**Status** : Accepted

### Context

Initial v0.1.0 positioning (per MEMENTO Insight #12, J12 PM) listed 4 differentiators:

1. Resources primitive demonstrated
2. Prompts primitive demonstrated
3. **Tasks primitive 2025-11-25 (cutting edge async, 0% public templates)**
4. PantryAPI fake SaaS end-to-end demo

Pre-sprint J14 verification confirmed `Tool #4 generate_meal_plan` uses `@mcp.tool(task=True)` decorator with `fastmcp.dependencies.Progress` — **the FastMCP framework abstraction**, not SEP-1686 RPC compliance.

SEP-1686 RPC methods absent from codebase: `tasks/get`, `tasks/result`, `tasks/list`, `tasks/cancel`, `notifications/tasks/status`, `CreateTaskResult` response type.

### Decision

Remove "Tasks primitive 2025-11-25 (SEP-1686)" claim from v0.1.0 marketing copy (README, Catalog Upwork, dev.to article, tweet thread).

Reposition the existing implementation as: **"Async tools with progress notifications via FastMCP `task=True`"** — honest, accurate, framework-feature description.

Move "Full SEP-1686 Tasks primitive RPC compliance" to **ROADMAP v0.3.0** (target end June 2026).

### Consequences

**Positive:**
- Marketing claim now defensible against any technical buyer review (cannot be contradicted by `grep` on the codebase)
- Eliminates 2-3h scope expansion risk on J15 sprint (would have required implementing `tasks/*` RPC methods + spec compliance tests)
- Roadmap v0.3.0 becomes credible feature, not a retro-fit

**Negative:**
- Drops from 4 to 3 differentiators in v0.1.0 — must lean harder on "Production-survival foundation" angle (5 pillars) as the primary USP

**Neutral:**
- The implementation `Tool #4 generate_meal_plan` keeps full functionality and demo value, just renamed

### Revised v0.1.0 differentiators (3, not 4)

1. Resources + Prompts primitives demonstrated end-to-end
2. **Production-survival foundation** (5 cohesive pillars: Streamable HTTP + auth + OTel + pinned + healthcheck) vs 1-2 in competing public templates
3. PantryAPI fake SaaS demo for plug-and-play self-validation

### Sources

- MCP spec 2025-11-25 SEP-1686 (`https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks`)
- MCP 2026 roadmap (March 2026): "Tasks primitive shipped as experimental, lifecycle gaps remain"
- gofastmcp.com docs on `Progress` dependency injection (FastMCP `task=True` decorator)
