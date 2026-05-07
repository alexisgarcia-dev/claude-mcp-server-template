# Anchor prompt -- Claude Code session FRESH J14 9h

> Coller en premier message dans une **nouvelle session Claude Code** (pas continuation J13).
> Ouvrir Claude Code dans le repo. Modele: Sonnet 4.6.

## Read order obligatoire (avant code)

1. `docs/CLAUDE.md` -- navigation map
2. `tasks/todo.md` -- sprint plan J14 + CUT GATE
3. `docs/design-v0.1.0.md` sections 1-3 -- architecture core
4. `docs/decisions.md` -- ADR (en particulier ADR-001 register pattern, ADR-003 tenacity)
5. `tasks/todo.md` section "Lessons learned J13" -- 9 frictions a eviter

Confirme: **"Read order done. Sprint goal: [X]. CUT GATE: [Y]."**

## Rappels critiques J14

- **Tool #4 Tasks primitive**: `from fastmcp.dependencies import Progress`, `@mcp.tool(task=True)`, `progress: Progress = Progress()`. Ne PAS utiliser ctx.report_progress() (c'est l'ancienne API raw mcp SDK).
- **Circular imports**: runtime import inside function body (pattern acte J13). NE PAS importer server.py au module level dans les tools.
- **Pydantic HttpUrl**: toujours str() pour comparaisons. type: ignore pour mypy sur defaults.
- **httpx.MockTransport**: requiert base_url= param dans les tests.
- **model_dump(mode='json')**: obligatoire sur tout model contenant Enum.
- **sprint.ps1 permissions**: deja configurees "don't ask again" pour pytest, ruff, sprint.ps1, uvicorn, curl.

## Workflow par module

implement -> `uv run pytest tests/unit/test_<module>.py -v` -> si vert -> `.\sprint.ps1 commit "feat: ..."` -> module suivant.

## CUT GATE 17h

`.\sprint.ps1 status` -> retourne JSON via cut-decision.py -> verdict KEEP/CUT_PROMPT/CUT_PROMPT_AND_RESOURCE -> enregistrer dans tasks/todo.md section "Verdict CUT GATE" -> commit.

## Premiere action

Lis les 5 fichiers du Read order, puis confirme **"Read order done. Sprint goal: [X]. CUT GATE: [Y]."** AVANT toute ecriture de code.
