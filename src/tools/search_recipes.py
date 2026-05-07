"""Tool #2: Search Recipes.

Search recipes by query with optional cuisine filter.
Demonstrates pagination pattern + manual OTel span (pedagogical).

See: docs/design-v0.1.0.md §4.2
"""

from fastmcp import FastMCP
from opentelemetry import trace

from src.models import SearchResult

# Get tracer for manual spans (pedagogical demonstration)
tracer = trace.get_tracer(__name__)


async def search_recipes_impl(
    query: str = "",
    cuisine: str | None = None,
    limit: int = 10,
    cursor: str | None = None,
) -> SearchResult:
    """Search recipes by query with optional filters.

    Args:
        query: Search term to match against recipe names (case-insensitive)
        cuisine: Optional cuisine filter (e.g., "Italian", "Indian")
        limit: Maximum number of results to return (default 10, max 100)
        cursor: Pagination cursor from previous search result (optional)

    Returns:
        SearchResult: Container with recipes list, total count, and next_cursor

    Raises:
        ValueError: Invalid cursor or limit out of range
        PermissionError: Authentication failed (401/403)
        RuntimeError: API error (5xx after retries exhausted)
    """
    from src.server import get_pantry_client  # Import at runtime to avoid circular

    # Manual OTel span for pedagogical demonstration
    with tracer.start_as_current_span(
        "search_recipes",
        attributes={
            "query": query,
            "cuisine": cuisine or "all",
            "limit": limit,
        },
    ):
        client = get_pantry_client()

        # Validate limit
        if limit < 1 or limit > 100:
            raise ValueError(
                "limit must be between 1 and 100. "
                f"Current value: {limit}. Adjust the parameter and retry."
            )

        # Build query params
        params = {
            "query": query,
            "limit": limit,
        }
        if cuisine:
            params["cuisine"] = cuisine
        if cursor:
            params["cursor"] = cursor

        data = await client.get("/recipes", params=params)
        return SearchResult(**data)


def register(mcp: FastMCP) -> None:
    """Register search_recipes tool with FastMCP instance.

    Called from server.py after mcp instance creation.
    Pattern avoids circular import from @mcp.tool() at module level.
    """

    @mcp.tool()
    async def search_recipes(
        query: str = "",
        cuisine: str | None = None,
        limit: int = 10,
        cursor: str | None = None,
    ) -> dict:
        """Search for recipes by query and filters.

        Find recipes matching your search criteria. Use cuisine parameter to filter by type.

        Args:
            query: Search term to match recipe names (e.g., "pasta", "chicken")
            cuisine: Filter by cuisine type (e.g., "Italian", "Indian", "American")
            limit: Maximum recipes to return (1-100, default 10)
            cursor: Pagination cursor from previous result (optional)

        Returns:
            Search results with recipes list, total count, and pagination cursor
        """
        result = await search_recipes_impl(query, cuisine, limit, cursor)
        return result.model_dump(mode="json")
