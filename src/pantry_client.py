"""Shared HTTP client for PantryAPI with auth, retry, and error handling.

Centralized middleware pattern: all 6 primitives import this client instead of
repeating auth/retry logic. Lifecycle managed by server.py lifespan.

Retry strategy: tenacity AsyncRetrying (not httpx native, which only retries ConnectError).

See: docs/design-v0.1.0.md §3
"""

from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

from src.config import Settings
from src.error_messages import ErrorMessages


def _is_retryable(e: BaseException) -> bool:
    """Retry on connection errors, timeouts, 429, and 5xx."""
    if isinstance(e, (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout)):
        return True
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code == 429 or e.response.status_code >= 500
    return False


class PantryClient:
    """Shared HTTP client for PantryAPI with auth, retry, and error handling."""

    def __init__(self, config: Settings):
        self.config = config
        self.base_url = str(config.api.base_url)
        self.timeout = config.api.timeout

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build auth headers from config.

        NOTE: v0.1.0 supports static API key auth only.
        OAuth client_credentials flow with token refresh ships in v0.2.0.
        The auth/oauth_middleware.py file contains the v0.2.0 integration scaffolding.
        """
        headers = {"Content-Type": "application/json"}

        api_key = self.config.api.api_key.get_secret_value()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        return headers

    async def _request_with_retry(self, method: str, path: str, **kwargs: Any) -> Any:
        """Execute HTTP request with retry on transient failures."""
        async for attempt in AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self.config.api.max_retries + 1),
            wait=wait_random_exponential(multiplier=1, max=10),
            reraise=True,
        ):
            with attempt:
                response = await self.client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()

    async def get(self, path: str, **kwargs: Any) -> Any:
        """GET request with automatic error mapping."""
        try:
            return await self._request_with_retry("GET", path, **kwargs)
        except httpx.HTTPStatusError as e:
            raise self._map_http_error(e, path) from e

    async def post(self, path: str, **kwargs: Any) -> Any:
        """POST request with automatic error mapping."""
        try:
            return await self._request_with_retry("POST", path, **kwargs)
        except httpx.HTTPStatusError as e:
            raise self._map_http_error(e, path) from e

    async def put(self, path: str, **kwargs: Any) -> Any:
        """PUT request with automatic error mapping."""
        try:
            return await self._request_with_retry("PUT", path, **kwargs)
        except httpx.HTTPStatusError as e:
            raise self._map_http_error(e, path) from e

    def _map_http_error(self, error: httpx.HTTPStatusError, path: str) -> Exception:
        """Map HTTP error to Python stdlib exception with agent-friendly message.

        Called after retries are exhausted. Always maps to a stdlib exception.
        """
        status = error.response.status_code

        # Map to stdlib exceptions with agent-friendly messages
        if status == 404:
            resource_type = path.split("/")[1] if "/" in path else "resource"
            return FileNotFoundError(
                ErrorMessages.RESOURCE_NOT_FOUND.format(
                    resource_type=resource_type, path=path
                )
            )

        if status in (401, 403):
            return PermissionError(
                ErrorMessages.AUTH_EXPIRED
                if status == 401
                else ErrorMessages.FORBIDDEN
            )

        if status == 422:
            try:
                detail = error.response.json().get("detail", "Invalid input")
            except Exception:
                detail = error.response.text[:200]
            return ValueError(ErrorMessages.VALIDATION_ERROR.format(detail=detail))

        # 429, 5xx, and any other errors map to RuntimeError
        return RuntimeError(
            ErrorMessages.API_ERROR.format(
                status=status, message=error.response.text[:200]
            )
        )

    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
