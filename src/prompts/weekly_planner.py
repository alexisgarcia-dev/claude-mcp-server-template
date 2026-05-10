"""Weekly meal planner prompt - guides agent to generate a 7-day plan.

Role-restricted per MCP 1.27 schema (PromptMessage.role enum: ['user', 'assistant'] only).
System context packed in first user message (mcp 1.27 pattern, source: docs/sources.md).

Demonstrates Prompt primitive end-to-end (only ~4% of public MCP servers ship Prompts, source: digitalapplied.com MCP Adoption Statistics 2026).

See: docs/design-v0.1.0.md §5
"""

from mcp.types import PromptMessage, TextContent


def register(mcp) -> None:
    """Register the weekly_planner prompt on the FastMCP instance."""

    @mcp.prompt(
        description=(
            "Generate a personalized 7-day meal plan based on dietary preferences. "
            "Uses search_recipes tool to find suitable options."
        ),
    )
    async def weekly_planner(
        dietary_preferences: str = "no restrictions",
        cuisine_focus: str = "varied",
    ) -> list[PromptMessage]:
        """Build the prompt message list for a weekly meal plan.

        Args:
            dietary_preferences: Free-text constraints (e.g. "vegetarian, no gluten").
            cuisine_focus: Cuisine emphasis (e.g. "Italian", "Asian", "varied").

        Returns:
            Single-message list with system context + task description packed in user role.
        """
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        "You are a meal planning assistant with access to a recipe API "
                        "via the search_recipes and get_recipe tools.\n\n"
                        f"Generate a 7-day meal plan covering breakfast, lunch, and dinner.\n"
                        f"Dietary preferences: {dietary_preferences}\n"
                        f"Cuisine focus: {cuisine_focus}\n\n"
                        "Workflow:\n"
                        "1. Call search_recipes for each meal slot with appropriate filters\n"
                        "2. Call get_recipe to fetch full details for selected items\n"
                        "3. Format the final plan as a markdown table with columns: "
                        "Day | Breakfast | Lunch | Dinner\n\n"
                        "Be concise. Avoid recipe duplication across the week."
                    ),
                ),
            )
        ]
