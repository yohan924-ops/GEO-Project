# GEO Analyzer backend — production image.
FROM python:3.12-slim

# uv for fast, locked installs.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached unless lock/manifest change).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# App source.
COPY app ./app

ENV PORT=8000
# Hosts (Render/Railway/Fly) inject $PORT; bind to 0.0.0.0 so it's reachable.
CMD ["sh", "-c", "uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
