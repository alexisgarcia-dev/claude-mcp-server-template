"""Unit tests for src/tools/search_recipes.py — Tool #2 search_recipes."""

import httpx
import pytest

from src.config import APIConfig, Settings
from src.models import SearchResult
from src.pantry_client import PantryClient
from src.tools.search_recipes import search_recipes_impl


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
async def test_search_recipes_success(mock_pantry_client, monkeypatch):
    """search_recipes returns SearchResult with recipes list."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/recipes"
        # Verify query params
        params = dict(request.url.params)
        assert params.get("query") == "pasta"
        assert params.get("limit") == "10"

        return httpx.Response(
            200,
            json={
                "recipes": [
                    {
                        "id": "1",
                        "name": "Spaghetti Carbonara",
                        "ingredients": ["pasta", "eggs", "bacon"],
                        "instructions": "Cook pasta. Mix with eggs.",
                        "cuisine": "Italian",
                        "prep_time_minutes": 30,
                    }
                ],
                "total": 1,
                "next_cursor": None,
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    result = await search_recipes_impl(query="pasta", limit=10)

    assert isinstance(result, SearchResult)
    assert len(result.recipes) == 1
    assert result.recipes[0].name == "Spaghetti Carbonara"
    assert result.total == 1
    assert result.next_cursor is None

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_with_cuisine_filter(mock_pantry_client, monkeypatch):
    """search_recipes filters by cuisine parameter."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        assert params.get("cuisine") == "Italian"

        return httpx.Response(
            200,
            json={
                "recipes": [
                    {
                        "id": "1",
                        "name": "Spaghetti Carbonara",
                        "ingredients": ["pasta", "eggs"],
                        "instructions": "Cook.",
                        "cuisine": "Italian",
                        "prep_time_minutes": 30,
                    }
                ],
                "total": 1,
                "next_cursor": None,
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    result = await search_recipes_impl(query="", cuisine="Italian", limit=10)

    assert len(result.recipes) == 1
    assert result.recipes[0].cuisine == "Italian"

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_empty_results(mock_pantry_client, monkeypatch):
    """search_recipes returns empty list when no matches found."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "recipes": [],
                "total": 0,
                "next_cursor": None,
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    result = await search_recipes_impl(query="nonexistent", limit=10)

    assert isinstance(result, SearchResult)
    assert len(result.recipes) == 0
    assert result.total == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_with_pagination_cursor(mock_pantry_client, monkeypatch):
    """search_recipes passes cursor parameter for pagination."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        assert params.get("cursor") == "page2"

        return httpx.Response(
            200,
            json={
                "recipes": [
                    {
                        "id": "3",
                        "name": "Pizza Margherita",
                        "ingredients": ["dough", "tomato", "mozzarella"],
                        "instructions": "Bake.",
                        "cuisine": "Italian",
                        "prep_time_minutes": 20,
                    }
                ],
                "total": 1,
                "next_cursor": None,
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    result = await search_recipes_impl(query="", cursor="page2", limit=10)

    assert len(result.recipes) == 1
    assert result.recipes[0].id == "3"

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_limit_validation_too_low(mock_pantry_client, monkeypatch):
    """search_recipes raises ValueError when limit < 1."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"recipes": [], "total": 0})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        await search_recipes_impl(query="test", limit=0)

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_limit_validation_too_high(mock_pantry_client, monkeypatch):
    """search_recipes raises ValueError when limit > 100."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"recipes": [], "total": 0})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        await search_recipes_impl(query="test", limit=101)

    await client.aclose()


@pytest.mark.asyncio
async def test_search_recipes_auth_error_raises_permissionerror(mock_pantry_client, monkeypatch):
    """search_recipes raises PermissionError when auth fails (401)."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Unauthorized"})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(PermissionError, match="Authentication expired"):
        await search_recipes_impl(query="test")

    await client.aclose()
