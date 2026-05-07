"""Tool #3: Update Pantry (Bulk POST).

Update pantry inventory in bulk. Returns partial failure tracking.
Demonstrates bulk pattern with structured error handling.

See: docs/design-v0.1.0.md §4.3
"""

from fastmcp import FastMCP

from src.models import BulkUpdateResult, PantryItem


async def update_pantry_impl(items: list[PantryItem]) -> BulkUpdateResult:
    """Send bulk pantry update to PantryAPI.

    Args:
        items: List of pantry items to update (name, quantity >= 0, unit)

    Returns:
        BulkUpdateResult: success_count, failure_count, failed_ids

    Raises:
        PermissionError: Authentication failed (401/403)
        RuntimeError: API error (5xx after retries exhausted)
    """
    from src.server import get_pantry_client  # Import at runtime to avoid circular

    client = get_pantry_client()
    payload = {"items": [item.model_dump(mode="json") for item in items]}
    data = await client.post("/pantry/bulk", json=payload)

    failures = data.get("failures", [])
    success_list = data.get("success", [])
    return BulkUpdateResult(
        success_count=len(success_list),
        failure_count=len(failures),
        failed_ids=[str(f["id"]) for f in failures],
    )


def register(mcp: FastMCP) -> None:
    """Register update_pantry tool with FastMCP instance."""

    @mcp.tool()
    async def update_pantry(items: list[PantryItem]) -> dict:
        """Update pantry inventory in bulk.

        Send multiple pantry item updates in a single request. Returns counts
        of successful and failed updates with IDs of any failures.

        Args:
            items: List of pantry items to update. Each item requires:
                   name (str), quantity (int >= 0), unit (str)

        Returns:
            Bulk result with success_count, failure_count, and failed_ids list
        """
        result = await update_pantry_impl(items)
        return result.model_dump(mode="json")
