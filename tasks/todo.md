# tasks/todo.md -- Sprint J13 jeudi 07/05/2026

> Source de verite du sprint en cours. Mis a jour par Claude Code a chaque transition de bloc.
> Audit final J13 18h via /sprint:check.

## Session goal

Implement config.py + pantry_client.py + pantry_mock_api.py + Tool #1 get_recipe avec tests, EOD J13 18h.

## Sprint plan J13 14h-18h

- [ ] **14h-15h** src/config.py (Pydantic-settings Pattern C hierarchical)
- [ ] **15h-16h45** src/pantry_client.py (tenacity AsyncRetrying + lazy singleton) + src/error_messages.py
- [ ] **16h45-17h** pantry_mock_api.py (FastAPI seed for testing, port 8001)
- [ ] **17h-18h** src/tools/get_recipe.py (Tool #1) + tests/unit/test_get_recipe.py + tests/integration/test_get_recipe_e2e.py

## Mid-session checkpoints

- [ ] **16h00** /sprint:check -- scope drift check vs design doc
- [ ] **18h00** /sprint:check -- EOD verdict + cut-decision.py output

## EOD criteria J13 (must be true at 18h)

- [ ] src/config.py implemente + tested (1 unit test minimum)
- [ ] src/pantry_client.py implemente + tested (1 unit test minimum)
- [ ] pantry_mock_api.py running localement on :8001 (curl http://localhost:8001/recipes/1 returns 200)
- [ ] src/tools/get_recipe.py registered + tested (1 integration test minimum vs mock API)
- [ ] uv run pytest -q exit 0
- [ ] 4 commits atomic minimum via .\sprint.ps1 commit
- [ ] Section "Lessons learned" mise a jour

## Lessons learned J13 (auto-update au cours de la session)

> Format: [HH:MM] | friction | regle/decision

(a remplir par Claude Code au cours du sprint)

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
