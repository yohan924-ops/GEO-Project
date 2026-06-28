"""Brand request/response schemas."""

from pydantic import BaseModel


class BrandCreate(BaseModel):
    name: str
    industry: str | None = None


class BrandRead(BaseModel):
    id: int
    name: str
    industry: str | None = None
