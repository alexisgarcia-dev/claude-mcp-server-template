"""Recipe resource - exposes recipe data via MCP Resource primitive.

URI scheme: recipe://{recipe_id}
MIME type: application/json

Demonstrates Resource primitive end-to-end (only ~11% of public MCP servers ship Resources, source: digitalapplied.com MCP Adoption Statistics 2026).

See: docs/design-v0.1.0.md §5
"""

from src.models import Recipe


async def recipe_resource_impl(recipe_id: str) -> Recipe:
    """Fetch a recipe by ID from upstream PantryAPI.

    Lazy import of get_pantry_client() avoids the None-at-import-time trap.
    """
    from src.server import get_pantry_client

    client = get_pantry_client()
    recipe_data = await client.get(f"/recipes/{recipe_id}")
    return Recipe.model_validate(recipe_data)


def register(mcp) -> None:
    """Register the recipe resource on the FastMCP instance."""

    @mcp.resource(
        uri="recipe://{recipe_id}",
        mime_type="application/json",
        description="Fetch a recipe by ID. Example URI: recipe://1",
    )
    async def recipe_resource(recipe_id: str) -> Recipe:
        return await recipe_resource_impl(recipe_id)
