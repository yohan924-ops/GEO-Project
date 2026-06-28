"""Service 4 strategy generation + endpoint tests (no API)."""

import pytest
from sqlmodel import Session

from app.config import get_settings
from app.models import Analysis, Brand, Mention, Prompt, ProviderRun
from app.services.citation import CitationShareResult
from app.services.ranking import RankingRow
from app.services.strategy import (
    GapContext,
    _build_context,
    _template_strategy,
    generate_strategy,
)


def test_template_strategy_low_exposure():
    ctx = GapContext(
        target="브랜드",
        target_appearance_rate=0.0,
        target_avg_rank=0.0,
        target_stability=0.0,
        target_citation_share=0.0,
        weakest_provider="gemini",
        top_competitors=["A", "B"],
    )
    items = _template_strategy(ctx)
    assert items[0].priority == 1
    assert "노출" in items[0].title
    # citation + provider strategies present
    titles = " ".join(i.title for i in items)
    assert "인용" in titles
    assert "Gemini" in titles
    assert all(i.action_items for i in items)


def test_build_context_finds_target():
    rankings = [
        RankingRow(
            brand_or_service="Comp",
            mention_count=9,
            appearance_rate=0.9,
            avg_rank=1.0,
            stability=0.9,
            by_provider={"openai": 0.9},
        ),
        RankingRow(
            brand_or_service="브랜드",
            mention_count=3,
            appearance_rate=0.3,
            avg_rank=2.0,
            stability=0.5,
            by_provider={"openai": 0.1, "gemini": 0.5},
        ),
    ]
    share = CitationShareResult(10, 4, [])
    ctx = _build_context("브랜드", rankings, share)
    assert ctx.target_appearance_rate == 0.3
    assert ctx.weakest_provider == "openai"  # target's weakest
    assert "Comp" in ctx.top_competitors


@pytest.mark.asyncio
async def test_generate_strategy_runs(client):
    from app.db import engine

    with Session(engine) as session:
        brand = Brand(name="브랜드")
        session.add(brand)
        session.flush()
        analysis = Analysis(brand_id=brand.id)
        session.add(analysis)
        session.flush()
        prompt = Prompt(analysis_id=analysis.id, type="question", text="q")
        session.add(prompt)
        session.flush()
        run = ProviderRun(prompt_id=prompt.id, provider="openai", model="m", run_index=0)
        session.add(run)
        session.flush()
        session.add(Mention(provider_run_id=run.id, brand_or_service="Comp", rank=1))
        session.commit()
        analysis_id = analysis.id

        items = await generate_strategy(analysis_id, session, get_settings())

    assert len(items) >= 2
    assert items[0].priority == 1


def test_strategy_endpoints(client):
    brand = client.post("/brands", json={"name": "브랜드", "industry": "운동화"}).json()
    gen = client.post(
        "/analyses/generate-prompts",
        json={"brand_id": brand["id"], "keyword_count": 1, "question_count": 1},
    ).json()
    analysis_id = gen["analysis"]["id"]
    client.post(f"/analyses/{analysis_id}/run", json={"repeats": 2})

    post = client.post(f"/analyses/{analysis_id}/strategy")
    assert post.status_code == 200
    strategies = post.json()["strategies"]
    assert len(strategies) >= 2
    assert strategies[0]["priority"] <= strategies[-1]["priority"]
    assert all(s["action_items"] for s in strategies)

    # GET returns the persisted report; regenerate keeps it stable in count.
    got = client.get(f"/analyses/{analysis_id}/strategy").json()
    assert len(got["strategies"]) == len(strategies)
    again = client.post(f"/analyses/{analysis_id}/strategy").json()
    assert len(again["strategies"]) == len(strategies)  # replaced, not duplicated


def test_strategy_missing_analysis(client):
    assert client.post("/analyses/999/strategy").status_code == 404
