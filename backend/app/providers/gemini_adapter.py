"""Gemini (Google) adapter — google_search grounding (CLAUDE.md §6.2).

Citations come from groundingMetadata.groundingChunks[].web.uri / .title.
Verify field names against the official google-genai docs when wiring keys.
"""

from __future__ import annotations

import time

from app.providers.base import Citation, ProviderAdapter, ProviderResult


class GeminiAdapter(ProviderAdapter):
    provider = "gemini"

    def __init__(self, api_key: str) -> None:
        from google import genai

        self._genai = genai
        self._client = genai.Client(api_key=api_key)

    async def search(self, prompt: str, *, model: str) -> ProviderResult:
        from google.genai import types

        start = time.monotonic()
        resp = await self._client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        answer_text = getattr(resp, "text", "") or ""
        citations: list[Citation] = []
        for cand in getattr(resp, "candidates", None) or []:
            meta = getattr(cand, "grounding_metadata", None)
            for chunk in getattr(meta, "grounding_chunks", None) or []:
                web = getattr(chunk, "web", None)
                url = getattr(web, "uri", None)
                if url:
                    citations.append(Citation(url=url, title=getattr(web, "title", None)))

        usage = _usage_dict(getattr(resp, "usage_metadata", None))
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
        "input_tokens": getattr(usage, "prompt_token_count", 0),
        "output_tokens": getattr(usage, "candidates_token_count", 0),
    }


def _dedupe(citations: list[Citation]) -> list[Citation]:
    seen: set[str] = set()
    out: list[Citation] = []
    for c in citations:
        if c.url not in seen:
            seen.add(c.url)
            out.append(c)
    return out
