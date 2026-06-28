"""Service 3 — citation mapping and per-brand share."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Analysis
from app.schemas.citation import CitationShareResponse, CitationShareRowRead
from app.services.citation import citation_share, map_citations

router = APIRouter(prefix="/analyses", tags=["citations"])


@router.post("/{analysis_id}/map-citations")
def remap_citations(
    analysis_id: int, session: Session = Depends(get_session)
) -> dict:
    if not session.get(Analysis, analysis_id):
        raise HTTPException(status_code=404, detail="analysis not found")
    matched = map_citations(analysis_id, session)
    return {"analysis_id": analysis_id, "matched": matched}


@router.get("/{analysis_id}/citation-share", response_model=CitationShareResponse)
def get_citation_share(
    analysis_id: int, session: Session = Depends(get_session)
) -> CitationShareResponse:
    if not session.get(Analysis, analysis_id):
        raise HTTPException(status_code=404, detail="analysis not found")
    result = citation_share(analysis_id, session)
    return CitationShareResponse(
        analysis_id=analysis_id,
        total_citations=result.total_citations,
        matched_citations=result.matched_citations,
        rows=[
            CitationShareRowRead(
                brand_id=r.brand_id,
                brand_name=r.brand_name,
                citation_count=r.citation_count,
                share=r.share,
                by_media_type=r.by_media_type,
            )
            for r in result.rows
        ],
    )
