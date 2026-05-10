"""Unit tests for recipe_resource - MockTransport pattern (ADR-006 Hybrid C)."""

import json
from unittest.mock import MagicMock

import httpx
import pytest

from src.config import APIConfig, Settings
from src.pantry_client import PantryClient
from src.resources.recipe_resource import recipe_resource_impl, register


@pytest.fixture
def mock_settings():
    return Settings(
        dev_mode=True,
        api=APIConfig(base_url="http://test.local", api_key=""),
    )


@pytest.mark.asyncio
async def test_recipe_resource_success(mock_settings, monkeypatch):
    """recipe_resource_impl returns Recipe model on 200 OK."""

    def handler(request):
        assert request.url.path == "/recipes/1"
        return httpx.Response(
            200,
            json={
                "id": "1",
                "name": "Spaghetti Carbonara",
                "ingredients": ["pasta", "eggs", "bacon"],
                "instructions": "Boil pasta. Mix eggs and bacon. Combine.",
                "cuisine": "Italian",
                "prep_time_minutes": 30,
            },
        )

    transport = httpx.MockTransport(handler)
    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=transport, base_url="http://test.local"
    )

    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    recipe = await recipe_resource_impl("1")

    assert recipe.id == "1"
    assert recipe.name == "Spaghetti Carbonara"
    assert recipe.cuisine == "Italian"

    await client.aclose()


@pytest.mark.asyncio
async def test_recipe_resource_not_found_raises(mock_settings, monkeypatch):
    """recipe_resource_impl raises FileNotFoundError on 404."""

    def handler(request):
        return httpx.Response(404, json={"detail": "Not found"})

    transport = httpx.MockTransport(handler)
    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=transport, base_url="http://test.local"
    )

    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(FileNotFoundError):
        await recipe_resource_impl("999")

    await client.aclose()


def test_register_callable_accepts_mcp_instance():
    """register() should call mcp.resource(...) decorator."""
    mcp = MagicMock()
    register(mcp)
    assert mcp.resource.called
