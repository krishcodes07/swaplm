"""Base provider class.

Each provider subclasses ``BaseProvider`` to declare its metadata.
The provider itself contains **no** request/response logic — that
lives entirely in the protocol layer.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from swaplm.exceptions import RegistryValidationError
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo


class BaseProvider:
    """Base class for all LLM providers.

    Subclasses must set the class-level ``info`` attribute with a
    ``ProviderInfo`` instance describing the provider's metadata.

    Models are loaded lazily from a ``models.json`` file located in the
    same directory as the provider module.
    """

    info: ProviderInfo
    """Provider metadata — must be set by each subclass."""

    _models: list[ModelInfo] | None = None

    def get_models(self) -> list[ModelInfo]:
        """Load and return the provider's model definitions.

        Reads from ``models.json`` in the same directory as the provider
        module.  Results are cached after the first call.

        Raises:
            RegistryValidationError: If models.json is invalid JSON or fails ModelInfo schema validation.
        """
        if self._models is not None:
            return self._models

        models_path = Path(self._get_models_path())
        if not models_path.exists():
            self._models = []
            return self._models

        try:
            with open(models_path, encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as exc:
            raise RegistryValidationError(
                f"Failed to parse models.json for provider '{self.info.id}': {exc}",
                provider_id=self.info.id,
                details=str(exc),
            ) from exc

        if not isinstance(raw, list):
            raise RegistryValidationError(
                f"Invalid models.json for provider '{self.info.id}': expected a JSON list of model objects.",
                provider_id=self.info.id,
            )

        parsed_models: list[ModelInfo] = []
        for idx, entry in enumerate(raw):
            try:
                parsed_models.append(ModelInfo.model_validate(entry))
            except ValidationError as exc:
                raise RegistryValidationError(
                    f"Model validation error in models.json for provider '{self.info.id}' at index {idx}: {exc}",
                    provider_id=self.info.id,
                    details=str(exc),
                ) from exc

        self._models = parsed_models
        return self._models

    def get_model(self, model_id: str) -> ModelInfo | None:
        """Look up a single model by its ID."""
        for m in self.get_models():
            if m.id == model_id:
                return m
        return None

    def _get_models_path(self) -> str:
        """Return the path to ``models.json`` for this provider.

        By default, looks in the same directory as the subclass module.
        """
        import inspect

        module_file = inspect.getfile(type(self))
        return str(Path(module_file).parent / "models.json")
