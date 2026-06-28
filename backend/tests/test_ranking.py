"""Mention extraction + ranking aggregation tests (no API)."""

import pytest
from sqlmodel import Session

from app.config import get_settings
from app.models import Analysis, Brand, Mention, Prompt, ProviderRun
from app.services.ranking import (
    aggregate_rankings,
    extract_mentions,
    extract_mentions_heuristic,
)


def test_heuristic_extracts_comma_list():
    text = "For 'shoes', popular options include BrandAlpha, BrandBeta, BrandGamma."
    assert extract_mentions_heuristic(text) == ["BrandAlpha", "BrandBeta", "BrandGamma"]


def test_heuristic_dedupes_case_insensitive():
    text = "include Nike, nike, Adidas."
    assert extract_mentions_heuristic(text) == ["Nike", "Adidas"]


def test_heuristic_empty():
    assert extract_mentions_heuristic("") == []


@pytest.mark.asyncio
async def test_extract_mentions_uses_heuristic_in_test_mode():
    out = await extract_mentions("include A, B.", get_settings())
    assert out == ["A", "B"]


def _seed_run(session: Session, prompt_id: int, provider: str, idx: int, brands: list[str]):
    run = ProviderRun(
        prompt_id=prompt_id, provider=provider, model="m", run_index=idx, answer_text="x"
    )
    session.add(run)
    session.flush()
    for rank, b in enumerate(brands, start=1):
        session.add(Mention(provider_run_id=run.id, brand_or_service=b, rank=rank))


def test_aggregate_rankings(client):
    # client fixture builds the engine; use its session directly.
    from app.db import engine

    with Session(engine) as session:
        brand = Brand(name="b")
        session.add(brand)
        session.flush()
        analysis = Analysis(brand_id=brand.id)
        session.add(analysis)
        session.flush()
        prompt = Prompt(analysis_id=analysis.id, type="question", text="q")
        session.add(prompt)
        session.flush()

        # 2 runs: Alpha appears in both (rank 1), Beta only once (rank 2).
        _seed_run(session, prompt.id, "openai", 0, ["Alpha", "Beta"])
        _seed_run(session, prompt.id, "openai", 1, ["Alpha"])
        session.commit()

        rows = aggregate_rankings(analysis.id, session)

    by_name = {r.brand_or_service: r for r in rows}
    assert by_name["Alpha"].mention_count == 2
    assert by_name["Alpha"].appearance_rate == 1.0
    assert by_name["Alpha"].avg_rank == 1.0
    assert by_name["Alpha"].stability == 1.0
    assert by_name["Beta"].appearance_rate == 0.5
    # Alpha ranks above Beta.
    assert rows[0].brand_or_service == "Alpha"
    assert by_name["Alpha"].by_provider["openai"] == 1.0
