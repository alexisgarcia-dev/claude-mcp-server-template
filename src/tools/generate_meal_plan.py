"""Tool #4: Generate Meal Plan (Tasks primitive — differentiateur #3).

Async long-running task with progress reporting via FastMCP Tasks primitive.
Uses @mcp.tool(task=True) + fastmcp.dependencies.Progress for streaming progress.

See: docs/design-v0.1.0.md §4.4
"""

from fastmcp import FastMCP
from fastmcp.dependencies import Progress


async def generate_meal_plan_impl(
    days: int,
    preferences: list[str],
    progress: Progress,
) -> dict:
    """Generate meal plan with progress reporting.

    Args:
        days: Number of days to plan (0 returns empty plan)
        preferences: Dietary preferences or cuisine types for recipe search
        progress: FastMCP Progress dependency for streaming updates

    Returns:
        dict: {"days": int, "preferences": list, "meal_plan": list[dict]}

    Raises:
        RuntimeError: API error during recipe search
    """
    from src.server import get_pantry_client  # Import at runtime to avoid circular

    client = get_pantry_client()
    await progress.set_total(days)
    meal_plan = []

    for day in range(days):
        await progress.set_message(f"Planning day {day + 1}/{days}...")
        query = preferences[0] if preferences else ""
        data = await client.get("/recipes", params={"query": query, "limit": 1})
        recipes = data.get("recipes", [])
        recipe_name = recipes[0]["name"] if recipes else "No recipe found"
        meal_plan.append({"day": day + 1, "recipe": recipe_name})
        await progress.increment()

    return {"days": days, "preferences": preferences, "meal_plan": meal_plan}


def register(mcp: FastMCP) -> None:
    """Register generate_meal_plan task tool with FastMCP instance."""

    @mcp.tool(task=True)
    async def generate_meal_plan(
        days: int,
        preferences: list[str],
        progress: Progress = Progress(),  # noqa: B008
    ) -> dict:
        """Generate a meal plan for the specified number of days.

        Long-running task with progress reporting. Searches for recipes matching
        your dietary preferences and composes a daily meal plan.

        Args:
            days: Number of days to generate plan for (0-30)
            preferences: Cuisine or dietary preferences (e.g., ["Italian", "vegetarian"])

        Returns:
            Meal plan with recipe assignments for each day
        """
        return await generate_meal_plan_impl(days, preferences, progress)
