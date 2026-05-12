"""Unit tests for src/tools/get_recipe.py — Tool #1 get_recipe."""

import httpx
import pytest

from src.config import APIConfig, Settings
from src.models import Recipe
from src.pantry_client import PantryClient
from src.tools.get_recipe import get_recipe_impl


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


@pytest.mark.asyncio
async def test_get_recipe_success(mock_pantry_client, monkeypatch):
    """get_recipe fetches recipe by ID and returns Recipe model."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/recipes/123"
        return httpx.Response(
            200,
            json={
                "id": "123",
                "name": "Test Recipe",
                "ingredients": ["flour", "sugar"],
                "instructions": "Mix and bake.",
                "cuisine": "Test",
                "prep_time_minutes": 30,
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    recipe = await get_recipe_impl("123")

    assert isinstance(recipe, Recipe)
    assert recipe.id == "123"
    assert recipe.name == "Test Recipe"
    assert recipe.ingredients == ["flour", "sugar"]
    assert recipe.cuisine == "Test"

    await client.aclose()


@pytest.mark.asyncio
async def test_get_recipe_not_found_raises_filenotfounderror(mock_pantry_client, monkeypatch):
    """get_recipe raises FileNotFoundError when recipe doesn't exist (404)."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not found"})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(FileNotFoundError, match="Resource recipes not found at /recipes/999"):
        await get_recipe_impl("999")

    await client.aclose()


@pytest.mark.asyncio
async def test_get_recipe_auth_error_raises_permissionerror(mock_pantry_client, monkeypatch):
    """get_recipe raises PermissionError when auth fails (401)."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Unauthorized"})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(PermissionError, match="Authentication expired"):
        await get_recipe_impl("123")

    await client.aclose()
