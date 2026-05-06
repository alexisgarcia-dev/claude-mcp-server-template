# Brainstorm input v3 — Superpowers session J13 AM

> Document préparation `/superpowers:brainstorm` jeudi 7 mai 2026 9h FR.
> Version v3 — repositioning "REST API to MCP wrapper template", 6 primitives.
> Auteur : Alexis Garcia. Date prep : mercredi 6 mai 2026 PM.
> Changelog v1 → v2 → v3 en fin de fichier.

---

## Section 1 — Anchor prompt à coller dans Claude Code

Lance Claude Code dans le repo (`claude` dans `C:\Users\Utilisateur\freelance\claude-mcp-server-template`), puis tape :

```
/superpowers:brainstorm
```

Puis colle le bloc CONTEXT/POSITIONING/COMMERCIAL/COMPETITIVE/PRIMITIVES/CONSTRAINTS/CRITERIA/QUESTIONS/POSTURE/START ci-dessous (un seul message).

```
CONTEXT
I am Alex, freelance Python developer launching first portfolio
asset for Upwork P1 phase. Building a production-ready MCP server
template (Python) for public release on GitHub by Saturday May 9, 2026 (J15).
Public release + dev.to article walk-through Monday May 11 (J17).

Stack already installed and verified at /freelance/claude-mcp-server-template:
- Python 3.14.4 (dev), Python >= 3.11 supported (production)
- uv 0.11.8 as package manager
- mcp 1.27.0 (official Anthropic SDK)
- fastmcp 3.2.4 (high-level decorator framework)
- pytest 9.0.3, pytest-asyncio 1.3.0, pytest-cov 7.1.0
- ruff 0.15.12, mypy 1.20.2

Repo state:
- Private GitHub repo: alexisgarcia-dev/claude-mcp-server-template
- Working tree clean. Three commits on main:
  1. Initial gh repo create with LICENSE MIT + .gitignore Python
  2. Scaffolding (uv init, deps installed)
  3. CLAUDE.md root + .claude/Constitution.md (immutable rules)

POSITIONING (v3 strategic decision)
This template is NOT another generic MCP scaffold. Positioning verrouille:
"Plug-and-play REST API to MCP wrapper. Clone, edit one config file,
point at your OpenAPI spec, ship in under 1 hour."

Three commercial buyer segments validated by recent Upwork briefs:
- Segment A (50% volume): founder technique presse, has REST API
  documented OpenAPI/Swagger, wants Claude/ChatGPT access in <3 weeks
- Segment B (30% volume): IT manager enterprise POC, wants OAuth real,
  audit logging, observability, will extend later
- Segment C (20% volume, highest ARPU): dev agency reselling, wants
  white-label-ready template for 5-10 clients per year

GOAL
Ship v0.1.0 with 6 MCP primitives demonstrating the wrapping patterns:
4 Tools + 1 Resource + 1 Prompt. Demonstration on a fake SaaS
"PantryAPI" (FastAPI mock running on localhost:8001) wrapped end-to-end.
This makes ours the only public template covering all 3 MCP primitives
with a production-quality fake API demo.

Will become base of Upwork Project Catalog tiered as:
- Starter $400 (3 days, up to 10 endpoints)
- Standard $900 (5 days, 20 endpoints, OAuth client_credentials, tests, Docker)
- Advanced $2400 (10 days, 40 endpoints, Tasks primitive async, OTel, monitoring)

COMPETITIVE LANDSCAPE (researched, sourced 2026)
Three direct competitors. Differentiation must be unique-to-us on 4+ axes.

| Competitor | What it does | Our differentiator |
|---|---|---|
| sarmakska/mcp-server-toolkit | Generic scaffold + OAuth PKCE + OTel + rate limiting | They are handler-centric (drop into plugins/), we are API-centric (config.toml + OpenAPI focus) |
| ltwlf/python-mcp-starter | Bare scaffold, hello-world only | Production patterns + 3 primitives + spec 2025-11-25 native |
| IBM/ibm-openpages-mcp-server | Domain-locked enterprise (OpenPages) | Domain-neutral PantryAPI demo, generalizable to any REST API |

Unique-to-us (4 axes minimum):
1. Resources primitive demonstrated (99% templates skip)
2. Prompts primitive demonstrated (99% templates skip)
3. Tasks primitive 2025-11-25 (cutting edge async, 0% public templates have)
4. PantryAPI fake SaaS end-to-end demo (sarmakska, IBM, ltwlf all lack)

PROPOSED 6 PRIMITIVES (validate or revise with me)
The PantryAPI domain (recipes + ingredients + meal planning) is borrowed from
the WorkOS official guide "Building an MCP server from a REST API" — neutral
domain, well-understood, allows clean comparison vs reference implementation.

1. Tool: get_recipe(id) — GET single resource pattern. 90% of wrappers need this.
2. Tool: search_recipes(query, filters, cursor) — LIST paginated + filters.
   Most complex pattern, most used in real-world.
3. Tool: update_pantry(changes: list[PantryChange]) — BULK write with
   Pydantic nested models. WorkOS pattern: bulk-operation replaces three
   thin CRUD tools with one useful one. Demonstrates WHY MCP design != REST design.
4. Tool: generate_meal_plan_async(start_date, days) — LONG-RUNNING via Tasks
   primitive (spec 2025-11-25). Returns task handle, client polls status.
   Differentiator unique 2026.
5. Resource: pantry://recipes/{id} URI template — read-only context exposure
   for LLM. 99% of public templates skip Resources entirely.
6. Prompt: weekly_meal_planner — parameterized reusable prompt template.
   Server-side LLM interaction pattern. 99% skip Prompts entirely.

CONSTRAINTS (locked, push back if proposed to relax)
- 3 days hard deadline: Thu May 7 - Sat May 9, 2026
- 6h coding budget per day = 18h total
- Single developer (me)
- Stack already installed and pinned (do not propose alternative)
- Must work with Claude Desktop AND Cursor at minimum
- Must demonstrate REAL patterns clients pay for, not toys
- v0.1.0 is MINIMAL VIABLE TEMPLATE, NOT feature-complete
- 6 primitives EXACTLY (4 Tools + 1 Resource + 1 Prompt). Not 5, not 7.
- OAuth 2.1 client_credentials flow (M2M) for Standard/Advanced tier demo.
  PKCE flow deferred to v0.2.0.
- I have shipped Anthropic Claude API in production before (csv-product-enricher,
  24-module POD pipeline). Have NEVER shipped a public MCP server end-to-end.

PLUG-AND-PLAY MECHANISM (commercial pillar)
Three pillars non-negotiable in template:
1. config.toml central — API_BASE_URL, API_KEY_ENV, allowed origins, OAuth issuer.
   30 min implementation effort.
2. One-command launch — `uv run server` launches stdio + Streamable HTTP simultaneously.
   30 min implementation effort.
3. Patterns demonstrated — 6 primitives on PantryAPI = template to copy.
   Core sprint work.

OpenAPI auto-ingestion (script that parses Swagger spec and generates draft tools)
is a TEASER in README "v0.1.1 roadmap" only. Too ambitious for 3-day sprint.

SUCCESS CRITERIA v0.1.0
- All 6 primitives functional via stdio AND Streamable HTTP
- pytest coverage on tools logic >= 70% (80% stretch goal, accept 70% if scope pressure)
- Docker compose `docker-compose up` runs server + PantryAPI mock + Jaeger end-to-end
- README quickstart works in <5 minutes for someone new to MCP — manually validated on fresh terminal context Sat May 9 EOD
- Code reviewed clean by security-guidance plugin (no input sanitization gaps)
- OpenTelemetry traces visible in Jaeger when running tools
- v0.1.0 git tag pushed Sat May 9 EOD

QUESTIONS I EXPECT YOU TO ASK ME (so I am ready)
- Why these 6 primitives specifically? Why 4+1+1 split?
- Why PantryAPI domain? Why not CRM/e-commerce that feels more enterprise?
- Why OAuth client_credentials and not PKCE for v0.1.0?
- What error model do I want (exceptions vs structured Tool Execution Errors per spec 2025-11-25)?
- What testing strategy for stdio vs Streamable HTTP transports? Mock vs integration?
- How do I structure the project layout? (src/tools/<one-per-tool>.py? src/server.py central registry?)
- What is the OpenTelemetry instrumentation level (auto vs manual span building)?
- How do I want to demo this in the README (terminal session, GIF, Loom video)?
- What is my measure of "production-grade" for v0.1.0?
- What is the configuration story (env vars only, .env file, config.toml, all three)?
- What is the v0.1.1 roadmap teasers in README to manage expectations?
- What is the stop strategy if scope pressure on Sat May 9 16h?

POSTURE
I want you to challenge me hard. If a constraint or scope item is wrong,
push back with reasoning. If a primitive choice is weak, propose alternative.
If I am under-thinking a security concern, flag it. The goal is a design doc
I can hand to my future self at J13 9am Friday and execute without re-thinking.

START.
```

