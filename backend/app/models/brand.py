"""Brand and owned-media registry models."""

from sqlmodel import Field, SQLModel


class Brand(SQLModel, table=True):
    """Analysis target brand."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    industry: str | None = None


class OwnedMedia(SQLModel, table=True):
    """Brand <-> owned-media mapping registry (core of service 3).

    media_type: web | instagram | blog | facebook
    domain_or_handle: e.g. "example.com" or "@brandhandle"
    """

    id: int | None = Field(default=None, primary_key=True)
    brand_id: int = Field(foreign_key="brand.id", index=True)
    media_type: str
    domain_or_handle: str = Field(index=True)
