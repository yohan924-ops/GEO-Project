"""Analysis run and generated prompt models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Analysis(SQLModel, table=True):
    """A single analysis run.

    status: pending | running | done | failed
    """

    id: int | None = Field(default=None, primary_key=True)
    brand_id: int = Field(foreign_key="brand.id", index=True)
    status: str = Field(default="pending")
    progress: float = Field(default=0.0)  # 0.0 .. 1.0
    total_calls: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=_utcnow)


class Prompt(SQLModel, table=True):
    """A generated keyword or question prompt (service 1).

    type: keyword | question
    """

    id: int | None = Field(default=None, primary_key=True)
    analysis_id: int = Field(foreign_key="analysis.id", index=True)
    type: str
    text: str
