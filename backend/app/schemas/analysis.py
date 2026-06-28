"""Analysis / prompt request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class PromptRead(BaseModel):
    id: int
    type: str  # keyword | question
    text: str


class AnalysisRead(BaseModel):
    id: int
    brand_id: int
    status: str
    progress: float
    total_calls: int
    cost_usd: float
    created_at: datetime


class GeneratePromptsRequest(BaseModel):
    """Create an analysis for an existing brand and generate prompts."""

    brand_id: int
    keyword_count: int | None = None
    question_count: int | None = None


class AnalysisWithPrompts(BaseModel):
    analysis: AnalysisRead
    prompts: list[PromptRead]
