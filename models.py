"""
Bandhu AI - Pydantic Data Models
================================

Defines Pydantic schemas for structured LLM response output parsing.
Provides schemas for educational formulas/diagrams and agricultural action steps.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    """Labeled concept item for educational diagrams (e.g. Base, Height)."""

    label: str = Field(description="Concept label name")
    desc: str = Field(description="Explanation or definition of the concept")


class RichData(BaseModel):
    """Structured payload for rendering interactive UI cards on the frontend."""

    type: Literal["education", "farming", "health"] = Field(
        description="Category card type"
    )
    title: str = Field(description="Title of the structured card")
    diagram_type: Optional[str] = Field(
        default=None, description="SVG visual diagram key (e.g. triangle, circle, rectangle)"
    )
    content: Optional[list[ContentItem]] = Field(
        default=None, description="Education only: labeled concept breakdown items."
    )
    formula: Optional[str] = Field(
        default=None, description="Education only: mathematical formula string."
    )
    points: Optional[list[str]] = Field(
        default=None, description="Farming/Health only: concise bullet points or action steps."
    )


class ChatOutput(BaseModel):
    """Root model for LLM structured output parsing."""

    response: str = Field(description="The conversational text reply in requested language.")
    rich_data: Optional[RichData] = Field(
        default=None,
        description=(
            "Only include when the answer benefits from a structured card "
            "(a formula/diagram, or a checklist of steps/points). Omit for simple conversational replies."
        ),
    )
