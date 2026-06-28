"""Test fixtures. Forces test mode + an isolated in-memory DB; no real API calls."""

import os

os.environ["GEO_TEST_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite://"  # in-memory
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("GOOGLE_API_KEY", None)

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

# Rebuild the engine on the in-memory URL with a shared connection pool so the
# schema created in tests is visible to request handlers.
from sqlalchemy import create_engine

import app.db as db_module
import app.models  # noqa: F401  (register models)

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_module.engine = _engine


@pytest.fixture(autouse=True)
def _fresh_db():
    SQLModel.metadata.create_all(_engine)
    yield
    SQLModel.metadata.drop_all(_engine)


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c
