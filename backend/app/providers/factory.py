"""Adapter factory: pick real adapters or fall back to mocks (test mode)."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.providers.base import ProviderAdapter
from app.providers.mock_adapter import MockAdapter

PROVIDERS = ("openai", "gemini", "anthropic")


def _model_for(provider: str, settings: Settings) -> str:
    return {
        "openai": settings.search_model_openai,
        "gemini": settings.search_model_gemini,
        "anthropic": settings.search_model_anthropic,
    }[provider]


def _api_key_for(provider: str, settings: Settings) -> str | None:
    return {
        "openai": settings.openai_api_key,
        "gemini": settings.google_api_key,
        "anthropic": settings.anthropic_api_key,
    }[provider]


def get_adapter(provider: str, settings: Settings | None = None) -> ProviderAdapter:
    """Return an adapter for ``provider``.

    Falls back to MockAdapter when test mode is on or the API key is missing,
    so the pipeline never makes a real (billable) call unintentionally.
    """
    settings = settings or get_settings()
    if provider not in PROVIDERS:
        raise ValueError(f"unknown provider: {provider}")

    key = _api_key_for(provider, settings)
    if settings.geo_test_mode or not key:
        return MockAdapter(provider)

    if provider == "openai":
        from app.providers.openai_adapter import OpenAIAdapter

        return OpenAIAdapter(key)
    if provider == "gemini":
        from app.providers.gemini_adapter import GeminiAdapter

        return GeminiAdapter(key)
    from app.providers.anthropic_adapter import AnthropicAdapter

    return AnthropicAdapter(key)


def active_providers(settings: Settings | None = None) -> list[str]:
    """Providers to actually use, honoring the user's selection.

    - ``ENABLED_PROVIDERS`` set → exactly those (in that order, valid ones only).
    - else test mode → all three (mocked).
    - else (real mode) → every provider whose API key is configured, so you
      run with only the engines you subscribe to.
    """
    settings = settings or get_settings()
    raw = settings.enabled_providers.strip()
    if raw:
        chosen = [p.strip() for p in raw.split(",")]
        return [p for p in chosen if p in PROVIDERS]
    if settings.geo_test_mode:
        return list(PROVIDERS)
    return [p for p in PROVIDERS if _api_key_for(p, settings)]


def get_all_adapters(
    settings: Settings | None = None,
) -> dict[str, tuple[ProviderAdapter, str]]:
    """Return ``{provider: (adapter, model)}`` for the active providers only."""
    settings = settings or get_settings()
    return {
        p: (get_adapter(p, settings), _model_for(p, settings))
        for p in active_providers(settings)
    }
