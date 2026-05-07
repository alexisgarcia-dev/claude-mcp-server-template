"""Tool #1: Get Recipe by ID.

Fetches a single recipe from PantryAPI by its unique identifier.
Demonstrates basic HTTP GET with error mapping.

See: docs/design-v0.1.0.md §4.1
"""

from fastmcp import FastMCP

from src.models import Recipe


async def get_recipe_impl(recipe_id: str) -> Recipe:
    """Fetch recipe by ID from PantryAPI.

    Args:
        recipe_id: Unique recipe identifier (e.g., "123", "abc-def")

    Returns:
        Recipe: Full recipe details including ingredients and instructions

    Raises:
        FileNotFoundError: Recipe not found (404)
        PermissionError: Authentication failed (401/403)
        RuntimeError: API error (5xx after retries exhausted)
    """
    from src.server import get_pantry_client  # Import at runtime to avoid circular

    client = get_pantry_client()
    data = await client.get(f"/recipes/{recipe_id}")
    return Recipe(**data)


def register(mcp: FastMCP) -> None:
    """Register get_recipe tool with FastMCP instance.

    Called from server.py after mcp instance creation.
    Pattern avoids circular import from @mcp.tool() at module level.
    """

    @mcp.tool()
    async def get_recipe(recipe_id: str) -> dict:
        """Get a recipe by its ID.

        Fetch detailed recipe information including ingredients and cooking instructions.

        Args:
            recipe_id: The unique identifier of the recipe to retrieve

        Returns:
            Recipe details as a dictionary with id, name, ingredients, instructions, etc.
        """
        recipe = await get_recipe_impl(recipe_id)
        return recipe.model_dump(mode="json")
