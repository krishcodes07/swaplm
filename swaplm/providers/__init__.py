"""Vendor-specific LLM provider adapters.

Re-exports the base class, registry, and default singleton.
"""

from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry, default_provider_registry

__all__ = [
    "BaseProvider",
    "ProviderRegistry",
    "default_provider_registry",
]
