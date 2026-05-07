"""Shared Pydantic models for PantryMCP.

Single source of truth for data models used across tools, resources, and prompts.
Avoids FastMCP schema generation duplication.
"""

from pydantic import BaseModel, Field


class PantryItem(BaseModel):
    """Pantry inventory item for bulk update operations."""

    name: str
    quantity: int = Field(ge=0)
    unit: str


class Recipe(BaseModel):
    """Recipe model matching PantryAPI schema."""

    id: str
    name: str
    ingredients: list[str]
    instructions: str
    cuisine: str | None = None
    prep_time_minutes: int | None = None


class SearchResult(BaseModel):
    """Search results container with pagination."""

    recipes: list[Recipe]
    total: int
    next_cursor: str | None = None


class BulkUpdateResult(BaseModel):
    """Bulk operation result with partial failure tracking."""

    success_count: int
    failure_count: int
    failed_ids: list[str] = Field(default_factory=list)


class MealPlan(BaseModel):
    """Generated meal plan for Tool #4 (Tasks primitive)."""

    days: list[str]
    recipes: list[Recipe]
    shopping_list: list[str]
    total_prep_time_minutes: int
