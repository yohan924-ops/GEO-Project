"""Provider adapter interface and normalized result types (CLAUDE.md §6.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class Citation:
    url: str
    title: str | None = None
    snippet: str | None = None
    domain: str = ""

    def __post_init__(self) -> None:
        if not self.domain and self.url:
            self.domain = extract_domain(self.url)


@dataclass
class ProviderResult:
    provider: str  # "openai" | "gemini" | "anthropic"
    model: str
    answer_text: str = ""
    citations: list[Citation] = field(default_factory=list)
    usage: dict = field(default_factory=dict)  # input/output tokens
    cost_usd: float = 0.0
    latency_ms: int = 0
    raw: dict = field(default_factory=dict)  # original response (debugging)


class ProviderAdapter:
    """Async interface implemented by every provider adapter."""

    provider: str = ""

    async def search(self, prompt: str, *, model: str) -> ProviderResult:
        raise NotImplementedError


def extract_domain(url: str) -> str:
    """Extract a normalized registrable host from a URL.

    Lowercases and strips a leading ``www.``. Subdomain-aware mapping
    (instagram.com/{handle}, etc.) is handled later in service 3.
    """
    if not url:
        return ""
    netloc = urlparse(url if "://" in url else f"//{url}").netloc.lower()
    if not netloc:
        # urlparse puts bare "example.com/x" into path; fall back.
        netloc = urlparse(f"//{url}").netloc.lower()
    netloc = netloc.split("@")[-1].split(":")[0]  # drop userinfo / port
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc
