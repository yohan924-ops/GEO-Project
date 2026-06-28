# GEO Analyzer — Backend

FastAPI backend for the GEO (Generative Engine Optimization) analysis tool.
See the repository-root `CLAUDE.md` for the full architecture and roadmap.

## Phase 1 scope

- Project scaffolding, DB, settings.
- Service 1: brand → keyword/question prompts.
- Provider adapters (OpenAI / Gemini / Anthropic) skeletons + a mock adapter.
- Endpoint to run a single prompt against all three providers once.

## Run

```bash
cd backend
uv sync --extra dev
cp .env.example .env          # fill in API keys (optional in test mode)
uv run uvicorn app.main:app --reload   # http://localhost:8000
```

API docs: http://localhost:8000/docs

## Test mode (no 3rd-party billing)

Set `GEO_TEST_MODE=true` (default in `.env.example`) to use template-based
prompt generation and mock provider adapters — **no real LLM API calls**, so
development costs nothing on OpenAI/Gemini/Anthropic.

```bash
uv run pytest          # all tests run fully mocked
uv run ruff check .
```
