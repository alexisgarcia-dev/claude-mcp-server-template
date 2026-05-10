"""Unit tests for weekly_planner prompt - role schema compliance + structure."""

from unittest.mock import MagicMock

import pytest
from mcp.types import PromptMessage

from src.prompts.weekly_planner import register


def _capture_prompt_fn(mcp_mock):
    """Extract the function passed to @mcp.prompt(...) decorator."""
    register(mcp_mock)
    decorator_call = mcp_mock.prompt.call_args
    assert decorator_call is not None, "register() did not call mcp.prompt(...)"
    decorator = mcp_mock.prompt.return_value
    fn = decorator.call_args[0][0]
    return fn


@pytest.mark.asyncio
async def test_weekly_planner_returns_user_role_only():
    """PromptMessage.role MUST be 'user' or 'assistant' (mcp 1.27 schema)."""
    mcp = MagicMock()
    fn = _capture_prompt_fn(mcp)

    messages = await fn(dietary_preferences="vegan", cuisine_focus="Mediterranean")

    assert len(messages) == 1
    msg = messages[0]
    assert isinstance(msg, PromptMessage)
    assert msg.role in ("user", "assistant"), \
        f"role={msg.role!r} violates mcp 1.27 schema"


@pytest.mark.asyncio
async def test_weekly_planner_packs_system_context_in_user_message():
    """System context (assistant role + tools) must be packed in first user message."""
    mcp = MagicMock()
    fn = _capture_prompt_fn(mcp)

    messages = await fn()

    text = messages[0].content.text
    assert "search_recipes" in text
    assert "get_recipe" in text
    assert "7-day" in text or "7 day" in text


@pytest.mark.asyncio
async def test_weekly_planner_injects_user_preferences():
    """Dietary preferences and cuisine focus must appear verbatim in prompt."""
    mcp = MagicMock()
    fn = _capture_prompt_fn(mcp)

    messages = await fn(dietary_preferences="gluten-free", cuisine_focus="Japanese")

    text = messages[0].content.text
    assert "gluten-free" in text
    assert "Japanese" in text


def test_register_callable_accepts_mcp_instance():
    """register() should call mcp.prompt(...) decorator."""
    mcp = MagicMock()
    register(mcp)
    assert mcp.prompt.called
