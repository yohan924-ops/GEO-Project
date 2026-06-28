"""Provider call results and derived mention/citation models."""

from sqlmodel import JSON, Column, Field, SQLModel


class ProviderRun(SQLModel, table=True):
    """One call of one prompt to one provider (run_index 0..9).

    raw/usage are stored as JSON to preserve the original response for
    re-aggregation and debugging (CLAUDE.md §5 aggregation rule).
    """

    id: int | None = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompt.id", index=True)
    provider: str = Field(index=True)  # openai | gemini | anthropic
    model: str
    run_index: int = Field(default=0)
    answer_text: str = Field(default="")
    usage: dict = Field(default_factory=dict, sa_column=Column(JSON))
    cost_usd: float = Field(default=0.0)
    latency_ms: int = Field(default=0)
    raw: dict = Field(default_factory=dict, sa_column=Column(JSON))


class Mention(SQLModel, table=True):
    """A brand/service that appeared in an answer (service 2)."""

    id: int | None = Field(default=None, primary_key=True)
    provider_run_id: int = Field(foreign_key="providerrun.id", index=True)
    brand_or_service: str = Field(index=True)
    rank: int | None = None


class Citation(SQLModel, table=True):
    """A citation source from an answer (service 3)."""

    id: int | None = Field(default=None, primary_key=True)
    provider_run_id: int = Field(foreign_key="providerrun.id", index=True)
    url: str
    title: str | None = None
    snippet: str | None = None
    domain: str = Field(index=True)
    matched_brand_id: int | None = Field(default=None, foreign_key="brand.id")
    media_type: str | None = None
