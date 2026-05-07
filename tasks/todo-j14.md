# tasks/todo.md -- Sprint J14 vendredi 08/05/2026

> Remplace tasks/todo.md pour la session J14. Mis a jour par Claude Code a chaque transition de bloc.

## Session goal

Implement Tools #2/#3/#4 + Security batch. CUT GATE formel 17h via .\sprint.ps1 status.

## Sprint plan J14 9h-17h

- [ ] **9h-11h** src/tools/search_recipes.py + tests/unit/test_search_recipes.py (Tool #2)
- [ ] **11h-13h** src/tools/update_pantry.py + tests/unit/test_update_pantry.py (Tool #3, bulk POST)
- [ ] **14h-16h** src/tools/generate_meal_plan.py + tests (Tool #4, Tasks primitive differenciateur #3)
- [ ] **16h-17h** Security batch: SecretStr OTel masking + dev_mode warning + OAuth boot validator

## Mid-session checkpoints

- [ ] **11h00** /sprint:check -- scope drift check
- [ ] **13h00** /sprint:check -- lunch check
- [ ] **17h00** .\sprint.ps1 status -- **CUT GATE FORMEL** (decision binaire, run tools/cut-decision.py)

## CUT GATE J14 17h -- decision binaire

| Verdict cut-decision.py | Action J15 |
|-------------------------|------------|
| KEEP_FULL_SCOPE (tools>=4, tests>=90%) | Resource #5 + Prompt #6 GO |
| KEEP_FULL_SCOPE_BUFFER_CONSUMED (tools=3, tests>=80%) | Resource + Prompt OK, zero slack |
| CUT_PROMPT (tools=3, tests<80%) | Cut Prompt #6, ship 5 primitives |
| CUT_PROMPT_AND_RESOURCE (tools<=2) | Ship 4 Tools + Tasks only, log ADR-011 |

**JAMAIS cut Tool #4** (Tasks primitive 2025-11-25, 0% public templates = differenciateur #3).

## EOD criteria J14 (must be true apres CUT GATE 17h)

- [ ] Tool #2 search_recipes implementee + tested
- [ ] Tool #3 update_pantry implementee + tested (bulk POST, Pydantic model_dump mode json)
- [ ] Tool #4 generate_meal_plan implementee + tested (Tasks + Progress from fastmcp.dependencies)
- [ ] Security batch done (SecretStr OTel masking, dev_mode stderr warning, OAuth boot validator)
- [ ] .\sprint.ps1 status run et verdict enregistre dans cette section
- [ ] uv run pytest -q exit 0
- [ ] 4+ commits atomiques via sprint.ps1
- [ ] Lessons learned mise a jour ci-dessous

## Verdict CUT GATE (a remplir apres sprint.ps1 status 17h)

Verdict: KEEP_FULL_SCOPE
tools_done: 4
tests_pass_pct: 100.0% (48/48 passed)
Action J15: Resource #5 + Prompt #6 GO. Full scope, zero cuts.

## Tool #4 generate_meal_plan -- spec Tasks primitive

Imports confirmes (verified live J13):
- from fastmcp.dependencies import Progress
- from fastmcp.server.tasks import TaskConfig
- import docket  # PyPI: pydocket, module: docket

Pattern:
```python
@mcp.tool(task=True)
async def generate_meal_plan(
    days: int,
    preferences: list[str],
    progress: Progress = Progress(),
) -> dict:
    await progress.set_total(days)
    for day in range(days):
        await progress.set_message(f"Planning day {day + 1}/{days}...")
        # ... do work ...
        await progress.increment()
    return result
```

## Lessons learned J14 (auto-update au cours de la session)

> Format: [HH:MM] | friction | regle/decision

[09:05] | sprint.ps1 ne fonctionne pas via bash tool (command not found) | Toujours utiliser PowerShell tool pour .\sprint.ps1, jamais Bash tool sur Windows
[09:10] | Ruff B008 sur Progress() default arg dans register() | Ajouter # noqa: B008 sur la ligne Progress = Progress() — pattern requis par FastMCP DI, non contournable
[09:15] | Ruff I001 import order ne respecte pas le noqa:I001 en ligne | Utiliser ruff check --fix pour auto-corriger, puis re-valider — ne pas tenter de corriger manuellement l'ordre isort
[09:20] | async_request_hook vs request_hook dans HTTPXClientInstrumentor | PantryClient utilise httpx.AsyncClient → toujours async_request_hook, jamais request_hook (silencieux sinon)
[09:25] | Security sub-tasks 4a + 4c + 4d deja implementes dans config.py avant J14 | Verifier l'etat du code existant avant d'implementer — evite doublons et regressions
[09:30] | BulkUpdateResult existait deja dans models.py (nomme differemment du spec) | Toujours lire models.py avant d'ajouter de nouveaux modeles — spec peut diverger du code existant

## Out of scope J14

- Resource #5 recipe_resource -> J15 9h-10h
- Prompt #6 weekly_planner -> J15 10h-11h
- OTel finalization (setup_telemetry + lifespan + HTTP exporter) -> J15 11h-12h
- Docker compose + Dockerfile + README quickstart -> J15 14h-15h
- Quickstart e2e clean install validation -> J15 15h-16h
- v0.1.0 tag + push -> J15 17h-17h30
- Catalog Upwork submit (draft) -> J14 EOD si CUT GATE done avant 17h30, sinon J15 EOD

## Stack pinned

Python 3.14.4 | mcp 1.27.0 | fastmcp 3.2.4 (pydocket 0.20.1) | pytest 9.0.3 | ruff 0.15.12 | mypy 1.20.2
