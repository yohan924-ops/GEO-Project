"""OwnedMedia registry CRUD (service 3 — brand <-> owned-media mapping)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Brand, OwnedMedia
from app.schemas.owned_media import OwnedMediaCreate, OwnedMediaRead

router = APIRouter(tags=["owned-media"])


@router.post(
    "/brands/{brand_id}/owned-media", response_model=OwnedMediaRead, status_code=201
)
def create_owned_media(
    brand_id: int,
    payload: OwnedMediaCreate,
    session: Session = Depends(get_session),
) -> OwnedMedia:
    if not session.get(Brand, brand_id):
        raise HTTPException(status_code=404, detail="brand not found")
    om = OwnedMedia(
        brand_id=brand_id,
        media_type=payload.media_type,
        domain_or_handle=payload.domain_or_handle.strip(),
    )
    session.add(om)
    session.commit()
    session.refresh(om)
    return om


@router.get("/brands/{brand_id}/owned-media", response_model=list[OwnedMediaRead])
def list_owned_media(
    brand_id: int, session: Session = Depends(get_session)
) -> list[OwnedMedia]:
    stmt = select(OwnedMedia).where(OwnedMedia.brand_id == brand_id)
    return list(session.exec(stmt).all())


@router.get("/owned-media", response_model=list[OwnedMediaRead])
def list_all_owned_media(session: Session = Depends(get_session)) -> list[OwnedMedia]:
    return list(session.exec(select(OwnedMedia)).all())


@router.delete("/owned-media/{om_id}", status_code=204)
def delete_owned_media(om_id: int, session: Session = Depends(get_session)) -> None:
    om = session.get(OwnedMedia, om_id)
    if not om:
        raise HTTPException(status_code=404, detail="owned media not found")
    session.delete(om)
    session.commit()
