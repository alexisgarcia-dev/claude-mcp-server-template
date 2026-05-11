"""Unit tests for dry-run mode in PantryClient.

See .superpowers/specs/2026-05-11-dry-run-mode-design.md §4 Task 3
"""

import json
from unittest.mock import AsyncMock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from src.config import Settings
from src.pantry_client import PantryClient

_OTEL_STATE: dict[str, object] = {}


@pytest.fixture
def otel_setup():
    """Per-test OTel isolation.

    `trace.set_tracer_provider` is a process-level singleton (subsequent calls
    are silently no-ops), so we lazily install one TracerProvider+exporter pair
    on first use, then clear the exporter between tests for isolation.
    """
    if "exporter" not in _OTEL_STATE:
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _OTEL_STATE["exporter"] = exporter
        _OTEL_STATE["provider"] = provider
    exporter = _OTEL_STATE["exporter"]
    provider = _OTEL_STATE["provider"]
    exporter.clear()
    yield exporter, provider
    exporter.clear()


@pytest.mark.asyncio
async def test_dry_run_disabled_by_default(monkeypatch):
    """Dry-run disabled by default: HTTP request proceeds normally."""
    monkeypatch.delenv("PANTRY_API__DRY_RUN", raising=False)
    monkeypatch.setenv("PANTRY_API__API_KEY", "test-key")
    settings = Settings()
    assert settings.api.dry_run is False

    client = PantryClient(settings)
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "name": "Test"}
    mock_response.raise_for_status.return_value = None
    client.client.request = AsyncMock(return_value=mock_response)

    await client.get("/recipes/1")

    assert client.client.request.call_count == 1
    await client.aclose()


@pytest.mark.asyncio
async def test_dry_run_intercepts_http(monkeypatch):
    """Dry-run enabled: HTTP short-circuited, sentinel dict returned."""
    monkeypatch.setenv("PANTRY_API__DRY_RUN", "true")
    monkeypatch.setenv("PANTRY_API__API_KEY", "test-key")
    settings = Settings()
    assert settings.api.dry_run is True

    client = PantryClient(settings)
    client.client.request = AsyncMock()

    result = await client.get("/recipes/1")

    assert client.client.request.call_count == 0
    assert result == {
        "_dry_run": True,
        "_method": "GET",
        "_path": "/recipes/1",
        "_payload_size": 0,
    }
    await client.aclose()


@pytest.mark.asyncio
async def test_dry_run_otel_preserved(monkeypatch, otel_setup):
    """Dry-run emits OTel span 'pantry.dry_run' with documented attributes."""
    exporter, provider = otel_setup
    monkeypatch.setenv("PANTRY_API__DRY_RUN", "true")
    monkeypatch.setenv("PANTRY_API__API_KEY", "test-key")
    settings = Settings()

    client = PantryClient(settings)
    client.client.request = AsyncMock()

    await client.post("/pantry/update", json={"item": "milk", "qty": 2})

    provider.force_flush()
    spans = exporter.get_finished_spans()

    pantry_dry_run_spans = [s for s in spans if s.name == "pantry.dry_run"]
    assert len(pantry_dry_run_spans) == 1

    span = pantry_dry_run_spans[0]
    assert span.attributes.get("mcp.dry_run") is True

    dry_run_events = [e for e in span.events if e.name == "dry_run.request"]
    assert len(dry_run_events) == 1

    event = dry_run_events[0]
    assert event.attributes.get("http.method") == "POST"
    assert event.attributes.get("http.url.path") == "/pantry/update"
    assert event.attributes.get("http.request.body.size") > 0
    preview = event.attributes.get("http.request.body.preview")
    assert preview is not None
    assert len(preview.encode("utf-8")) <= 2048

    await client.aclose()


@pytest.mark.asyncio
async def test_dry_run_scrubs_authorization_header(monkeypatch, otel_setup):
    """Sensitive headers must be redacted in the dry-run OTel event payload."""
    exporter, provider = otel_setup
    monkeypatch.setenv("PANTRY_API__DRY_RUN", "true")
    monkeypatch.setenv("PANTRY_API__API_KEY", "test-key")
    settings = Settings()

    client = PantryClient(settings)
    client.client.request = AsyncMock()

    secret_values = ("secret-key-123", "Bearer abc")

    await client.post(
        "/pantry/update",
        json={"item": "milk"},
        headers={"X-Api-Key": "secret-key-123", "Authorization": "Bearer abc"},
    )

    provider.force_flush()
    spans = exporter.get_finished_spans()
    pantry_dry_run_spans = [s for s in spans if s.name == "pantry.dry_run"]
    assert len(pantry_dry_run_spans) == 1
    span = pantry_dry_run_spans[0]

    dry_run_events = [e for e in span.events if e.name == "dry_run.request"]
    assert len(dry_run_events) == 1
    event = dry_run_events[0]

    raw_scrubbed = event.attributes.get("http.request.headers.scrubbed")
    assert raw_scrubbed is not None
    scrubbed = json.loads(raw_scrubbed)
    lc_scrubbed = {k.lower(): v for k, v in scrubbed.items()}
    assert lc_scrubbed.get("authorization") == "<redacted>"
    assert lc_scrubbed.get("x-api-key") == "<redacted>"

    def _stringify(value: object) -> str:
        return json.dumps(value, default=str)

    span_attr_blob = _stringify(dict(span.attributes or {}))
    for secret in secret_values:
        assert secret not in span_attr_blob
    for ev in span.events:
        ev_blob = _stringify(dict(ev.attributes or {}))
        for secret in secret_values:
            assert secret not in ev_blob

    await client.aclose()
