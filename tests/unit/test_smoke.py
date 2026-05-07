"""Smoke test -- guarantees pytest discovery + sprint.ps1 commit pipeline works.

Will be replaced/expanded J13 14h+ as actual tests are written for config.py,
pantry_client.py, and Tool #1 get_recipe.
"""


def test_smoke() -> None:
    """Trivial test to keep pytest green during sprint setup phase."""
    assert True
