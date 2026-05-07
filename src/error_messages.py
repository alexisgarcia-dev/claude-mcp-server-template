"""Agent-friendly error messages.

Each constant is a .format()-compatible template that tells the agent both
what went wrong and what to do next — reducing LLM retry loops caused by
opaque HTTP status codes.
"""


class ErrorMessages:
    """String constants for user- and agent-facing error messages."""

    RESOURCE_NOT_FOUND: str = (
        "Resource {resource_type} not found at {path}. "
        "Use search_recipes to list available recipes."
    )
    AUTH_EXPIRED: str = "Authentication expired. Check your API key in settings."
    FORBIDDEN: str = "Access denied. Verify your permissions for this resource."
    VALIDATION_ERROR: str = "Validation error: {detail}. Check input parameters."
    API_ERROR: str = (
        "API error (HTTP {status}): {message}. Retry or check server status."
    )
    SEARCH_NO_RESULTS: str = (
        "No results found for '{query}'. Try broader search terms."
    )
    INVALID_CURSOR: str = "Invalid pagination cursor. Start a new search."
    BULK_PARTIAL_FAILURE: str = (
        "Bulk operation: {success_count} succeeded, {failure_count} failed. "
        "Failed IDs: {failed_ids}"
    )
    TASK_NOT_FOUND: str = (
        "Task {task_id} not found. It may have expired or been cancelled."
    )
    TASK_FAILED: str = "Task {task_id} failed: {error}. Check logs for details."
    CONFIG_MISSING_API_KEY: str = (
        "API key not configured. Set PANTRY_API__API_KEY or add to config.toml."
    )
    CONFIG_INVALID_URL: str = (
        "Invalid API URL: {url}. Expected format: http(s)://host:port"
    )
