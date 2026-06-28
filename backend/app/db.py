"""SQLModel engine and session management."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

_settings = get_settings()

# check_same_thread=False is required for SQLite under FastAPI's threadpool.
_connect_args = (
    {"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(_settings.database_url, echo=False, connect_args=_connect_args)


def init_db() -> None:
    """Create all tables. Import models first so they register with metadata."""
    import app.models  # noqa: F401  (ensures models are imported)

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""
    with Session(engine) as session:
        yield session
