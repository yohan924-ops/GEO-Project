"""Service 4 — strategy report schemas."""

from pydantic import BaseModel


class StrategyRead(BaseModel):
    id: int
    analysis_id: int
    priority: int
    title: str
    rationale: str | None = None
    action_items: list[str]


class StrategyResponse(BaseModel):
    analysis_id: int
    strategies: list[StrategyRead]
