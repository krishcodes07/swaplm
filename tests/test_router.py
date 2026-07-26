"""Tests for the router."""

import pytest

from swaplm.exceptions import InvalidModelError, InvalidProviderError
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry
from swaplm.router.router import Router


class _FakeProvider(BaseProvider):
    """Test provider with an in-memory model list."""

    info = ProviderInfo(
        id="fake",
        name="Fake",
        protocol="openai",
        base_url="https://api.fake.com/v1",
        env_var="FAKE_API_KEY",
    )

    def __init__(self, models: list[ModelInfo] | None = None):
        self._models = models


def _make_router(providers: list[BaseProvider] | None = None) -> Router:
    registry = ProviderRegistry()
    registry._discovered = True  # skip auto-discover
    for p in providers or []:
        registry.register(p)
    return Router(provider_registry=registry)


class TestRouterParsing:
    def test_valid_model_string(self):
        provider = _FakeProvider()
        router = _make_router([provider])
        resolved_provider, model_id = router.resolve("fake/my-model")
        assert resolved_provider is provider
        assert model_id == "my-model"

    def test_model_string_with_nested_slash(self):
        provider = _FakeProvider()
        router = _make_router([provider])
        _, model_id = router.resolve("fake/org/model-name")
        assert model_id == "org/model-name"

    def test_missing_slash_treated_as_alias(self):
        router = _make_router()
        with pytest.raises(InvalidModelError, match="Model alias 'gpt-5' was not found"):
            router.resolve("gpt-5")

    def test_empty_provider_raises(self):
        router = _make_router()
        with pytest.raises(InvalidModelError, match="non-empty"):
            router.resolve("/gpt-5")

    def test_empty_model_raises(self):
        router = _make_router()
        with pytest.raises(InvalidModelError, match="non-empty"):
            router.resolve("openai/")


class TestRouterProviderLookup:
    def test_unknown_provider_raises(self):
        router = _make_router()
        with pytest.raises(InvalidProviderError, match="Unknown provider"):
            router.resolve("unknown/model")


class TestRouterModelValidation:
    def test_passthrough_when_no_models(self):
        """Providers with no models.json accept any model."""
        provider = _FakeProvider(models=[])
        router = _make_router([provider])
        _, model_id = router.resolve("fake/anything")
        assert model_id == "anything"

    def test_valid_model(self):
        provider = _FakeProvider(models=[ModelInfo(id="my-model")])
        router = _make_router([provider])
        _, model_id = router.resolve("fake/my-model")
        assert model_id == "my-model"

    def test_invalid_model_raises(self):
        provider = _FakeProvider(models=[ModelInfo(id="my-model")])
        router = _make_router([provider])
        with pytest.raises(InvalidModelError, match="not found"):
            router.resolve("fake/nonexistent")
