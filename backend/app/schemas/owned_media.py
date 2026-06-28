"""OwnedMedia registry schemas (service 3)."""

from typing import Literal

from pydantic import BaseModel

MediaType = Literal["web", "instagram", "blog", "facebook"]


class OwnedMediaCreate(BaseModel):
    media_type: MediaType
    domain_or_handle: str


class OwnedMediaRead(BaseModel):
    id: int
    brand_id: int
    media_type: str
    domain_or_handle: str
