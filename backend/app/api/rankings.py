"""Service 2 — trigger a search run and read aggregated rankings."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models import Analysis, Prompt, ProviderRun
from app.schemas.analysis import AnalysisRead
from app.schemas.ranking import RankingResponse, RankingRowRead, RunRequest
from app.services.ranking import aggregate_rankings
from app.services.search_runner import run_analysis

router = APIRouter(prefix="/analyses", tags=["rankings"])


@router.post("/{analysis_id}/run", response_model=AnalysisRead)
async def run(
    analysis_id: int,
    payload: RunRequest | None = None,
    session: Session = Depends(get_session),
) -> Analysis:
    """Start the search job (prompts × 3 providers × N repeats).

    In test mode the job runs inline (fast, mocked). Otherwise it is launched
    as a background task and progress is polled via GET /analyses/{id}.
    """
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="analysis not found")
    has_prompts = session.exec(
        select(Prompt.id).where(Prompt.analysis_id == analysis_id).limit(1)
    ).first()
    if not has_prompts:
        raise HTTPException(status_code=400, detail="analysis has no prompts")

    settings = get_settings()
    repeats = payload.repeats if payload else None

    if settings.geo_test_mode:
        await run_analysis(analysis_id, repeats=repeats, settings=settings)
        session.refresh(analysis)
    else:
        analysis.status = "running"
        analysis.progress = 0.0
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        asyncio.create_task(run_analysis(analysis_id, repeats=repeats, settings=settings))
    return analysis


@router.get("/{analysis_id}/rankings", response_model=RankingResponse)
def rankings(
    analysis_id: int, session: Session = Depends(get_session)
) -> RankingResponse:
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="analysis not found")

    total_runs = len(
        session.exec(
            select(ProviderRun.id)
            .join(Prompt, Prompt.id == ProviderRun.prompt_id)
            .where(Prompt.analysis_id == analysis_id)
        ).all()
    )
    rows = aggregate_rankings(analysis_id, session)
    return RankingResponse(
        analysis=AnalysisRead.model_validate(analysis, from_attributes=True),
        total_runs=total_runs,
        rankings=[
            RankingRowRead(
                brand_or_service=r.brand_or_service,
                mention_count=r.mention_count,
                appearance_rate=r.appearance_rate,
                avg_rank=r.avg_rank,
                stability=r.stability,
                by_provider=r.by_provider,
            )
            for r in rows
        ],
    )
