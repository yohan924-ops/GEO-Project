"""Provider adapter + factory tests (mock mode, no real calls)."""

import pytest

from app.config import get_settings
from app.providers import extract_domain, get_adapter, get_all_adapters
from app.providers.mock_adapter import MockAdapter


def test_extract_domain_strips_www_and_port():
    assert extract_domain("https://www.Example.com/path?q=1") == "example.com"
    assert extract_domain("http://blog.example.org:8080/p/1") == "blog.example.org"
    assert extract_domain("instagram.com/brandhandle") == "instagram.com"
    assert extract_domain("") == ""


def test_factory_returns_mock_in_test_mode():
    adapter = get_adapter("anthropic", get_settings())
    assert isinstance(adapter, MockAdapter)


def test_factory_unknown_provider():
    with pytest.raises(ValueError):
        get_adapter("bing", get_settings())


def test_get_all_adapters_covers_three():
    adapters = get_all_adapters(get_settings())
    assert set(adapters) == {"openai", "gemini", "anthropic"}


@pytest.mark.asyncio
async def test_mock_search_is_deterministic():
    a = MockAdapter("anthropic")
    r1 = await a.search("운동화 추천", model="claude-sonnet-4-6")
    r2 = await a.search("운동화 추천", model="claude-sonnet-4-6")
    assert r1.answer_text == r2.answer_text
    assert r1.provider == "anthropic"
    assert len(r1.citations) == 3
    assert all(c.domain for c in r1.citations)
    assert r1.cost_usd == 0.0
