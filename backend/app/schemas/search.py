"""Single-search (Phase 1 adapter verification) schemas."""

from pydantic import BaseModel


class CitationRead(BaseModel):
    url: str
    title: str | None = None
    snippet: str | None = None
    domain: str


class ProviderResultRead(BaseModel):
    provider: str
    model: str
    answer_text: str
    citations: list[CitationRead]
    usage: dict
    cost_usd: float
    latency_ms: int


class SingleSearchRequest(BaseModel):
    prompt: str


class SingleSearchResponse(BaseModel):
    prompt: str
    test_mode: bool
    results: list[ProviderResultRead]
