"""Service 2 — run trigger and ranking response schemas."""

from pydantic import BaseModel

from app.schemas.analysis import AnalysisRead


class RunRequest(BaseModel):
    repeats: int | None = None  # override default (config.search_repeats)


class RankingRowRead(BaseModel):
    brand_or_service: str
    mention_count: int
    appearance_rate: float
    avg_rank: float
    stability: float
    by_provider: dict[str, float]


class RankingResponse(BaseModel):
    analysis: AnalysisRead
    total_runs: int
    rankings: list[RankingRowRead]
