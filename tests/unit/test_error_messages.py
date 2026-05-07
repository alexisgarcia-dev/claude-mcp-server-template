"""Tests for ErrorMessages constants."""

import inspect

from src.error_messages import ErrorMessages


def _all_constants() -> list[tuple[str, str]]:
    return [
        (name, value)
        for name, value in inspect.getmembers(ErrorMessages)
        if name.isupper() and isinstance(value, str)
    ]


def test_all_constants_exist_and_are_strings() -> None:
    expected = {
        "RESOURCE_NOT_FOUND",
        "AUTH_EXPIRED",
        "FORBIDDEN",
        "VALIDATION_ERROR",
        "API_ERROR",
        "SEARCH_NO_RESULTS",
        "INVALID_CURSOR",
        "BULK_PARTIAL_FAILURE",
        "TASK_NOT_FOUND",
        "TASK_FAILED",
        "CONFIG_MISSING_API_KEY",
        "CONFIG_INVALID_URL",
    }
    actual = {name for name, _ in _all_constants()}
    assert expected == actual
    for _, value in _all_constants():
        assert isinstance(value, str)
        assert len(value) > 0


def test_resource_not_found_format() -> None:
    msg = ErrorMessages.RESOURCE_NOT_FOUND.format(
        resource_type="recipe", path="/recipes/42"
    )
    assert "recipe" in msg
    assert "/recipes/42" in msg
    assert "search_recipes" in msg


def test_bulk_partial_failure_format() -> None:
    msg = ErrorMessages.BULK_PARTIAL_FAILURE.format(
        success_count=7, failure_count=3, failed_ids="[101, 102, 103]"
    )
    assert "7" in msg
    assert "3" in msg
    assert "[101, 102, 103]" in msg
