"""Tests for models.json registry schema validation in BaseProvider."""

import json
from pathlib import Path

import pytest

from swaplm.exceptions import RegistryValidationError
from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class _BadProvider(BaseProvider):
    def __init__(self, models_path: Path):
        self._models_file = str(models_path)
        self.info = ProviderInfo(
            id="bad",
            name="Bad",
            protocol="openai",
            base_url="https://api.bad.com",
            env_var="BAD_KEY",
        )

    def _get_models_path(self) -> str:
        return self._models_file


class TestRegistryValidation:
    def test_invalid_json_raises_registry_validation_error(self, tmp_path):
        bad_json = tmp_path / "models.json"
        bad_json.write_text("{invalid json", encoding="utf-8")

        provider = _BadProvider(bad_json)
        with pytest.raises(RegistryValidationError, match=r"Failed to parse models\.json"):
            provider.get_models()

    def test_non_list_json_raises_registry_validation_error(self, tmp_path):
        bad_json = tmp_path / "models.json"
        bad_json.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        provider = _BadProvider(bad_json)
        with pytest.raises(RegistryValidationError, match=r"expected a JSON list"):
            provider.get_models()

    def test_invalid_schema_entry_raises_registry_validation_error(self, tmp_path):
        bad_json = tmp_path / "models.json"
        # Invalid context_window type (string instead of int)
        bad_json.write_text(
            json.dumps([{"id": "m1", "context_window": "invalid_number"}]),
            encoding="utf-8",
        )

        provider = _BadProvider(bad_json)
        with pytest.raises(RegistryValidationError, match=r"Model validation error"):
            provider.get_models()
