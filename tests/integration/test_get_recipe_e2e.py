"""Integration test for get_recipe — end-to-end against pantry_mock_api.

NOTE: Requires pantry_mock_api.py running on localhost:8001
Start with: uv run uvicorn pantry_mock_api:app --port 8001

If port conflict, update config.toml base_url to match (8011/8021).
"""

import pytest

from src.config import APIConfig, Settings
from src.pantry_client import PantryClient
from src.tools.get_recipe import get_recipe_impl


@pytest.fixture
async def live_client():
    """Create PantryClient against real mock API on localhost:8001."""
    settings = Settings(
        dev_mode=True,
        api=APIConfig(
            base_url="http://localhost:8001",
            api_key="",  # Mock API doesn't validate auth
        ),
    )
    client = PantryClient(settings)
    yield client
    await client.aclose()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recipe_e2e_against_mock_api(live_client, monkeypatch):
    """get_recipe fetches real recipe from pantry_mock_api.

    Recipe ID "1" is seeded in pantry_mock_api.py as "Spaghetti Carbonara".
    """
    monkeypatch.setattr("src.server.get_pantry_client", lambda: live_client)

    recipe = await get_recipe_impl("1")

    assert recipe.id == "1"
    assert recipe.name == "Spaghetti Carbonara"
    assert "pasta" in recipe.ingredients
    assert recipe.cuisine == "Italian"
    assert recipe.prep_time_minutes == 30


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recipe_e2e_not_found(live_client, monkeypatch):
    """get_recipe raises FileNotFoundError for non-existent recipe."""
    monkeypatch.setattr("src.server.get_pantry_client", lambda: live_client)

    with pytest.raises(FileNotFoundError, match="Resource recipes not found"):
        await get_recipe_impl("999999")
