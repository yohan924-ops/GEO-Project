"""FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    analyses,
    brands,
    citations,
    owned_media,
    rankings,
    search,
    strategy,
)
from app.config import get_settings
from app.db import init_db
from app.providers import active_providers


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="GEO Analyzer", version="0.1.0", lifespan=lifespan)

# Allowed origins come from settings (CORS_ORIGINS); defaults to the local
# Next.js dev server. Set the deployed frontend URL when deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(analyses.router)
app.include_router(rankings.router)
app.include_router(owned_media.router)
app.include_router(citations.router)
app.include_router(strategy.router)
app.include_router(search.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "test_mode": get_settings().geo_test_mode}


@app.get("/providers", tags=["meta"])
def providers() -> dict:
    """Which LLM engines are active for this deployment (and test-mode flag)."""
    settings = get_settings()
    return {
        "test_mode": settings.geo_test_mode,
        "providers": active_providers(settings),
    }