---

## Section 2 — Fiche réponses pré-rédigées

Anticipation des 12 questions probables Superpowers. Réponse cadre prête à coller.

### Q1 — Pourquoi 6 primitives 4+1+1 split ?
> 4 Tools couvrent les 4 patterns de wrapping REST récurrents (single GET, list paginated, bulk write, async long-running). 1 Resource + 1 Prompt = différenciation unique vs concurrence (99% des templates publics ne montrent que les Tools). 6 = équilibre couverture/scope sur 3 jours. 7 = scope creep, 5 = sous-démo.

### Q2 — Pourquoi PantryAPI domain ?
> Domaine neutre, lisible, repris du WorkOS official guide "Building MCP from REST API" (référence reconnue). Permet comparaison directe vs implémentation de référence. CRM/e-commerce = perçu plus enterprise mais 2x plus de scope (entités, états, edge cases). PantryAPI = scope contrôlé sur 3 jours.

### Q3 — Pourquoi positioning REST→MCP wrapper et pas generic MCP scaffold ?
> Briefs Upwork récents (Unilog 337+301 APIs, mars 2026) confirment que le marché paie pour wrapper son API existante, pas pour un template generic. sarmakska/mcp-server-toolkit fait déjà le scaffold generic. Notre angle PnP "config.toml → point at your OpenAPI" est différent (API-centrique vs handler-centrique).

