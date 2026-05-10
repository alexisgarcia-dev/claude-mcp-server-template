# Contributing

Thanks for your interest in improving `claude-mcp-server-template`. This guide covers the workflow for opening issues, sending pull requests, and shipping high-quality changes.

## Quick Start

1. **Open an issue first.** For non-trivial changes, file an issue (or comment on an existing one) so we can align on scope before you spend time on a PR.
2. **Fork** the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-change main
   ```
3. **Set up the dev environment** (see below).
4. **Run the test suite** before pushing:
   ```bash
   uv run pytest
   uv run ruff check . && uv run ruff format --check .
   ```
5. **Open a PR** linked to the issue, fill in the PR template, and sign off your commits per the [Developer Certificate of Origin](https://developercertificate.org/):
   ```bash
   git commit -s -m "feat: add weekly planner prompt"
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/<your-user>/claude-mcp-server-template.git
cd claude-mcp-server-template

# Install dependencies (uv-managed)
uv sync --all-extras --dev

# Configure environment
cp .env.example .env

# Run the test suite
uv run pytest

# Run the MCP server (stdio transport)
uv run python -m src.server

# Or bring up the full demo stack (MCP + Pantry mock + Jaeger)
docker compose up -d
```

The Jaeger UI is available at <http://localhost:16686> once the stack is running.

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional-scope>): <short summary>
```

Common types:

- `feat` — a new user-facing feature
- `fix` — a bug fix
- `docs` — documentation-only change
- `chore` — tooling, dependencies, or repo maintenance
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or correcting tests
- `ci` — CI configuration change

Example: `feat(tools): add inventory_check tool with retry middleware`.

## Pull Request Requirements

Every PR should:

- **Pass CI.** `ruff check`, `ruff format --check`, and the `pytest` matrix on Python 3.11/3.12/3.13 must be green.
- **Include tests.** New features need unit tests; aim for **80%+ coverage on new code**. Follow the existing `tests/unit/` layout that mirrors `src/`.
- **Document breaking changes** in `CHANGELOG.md` under an `Unreleased` section.
- **Add an ADR** in `docs/decisions.md` for architectural choices (new primitive types, transport changes, dependency swaps, etc.).
- **Be linked to an issue.** Reference it with `Closes #123` or `Refs #123` in the PR description.
- **Be signed off** with `git commit -s` (DCO).

Keep PRs focused. Small, single-purpose PRs review faster than large ones.

## Code Style

- **Python 3.11+** syntax. Type hints are required on public functions and class methods.
- Prefer modern union syntax: `X | None` over `typing.Optional[X]`, `list[str]` over `List[str]`.
- **Ruff** is the source of truth for lint and formatting. Line length is **100**. Run `uv run ruff format .` before committing.
- **Docstrings** on public functions, classes, and modules. One-liners are fine when the name is self-explanatory.
- Tests live in `tests/unit/` and mirror the `src/` package layout (e.g., `src/tools/foo.py` → `tests/unit/test_foo.py`).
- Logger over `print()`. Use `logging.getLogger(__name__)`.

## Reporting Bugs and Requesting Features

Use the templates in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE):

- **Bug report** — for reproducible defects. Please include version, transport, Python version, and a minimal reproduction.
- **Feature request** — for proposals. Describe the use case, the proposed API, and any alternatives considered.

For security issues, **do not** open a public issue. See [`SECURITY.md`](SECURITY.md).

## Code of Conduct

Be kind, be specific, and assume good faith. Maintainers reserve the right to lock or close threads that become unproductive.

Thank you for contributing!
