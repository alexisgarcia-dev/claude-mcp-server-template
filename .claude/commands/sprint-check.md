---
description: Scope drift check 30 sec -- sprint MCP server template v0.1.0
---

Scope drift check sprint MCP server template v0.1.0 (J13-J15, ship samedi 09/05/2026).

## Étapes silencieuses

1. Lire `docs/design-v0.1.0.md` sections 1-3 (architecture core), `docs/CLAUDE.md` (sprint plan)
2. Run `git log --oneline --since='2026-05-07 09:00' | head -10`
3. Run `uv run python tools/cut-decision.py` (sortie JSON)
4. Comparer state actuel vs sprint plan attendu pour l'heure courante

## Output (≤8 lignes total, format strict)

```
SCOPE DRIFT CHECK -- [HH:MM J_X]
Tools: X/4 | Resource: Y/1 | Prompt: Z/1 | Tests: W% pass
Verdict cut-decision: [VERDICT]
Drift vs plan: [ALIGNED | DRIFT_X%_AREA | BLOCKER]
Recommandation: [continuer | cut | pause | debug]
Next bloc target: [tâche du prochain Pomodoro selon sprint plan]
```

## Posture

- Pas d'analyse longue. Verdict en 8 lignes max.
- Pas de fluff, pas de "souhaitez-vous", pas de proposition d'action additionnelle.
- Si BLOCKER -> mention claire, pas de minimisation.
- Si ALIGNED -> output puis silence, on continue.

## Trigger conseillé

À chaque transition bloc Pomodoro:
- J13: 16h, 18h
- J14: 13h, 17h (CUT GATE -- décision binaire ici)
- J15: 12h, 14h, 16h
