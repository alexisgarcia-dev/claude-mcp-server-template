# CLAUDE.md — claude-mcp-server-template

## Project context

Production-ready Python MCP server template. Public open-source asset.
First freelance portfolio piece for Alexis Garcia (Upwork P1 phase).
Built to demonstrate real-world MCP patterns clients pay for.

## Stack pinned

- Python >= 3.11 (dev on 3.14.4)
- uv as package manager
- mcp[cli] >= 1.27 (official Anthropic SDK)
- fastmcp >= 3.0 (high-level decorator framework, FastMCP 3.0 released Jan 19, 2026)
- pytest, pytest-asyncio, pytest-cov for testing
- ruff for linting, mypy for type checking
- Docker compose for local dev (deferred to J15)

## Constraints v0.1.0

- Hard deadline: Saturday May 9, 2026 (J15)
- 3 dev days budget: J13 Thu, J14 Fri, J15 Sat (6h/day = 18h total)
- 5 sample tools, EXACTLY (not 4, not 6 — discipline scope strict)
- Both stdio AND Streamable HTTP transports working
- pytest coverage >= 80% on tools logic
- README quickstart that works in <5 minutes for someone new to MCP

## Workflow rules

- All work happens on `feature/<task-name>` branches, NEVER on `main` directly.
- No commit without tests passing locally.
- Run ruff + mypy before any commit.
- Use Superpowers `/superpowers:brainstorm` BEFORE any code (J13 AM).
- Use security-guidance plugin to review every tool that accepts user input.
- Use code-review plugin before merging feature branches to main.

## Out of scope v0.1.0 (deferred to v0.2.0+)

- Real OAuth 2.1 implementation (stub middleware shape only in v0.1.0)
- Multi-tenant isolation
- Sampling and Elicitation primitives
- Resources and Prompts primitives (tools only in v0.1.0)
- Production deployment patterns beyond Docker

## Repo public release timing

- v0.1.0 ship target Sat May 9, 2026 EOD
- Repo stays PRIVATE during build (J13-J15)
- Goes PUBLIC at v0.1.0 ship + dev.to article publish J17 Mon

## Reference

- MCP spec: https://modelcontextprotocol.io
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- FastMCP docs: https://gofastmcp.com
- Constitution (immutable rules): see `.claude/Constitution.md`