### Q4 — Différenciation vs sarmakska/IBM/ltwlf ?
> sarmakska = handler-centric scaffold (drop into plugins/). Ours = API-centric wrapper (config.toml). ltwlf = bare scaffold. Ours = production patterns + 3 primitives + spec 2025-11-25. IBM = domain-locked OpenPages. Ours = domain-neutral PantryAPI generalizable. 4 différenciateurs uniques : Resources, Prompts, Tasks, PantryAPI demo.

### Q5 — OAuth client_credentials choice (pas PKCE) ?
> M2M flow = realistic enterprise scenario (Segment B IT manager). PKCE flow = consumer/desktop app pattern, moins représentatif d'une intégration production REST API. PKCE differé v0.2.0 si demande. Auth0 ou Okta integration v0.2.0 aussi.

### Q6 — Tasks primitive support dans mcp 1.27 SDK ?
> Spec 2025-11-25 introduit Tasks. mcp 1.27.0 SDK officiel Anthropic devrait supporter (Tasks est dans changelog spec novembre). À vérifier early J13 AM (5 min lecture du changelog SDK et de la doc Tasks). Si pas encore implémenté côté SDK : fallback pattern manuel async avec state SQLite, même UX, sans tag "spec native". Décision dans 30 premières minutes du sprint.

### Q7 — OpenTelemetry instrumentation level (auto vs manual) ?
> Auto-instrumentation via `opentelemetry-instrument` CLI = 30 min setup, traces sur tous les tools automatiquement via FastMCP middleware. Pas de manual span building en v0.1.0 (trou noir 3-4h). Manual spans v0.1.1+ si demande. Sortie traces JSON OTLP exporter vers Jaeger local en docker-compose.

### Q8 — Coverage 70% vs 80% strict ?
> 70% acceptable v0.1.0, 80% stretch. Pertinente : tests par tool (logique métier + edge cases auth/errors/limits) + integration test stdio + integration test HTTP. Pas du test_init pour faire monter score. Si scope pressure J15 16h : on cap à 70% pertinent vs 80% partiel.

### Q9 — Pricing rationale segments ?
> Starter $400 = Segment A (founder pressé, 10 endpoints suffisent pour POC). Standard $900 = Segment B (IT manager POC, 20 endpoints + OAuth + tests = niveau due-diligence enterprise). Advanced $2400 = Segment C (agence dev reselling, 40 endpoints + Tasks + OTel + production deploy = template white-label). ARPU mix 30/40/30 = $1100 moyenne contrat.

### Q10 — Stop conditions par primitive si scope pressure ?
> Ordre de coupe priorité haute → faible : Prompt (le moins critique commercialement) → Resource (plus critique mais coupable) → Tool 4 Tasks async (cutting edge mais peut être v0.1.1 documented). Tools 1+2+3 + OAuth + OTel + Docker = floor minimum non négociable v0.1.0. Garde 5/6 primitives si J14 PM 18h pas fini Tool 4. Garde 4/6 si J15 14h pas Resource. Documente reste v0.1.1 dans README.

