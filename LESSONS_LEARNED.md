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

## Catégorie 8: Posture & process Claude (J13-J14)

### L8.1 — Capability blindness drift (3x oubli MCP claude_code en conv J13)
**Source**: Conv J13 07/05/2026 — bilan
**Pattern**: Claude oublie 3x sur 6 messages la disponibilité du MCP claude_code et propose à Alex de copier-coller des prompts dans Claude Code interactive. Coût: ~10K tokens copy-paste manuel + friction relation.
**Next time I will**: Avant tout prompt à l'utilisateur, vérifier d'abord si MCP claude_code peut faire l'opération à sa place (file ops <5K, git, run scripts, edit configs). Si oui = exécuter via MCP. Memory entry #20 acte ce mécanisme.

### L8.2 — Verification theater (claims sans timestamp)
**Source**: Conv J13 07/05/2026 — bilan
**Pattern**: Claude affirme "fastmcp[tasks] extras non vérifié" comme red flag, puis "pydocket import OK" comme verified — les deux étaient en réalité non testés live. Risque: décisions techniques sur claims fragiles. Coût: pre-flight failed, traceback caché par PowerShell wrapping.
**Next time I will**: Tout claim technique inclut marqueur source: [verified live HH:MM via MCP/web_search] OU [verified Project Files] OU [from training, à vérifier si critique]. Aucun claim "naturalisé" sans marqueur. Memory entry #21.

### L8.3 — Re-débat post-décision (push-back après GO)
**Source**: Conv J13 07/05/2026 — bilan
**Pattern**: Alex décide "sprint MCP l99" → Claude répond avec une couche stratégique entière re-débattant la décision. Confusion "push-back honnête avant décision" vs "challenge après décision". Coût: ~3K tokens de noise + friction posture mentor.
**Next time I will**: Quand Alex dit GO/on continue/fait ça → posture EXÉCUTION uniquement. Push-back arrive AVANT le GO. Si risque détecté post-GO → format strict "Décision actée. Risque résiduel: X. Je continue, je signale, tu décides si pivot." Memory entry #22.

### L8.4 — MCP architecture: 1 atomic task = 1 MCP call
**Source**: Conv J13 07/05/2026 — MCP timeout post-bilan
**Pattern**: Tentative de prompt monolithique "Tool #2 commit + Tool #3 + Tool #4 + Security + CUT GATE" en 1 MCP call → timeout 4 min garanti. 5 modules ne tiennent pas dans le budget temps MCP.
**Next time I will**: 1 atomic task = 1 MCP call. Si estimation >3 min → découper en N calls séquentiels avec retour entre chaque. Format real-time obligatoire: "CALL X/Y -- [objectif] (~budget, [%] -> [%])" avant + 2-3 lignes brut après. Memory entry #23.

### L8.5 — Listening loop sur signaux Alex
**Source**: Conv J13 07/05/2026 — bilan
**Pattern**: Alex dit "le copy-paste ne marche pas" → Claude propose le tour suivant un workflow basé sur copy-paste. Trigger ignoré.
**Next time I will**: Triggers Alex (drift / encore / ne marche pas / PK) → STOP immédiat, ne JAMAIS re-proposer la même solution avant d'avoir compris pourquoi la précédente a foiré. Memory entry #24.
