"""Unit tests for src/tools/generate_meal_plan.py — Tool #4 generate_meal_plan."""

import httpx
import pytest

from src.config import APIConfig, Settings
from src.pantry_client import PantryClient
from src.tools.generate_meal_plan import generate_meal_plan_impl


class MockProgress:
    """Minimal mock for fastmcp.dependencies.Progress in unit tests."""

    def __init__(self):
        self.total: int | None = None
        self.messages: list[str] = []
        self.increments: int = 0

    async def set_total(self, total: int) -> None:
        self.total = total

    async def set_message(self, message: str) -> None:
        self.messages.append(message)

    async def increment(self) -> None:
        self.increments += 1


@pytest.fixture
def mock_pantry_client(monkeypatch):
    """Create mock PantryClient with MockTransport."""

    def _create_client(handler):
        settings = Settings(
            dev_mode=True,
            api=APIConfig(
                base_url="http://localhost:8001",
                api_key="test-key",
            ),
        )
        client = PantryClient(settings)
        client.client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url=client.base_url,
        )
        return client

    return _create_client


def _recipe_response(name: str = "Pasta Carbonara") -> dict:
    return {
        "recipes": [
            {
                "id": "1",
                "name": name,
                "ingredients": ["pasta", "eggs"],
                "instructions": "Cook.",
                "cuisine": "Italian",
                "prep_time_minutes": 30,
            }
        ],
        "total": 1,
        "next_cursor": None,
    }


@pytest.mark.asyncio
async def test_generate_meal_plan_happy_path(mock_pantry_client, monkeypatch):
    """generate_meal_plan returns plan with correct day count."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_recipe_response())

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    result = await generate_meal_plan_impl(3, ["Italian"], progress)

    assert result["days"] == 3
    assert len(result["meal_plan"]) == 3
    assert result["meal_plan"][0]["day"] == 1
    assert result["meal_plan"][2]["day"] == 3

    await client.aclose()


@pytest.mark.asyncio
async def test_generate_meal_plan_days_zero(mock_pantry_client, monkeypatch):
    """generate_meal_plan with days=0 returns empty meal_plan."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_recipe_response())

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    result = await generate_meal_plan_impl(0, [], progress)

    assert result["days"] == 0
    assert result["meal_plan"] == []

    await client.aclose()


@pytest.mark.asyncio
async def test_generate_meal_plan_progress_reporting(mock_pantry_client, monkeypatch):
    """generate_meal_plan calls set_total, set_message, and increment correctly."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_recipe_response())

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    await generate_meal_plan_impl(3, ["Italian"], progress)

    assert progress.total == 3
    assert progress.increments == 3
    assert len(progress.messages) == 3
    assert progress.messages[0] == "Planning day 1/3..."
    assert progress.messages[2] == "Planning day 3/3..."

    await client.aclose()


@pytest.mark.asyncio
async def test_generate_meal_plan_preferences_filtering(mock_pantry_client, monkeypatch):
    """generate_meal_plan passes first preference as query param to recipe search."""

    received_queries = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        received_queries.append(params.get("query", ""))
        return httpx.Response(200, json=_recipe_response("Sushi"))

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    result = await generate_meal_plan_impl(2, ["Japanese"], progress)

    assert all(q == "Japanese" for q in received_queries)
    assert result["preferences"] == ["Japanese"]

    await client.aclose()


@pytest.mark.asyncio
async def test_generate_meal_plan_no_recipes_found(mock_pantry_client, monkeypatch):
    """generate_meal_plan uses fallback name when API returns no recipes."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"recipes": [], "total": 0, "next_cursor": None})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    result = await generate_meal_plan_impl(1, [], progress)

    assert result["meal_plan"][0]["recipe"] == "No recipe found"

    await client.aclose()


@pytest.mark.asyncio
async def test_generate_meal_plan_api_error_propagates(mock_pantry_client, monkeypatch):
    """generate_meal_plan propagates RuntimeError when API returns 500."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "Internal Server Error"})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    progress = MockProgress()
    with pytest.raises(RuntimeError, match="API error"):
        await generate_meal_plan_impl(1, [], progress)

    await client.aclose()
