"""OpenAI (ChatGPT) adapter — Responses API + web_search tool (CLAUDE.md §6.2).

Field names/SDK signatures for web search evolve; verify against the official
docs when wiring real keys.
"""

from __future__ import annotations

import time

from app.providers.base import Citation, ProviderAdapter, ProviderResult


class OpenAIAdapter(ProviderAdapter):
    provider = "openai"

    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)

    async def search(self, prompt: str, *, model: str) -> ProviderResult:
        start = time.monotonic()
        resp = await self._client.responses.create(
            model=model,
            input=prompt,
            tools=[{"type": "web_search"}],
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        answer_text = getattr(resp, "output_text", "") or ""
        citations: list[Citation] = []
        for item in getattr(resp, "output", None) or []:
            for content in getattr(item, "content", None) or []:
                for ann in getattr(content, "annotations", None) or []:
                    url = getattr(ann, "url", None)
                    if url:
                        citations.append(
                            Citation(url=url, title=getattr(ann, "title", None))
                        )

        usage = _usage_dict(getattr(resp, "usage", None))
        return ProviderResult(
            provider=self.provider,
            model=model,
            answer_text=answer_text.strip(),
            citations=_dedupe(citations),
            usage=usage,
            cost_usd=0.0,  # fill via official pricing when enabled
            latency_ms=latency_ms,
            raw=resp.model_dump() if hasattr(resp, "model_dump") else {},
        )


def _usage_dict(usage: object) -> dict:
    if usage is None:
        return {}
    return {
        "input_tokens": getattr(usage, "input_tokens", 0),
        "output_tokens": getattr(usage, "output_tokens", 0),
    }


def _dedupe(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out: list[Citation] = []
    for c in citations:
        if c.url not in seen:
            seen.add(c.url)
            out.append(c)
    return out
