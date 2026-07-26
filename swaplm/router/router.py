"""Model string resolution and provider routing.

Supports:
1. Explicit ``"provider/model"`` (e.g. ``"groq/llama-3.3-70b-versatile"``)
2. Virtual ``"free/model"`` (e.g. ``"free/qwen3-30b"``)
3. Alias lookup (e.g. ``"llama-3.3-70b-versatile"``) with ambiguity detection
"""

from __future__ import annotations

from swaplm.exceptions import AmbiguousModelError, InvalidModelError
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry, default_provider_registry


class Router:
    """Resolves model strings to provider instances and model IDs."""

    def __init__(
        self,
        provider_registry: ProviderRegistry | None = None,
    ) -> None:
        self._provider_registry = provider_registry or default_provider_registry

    def resolve(self, model_string: str) -> tuple[BaseProvider, str]:
        """Parse a model string and return the provider + model ID.

        Resolution Order:
        1. Explicit ``"provider/model"`` (e.g. ``"groq/llama-3.3-70b-versatile"``)
        2. Virtual ``"free/model"`` (e.g. ``"free/qwen3-30b"``)
        3. Alias lookup (e.g. ``"llama-3.3-70b-versatile"``)

        Returns:
            A tuple of ``(provider_instance, model_id)``.

        Raises:
            AmbiguousModelError: If an alias matches multiple providers.
            InvalidModelError: If model is not found or format is invalid.
            InvalidProviderError: If the explicit provider ID is not registered.
        """
        if not model_string or not model_string.strip():
            raise InvalidModelError("Model string cannot be empty.", model=model_string)

        model_string = model_string.strip()

        # ── 1 & 2. Explicit or Virtual Provider ─────────────────────
        if "/" in model_string:
            provider_id, model_id = model_string.split("/", 1)
            if not provider_id or not model_id:
                raise InvalidModelError(
                    f"Invalid model format: '{model_string}'. Both provider and model must be non-empty.",
                    model=model_string,
                )

            # Virtual free provider
            if provider_id.lower() == "free":
                return self._resolve_free_provider(model_id)

            # Explicit provider
            provider = self._provider_registry.get(provider_id)
            self._validate_model(provider, model_id)
            return provider, model_id

        # ── 3. Alias Lookup ─────────────────────────────────────────
        return self._resolve_alias(model_string)

    def resolve_explicit(self, provider_id: str, model_id: str) -> tuple[BaseProvider, str]:
        """Resolve directly from an explicit provider ID and model ID.

        Bypasses model-string parsing. Validates that the provider
        exists and the model is valid for that provider.

        Args:
            provider_id: The provider slug (e.g. ``"groq"``).
            model_id: The raw model identifier (e.g. ``"llama-3.3-70b-versatile"``).

        Returns:
            A tuple of ``(provider_instance, model_id)``.
        """
        provider = self._provider_registry.get(provider_id)
        self._validate_model(provider, model_id)
        return provider, model_id

    def _resolve_free_provider(self, model_id: str) -> tuple[BaseProvider, str]:
        """Search all registered providers for a free provider matching model_id."""
        registered_ids = self._provider_registry.list_providers()
        free_matches: list[BaseProvider] = []

        for p_id in registered_ids:
            provider = self._provider_registry.get(p_id)
            if (provider.info.is_free or not provider.info.requires_api_key) and provider.get_model(
                model_id
            ) is not None:
                free_matches.append(provider)

        if not free_matches:
            # Fallback check: any free provider without models.json (pass-through)
            for p_id in registered_ids:
                provider = self._provider_registry.get(p_id)
                if (
                    provider.info.is_free or not provider.info.requires_api_key
                ) and not provider.get_models():
                    return provider, model_id

            raise InvalidModelError(
                f"No free provider found exposing model '{model_id}'.",
                model=model_id,
            )

        return free_matches[0], model_id

    def _resolve_alias(self, alias: str) -> tuple[BaseProvider, str]:
        """Search all registered providers for a model alias."""
        registered_ids = self._provider_registry.list_providers()
        matching_providers: list[BaseProvider] = []

        for p_id in registered_ids:
            provider = self._provider_registry.get(p_id)
            if provider.get_model(alias) is not None:
                matching_providers.append(provider)

        if len(matching_providers) == 1:
            return matching_providers[0], alias

        if len(matching_providers) > 1:
            provider_slugs = [p.info.id for p in matching_providers]
            raise AmbiguousModelError(
                model=alias,
                matching_providers=provider_slugs,
            )

        raise InvalidModelError(
            f"Model alias '{alias}' was not found in any registered provider.",
            model=alias,
        )

    @staticmethod
    def _validate_model(provider: BaseProvider, model_id: str) -> None:
        """Check the model exists in the provider's model list.

        Skips validation if the provider has no ``models.json`` registered.
        """
        models = provider.get_models()
        if not models:
            return
        if provider.get_model(model_id) is None:
            available = ", ".join(m.id for m in models[:10])
            raise InvalidModelError(
                f"Model '{model_id}' not found for provider '{provider.info.id}'. Available models: {available}",
                model=model_id,
            )
