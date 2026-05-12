"""Security tests — SecretStr, OTel masking, dev_mode warning, OAuth validator.

Covers security batch sub-tasks:
  4a: SecretStr prevents api_key from leaking in repr/dump
  4b: OTel header masking replaces Authorization value with ***MASKED***
  4c: dev_mode warning printed to stderr at boot
  4d: OAuth boot validator raises on enabled=True without issuer (already in test_config.py)
"""

from unittest.mock import MagicMock

import httpx
import pytest
from opentelemetry.instrumentation.httpx import RequestInfo

from src.config import APIConfig, Settings
from src.telemetry import _mask_auth_header

# --- 4b: OTel header masking ---


@pytest.mark.asyncio
async def test_otel_masking_hook_masks_authorization():
    """_mask_auth_header replaces Authorization header value with ***MASKED***."""
    span = MagicMock()
    request_info = RequestInfo(
        method=b"GET",
        url=httpx.URL("http://localhost:8001/recipes"),
        headers=httpx.Headers({"authorization": "Bearer actual-api-key-secret"}),
        stream=None,
        extensions=None,
    )

    await _mask_auth_header(span, request_info)

    span.set_attribute.assert_called_once_with("http.request.header.authorization", "***MASKED***")
    for call in span.set_attribute.call_args_list:
        assert "actual-api-key-secret" not in str(call.args)


@pytest.mark.asyncio
async def test_otel_masking_hook_no_auth_header_no_attribute():
    """_mask_auth_header does nothing when Authorization header is absent."""
    span = MagicMock()
    request_info = RequestInfo(
        method=b"GET",
        url=httpx.URL("http://localhost:8001/recipes"),
        headers=httpx.Headers({"content-type": "application/json"}),
        stream=None,
        extensions=None,
    )

    await _mask_auth_header(span, request_info)

    span.set_attribute.assert_not_called()


@pytest.mark.asyncio
async def test_otel_masking_hook_none_headers():
    """_mask_auth_header handles None headers gracefully."""
    span = MagicMock()
    request_info = RequestInfo(
        method=b"GET",
        url=httpx.URL("http://localhost:8001/recipes"),
        headers=None,
        stream=None,
        extensions=None,
    )

    await _mask_auth_header(span, request_info)

    span.set_attribute.assert_not_called()


# --- 4c: dev_mode warning to stderr ---


def test_dev_mode_warning_printed_to_stderr(capsys):
    """Settings with dev_mode=True prints security warning to stderr."""
    Settings(
        dev_mode=True,
        api=APIConfig(base_url="http://localhost:8001", api_key="test-key"),
    )
    captured = capsys.readouterr()
    assert "dev_mode" in captured.err.lower()


def test_dev_mode_false_no_warning_to_stderr(capsys, monkeypatch):
    """Settings with dev_mode=False does not print dev_mode warning."""
    monkeypatch.setenv("PANTRY_DEV_MODE", "false")
    monkeypatch.setenv("PANTRY_API__API_KEY", "prod-secret-key")
    Settings()
    captured = capsys.readouterr()
    assert "dev_mode" not in captured.err.lower()


# --- 4a: SecretStr prevents leakage (supplement to test_config.py) ---


def test_api_key_secretstr_not_in_settings_repr():
    """api_key SecretStr is masked in Settings repr — no key leak in logs."""
    settings = Settings(
        dev_mode=True,
        api=APIConfig(base_url="http://localhost:8001", api_key="super-secret-key"),
    )
    assert "super-secret-key" not in repr(settings)
    assert "super-secret-key" not in str(settings.model_dump())
