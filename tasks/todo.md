# tasks/todo.md -- Sprint J13 jeudi 07/05/2026

> Source de verite du sprint en cours. Mis a jour par Claude Code a chaque transition de bloc.
> Audit final J13 18h via /sprint:check.

## Session goal

Implement config.py + pantry_client.py + pantry_mock_api.py + Tool #1 get_recipe avec tests, EOD J13 18h.

## Sprint plan J13 14h-18h

- [x] **14h-15h** src/config.py (Pydantic-settings Pattern C hierarchical)
- [x] **15h-16h45** src/pantry_client.py (tenacity AsyncRetrying + lazy singleton) + src/error_messages.py
- [x] **16h45-17h** pantry_mock_api.py (FastAPI seed for testing, port 8001)
- [x] **17h-18h** src/tools/get_recipe.py (Tool #1) + tests/unit/test_get_recipe.py + tests/integration/test_get_recipe_e2e.py

## Mid-session checkpoints

- [ ] **16h00** /sprint:check -- scope drift check vs design doc
- [ ] **18h00** /sprint:check -- EOD verdict + cut-decision.py output

## EOD criteria J13 (must be true at 18h)

- [x] src/config.py implemente + tested (8 unit tests)
- [x] src/pantry_client.py implemente + tested (9 unit tests)
- [x] pantry_mock_api.py running localement on :8001 (curl http://localhost:8001/recipes/1 returns 200)
- [x] src/tools/get_recipe.py registered + tested (3 unit + 2 integration tests)
- [x] uv run pytest -q exit 0 (23 passed, 2 integration deselected)
- [x] 4 commits atomic minimum via .\sprint.ps1 commit (4 commits total)
- [x] Section "Lessons learned" mise a jour

## Lessons learned J13 (auto-update au cours de la session)

> Format: [HH:MM] | friction | regle/decision

[14:25] | Pydantic HttpUrl adds trailing slash | Use str(url) in tests, expect "http://localhost:8001/"
[14:30] | mypy rejects HttpUrl = "string" default | Use type: ignore[assignment] comment for Pydantic coercion
[15:35] | httpx.MockTransport needs base_url | Always pass base_url=client.base_url when creating mock client
[15:45] | Error mapping returned original for 5xx | Always map to stdlib exception after retries exhausted (simplified logic)
[16:55] | FastMCP() no longer accepts host/port | host/port moved to run() method, not constructor (FastMCP 3.2.4)
[17:10] | Circular import server <-> tools | Import get_pantry_client inside function, not at module level
[17:25] | monkeypatch needs correct target | Patch "src.server.get_pantry_client", not "src.tools.get_recipe.get_pantry_client"
[17:45] | Integration tests fail in CI | Add pytest markers and addopts="-m 'not integration'" to skip by default
[17:50] | Ruff E402 module import not at top | Add # noqa: E402 for tool registration after mcp definition

## Frictions techniques anticipees

1. **Pydantic-settings Pattern C** ordre d'override env > config.toml > defaults : verifier en pratique sur 1 test
2. **tenacity AsyncRetrying context manager** : preferer `async with AsyncRetrying(...) as retrying: async for attempt in retrying:` pattern (PAS @retry decorator car async support fragile)
3. **FastAPI mock port 8001** : si conflit port, fallback 8011/8021. Documenter dans pantry_mock_api.py docstring.
4. **Tool #1 get_recipe** doit retourner Pydantic model, model_dump(mode='json') obligatoire si Enum

## Out of scope J13

- Tools #2 search_recipes -- J14 9h-11h
- Tool #3 update_pantry -- J14 11h-13h
- Tool #4 generate_meal_plan (Tasks primitive) -- J14 14h-16h
- Security batch (SecretStr + OTel masking) -- J14 16h-17h
- Resource #5 + Prompt #6 -- J15
- OTel finalization -- J15 11h-12h
- Docker compose + Quickstart -- J15 14h-16h
- v0.1.0 tag + push -- J15 17h-17h30

## Cut sequence rule

A J14 17h via .\sprint.ps1 status :

| Verdict | Action |
|---------|--------|
| KEEP_FULL_SCOPE (tools>=4, tests>=90%) | Resource + Prompt J15 GO |
| KEEP_FULL_SCOPE_BUFFER_CONSUMED (tools=3, tests>=80%) | OK mais zero slack J15 |
| CUT_PROMPT (tools=3, tests<80%) | Cut Prompt #6, ship 5 primitives |
| CUT_PROMPT_AND_RESOURCE (tools<=2) | Ship 4 Tools + Tasks only, log ADR-011 |

**JAMAIS cut Tool #4** (differenciateur Tasks 2025-11-25, 0% public templates).

## Stack pinned

- Python 3.14.4
- mcp 1.27.0
- fastmcp 3.2.4 (extra [tasks] -- pydocket 0.20.1)
- pytest 9.0.3
- ruff 0.15.12
- mypy 1.20.2
