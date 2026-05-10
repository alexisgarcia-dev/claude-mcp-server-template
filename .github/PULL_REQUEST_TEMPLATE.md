## Summary

<!-- 1-3 sentences describing what this PR changes and why. -->

## Linked issue

Closes #

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] CI / build / tooling

## Testing

- [ ] `uv run pytest` passes locally (all 58+ tests green)
- [ ] `uv run ruff check .` clean
- [ ] `uv run ruff format --check .` clean
- [ ] If Docker change: `docker compose up -d` validated locally
- [ ] If MCP primitive change: tested with `npx @modelcontextprotocol/inspector`

## Checklist

- [ ] PR title follows conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- [ ] Commits are signed off (DCO `git commit -s`)
- [ ] `CHANGELOG.md` updated if user-facing
- [ ] ADR added in `docs/decisions.md` if architectural

## Notes for reviewer

<!-- Anything specific you'd like the reviewer to focus on, known caveats, follow-ups, etc. -->
