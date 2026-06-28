"""Provider selection (active_providers) + /providers endpoint tests."""

from app.config import Settings
from app.providers import active_providers, get_all_adapters


def test_test_mode_uses_all_three():
    s = Settings(geo_test_mode=True, enabled_providers="")
    assert active_providers(s) == ["openai", "gemini", "anthropic"]


def test_explicit_selection_single():
    s = Settings(geo_test_mode=True, enabled_providers="anthropic")
    assert active_providers(s) == ["anthropic"]
    assert set(get_all_adapters(s)) == {"anthropic"}


def test_explicit_selection_preserves_order_and_filters_invalid():
    s = Settings(geo_test_mode=True, enabled_providers="anthropic, bing, openai")
    assert active_providers(s) == ["anthropic", "openai"]


def test_real_mode_auto_selects_by_key():
    s = Settings(geo_test_mode=False, enabled_providers="", anthropic_api_key="x")
    assert active_providers(s) == ["anthropic"]


def test_real_mode_two_keys():
    s = Settings(
        geo_test_mode=False,
        enabled_providers="",
        openai_api_key="x",
        anthropic_api_key="y",
    )
    assert active_providers(s) == ["openai", "anthropic"]


def test_real_mode_no_keys_is_empty():
    s = Settings(geo_test_mode=False, enabled_providers="")
    assert active_providers(s) == []


def test_explicit_overrides_keys():
    # Explicit selection wins even if a different key is present.
    s = Settings(
        geo_test_mode=False, enabled_providers="anthropic", openai_api_key="x"
    )
    assert active_providers(s) == ["anthropic"]


def test_providers_endpoint(client):
    resp = client.get("/providers")
    assert resp.status_code == 200
    body = resp.json()
    assert body["test_mode"] is True
    assert body["providers"] == ["openai", "gemini", "anthropic"]
