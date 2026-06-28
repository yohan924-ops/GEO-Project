"""Anthropic (Claude) adapter — web search via web_search_20260209 (CLAUDE.md §6.3)."""

from __future__ import annotations

import time

from app.providers.base import Citation, ProviderAdapter, ProviderResult

# Per-1M-token prices (USD), input/output. Used for rough cost tracking.
_PRICES = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


class AnthropicAdapter(ProviderAdapter):
    provider = "anthropic"

    def __init__(self, api_key: str) -> None:
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(api_key=api_key)

    async def search(self, prompt: str, *, model: str) -> ProviderResult:
        start = time.monotonic()
        resp = await self._client.messages.create(
            model=model,
            max_tokens=4096,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        answer_parts: list[str] = []
        citations: list[Citation] = []
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                answer_parts.append(block.text)
                # Inline citations attached to text blocks (if present).
                for c in getattr(block, "citations", None) or []:
                    url = getattr(c, "url", None)
                    if url:
                        citations.append(
                            Citation(
                                url=url,
                                title=getattr(c, "title", None),
                                snippet=getattr(c, "cited_text", None),
                            )
                        )
            elif btype == "web_search_tool_result":
                for item in getattr(block, "content", None) or []:
                    url = getattr(item, "url", None)
                    if url:
                        citations.append(
                            Citation(
                                url=url,
                                title=getattr(item, "title", None),
                                snippet=getattr(item, "page_age", None),
                            )
                        )

        usage = _usage_dict(getattr(resp, "usage", None))
        return ProviderResult(
            provider=self.provider,
            model=model,
            answer_text="".join(answer_parts).strip(),
            citations=_dedupe(citations),
            usage=usage,
            cost_usd=_cost(model, usage),
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


def _cost(model: str, usage: dict) -> float:
    inp, out = _PRICES.get(model, (0.0, 0.0))
    return (
        usage.get("input_tokens", 0) * inp + usage.get("output_tokens", 0) * out
    ) / 1_000_000


def _dedupe(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out: list[Citation] = []
    for c in citations:
        if c.url not in seen:
            seen.add(c.url)
            out.append(c)
    return out
