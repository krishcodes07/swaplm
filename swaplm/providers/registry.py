"""Dynamic provider registry.

Providers are auto-discovered by scanning ``swaplm/providers/*/provider.py``
for ``BaseProvider`` subclasses.  Adding a new provider only requires
creating a new directory with a ``provider.py`` module.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

from swaplm.exceptions import InvalidProviderError
from swaplm.providers.base import BaseProvider


class ProviderRegistry:
    """Registry of available LLM providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        self._discovered = False

    def register(self, provider: BaseProvider) -> None:
        """Register a provider instance.

        Args:
            provider: A ``BaseProvider`` subclass instance with ``info`` set.
        """
        self._providers[provider.info.id] = provider

    def get(self, provider_id: str) -> BaseProvider:
        """Retrieve a registered provider by its ID.

        Triggers auto-discovery on first access.

        Raises:
            InvalidProviderError: If the provider ID is not registered.
        """
        self._ensure_discovered()
        if provider_id not in self._providers:
            available = ", ".join(sorted(self._providers)) or "(none)"
            raise InvalidProviderError(
                f"Unknown provider '{provider_id}'. Available providers: {available}",
                provider=provider_id,
            )
        return self._providers[provider_id]

    def list_providers(self) -> list[str]:
        """Return all registered provider IDs."""
        self._ensure_discovered()
        return list(self._providers)

    def list_instances(self) -> list[BaseProvider]:
        """Return all registered provider instances."""
        self._ensure_discovered()
        return list(self._providers.values())

    def auto_discover(self) -> None:
        """Scan ``swaplm/providers/*/provider.py`` for ``BaseProvider`` subclasses.

        Each discovered subclass is instantiated and registered.  This is
        called lazily on the first ``get()`` or ``list_providers()`` call.
        """
        providers_dir = Path(__file__).parent

        for module_info in pkgutil.iter_modules([str(providers_dir)]):
            if not module_info.ispkg:
                continue

            module_name = f"swaplm.providers.{module_info.name}.provider"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue

            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseProvider)
                    and obj is not BaseProvider
                    and hasattr(obj, "info")
                ):
                    instance = obj()
                    if instance.info.id not in self._providers:
                        self.register(instance)

        self._discovered = True

    def _ensure_discovered(self) -> None:
        """Run auto-discovery if it hasn't happened yet."""
        if not self._discovered:
            self.auto_discover()


# Module-level singleton
default_provider_registry = ProviderRegistry()
