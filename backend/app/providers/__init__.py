"""Provider adapters (CLAUDE.md §6)."""

from app.providers.base import Citation, ProviderAdapter, ProviderResult, extract_domain
from app.providers.factory import active_providers, get_adapter, get_all_adapters

__all__ = [
    "Citation",
    "ProviderResult",
    "ProviderAdapter",
    "extract_domain",
    "get_adapter",
    "get_all_adapters",
    "active_providers",
]
