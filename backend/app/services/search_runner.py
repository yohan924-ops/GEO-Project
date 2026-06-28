"""Async search job runner (CLAUDE.md §6.5).

Runs every prompt against all three providers N times with per-provider
concurrency limits and exponential-backoff retries, persists each call as a
ProviderRun (+ extracted Mentions and Citations), and tracks progress on the
Analysis. Permanent errors fail a single ProviderRun but never the whole job.
"""

from __future__ import annotations

import asyncio

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

import app.db as db_module
from app.config import Settings, get_settings
from app.models import Analysis, Citation, Mention, Prompt, ProviderRun
from app.providers import get_all_adapters
from app.providers.base import ProviderResult, extract_domain
from app.services.ranking import extract_mentions


async def _call_with_retry(
    adapter, prompt: str, model: str, settings: Settings
) -> ProviderResult | None:
    """Call an adapter, retrying transient errors with exponential backoff.

    Returns None on permanent failure (the ProviderRun is recorded as failed).
    """
    delay = 1.0
    for attempt in range(settings.max_retries + 1):
        try:
            return await adapter.search(prompt, model=model)
        except Exception:
            if attempt >= settings.max_retries:
                return None
            await asyncio.sleep(delay)
            delay *= 2
    return None


def _persist_progress(engine: Engine, analysis_id: int, progress: float) -> None:
    with Session(engine) as s:
        analysis = s.get(Analysis, analysis_id)
        if analysis:
            analysis.progress = round(progress, 4)
            s.add(analysis)
            s.commit()


async def run_analysis(
    analysis_id: int,
    *,
    repeats: int | None = None,
    settings: Settings | None = None,
    engine: Engine | None = None,
) -> None:
    settings = settings or get_settings()
    repeats = repeats if repeats is not None else settings.search_repeats
    engine = engine or db_module.engine
    adapters = get_all_adapters(settings)

    with Session(engine) as s:
        analysis = s.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"analysis {analysis_id} not found")
        prompt_items = [
            (p.id, p.text)
            for p in s.exec(
                select(Prompt).where(Prompt.analysis_id == analysis_id)
            ).all()
        ]
        analysis.status = "running"
        analysis.progress = 0.0
        analysis.total_calls = len(prompt_items) * len(adapters) * repeats
        analysis.cost_usd = 0.0
        s.add(analysis)
        s.commit()

    total = max(1, len(prompt_items) * len(adapters) * repeats)
    sems = {p: asyncio.Semaphore(settings.provider_concurrency) for p in adapters}
    lock = asyncio.Lock()
    collected: list[tuple[int, str, int, ProviderResult | None, list[str]]] = []
    done = 0
    step = max(1, total // 20)

    async def one(prompt_id: int, text: str, provider: str, run_index: int) -> None:
        nonlocal done
        adapter, model = adapters[provider]
        async with sems[provider]:
            res = await _call_with_retry(adapter, text, model, settings)
        mentions = await extract_mentions(res.answer_text, settings) if res else []
        async with lock:
            collected.append((prompt_id, provider, run_index, res, mentions))
            done += 1
            if done % step == 0 or done == total:
                _persist_progress(engine, analysis_id, done / total)

    try:
        await asyncio.gather(
            *(
                one(pid, text, provider, ri)
                for (pid, text) in prompt_items
                for provider in adapters
                for ri in range(repeats)
            )
        )
        _persist_results(engine, analysis_id, collected, settings)
        _finalize(engine, analysis_id, status="done")
    except Exception:
        _finalize(engine, analysis_id, status="failed")
        raise


def _persist_results(
    engine: Engine,
    analysis_id: int,
    collected: list[tuple[int, str, int, ProviderResult | None, list[str]]],
    settings: Settings,
) -> None:
    models = {
        "openai": settings.search_model_openai,
        "gemini": settings.search_model_gemini,
        "anthropic": settings.search_model_anthropic,
    }
    total_cost = 0.0
    with Session(engine) as s:
        for prompt_id, provider, run_index, res, mentions in collected:
            run = ProviderRun(
                prompt_id=prompt_id,
                provider=provider,
                model=res.model if res else models.get(provider, ""),
                run_index=run_index,
                answer_text=res.answer_text if res else "",
                usage=res.usage if res else {},
                cost_usd=res.cost_usd if res else 0.0,
                latency_ms=res.latency_ms if res else 0,
                raw=res.raw if res else {"error": "permanent_failure"},
            )
            s.add(run)
            s.flush()  # assign run.id
            total_cost += run.cost_usd

            for rank, brand in enumerate(mentions, start=1):
                s.add(
                    Mention(
                        provider_run_id=run.id, brand_or_service=brand, rank=rank
                    )
                )
            if res:
                for c in res.citations:
                    s.add(
                        Citation(
                            provider_run_id=run.id,
                            url=c.url,
                            title=c.title,
                            snippet=c.snippet,
                            domain=c.domain or extract_domain(c.url),
                        )
                    )
        s.commit()

    with Session(engine) as s:
        analysis = s.get(Analysis, analysis_id)
        if analysis:
            analysis.cost_usd = round(total_cost, 6)
            s.add(analysis)
            s.commit()


def _finalize(engine: Engine, analysis_id: int, *, status: str) -> None:
    with Session(engine) as s:
        analysis = s.get(Analysis, analysis_id)
        if analysis:
            analysis.status = status
            if status == "done":
                analysis.progress = 1.0
            s.add(analysis)
            s.commit()
