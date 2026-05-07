"""Unit tests for src/pantry_client.py — HTTP client with retry and error mapping."""

import httpx
import pytest
from pydantic import SecretStr

from src.config import APIConfig, Settings
from src.pantry_client import PantryClient


@pytest.fixture
def mock_settings():
    """Create test settings with dev_mode enabled."""
    return Settings(
        dev_mode=True,
        api=APIConfig(
            base_url="http://localhost:8001",
            api_key=SecretStr("test-key-123"),
            timeout=30,
            max_retries=3,
        ),
    )


@pytest.mark.asyncio
async def test_get_success(mock_settings):
    """GET request succeeds and returns JSON."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key-123"
        return httpx.Response(200, json={"id": "123", "name": "Test Recipe"})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
        headers=client._build_headers(),
    )

    result = await client.get("/recipes/123")
    assert result == {"id": "123", "name": "Test Recipe"}

    await client.aclose()


@pytest.mark.asyncio
async def test_get_404_maps_to_filenotfounderror(mock_settings):
    """GET 404 raises FileNotFoundError with agent-friendly message."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not found"})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    with pytest.raises(FileNotFoundError, match="Resource recipes not found at /recipes/999"):
        await client.get("/recipes/999")

    await client.aclose()


@pytest.mark.asyncio
async def test_get_401_maps_to_permissionerror(mock_settings):
    """GET 401 raises PermissionError (auth expired)."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Unauthorized"})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    with pytest.raises(PermissionError, match="Authentication expired"):
        await client.get("/recipes/123")

    await client.aclose()


@pytest.mark.asyncio
async def test_get_422_maps_to_valueerror(mock_settings):
    """GET 422 raises ValueError with validation detail."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Invalid recipe_id format"})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    with pytest.raises(ValueError, match="Validation error: Invalid recipe_id format"):
        await client.get("/recipes/invalid")

    await client.aclose()


@pytest.mark.asyncio
async def test_post_success(mock_settings):
    """POST request succeeds and returns JSON."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(201, json={"id": "456", "status": "created"})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    result = await client.post("/recipes", json={"name": "New Recipe"})
    assert result == {"id": "456", "status": "created"}

    await client.aclose()


@pytest.mark.asyncio
async def test_retry_on_500(mock_settings):
    """500 error triggers retry, succeeds on 2nd attempt."""
    attempt_count = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count == 1:
            return httpx.Response(500, text="Server error")
        return httpx.Response(200, json={"recovered": True})

    client = PantryClient(mock_settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    result = await client.get("/recipes/123")
    assert result == {"recovered": True}
    assert attempt_count == 2  # First failed, second succeeded

    await client.aclose()


@pytest.mark.asyncio
async def test_retry_exhausted_raises_runtimeerror(mock_settings):
    """500 error exhausts retries and raises RuntimeError."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Persistent server error")

    # Set max_retries=1 for faster test
    settings = Settings(
        dev_mode=True,
        api=APIConfig(
            base_url="http://localhost:8001",
            api_key=SecretStr("test-key"),
            max_retries=1,
        ),
    )
    client = PantryClient(settings)
    client.client = httpx.AsyncClient(
        transport=httpx.MockTransport(mock_handler),
        base_url=client.base_url,
    )

    with pytest.raises(RuntimeError, match="API error .* 500"):
        await client.get("/recipes/123")

    await client.aclose()


@pytest.mark.asyncio
async def test_build_headers_includes_api_key(mock_settings):
    """Headers include Bearer token from api_key."""
    client = PantryClient(mock_settings)
    headers = client._build_headers()

    assert headers["Authorization"] == "Bearer test-key-123"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_build_headers_no_api_key_when_empty(mock_settings):
    """Headers omit Authorization when api_key is empty."""
    settings = Settings(
        dev_mode=True,
        api=APIConfig(base_url="http://localhost:8001", api_key=SecretStr("")),
    )
    client = PantryClient(settings)
    headers = client._build_headers()

    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"
