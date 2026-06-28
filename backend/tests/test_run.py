"""Search runner + run/rankings API tests (test mode, mocked providers)."""

import pytest
from sqlmodel import Session, select

from app.config import get_settings
from app.models import Analysis, Brand, Mention, Prompt, ProviderRun
from app.services.search_runner import run_analysis


@pytest.mark.asyncio
async def test_run_analysis_persists_runs_and_progress():
    from app.db import engine

    with Session(engine) as s:
        brand = Brand(name="b")
        s.add(brand)
        s.flush()
        analysis = Analysis(brand_id=brand.id)
        s.add(analysis)
        s.flush()
        for i in range(2):
            s.add(Prompt(analysis_id=analysis.id, type="question", text=f"q{i}"))
        s.commit()
        analysis_id = analysis.id

    await run_analysis(analysis_id, repeats=2, settings=get_settings())

    with Session(engine) as s:
        analysis = s.get(Analysis, analysis_id)
        assert analysis.status == "done"
        assert analysis.progress == 1.0
        # 2 prompts × 3 providers × 2 repeats
        assert analysis.total_calls == 12
        runs = s.exec(
            select(ProviderRun)
            .join(Prompt, Prompt.id == ProviderRun.prompt_id)
            .where(Prompt.analysis_id == analysis_id)
        ).all()
        assert len(runs) == 12
        run_ids = [r.id for r in runs]
        mentions = s.exec(
            select(Mention).where(Mention.provider_run_id.in_(run_ids))
        ).all()
        assert len(mentions) > 0


def test_run_and_rankings_endpoints(client):
    brand = client.post("/brands", json={"name": "브랜드", "industry": "운동화"}).json()
    gen = client.post(
        "/analyses/generate-prompts",
        json={"brand_id": brand["id"], "keyword_count": 2, "question_count": 2},
    ).json()
    analysis_id = gen["analysis"]["id"]

    run = client.post(f"/analyses/{analysis_id}/run", json={"repeats": 2})
    assert run.status_code == 200
    assert run.json()["status"] == "done"
    assert run.json()["progress"] == 1.0

    resp = client.get(f"/analyses/{analysis_id}/rankings")
    assert resp.status_code == 200
    body = resp.json()
    # 4 prompts × 3 providers × 2 repeats
    assert body["total_runs"] == 24
    assert len(body["rankings"]) > 0
    top = body["rankings"][0]
    assert 0.0 <= top["appearance_rate"] <= 1.0
    assert set(top["by_provider"]).issubset({"openai", "gemini", "anthropic"})


def test_run_missing_analysis(client):
    assert client.post("/analyses/999/run", json={}).status_code == 404


def test_rankings_empty_before_run(client):
    brand = client.post("/brands", json={"name": "b", "industry": "x"}).json()
    gen = client.post(
        "/analyses/generate-prompts",
        json={"brand_id": brand["id"], "keyword_count": 1, "question_count": 1},
    ).json()
    resp = client.get(f"/analyses/{gen['analysis']['id']}/rankings")
    assert resp.status_code == 200
    assert resp.json()["total_runs"] == 0
    assert resp.json()["rankings"] == []
