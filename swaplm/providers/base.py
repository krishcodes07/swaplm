"""Base provider class.

Each provider subclasses ``BaseProvider`` to declare its metadata.
The provider itself contains **no** request/response logic — that
lives entirely in the protocol layer.
"""

from __future__ import annotations

import json
from pathlib import Path

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
        """
        if self._models is not None:
            return self._models

        models_path = Path(self._get_models_path())
        if not models_path.exists():
            self._models = []
            return self._models

        with open(models_path) as f:
            raw = json.load(f)

        self._models = [ModelInfo.model_validate(entry) for entry in raw]
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
