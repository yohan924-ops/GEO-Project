"""Deterministic mock adapter for test mode — no real API calls, no cost."""

from __future__ import annotations

import hashlib

from app.providers.base import Citation, ProviderAdapter, ProviderResult


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


class MockAdapter(ProviderAdapter):
    """Returns stable, prompt-derived fake answers and citations.

    Used whenever GEO_TEST_MODE is on or an API key is missing, so the rest
    of the pipeline can be developed and tested without 3rd-party billing.
    """

    def __init__(self, provider: str) -> None:
        self.provider = provider

    async def search(self, prompt: str, *, model: str) -> ProviderResult:
        seed = _seed(f"{self.provider}:{prompt}")
        brands = ["BrandAlpha", "BrandBeta", "BrandGamma"]
        ordered = brands[seed % 3 :] + brands[: seed % 3]
        answer = (
            f"[mock:{self.provider}] For '{prompt[:40]}', popular options include "
            + ", ".join(ordered)
            + "."
        )
        domains = ["example.com", "blog.example.org", "instagram.com"]
        citations = [
            Citation(
                url=f"https://{domains[i % 3]}/p/{(seed >> (i * 4)) % 1000}",
                title=f"{ordered[i % 3]} review",
                snippet="mock snippet",
            )
            for i in range(3)
        ]
        return ProviderResult(
            provider=self.provider,
            model=f"mock-{model}",
            answer_text=answer,
            citations=citations,
            usage={"input_tokens": 10, "output_tokens": 30},
            cost_usd=0.0,
            latency_ms=1,
            raw={"mock": True, "prompt": prompt},
        )
