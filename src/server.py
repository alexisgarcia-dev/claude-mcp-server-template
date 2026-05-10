"""MCP server entry point with lifespan-managed PantryClient.

Lazy singleton pattern: Tools call get_pantry_client() at runtime (not import time).
Lifecycle: lifespan initializes client at boot, tears down at shutdown.

See: docs/design-v0.1.0.md §3
"""

from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from src.config import Settings
from src.pantry_client import PantryClient
from src.telemetry import setup_telemetry

# Lazy singleton accessor
_pantry_client: PantryClient | None = None


def get_pantry_client() -> PantryClient:
    """Return the lifespan-managed PantryClient.

    Tools call this at runtime (not import time) to avoid None-at-import-time trap.
    """
    if _pantry_client is None:
        raise RuntimeError(
            "PantryClient not initialized. This indicates the server lifespan didn't run. "
            "Check that FastMCP(lifespan=lifespan) is set in server.py."
        )
    return _pantry_client


@asynccontextmanager
async def lifespan(app):
    """FastMCP lifespan: initialize and teardown shared resources."""
    global _pantry_client
    config = Settings()
    _pantry_client = PantryClient(config)
    tracer_provider = setup_telemetry(config)
    try:
        yield
    finally:
        await _pantry_client.aclose()
        if tracer_provider:
            tracer_provider.shutdown()


# Demo tokens for v0.1.0 — DEV/PREVIEW USE ONLY
# v0.2.0 will ship JWTVerifier with OAuth 2.1 + PKCE (Auth0, WorkOS, Azure Entra ID).
# See: README.md "Authentication" section + ROADMAP.md v0.2.0
_demo_token_verifier = StaticTokenVerifier(
    tokens={
        "demo-readonly": {"client_id": "ro", "scopes": ["read:pantry"]},
        "demo-readwrite": {"client_id": "rw", "scopes": ["read:pantry", "write:pantry"]},
    },
    required_scopes=["read:pantry"],
)


mcp = FastMCP(
    "PantryMCP",
    lifespan=lifespan,
    auth=_demo_token_verifier,
)

# Tools/Resources/Prompts registration happens here:
from src.tools import generate_meal_plan, get_recipe, search_recipes, update_pantry  # noqa: E402

get_recipe.register(mcp)
search_recipes.register(mcp)
update_pantry.register(mcp)
generate_meal_plan.register(mcp)

# Register Resources and Prompts (Resource: ~11% of public MCP servers / Prompt: ~4%)
# Source: digitalapplied.com MCP Adoption Statistics 2026
from src.prompts import weekly_planner  # noqa: E402
from src.resources import recipe_resource  # noqa: E402

recipe_resource.register(mcp)
weekly_planner.register(mcp)


if __name__ == "__main__":
    import os

    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        # Docker / remote deployment path. ADR-010: 127.0.0.1 default,
        # 0.0.0.0 only behind reverse proxy or Docker network (documented README).
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", "8000"))
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        # Local stdio (default) — Claude Desktop, Cursor, Windsurf
        mcp.run()