### Q11 — README quickstart 5 min validation ?
> Test manual sur terminal fresh (nouveau Powershell, pas de history), suivre exactement les étapes du README, chrono activé. Cible <5 min de "git clone" jusqu'à "tool call working from Claude Desktop". Si >5 min : raffinage README J15 17h, pas accepté de ship sans validation.

### Q12 — v0.1.1 roadmap teasers dans README ?
> Documenter explicitly dans README section "Roadmap" : (a) OpenAPI auto-ingestion script, (b) PKCE OAuth flow, (c) Real Auth0/Okta integration, (d) Manual OpenTelemetry span building, (e) Multi-tenant isolation, (f) Sampling and Elicitation primitives. Manage client expectations + signal "active project" = trust signal.

---

## Section 3 — Hard rules push-back ready

Si Superpowers propose ce qui suit, voici la réponse standard :

### Push-back 1 — "Why not Node.js / TypeScript?"
> Stack pinned in CLAUDE.md and Constitution.md. Python is my vertical. Brief Unilog accepts Python explicitly. Non-negotiable.

### Push-back 2 — "Maybe 7 or 8 primitives would be more impressive?"
> Constitution.md hard rule: 6 primitives EXACTLY (4 Tools + 1 Resource + 1 Prompt). Scope creep risk on 3-day sprint. v0.2.0 can add more.

### Push-back 3 — "Add MCP Apps extension v0.1.0 for interactive UI?"
> SEP-1865 still experimental, not core spec. v0.1.0 ships core compliant only. v0.1.1 explores Apps extension if community traction.

### Push-back 4 — "Real Auth0/Okta integration in v0.1.0?"
> OAuth client_credentials flow demonstrated with fake auth route in PantryAPI mock. Real Auth0 = trou noir 4-8h. Stub structure + comment paths to v0.2.0. Constitution rule maintained.

### Push-back 5 — "Skip Resources or Prompts (they are not as used as Tools)"
> Resources + Prompts are EXACTLY my differentiator vs sarmakska/IBM/ltwlf. They are 33% of MCP protocol surface and 99% public templates skip them. Keeping both.

### Push-back 6 — "Different demo domain (CRM, e-commerce)?"
> PantryAPI = WorkOS reference convention, neutral, scope-controlled on 3 days. CRM/e-commerce = 2x scope (entities, states, edge cases). v0.1.1 or follow-up template can pivot domain.

### Push-back 7 — "Different package manager (poetry, hatch)?"
> uv is locked. Already installed and configured. Modern 2026 standard per Anthropic official MCP docs.

### Push-back 8 — "Maybe public from day 1 is better for traction?"
> Private during build to avoid v0.0.x abandoned visible to early visitors. Public at v0.1.0 ship + dev.to article = managed launch with quality bar met. Constitution rule.

### Push-back 9 — "Skip OpenTelemetry for v0.1.0?"
> OTel = part of "production-ready" claim and is core differentiator vs ltwlf. Auto-instrumentation = 30 min only, low cost. Keeping in scope.

### Push-back 10 — "Skip Docker compose for v0.1.0?"
> Docker compose = part of plug-and-play story (1 command demo). If time pressure J15 14h check-in, OK to ship without Docker AND adjust README to mark v0.1.1 deliverable. Decision-point at J15 14h, not before.

---

## Section 4 — Outputs attendus du brainstorm

À la fin de la session Superpowers, je dois sortir avec :

1. Design doc Markdown clair (à sauver dans `docs/design-v0.1.0.md`) avec sections :
   - Architecture decisions (src layout, registry pattern, transport switch)
   - 6 primitives finalized specs (input/output schemas, error model, security)
   - PantryAPI mock design (entities, endpoints, OAuth fake routes)
   - Tests strategy (unit, integration stdio, integration HTTP, coverage targets)
   - OpenTelemetry instrumentation plan
   - Streamable HTTP deployment plan
   - Open questions résolues with rationale

2. Confirmation ou révision des 6 primitives proposées
3. Project layout decision (src/tools/<one-per-tool>.py vs central registry vs hybrid)
4. Clear stop sequence J14 PM if scope pressure (which primitive to cut first)
5. Prêt pour `/superpowers:write-plan` lancé en SESSION FRESH J13 14h après lunch

