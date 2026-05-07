"""MCP server entry point with lifespan-managed PantryClient.

Lazy singleton pattern: Tools call get_pantry_client() at runtime (not import time).
Lifecycle: lifespan initializes client at boot, tears down at shutdown.

See: docs/design-v0.1.0.md §3
"""

from contextlib import asynccontextmanager

from fastmcp import FastMCP

from src.config import Settings
from src.pantry_client import PantryClient

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
    # TODO J14 16h: tracer_provider = setup_telemetry(config)
    try:
        yield
    finally:
        await _pantry_client.aclose()
        # TODO J14 16h: if tracer_provider: tracer_provider.shutdown()


mcp = FastMCP(
    "PantryMCP",
    lifespan=lifespan,
)

# Tools/Resources/Prompts registration happens here:
from src.tools import generate_meal_plan, get_recipe, search_recipes, update_pantry  # noqa: E402

get_recipe.register(mcp)
search_recipes.register(mcp)
update_pantry.register(mcp)
generate_meal_plan.register(mcp)

if __name__ == "__main__":
    mcp.run()
