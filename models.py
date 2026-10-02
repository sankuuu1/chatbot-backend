from typing import Literal, Optional
from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    label: str
    desc: str


class RichData(BaseModel):
    """Structured payload the frontend renders as a card."""

    type: Literal["education", "farming", "health"]
    title: str
    diagram_type: Optional[str] = Field(default=None, description="e.g. triangle, circle, rectangle")
    content: Optional[list[ContentItem]] = Field(
        default=None, description="Education only: labeled concept breakdown."
    )
    formula: Optional[str] = Field(default=None, description="Education only: the formula, if any.")
    points: Optional[list[str]] = Field(
        default=None, description="Farming/health only: concise actionable bullet points."
    )


class ChatOutput(BaseModel):
    response: str = Field(description="The conversational reply, in Marathi.")
    rich_data: Optional[RichData] = Field(
        default=None,
        description=(
            "Only include when the answer benefits from a structured card "
            "(a formula/diagram, or a checklist of steps/points). Omit for simple conversational replies."
        ),
    )
