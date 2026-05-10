"""PantryAPI mock - standalone FastAPI app for the v0.1.0 demo stack.

Seeded with 3 recipes (varied cuisines for weekly_planner prompt demo) matching
the integration test in tests/integration/test_get_recipe_e2e.py.

Run standalone:
    uv run uvicorn pantry_mock_api:app --port 8001

Or via docker-compose:
    docker-compose up pantry-mock
"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="PantryAPI Mock", version="0.1.0")

# Seed data - id="1" Spaghetti Carbonara required by integration test.
# `instructions` is a required field on the Recipe model (src/models.py).
_RECIPES: dict[str, dict] = {
    "1": {
        "id": "1",
        "name": "Spaghetti Carbonara",
        "ingredients": ["pasta", "eggs", "bacon", "parmesan", "black pepper"],
        "instructions": (
            "Boil pasta until al dente. Fry bacon until crisp. "
            "Whisk eggs with parmesan and black pepper. "
            "Combine drained pasta with bacon, then off-heat fold in egg mixture."
        ),
        "cuisine": "Italian",
        "prep_time_minutes": 30,
    },
    "2": {
        "id": "2",
        "name": "Vegetable Stir-Fry",
        "ingredients": ["broccoli", "bell pepper", "tofu", "soy sauce", "ginger"],
        "instructions": (
            "Cube tofu and pan-sear until golden. Stir-fry broccoli and bell pepper "
            "with grated ginger over high heat. Add tofu and soy sauce; toss to coat."
        ),
        "cuisine": "Asian",
        "prep_time_minutes": 20,
    },
    "3": {
        "id": "3",
        "name": "Greek Salad",
        "ingredients": ["cucumber", "tomato", "feta", "olives", "olive oil"],
        "instructions": (
            "Dice cucumber and tomato. Combine with crumbled feta and olives. "
            "Dress with olive oil and serve immediately."
        ),
        "cuisine": "Greek",
        "prep_time_minutes": 10,
    },
}

_PANTRY: dict[str, int] = {
    "pasta": 500,
    "eggs": 12,
    "bacon": 200,
}


@app.get("/")
async def root() -> dict[str, str]:
    """Liveness probe (HEAD-compatible). Used by Docker healthcheck."""
    return {"service": "pantry-api-mock", "version": "0.1.0", "status": "ok"}


@app.head("/")
async def root_head() -> None:
    """HEAD support for healthcheck and PantryClient pings."""
    return None


@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str) -> dict:
    if recipe_id not in _RECIPES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource recipes not found: {recipe_id}",
        )
    return _RECIPES[recipe_id]


@app.get("/recipes")
async def search_recipes(
    query: str = "",
    cuisine: str | None = None,
    limit: int = 10,
    cursor: str | None = None,
) -> dict:
    results = list(_RECIPES.values())
    if cuisine:
        results = [r for r in results if r["cuisine"].lower() == cuisine.lower()]
    if query:
        q = query.lower()
        results = [r for r in results if q in r["name"].lower()]
    sliced = results[:limit]
    return {"recipes": sliced, "total": len(results), "next_cursor": None}


@app.get("/pantry")
async def get_pantry() -> dict:
    return {"items": [{"name": k, "quantity": v} for k, v in _PANTRY.items()]}


@app.post("/pantry/bulk")
async def update_pantry_bulk(payload: dict) -> dict:
    """Bulk pantry update matching the contract in src/tools/update_pantry.py.

    Request:  {"items": [{"name": str, "quantity": int, "unit": str}, ...]}
    Response: {"success": [name, ...], "failures": [{"id": name, "error": str}, ...]}
    """
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'items' must be a list",
        )

    success: list[str] = []
    failures: list[dict] = []

    for item in items:
        name = item.get("name")
        qty = item.get("quantity", 0)

        if not isinstance(name, str) or not name.strip():
            failures.append({"id": str(name), "error": "name must be a non-empty string"})
            continue
        if not isinstance(qty, int) or qty < 0:
            failures.append({"id": name, "error": f"invalid quantity {qty} (must be int >= 0)"})
            continue

        _PANTRY[name] = qty
        success.append(name)

    return {"success": success, "failures": failures}
