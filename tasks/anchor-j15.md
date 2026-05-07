# Anchor prompt -- Claude Code session FRESH J15 9h (samedi 09/05/2026)

> Coller en premier message dans une **nouvelle session Claude Code** (pas continuation J14).
> Ouvrir Claude Code dans le repo. Modele: Sonnet 4.6.

## Read order obligatoire (avant code)

1. `LESSONS_LEARNED.md` -- categories 5-8 (frictions deja documentees)
2. `tasks/todo-j14.md` -- verdict CUT GATE J14 + lessons J14
3. `docs/CLAUDE.md` -- navigation map
4. `docs/design-v0.1.0.md` sections 4-8 (sections abregees v0.1.0 -- Resources/Prompts/Docker/Quickstart specs)
5. `docs/decisions.md` -- ADR (en particulier ADR-002 Resource MIME type, ADR-005 Docker patterns)

Confirme: **"Read order done. Sprint goal: [X]. Ship target: [Y]."**

## Contexte verdict J14
- CUT GATE = KEEP_FULL_SCOPE (4/4 tools, 100% tests)
- Resource + Prompt J15 GO sans cut
- Tasks primitive (différenciateur #3) deja committed J14

## Sprint plan J15 9h-17h30

| Bloc | Tache | Validation |
|------|-------|------------|
| 9h-10h | src/resources/recipe_resource.py + tests | MIME type required (mcp 1.27) |
| 10h-11h | src/prompts/weekly_planner.py + tests | PromptMessage role=user/assistant only (mcp 1.27 rejette role=system) |
| 11h-12h | src/telemetry.py finalization (setup_telemetry + lifespan + HTTP exporter) | Span exporte visible |
| 12h-12h30 | Integration tests batch (memory + http transport + tasks smoke) | 3+ integration tests verts |
| 14h-15h | Docker compose + Dockerfile + README quickstart 3-line | docker compose up clean |
| 15h-16h | Quickstart e2e clean install validation | **PLUG-AND-PLAY VERITY MOMENT** |
| 16h-17h | Buffer Hofstadter (loi immuable) | -- |
| 17h-17h30 | `.\sprint.ps1 ship` -> tag v0.1.0 + push | Release shipped |

## Quickstart e2e -- protocole strict (15h-16h)

**Crucial pour eviter faux positif** : tester sur env clean different du dev.

```powershell
$cleanDir = "C:\temp\mcp-quickstart-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
git clone $repoRoot $cleanDir
cd $cleanDir
# Optionnel: clean uv cache pour test plus stricte
# Remove-Item -Recurse $env:LOCALAPPDATA\uv\cache\fastmcp* -ErrorAction SilentlyContinue
uv sync
# Suivre EXACTEMENT le README quickstart 3-line, observer comportement user neuf
```

Pattern integre dans `.\sprint.ps1 ship` STEP 2 (deja code).

## Discipline obligatoire

1. Tests d'abord ou simultanes. Aucun module sans 1+ test unitaire.
2. Workflow par bloc: implement -> pytest local -> green -> `.\sprint.ps1 commit "feat: ..."` -> module suivant.
3. Patterns sourced PATTERNS_LIBRARY (deja appliques J13-J14):
   - `register(mcp)` function pattern (evite circular import)
   - Lazy singleton + FastMCP lifespan
   - tenacity AsyncRetrying (PAS @retry decorator)
   - model_dump(mode='json') pour Enum serialization
4. Pomodoro 50/10
5. Triggers `/sprint:check`: 11h, 14h, 17h
6. Bug -> logs + cause racine + fix direct. Frictions nouvelles -> LESSONS_LEARNED.md (categorie 9 J15)

## Critères ship v0.1.0 (must be true a 17h30)

- [ ] Resource #5 recipe_resource implemente + tested
- [ ] Prompt #6 weekly_planner implemente + tested
- [ ] OTel pipeline end-to-end (boot -> request -> span visible)
- [ ] docker compose up demarre clean
- [ ] README quickstart 3-line verifie sur env clean
- [ ] uv run pytest -q exit 0 (target ~60 tests)
- [ ] git tag v0.1.0 + push origin v0.1.0

## Rappels critiques J15

- **Resource MIME type**: `mime_type` parametre obligatoire dans le decorator. Sourced mcp 1.27 schema verified live J13.
- **Prompt PromptMessage role**: `user` ou `assistant` UNIQUEMENT. role=`system` interdit par mcp 1.27 PromptMessage schema. Fail at validation.
- **Docker healthcheck**: Python httpx (PAS curl, image plus petite, attack surface reduite). Pattern documente.
- **DNS rebinding mitigation**: FastMCP host=127.0.0.1 (CVE-2025-49596 verified J13).
- **Stack pinned**: Python 3.14.4, mcp 1.27.0, fastmcp 3.2.4 (pydocket 0.20.1, **module=docket** pas pydocket), pytest 9.0.3, ruff 0.15.12, mypy 1.20.2.

## Premiere action

Lis les 5 fichiers du Read order, puis confirme **"Read order done. Sprint goal: [X]. Ship target: [Y]."** AVANT toute ecriture de code.

## Apres ship v0.1.0 -- post-ship workflow

1. Submit Catalog Upwork draft (marketing/post-ship-bundle.md §1)
2. Tomorrow J17 9h: dev.to article publish
3. Tomorrow J17 10h: Twitter thread
4. Tomorrow J17 14h: Reddit r/mcp post si Twitter traction
