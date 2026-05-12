# Constitution — claude-mcp-server-template

## Hard rules (immutable)

These rules cannot be relaxed by any agent, brainstorm session,
or scope discussion. If a proposal violates one of these, push back
or stop until human (Alexis) explicitly overrides.

1. NO push to `main` directly. Always feature branch + pull request.

2. NO commit without tests passing locally. `uv run pytest` must
   exit 0 before any `git commit`.

3. NO scope creep on v0.1.0. Five (5) tools, exactly. Not four,
   not six. Tool list locked at end of brainstorm session J13 AM.

4. NO real credentials, API keys, or tokens in code or tests.
   Use `.env.example` with dummy values only. `.env` is gitignored.

5. NO copy-paste of code from public MCP servers without explicit
   attribution in a `NOTICE` file or inline comment with source URL.

6. NO security-guidance plugin warning ignored silently. Either
   fix the warning or document explicitly in code comment why
   the warning does not apply.

7. NO ship of v0.1.0 to public without README quickstart manually
   validated end-to-end on a fresh machine context.

8. NO public push of the repo before scope completed and human
   explicitly says "ship".

## Override policy

The only entity that can override these rules is Alexis Garcia
typing the exact phrase "OVERRIDE rule N" where N is the rule
number. Anything less specific (vague approval, implicit consent)
does NOT count as override.
