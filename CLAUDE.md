# claude-mcp-server-template

> Plug-and-play REST API → MCP wrapper template. v0.1.0 ships with PantryAPI mock demo.

## What is this project?

Production-grade MCP server template demonstrating 6 primitives (4 Tools + 1 Resource + 1 Prompt) wrapping a REST API. Buyers copy patterns for their own API → MCP integration. Sold on Upwork: $400 Starter / $900 Standard / $2400 Advanced (humble first project pricing, J0-J60 review accumulation phase).

## Navigation map (Claude reading priority)

For any task on this repo, read in this order:

1. **`CLAUDE.md`** (this file) — Navigation + quick commands
2. **`docs/runbook.md`** — Bug-fix triage by symptom (3-5 min lookup)
3. **`docs/decisions.md`** — 10 ADR-light decisions (5 min lookup)
4. **`docs/design-v0.1.0.md`** — Full architecture decisions + 30+ technical fixes (deep reference)
5. **`docs/sources.md`** — Sources verified with dates (re-verify if older than 30 days)

## Quick commands

```bash
# Install dependencies (uv-managed)
uv sync

# Pre-flight verification (run after fresh clone)
uv run python -c "
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource
from fastmcp import Context
from tenacity import AsyncRetrying
import sys
assert sys.version_info >= (3, 11), 'Python 3.11+ required'
print('Pre-flight OK')
"

# Run tests
uv run pytest

# Coverage with per-file floor enforcement
uv run pytest --cov=src --cov-fail-under=70

# Linting
uv run ruff check src tests
uv run mypy src

# Run MCP server (stdio transport, default)
uv run server

# Run full demo stack (3 services: PantryAPI mock + MCP + Jaeger)
docker-compose up

# Open Jaeger UI
# http://localhost:16686
```

## Project structure

```
claude-mcp-server-template/
├── CLAUDE.md                       # This file (navigation map)
├── README.md                       # Buyer-facing setup + quickstart
├── pyproject.toml                  # uv-managed dependencies
├── docker-compose.yml              # 3-service demo stack
├── Dockerfile                      # MCP server container
├── Dockerfile.pantry-mock          # FastAPI mock container
├── config.toml                     # Committed structure (no secrets)
├── .env.example                    # Committed template (no real values)
├── .env                            # Gitignored (real secrets)
├── .gitignore                      # Explicit security entries
├── src/
│   ├── server.py                   # FastMCP instance + lifespan + register primitives
│   ├── config.py                   # Pydantic-settings Pattern C
│   ├── pantry_client.py            # Shared HTTP client + tenacity retry
│   ├── error_messages.py           # Agent-friendly error templates
│   ├── models.py                   # Shared Pydantic models (Recipe, etc.)
│   ├── telemetry.py                # OTel setup + masking hooks
│   ├── tools/                      # 4 Tools (one file each + register fn)
│   ├── resources/                  # 1 Resource
│   ├── prompts/                    # 1 Prompt
│   └── auth/                       # OAuth stub for v0.2.0
├── tests/
│   ├── unit/                       # httpx.MockTransport per primitive
│   └── integration/                # memory + http transport + tasks
├── docs/
│   ├── design-v0.1.0.md            # Full architecture decisions
│   ├── decisions.md                # ADR-light log
│   ├── runbook.md                  # Bug-fix triage
│   └── sources.md                  # Verified sources
└── .claude/
    ├── Constitution.md             # 8 hard rules for Claude Code
    └── (commands/, agents/ — added post-J14 if needed)
```

## Key technical decisions (TL;DR)

- **Architecture**: Hybrid Pattern B (one-file-per-tool + shared client middleware)
- **Config**: Pydantic-settings Pattern C, hierarchical priority (ENV > .env > config.toml > defaults)
- **HTTP retry**: tenacity AsyncRetrying (not httpx native — verified insufficient)
- **Tasks primitive**: Native FastMCP `@mcp.tool(task=True)`, in-process pydocket worker
- **Observability**: OpenTelemetry hybrid (auto httpx + manual pédagogique spans Tool #2/#4)
- **Security**: API key v0.1.0, OAuth stub v0.2.0. DNS rebinding mitigated via host="127.0.0.1" default. SecretStr Pydantic + OTel header masking.
- **Testing**: Hybrid C — unit MockTransport + integration native MCP utilities. 70% per-file floor coverage.

## Sprint timeline (v0.1.0 ship)

- J13 jeudi 07/05/2026: Config + HTTP client + Tool #1 (5h)
- J14 vendredi 08/05/2026: Tools #2 + #3 + #4 + Security batch (6h)
- J15 samedi 09/05/2026: Resource + Prompt + OTel + Tests + Docker + README + e2e validation + ship (6h+1h buffer)

## v0.1.1 roadmap

- Retry-After header parsing (RFC 6585)
- OAuth client_credentials full implementation
- OpenAPI auto-generation script (REST API → MCP scaffold)
- MCP sampling middleware
- Multi-tenant token isolation
- Jaeger 1.76 upgrade
- Tool #3 partial failure return-with-warning pattern (revisit raise vs return based on buyer feedback)

## Pre-flight checklist (any new session)

1. `cd C:\Users\Utilisateur\freelance\claude-mcp-server-template`
2. Read this CLAUDE.md (you're here)
3. Read `docs/runbook.md` if fixing a bug
4. Read `docs/design-v0.1.0.md` §X for specific subsystem deep dive
5. Verify pre-flight passes (see Quick commands above)
6. `git status` — verify clean working tree before changes

## Reading order priority for bug fixes

bug → `docs/runbook.md` (find symptom)  
→ if pointer to design § → `docs/design-v0.1.0.md` (deep context)  
→ if needs source verification → `docs/sources.md` (re-verify if old)  
→ if architectural question → `docs/decisions.md` (ADR rationale)
