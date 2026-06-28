"""Phase 1 adapter verification — run one prompt against all 3 providers once."""

import asyncio

from fastapi import APIRouter

from app.config import get_settings
from app.providers import get_all_adapters
from app.providers.base import ProviderResult
from app.schemas.search import (
    CitationRead,
    ProviderResultRead,
    SingleSearchRequest,
    SingleSearchResponse,
)

router = APIRouter(prefix="/search", tags=["search"])


def _to_read(result: ProviderResult) -> ProviderResultRead:
    return ProviderResultRead(
        provider=result.provider,
        model=result.model,
        answer_text=result.answer_text,
        citations=[
            CitationRead(url=c.url, title=c.title, snippet=c.snippet, domain=c.domain)
            for c in result.citations
        ],
        usage=result.usage,
        cost_usd=result.cost_usd,
        latency_ms=result.latency_ms,
    )


@router.post("/single", response_model=SingleSearchResponse)
async def single_search(payload: SingleSearchRequest) -> SingleSearchResponse:
    """Call one prompt once on OpenAI, Gemini, and Anthropic concurrently.

    In test mode every provider is a MockAdapter, so this is free to run.
    """
    settings = get_settings()
    adapters = get_all_adapters(settings)

    async def run(provider: str) -> ProviderResult:
        adapter, model = adapters[provider]
        return await adapter.search(payload.prompt, model=model)

    results = await asyncio.gather(*(run(p) for p in adapters))
    return SingleSearchResponse(
        prompt=payload.prompt,
        test_mode=settings.geo_test_mode,
        results=[_to_read(r) for r in results],
    )
