"""Strategy report model (service 4)."""

from sqlmodel import JSON, Column, Field, SQLModel


class Strategy(SQLModel, table=True):
    """A prioritized strategy report item."""

    id: int | None = Field(default=None, primary_key=True)
    analysis_id: int = Field(foreign_key="analysis.id", index=True)
    priority: int = Field(default=0)
    title: str
    rationale: str | None = None
    action_items: list[str] = Field(default_factory=list, sa_column=Column(JSON))
