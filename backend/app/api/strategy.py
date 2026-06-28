"""Service 4 — generate and read the GEO strategy report."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Analysis, Strategy
from app.schemas.strategy import StrategyRead, StrategyResponse
from app.services.strategy import generate_strategy

router = APIRouter(prefix="/analyses", tags=["strategy"])


def _read(s: Strategy) -> StrategyRead:
    return StrategyRead(
        id=s.id,
        analysis_id=s.analysis_id,
        priority=s.priority,
        title=s.title,
        rationale=s.rationale,
        action_items=list(s.action_items or []),
    )


@router.post("/{analysis_id}/strategy", response_model=StrategyResponse)
async def create_strategy(
    analysis_id: int, session: Session = Depends(get_session)
) -> StrategyResponse:
    """Generate (and persist) the strategy report, replacing any prior one."""
    if not session.get(Analysis, analysis_id):
        raise HTTPException(status_code=404, detail="analysis not found")

    items = await generate_strategy(analysis_id, session)

    # Replace any existing strategies for a clean regenerate.
    existing = session.exec(
        select(Strategy).where(Strategy.analysis_id == analysis_id)
    ).all()
    for s in existing:
        session.delete(s)

    saved: list[Strategy] = []
    for item in items:
        s = Strategy(
            analysis_id=analysis_id,
            priority=item.priority,
            title=item.title,
            rationale=item.rationale,
            action_items=item.action_items,
        )
        session.add(s)
        saved.append(s)
    session.commit()
    for s in saved:
        session.refresh(s)

    saved.sort(key=lambda s: s.priority)
    return StrategyResponse(
        analysis_id=analysis_id, strategies=[_read(s) for s in saved]
    )


@router.get("/{analysis_id}/strategy", response_model=StrategyResponse)
def get_strategy(
    analysis_id: int, session: Session = Depends(get_session)
) -> StrategyResponse:
    if not session.get(Analysis, analysis_id):
        raise HTTPException(status_code=404, detail="analysis not found")
    rows = session.exec(
        select(Strategy)
        .where(Strategy.analysis_id == analysis_id)
        .order_by(Strategy.priority)
    ).all()
    return StrategyResponse(
        analysis_id=analysis_id, strategies=[_read(s) for s in rows]
    )
