"""Service 2 — brand/service mention extraction and ranking aggregation.

Mentions are extracted from each answer (order of appearance = rank), then
aggregated with pandas across prompts, providers, and repeats to produce
frequency, appearance rate, average rank, and repeat stability.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import pandas as pd
from sqlmodel import Session, select

from app.config import Settings, get_settings
from app.models import Mention, Prompt, ProviderRun

# Matches the "... include A, B, C." shape (covers mock answers and many real
# list-style answers); falls back to Capitalized/CamelCase tokens otherwise.
_LIST_RE = re.compile(r"(?:include|includes|including|추천\w*)[:\s]+(.+?)(?:[.\n]|$)", re.I)
_SPLIT_RE = re.compile(r",|·|/|\band\b|및|그리고", re.I)
_TOKEN_RE = re.compile(r"[A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?")


def extract_mentions_heuristic(text: str) -> list[str]:
    """Deterministic, no-API extraction (test mode / fallback)."""
    if not text:
        return []
    items: list[str] = []
    m = _LIST_RE.search(text)
    if m:
        items = [s.strip(" .'\"") for s in _SPLIT_RE.split(m.group(1)) if s.strip()]
    if not items:
        items = [t.strip() for t in _TOKEN_RE.findall(text)]
    seen: set[str] = set()
    ordered: list[str] = []
    for it in items:
        key = it.lower()
        if it and key not in seen:
            seen.add(key)
            ordered.append(it)
    return ordered


_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "brands": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Brand/service names mentioned, in order of appearance.",
        }
    },
    "required": ["brands"],
}


async def extract_mentions_llm(text: str, settings: Settings) -> list[str]:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    resp = await client.messages.create(
        model=settings.gen_model_anthropic,
        max_tokens=1024,
        tools=[
            {
                "name": "emit_brands",
                "description": "Return brand/service names mentioned in the text.",
                "input_schema": _EXTRACT_SCHEMA,
            }
        ],
        tool_choice={"type": "tool", "name": "emit_brands"},
        messages=[
            {
                "role": "user",
                "content": (
                    "다음 답변에서 언급된 브랜드/서비스명을 등장 순서대로 추출해줘.\n\n" + text
                ),
            }
        ],
    )
    for block in getattr(resp, "content", None) or []:
        if getattr(block, "type", None) == "tool_use":
            data = block.input if isinstance(block.input, dict) else json.loads(block.input)
            return list(dict.fromkeys(data.get("brands", [])))
    return []


async def extract_mentions(text: str, settings: Settings | None = None) -> list[str]:
    settings = settings or get_settings()
    if settings.geo_test_mode or not settings.anthropic_api_key:
        return extract_mentions_heuristic(text)
    return await extract_mentions_llm(text, settings)


@dataclass
class RankingRow:
    brand_or_service: str
    mention_count: int
    appearance_rate: float  # fraction of all runs that mention it
    avg_rank: float
    stability: float  # mean per-(prompt,provider) repeat consistency, 0..1
    by_provider: dict[str, float] = field(default_factory=dict)  # provider -> rate


def aggregate_rankings(analysis_id: int, session: Session) -> list[RankingRow]:
    """Aggregate stored mentions into a ranking table (pandas)."""
    rows = session.exec(
        select(ProviderRun.id, ProviderRun.provider, ProviderRun.prompt_id)
        .join(Prompt, Prompt.id == ProviderRun.prompt_id)
        .where(Prompt.analysis_id == analysis_id)
    ).all()
    if not rows:
        return []

    runs_df = pd.DataFrame(rows, columns=["run_id", "provider", "prompt_id"])
    total_runs = len(runs_df)

    run_ids = runs_df["run_id"].tolist()
    mention_rows = session.exec(
        select(Mention.provider_run_id, Mention.brand_or_service, Mention.rank).where(
            Mention.provider_run_id.in_(run_ids)
        )
    ).all()
    if not mention_rows:
        return []

    men_df = pd.DataFrame(
        mention_rows, columns=["run_id", "brand_or_service", "rank"]
    ).merge(runs_df, on="run_id", how="left")

    # repeats per (prompt, provider) group — denominator for stability.
    group_sizes = (
        runs_df.groupby(["prompt_id", "provider"]).size().rename("group_runs").reset_index()
    )

    results: list[RankingRow] = []
    for brand, bdf in men_df.groupby("brand_or_service"):
        mention_count = len(bdf)
        appearance_rate = mention_count / total_runs
        avg_rank = float(bdf["rank"].dropna().mean()) if bdf["rank"].notna().any() else 0.0

        # stability: for each (prompt, provider) group, appearances / repeats.
        appfor = bdf.groupby(["prompt_id", "provider"]).size().rename("hits").reset_index()
        merged = appfor.merge(group_sizes, on=["prompt_id", "provider"], how="left")
        per_group = (merged["hits"] / merged["group_runs"]).clip(upper=1.0)
        stability = float(per_group.mean()) if not per_group.empty else 0.0

        by_provider: dict[str, float] = {}
        for provider, pdf in bdf.groupby("provider"):
            denom = int((runs_df["provider"] == provider).sum())
            by_provider[str(provider)] = (len(pdf) / denom) if denom else 0.0

        results.append(
            RankingRow(
                brand_or_service=str(brand),
                mention_count=mention_count,
                appearance_rate=round(appearance_rate, 4),
                avg_rank=round(avg_rank, 2),
                stability=round(stability, 4),
                by_provider={k: round(v, 4) for k, v in by_provider.items()},
            )
        )

    results.sort(key=lambda r: (-r.appearance_rate, r.avg_rank or 1e9))
    return results
