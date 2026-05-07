# Anchor prompt -- Claude Code session FRESH J13 14h

> Coller en premier message dans une **nouvelle session Claude Code** (pas continuation J13 AM).
> Ouvrir Claude Code dans le repo. Modele: Sonnet 4.6 (Opus 4.7 reserve bug architectural ou decision majeure).

## Read order obligatoire (avant code)

1. `docs/CLAUDE.md` -- navigation map
2. `tasks/todo.md` -- sprint plan + EOD
3. `docs/design-v0.1.0.md` sections 1-3 -- architecture core
4. `docs/decisions.md` -- 10 ADR
5. `docs/sources.md` -- sources verified (re-verifier si >30 jours)

Confirme avec: **"Read order done. Sprint goal: [X]. EOD criteria: [Y]."**

## Sprint plan J13 14h-18h

| Bloc | Tache | Validation |
|------|-------|------------|
| 14h-15h | src/config.py (Pydantic-settings Pattern C) | 1+ unit test |
| 15h-16h45 | src/pantry_client.py (tenacity AsyncRetrying + lazy singleton) + src/error_messages.py | 1+ unit test |
| 16h45-17h | pantry_mock_api.py FastAPI seed (port 8001) | uvicorn demarre |
| 17h-18h | src/tools/get_recipe.py + tests/unit/test_get_recipe.py + tests/integration/test_get_recipe_e2e.py | pytest vert |

## Discipline obligatoire

1. **Tests d'abord ou simultanes.** Aucun module sans 1+ test unitaire.
2. **Workflow par bloc** : implement -> test local (`uv run pytest tests/unit/test_<module>.py -v`) -> si vert `.\sprint.ps1 commit "feat: <description>"` (wrapper run ruff + mypy + pytest + commit + push atomique). Si rouge -> debug avant commit.
3. **Patterns sourced PATTERNS_LIBRARY.md** :
   - `register(mcp)` function dans chaque tool/resource/prompt module (evite circular import du `@mcp.tool()` au module level)
   - Lazy singleton + FastMCP lifespan pour HTTP client (single instance, init au boot, teardown clean)
   - `tenacity AsyncRetrying` (PAS `httpx native retries`)
   - `wait_random_exponential` (jitter anti-thundering-herd)
   - `model_dump(mode='json')` pour Enum serialization (default leak instance Enum)
   - `Pydantic SecretStr` pour API keys + OTel header masking
   - Pydantic-settings Pattern C hierarchical (env > config.toml > defaults)
4. **Pomodoro 50/10** : 50 min focus + 10 min pause off-screen.
5. **Triggers `/sprint:check`** : 16h00 (mi-bloc, scope drift) + 18h00 (EOD verdict + cut-decision.py).
6. **Bug** : logs + cause racine + fix direct. Pas de "TODO: fix later". Frictions nouvelles -> `tasks/todo.md` section "Lessons learned" format `[HH:MM] | erreur | regle`.

## EOD criteres J13 (must be true a 18h)

- [ ] src/config.py + tested
- [ ] src/pantry_client.py + tested
- [ ] pantry_mock_api.py running localement on :8001 (curl http://localhost:8001/recipes/1 returns 200)
- [ ] src/tools/get_recipe.py registered + tested (1 integration test min vs mock API)
- [ ] uv run pytest -q exit 0
- [ ] 4+ commits atomic via `.\sprint.ps1 commit`
- [ ] tasks/todo.md "Lessons learned" mise a jour

## Out of scope J13

Tools #2/#3/#4 -> J14. Resource + Prompt -> J15. OTel batch -> J14 16h-17h. Docker + Quickstart e2e -> J15 14h-16h. Marketing assets deja pre-ecrits dans `marketing/post-ship-bundle.md`.

## Rappels critiques

- **Branch** : `main` (push direct, pas de feature branch en sprint serre)
- **Stack pinned** : Python 3.14.4, mcp 1.27.0, fastmcp 3.2.4, pytest 9.0.3, ruff 0.15.12, mypy 1.20.2. Si `>=` apparait -> alerte avant install.
- **Pre-flight deja cleared** : pas besoin de re-run `.\sprint.ps1 preflight`. Toutes les deps sont installees (commit f153556).
- **Cut sequence J14 17h** via `.\sprint.ps1 status` : cut Prompt #6 > Resource #5 > JAMAIS Tools. Tool #4 (Tasks primitive) est le differenciateur n.3, on ne le cut jamais.

## Premiere action

Lis les 5 fichiers du Read order, puis confirme avec **"Read order done. Sprint goal: [X]. EOD criteria: [Y]."** AVANT toute ecriture de code.
