# Lessons learned — claude-mcp-server-template

> Frictions techniques rencontrées et règles dégagées au fil des sprints.

## Catégorie 5: Pydantic / FastMCP / httpx runtime behaviors (J13)

### L5.1 — Pydantic HttpUrl ajoute trailing slash
**Source**: Sprint J13 07/05/2026 (config.py tests)
**Pattern**: `HttpUrl("http://localhost:8001")` devient `"http://localhost:8001/"` — le slash est ajouté automatiquement par Pydantic v2. Utiliser `str(url).rstrip("/")` dans les comparaisons et la construction d'URLs.
**Next time I will**: Toujours wrapper les HttpUrl en str() avec rstrip avant concatenation de path.

### L5.2 — mypy + HttpUrl string defaults requiert type: ignore
**Source**: Sprint J13 07/05/2026 (config.py mypy pass)
**Pattern**: `base_url: HttpUrl = "http://localhost:8001"` → mypy se plaint. Fix: `# type: ignore[assignment]` sur la ligne de default.
**Next time I will**: Ajouter le type: ignore systematiquement sur les HttpUrl defaults dans BaseSettings/BaseModel.

### L5.3 — httpx.MockTransport requiert base_url dans AsyncClient
**Source**: Sprint J13 07/05/2026 (pantry_client.py tests)
**Pattern**: `httpx.AsyncClient(transport=MockTransport(...))` sans `base_url` → les requetes relatives echouent. Toujours passer `base_url=` explicitement.
**Next time I will**: Template de test pantry_client: `httpx.AsyncClient(transport=mock, base_url="http://test")`.

### L5.4 — FastMCP 3.2.4 host/port sur run(), pas constructor
**Source**: Sprint J13 07/05/2026 (server.py lifespan)
**Pattern**: `FastMCP("name", host="127.0.0.1")` → TypeError. Correct: `mcp.run(host="127.0.0.1", port=8000)`.
**Next time I will**: Verifier FastMCP changelog avant de passer kwargs au constructor.

### L5.5 — Circular imports: runtime import inside function body
**Source**: Sprint J13 07/05/2026 (tools/get_recipe.py)
**Pattern**: `from src.server import get_pantry_client` au module level → ImportError circular. Fix: import inside the function body at runtime.
**Next time I will**: Convention tools: tous les imports de server.py = inside function body uniquement. Jamais au module level.

## Catégorie 6: Testing patterns (J13)

### L6.1 — Integration tests: pytest markers + addopts pour exclusion par defaut
**Source**: Sprint J13 07/05/2026 (pytest pipeline green sans mock API running)
**Pattern**: Ajouter `@pytest.mark.integration` + dans pyproject.toml: `addopts = "--deselect tests/integration"`. Permet `pytest -q` de passer sans le serveur mock running.
**Next time I will**: Setup markers dans pyproject.toml des le scaffold initial (pas en cours de sprint).

## Catégorie 7: Workflow sprint (J13)

### L7.1 — sprint.ps1 permissions "don't ask again" a configurer session 1
**Source**: Sprint J13 07/05/2026
**Pattern**: Claude Code demande permission pour chaque type de commande (pytest, ruff, sprint.ps1, uvicorn, curl). Selectionner "2. Yes, don't ask again" la premiere fois pour chaque type. Permanent dans le repo.
**Next time I will**: Premiere session Claude Code sur un nouveau repo = passer methodiquement par chaque type de commande et selectionner "don't ask again".

### L7.2 — Token conservation: Claude Code FRESH local = zero tokens claude.ai
**Source**: Sprint J13 07/05/2026 (decision suite saturation contexte 81%)
**Pattern**: Implementation modules (code) = Claude Code FRESH sur machine locale. Claude.ai reserve pour strategy/L99, debrief/EOD, debug blockers. Eviter contexte cumulé >30K tokens en conv claude.ai active.
**Next time I will**: Toujours ouvrir Claude Code FRESH pour les sprints d'implementation. Revenir claude.ai uniquement pour EOD ou blockers critiques.
