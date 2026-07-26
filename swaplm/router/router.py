"""Model string resolution and provider routing.

Parses ``"provider/model"`` strings, looks up the provider in the
registry, and validates the model exists.
"""

from __future__ import annotations

from swaplm.exceptions import InvalidModelError
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry, default_provider_registry


class Router:
    """Resolves ``"provider/model"`` strings to provider instances."""

    def __init__(
        self,
        provider_registry: ProviderRegistry | None = None,
    ) -> None:
        self._provider_registry = provider_registry or default_provider_registry

    def resolve(self, model_string: str) -> tuple[BaseProvider, str]:
        """Parse a model string and return the provider + model ID.

        Args:
            model_string: A string in ``"provider/model"`` format.

        Returns:
            A tuple of ``(provider_instance, model_id)``.

        Raises:
            InvalidModelError: If the model string format is invalid
                or the model is not in the provider's registry.
            InvalidProviderError: If the provider ID is not registered.
        """
        provider_id, model_id = self._parse_model_string(model_string)
        provider = self._provider_registry.get(provider_id)
        self._validate_model(provider, model_id)
        return provider, model_id

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _parse_model_string(model_string: str) -> tuple[str, str]:
        """Split ``"provider/model"`` into its components.

        Raises:
            InvalidModelError: If the string is not in the expected format.
        """
        if "/" not in model_string:
            raise InvalidModelError(
                f"Invalid model format: '{model_string}'. "
                "Expected 'provider/model' (e.g. 'openai/gpt-5').",
                model=model_string,
            )
        provider_id, model_id = model_string.split("/", 1)
        if not provider_id or not model_id:
            raise InvalidModelError(
                f"Invalid model format: '{model_string}'. "
                "Both provider and model must be non-empty.",
                model=model_string,
            )
        return provider_id, model_id

    @staticmethod
    def _validate_model(provider: BaseProvider, model_id: str) -> None:
        """Check the model exists in the provider's model list.

        Skips validation if the provider has no ``models.json`` registered.
        This allows pass-through for providers that accept arbitrary models.
        """
        models = provider.get_models()
        if not models:
            # No model list → accept anything (pass-through)
            return
        if provider.get_model(model_id) is None:
            available = ", ".join(m.id for m in models[:10])
            raise InvalidModelError(
                f"Model '{model_id}' not found for provider '{provider.info.id}'. "
                f"Available models: {available}",
                model=model_id,
            )
