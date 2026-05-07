"""Unit tests for src/tools/update_pantry.py — Tool #3 update_pantry."""

import httpx
import pytest
from pydantic import ValidationError

from src.config import APIConfig, Settings
from src.models import BulkUpdateResult, PantryItem
from src.pantry_client import PantryClient
from src.tools.update_pantry import update_pantry_impl


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
async def test_update_pantry_all_success(mock_pantry_client, monkeypatch):
    """update_pantry returns all-success BulkUpdateResult when API succeeds."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/pantry/bulk"
        import json

        body = json.loads(request.content)
        assert "items" in body
        assert len(body["items"]) == 2

        return httpx.Response(
            200,
            json={
                "success": ["item-1", "item-2"],
                "failures": [],
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    items = [
        PantryItem(name="milk", quantity=2, unit="liters"),
        PantryItem(name="eggs", quantity=12, unit="units"),
    ]
    result = await update_pantry_impl(items)

    assert isinstance(result, BulkUpdateResult)
    assert result.success_count == 2
    assert result.failure_count == 0
    assert result.failed_ids == []

    await client.aclose()


@pytest.mark.asyncio
async def test_update_pantry_partial_failure(mock_pantry_client, monkeypatch):
    """update_pantry returns partial failure with failed_ids."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "success": ["item-1"],
                "failures": [{"id": "item-2", "error": "out of stock"}],
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    items = [
        PantryItem(name="milk", quantity=2, unit="liters"),
        PantryItem(name="eggs", quantity=12, unit="units"),
    ]
    result = await update_pantry_impl(items)

    assert result.success_count == 1
    assert result.failure_count == 1
    assert "item-2" in result.failed_ids

    await client.aclose()


@pytest.mark.asyncio
async def test_update_pantry_empty_list(mock_pantry_client, monkeypatch):
    """update_pantry handles empty items list (no-op)."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"success": [], "failures": []},
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    result = await update_pantry_impl([])

    assert result.success_count == 0
    assert result.failure_count == 0
    assert result.failed_ids == []

    await client.aclose()


def test_update_pantry_negative_quantity_validation():
    """PantryItem raises ValidationError on negative quantity (ge=0 constraint)."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        PantryItem(name="milk", quantity=-1, unit="liters")


@pytest.mark.asyncio
async def test_update_pantry_large_bulk_50_items(mock_pantry_client, monkeypatch):
    """update_pantry handles 50+ items in a single request."""

    received_count = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        import json

        body = json.loads(request.content)
        count = len(body["items"])
        received_count.append(count)
        return httpx.Response(
            200,
            json={
                "success": [f"item-{i}" for i in range(count)],
                "failures": [],
            },
        )

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    items = [PantryItem(name=f"item-{i}", quantity=i, unit="units") for i in range(55)]
    result = await update_pantry_impl(items)

    assert received_count[0] == 55
    assert result.success_count == 55
    assert result.failure_count == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_update_pantry_auth_error(mock_pantry_client, monkeypatch):
    """update_pantry raises PermissionError on 401 response."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Unauthorized"})

    client = mock_pantry_client(mock_handler)
    monkeypatch.setattr("src.server.get_pantry_client", lambda: client)

    with pytest.raises(PermissionError, match="Authentication expired"):
        await update_pantry_impl([PantryItem(name="milk", quantity=1, unit="liter")])

    await client.aclose()
