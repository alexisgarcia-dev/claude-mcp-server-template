"""PantryAPI Mock Server for local testing.

Minimal FastAPI mock that implements recipe endpoints for MCP server integration tests.
Run with: uv run uvicorn pantry_mock_api:app --port 8001

Port conflict fallback: try 8011 or 8021 if 8001 is occupied.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="PantryAPI Mock", version="0.1.0")


class Recipe(BaseModel):
    """Recipe model matching src/models.py."""

    id: str
    name: str
    ingredients: list[str]
    instructions: str
    cuisine: str | None = None
    prep_time_minutes: int | None = None


# In-memory mock data
MOCK_RECIPES = {
    "1": Recipe(
        id="1",
        name="Spaghetti Carbonara",
        ingredients=["pasta", "eggs", "bacon", "parmesan"],
        instructions="Cook pasta. Fry bacon. Mix with eggs and cheese.",
        cuisine="Italian",
        prep_time_minutes=30,
    ),
    "2": Recipe(
        id="2",
        name="Caesar Salad",
        ingredients=["romaine lettuce", "croutons", "parmesan", "caesar dressing"],
        instructions="Toss lettuce with dressing. Add croutons and cheese.",
        cuisine="American",
        prep_time_minutes=15,
    ),
    "3": Recipe(
        id="3",
        name="Chicken Tikka Masala",
        ingredients=["chicken", "tomato sauce", "cream", "spices"],
        instructions="Marinate chicken. Cook in spiced tomato cream sauce.",
        cuisine="Indian",
        prep_time_minutes=45,
    ),
}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "PantryAPI Mock", "version": "0.1.0"}


@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get recipe by ID.

    Matches Tool #1 get_recipe endpoint.
    Returns 404 if recipe_id not found.
    """
    if recipe_id not in MOCK_RECIPES:
        raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")
    return MOCK_RECIPES[recipe_id].model_dump(mode="json")


@app.get("/recipes")
async def search_recipes(query: str = "", cuisine: str | None = None, limit: int = 10):
    """Search recipes by query and optional cuisine filter.

    Matches Tool #2 search_recipes endpoint.
    """
    results = list(MOCK_RECIPES.values())

    # Filter by query (case-insensitive name match)
    if query:
        results = [r for r in results if query.lower() in r.name.lower()]

    # Filter by cuisine
    if cuisine:
        results = [r for r in results if r.cuisine and r.cuisine.lower() == cuisine.lower()]

    # Limit results
    results = results[:limit]

    return {
        "recipes": [r.model_dump(mode="json") for r in results],
        "total": len(results),
        "next_cursor": None,  # Simplified: no pagination in v0.1.0 mock
    }


if __name__ == "__main__":
    import uvicorn

    # Run with: python pantry_mock_api.py
    # Or: uv run uvicorn pantry_mock_api:app --port 8001 --reload
    uvicorn.run(app, host="127.0.0.1", port=8001)