---

## Section 5 — Recommandations communautaires Superpowers (sourced)

- Anchor prompt spécifique → questions pointues. Vague input → vague questions → weak design doc.
- Après brainstorm signed-off, NE PAS lancer write-plan dans la même session. Démarrer fresh session Claude Code AVANT write-plan pour éviter pollution context.
- Le 5-min chunk model des subagents Superpowers est plus token-efficient qu'une session unstructured.
- Si Claude drifte mid-session et "oublie" Superpowers : tape `/using-superpowers` pour reload.
- Si je veux questionner une partie du design doc : taper `DRIFT scope` ou `DRIFT [section]` pour recadrer.

---

## Section 6 — Stop conditions de la session

La session brainstorm STOP si :
- Design doc signé par moi (output normal attendu, ~60-90 min)
- Fatigue cognitive 8/10+ (qualité décline, reprend J13 14h fresh post-lunch)
- Push-back sur hard rules ignoré 2 fois (Constitution violation, je quitte)
- 90 min écoulées (signal que scope ou anchor prompt à raffiner, pas à acharner)

Stop strict 23h ce soir indépendamment de l'avancement.

---

## Section 7 — Plan exécution sprint 3 jours (post-brainstorm)

### J13 jeudi 7 mai 2026 — 6h dev — "Foundation + 3 wrapping patterns"

| Bloc | Heure FR | Durée | Output |
|---|---|---|---|
| Brainstorm Superpowers + signature design doc | 9h-11h | 2h | Design doc signed in `docs/design-v0.1.0.md` |
| /superpowers:write-plan in fresh session | 11h-12h | 1h | `docs/plan-v0.1.0.md` 500-line plan |
| Lunch + recharge | 12h-14h | 2h | -- |
| Setup PantryAPI mock FastAPI | 14h-15h | 1h | `pantry_mock_api.py` runs on :8001, SQLite seed |
| Tool 1 `get_recipe` | 15h-16h | 1h | type hints, error 404 handling, 1 unit test |
| Tool 2 `search_recipes` | 16h-18h | 2h | cursor pagination + 3 filters, 2 unit tests |

J13 EOD checkpoint: 2 tools functional, mock running, tests passing.

### J14 vendredi 8 mai 2026 — 6h dev — "Patterns avancés + auth"

| Bloc | Heure FR | Durée | Output |
|---|---|---|---|
| Tool 3 `update_pantry` (bulk) | 9h-11h | 2h | Pydantic nested models, atomicity, 2 unit tests |
| Tool 4 `generate_meal_plan_async` via Tasks | 11h-13h | 2h | Spec 2025-11-25 Tasks integration. Fallback manual async if SDK gap. |
| Lunch | 13h-14h | 1h | -- |
| Resource 5 `pantry://recipes/{id}` URI templates | 14h-15h | 1h | Resources primitive demo, 1 test |
| Prompt 6 `weekly_meal_planner` | 15h-16h | 1h | Prompts primitive demo, 1 test |
| OAuth 2.1 client_credentials flow | 16h-17h30 | 1h30 | Real flow with fake auth route in PantryAPI mock |

J14 EOD checkpoint: 6 primitives functional, OAuth working, tests >= 60%.

### J15 samedi 9 mai 2026 — 6h dev — "Production layer + ship"

| Bloc | Heure FR | Durée | Output |
|---|---|---|---|
| Streamable HTTP transport + Origin header check (spec 2025-11-25) | 9h-10h | 1h | dual transport, security compliant |
| OpenTelemetry auto-instrumentation | 10h-11h30 | 1h30 | Traces in Jaeger via OTLP exporter |
| Docker compose (mcp + mock-api + jaeger) | 11h30-12h | 30min | 1-command demo |
| Lunch + checkpoint scope (decide cut if needed) | 12h-14h | 2h | -- |
| README pro + quickstart 5 min validate | 14h-15h30 | 1h30 | Test on fresh terminal context |
| Draft article dev.to | 15h30-16h30 | 1h | Markdown 800-1200 words, screenshots |
| v0.1.0 tag + push public + repo settings to public | 16h30-17h | 30min | v0.1.0 LIVE on GitHub public |

J15 EOD: v0.1.0 SHIPPED public. Article dev.to drafted, scheduled J17.

---

## Section 8 — Pricing & marketing post-ship

