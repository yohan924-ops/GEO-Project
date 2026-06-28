"""Service 3 — citation share response schemas."""

from pydantic import BaseModel


class CitationShareRowRead(BaseModel):
    brand_id: int
    brand_name: str
    citation_count: int
    share: float
    by_media_type: dict[str, int]


class CitationShareResponse(BaseModel):
    analysis_id: int
    total_citations: int
    matched_citations: int
    rows: list[CitationShareRowRead]
