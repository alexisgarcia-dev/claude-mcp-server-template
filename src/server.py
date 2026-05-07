"""MCP server entry point -- to be implemented J13 14h+."""
from fastmcp import FastMCP

mcp = FastMCP("PantryMCP")

# Tools/Resources/Prompts registration happens here:
# from src.tools import get_recipe, search_recipes, update_pantry, generate_meal_plan
# get_recipe.register(mcp)
# search_recipes.register(mcp)
# update_pantry.register(mcp)
# generate_meal_plan.register(mcp)

if __name__ == "__main__":
    mcp.run()
