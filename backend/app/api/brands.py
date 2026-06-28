"""Brand CRUD (minimal, Phase 1)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Brand
from app.schemas.brand import BrandCreate, BrandRead

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("", response_model=BrandRead, status_code=201)
def create_brand(payload: BrandCreate, session: Session = Depends(get_session)) -> Brand:
    brand = Brand(name=payload.name, industry=payload.industry)
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand


@router.get("", response_model=list[BrandRead])
def list_brands(session: Session = Depends(get_session)) -> list[Brand]:
    return list(session.exec(select(Brand)).all())


@router.get("/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, session: Session = Depends(get_session)) -> Brand:
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="brand not found")
    return brand