### Project Catalog Upwork (à créer J17 lundi 11 mai)

| Tier | Prix | Délai | Scope client | Cible segment |
|---|---|---|---|---|
| Starter | $400 | 3 jours | Wrap up to 10 endpoints + basic auth + README + 1 revision | A founder pressé |
| Standard | $900 | 5 jours | Starter + 20 endpoints + OAuth client_credentials + tests + Docker + 2 revisions | B IT manager POC |
| Advanced | $2,400 | 10 jours | Standard + 40 endpoints + Tasks async + OpenTelemetry + Streamable HTTP production deploy + monitoring + 5 revisions + architecture review | C agence reselling |

### Article dev.to J17

Titre proposé : "How I built a production MCP server template in 3 days (Python, Tasks primitive, OAuth, OpenTelemetry)"

Sections :
1. Why generic templates miss the mark for real REST API wrappers
2. The 6 primitives I picked and why
3. PantryAPI: a fake SaaS to demo end-to-end
4. Spec 2025-11-25 features I integrated
5. Production patterns: OAuth, OTel, Streamable HTTP
6. Code walkthrough with snippets
7. Roadmap v0.1.1+ and how to contribute

CTA : link to GitHub repo + Upwork Catalog.

### Update Upwork bio J17

New title : "AI-augmented Python Developer | MCP Servers + Claude API + RAG Pipelines"
Add to Skills (replace 1 weak skill): MCP

### Social posts J17

- LinkedIn long-form (300 words, link to article + repo)
- Twitter thread (5 tweets, key technical points)
- Reddit r/ClaudeAI 1 post (focus on PantryAPI demo and Tasks primitive)

---

## Section 9 — Risques anticipés + mitigation

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Tasks primitive support incomplete dans mcp 1.27 SDK | Moyen | Moyen | Vérification J13 9h05 (5 min check changelog SDK + Tasks doc). Si gap : fallback pattern manuel async + state SQLite, mêmes UX, no spec native tag. Décision dans 30 premières min. |
| Resource + Prompt = scope creep J14 PM | Élevé | Moyen | Cap timer J14 16h. Si pas fini Prompt à 16h → coupe Prompt, on a 5/6, document v0.1.1 dans README. |
| OpenTelemetry trou noir J15 11h-13h | Moyen | Faible | Use `opentelemetry-instrument` auto-instrumentation = 30 min setup. Pas de manual span building. Si auto-instrument bug : skip OTel v0.1.0, document v0.1.1, focus README quality. |
| OAuth client_credentials demo flow = 1h30 sous-estimé J14 16h | Moyen | Moyen | Use lib existante `authlib` + fake auth route dans PantryAPI mock (pas Auth0 réel). Si bug auth : skip OAuth v0.1.0, mark "v0.1.1: OAuth flow", focus complete primitives. |
| Test coverage 70% non atteint J15 EOD | Moyen | Faible | Cap 60% acceptable v0.1.0 minimum. Communicate dans README "coverage 60% v0.1.0, 80% target v0.1.1" honest signal. |
| README quickstart >5 min sur fresh terminal J15 17h | Faible | Élevé | Validate à J15 14h pas 17h. Ajustement itératif si besoin. Si toujours >5 min à 17h : cut une étape de setup, focus minimum viable demo path. |
| Push public friction J15 17h (settings GitHub change visibility) | Faible | Faible | Anticipation : tester `gh repo edit alexisgarcia-dev/claude-mcp-server-template --visibility public` syntax J14 EOD pour confirmer command. |
| Scope creep "encore 1 dernier petit truc" J15 18h | Élevé | Moyen | Hard stop 17h30 ship v0.1.0. Tout après = v0.1.1. Constitution rule. |

---

## Section 10 — Changelog ce document

| Version | Date | Auteur | Change |
|---|---|---|---|
| v1 | 6 mai PM | Claude | Initial: 5 generic tools (FS, HTTP, SQLite, 2 mocks). 10K bytes. |
| v2 | 6 mai PM | Claude | Repositioning REST→MCP wrapper, 5 patterns sample. Pricing $500/$900/$1400. Discarded. |
| v3 | 6 mai PM | Claude | 6 primitives (4 Tools + 1 Resource + 1 Prompt), PantryAPI demo, pricing $400/$900/$2400, segments A/B/C, competitive matrix sourced 2026, plan exécution détaillé, marketing post-ship. **CURRENT.** |

---

End of brainstorm-input.md v3.
