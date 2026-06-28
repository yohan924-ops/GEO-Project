"""Analysis creation + service 1 prompt generation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Analysis, Brand, Prompt
from app.schemas.analysis import (
    AnalysisRead,
    AnalysisWithPrompts,
    GeneratePromptsRequest,
    PromptRead,
)
from app.services.prompt_gen import generate_prompts

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("/generate-prompts", response_model=AnalysisWithPrompts, status_code=201)
async def create_analysis_with_prompts(
    payload: GeneratePromptsRequest, session: Session = Depends(get_session)
) -> AnalysisWithPrompts:
    """Service 1: create an analysis and generate keyword/question prompts."""
    brand = session.get(Brand, payload.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="brand not found")

    analysis = Analysis(brand_id=brand.id, status="running")
    session.add(analysis)
    session.commit()
    session.refresh(analysis)

    generated = await generate_prompts(
        brand.name,
        brand.industry,
        keyword_count=payload.keyword_count,
        question_count=payload.question_count,
    )

    prompts: list[Prompt] = []
    for text in generated.keywords:
        prompts.append(Prompt(analysis_id=analysis.id, type="keyword", text=text))
    for text in generated.questions:
        prompts.append(Prompt(analysis_id=analysis.id, type="question", text=text))
    session.add_all(prompts)

    analysis.status = "done"
    analysis.progress = 1.0
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    for p in prompts:
        session.refresh(p)

    return AnalysisWithPrompts(
        analysis=AnalysisRead.model_validate(analysis, from_attributes=True),
        prompts=[PromptRead.model_validate(p, from_attributes=True) for p in prompts],
    )


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, session: Session = Depends(get_session)) -> Analysis:
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="analysis not found")
    return analysis


@router.get("/{analysis_id}/prompts", response_model=list[PromptRead])
def list_prompts(
    analysis_id: int, session: Session = Depends(get_session)
) -> list[Prompt]:
    if not session.get(Analysis, analysis_id):
        raise HTTPException(status_code=404, detail="analysis not found")
    stmt = select(Prompt).where(Prompt.analysis_id == analysis_id)
    return list(session.exec(stmt).all())
