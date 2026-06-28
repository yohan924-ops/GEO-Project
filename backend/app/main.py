"""FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyses, brands, citations, owned_media, rankings, search
from app.config import get_settings
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="GEO Analyzer", version="0.1.0", lifespan=lifespan)

# Single-user internal tool; allow the local Next.js dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(analyses.router)
app.include_router(rankings.router)
app.include_router(owned_media.router)
app.include_router(citations.router)
app.include_router(search.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "test_mode": get_settings().geo_test_mode}
