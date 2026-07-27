"""Tests for advanced router resolution: aliases and ambiguity detection."""

import pytest

from swaplm.exceptions import AmbiguousModelError, InvalidModelError
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry
from swaplm.router.router import Router


class _MockProvider(BaseProvider):
    def __init__(
        self,
        p_id: str,
        requires_api_key: bool = True,
        models: list[ModelInfo] | None = None,
    ):
        self.info = ProviderInfo(
            id=p_id,
            name=p_id.capitalize(),
            protocol="openai",
            base_url=f"https://api.{p_id}.com",
            env_var=f"{p_id.upper()}_API_KEY",
            requires_api_key=requires_api_key,
        )
        self._models = models or []


def _build_router(providers: list[BaseProvider]) -> Router:
    reg = ProviderRegistry()
    reg._discovered = True
    for p in providers:
        reg.register(p)
    return Router(provider_registry=reg)


class TestAdvancedRouter:
    def test_explicit_routing(self):
        p1 = _MockProvider("provider1", models=[ModelInfo(id="m1")])
        router = _build_router([p1])

        provider, model_id = router.resolve("provider1/m1")
        assert provider.info.id == "provider1"
        assert model_id == "m1"

    def test_alias_single_match(self):
        p1 = _MockProvider("provider1", models=[ModelInfo(id="unique-model")])
        p2 = _MockProvider("provider2", models=[ModelInfo(id="other-model")])
        router = _build_router([p1, p2])

        provider, model_id = router.resolve("unique-model")
        assert provider.info.id == "provider1"
        assert model_id == "unique-model"

    def test_alias_ambiguous_raises(self):
        p1 = _MockProvider("provider1", models=[ModelInfo(id="shared-model")])
        p2 = _MockProvider("provider2", models=[ModelInfo(id="shared-model")])
        router = _build_router([p1, p2])

        with pytest.raises(AmbiguousModelError) as exc_info:
            router.resolve("shared-model")

        assert "shared-model" in str(exc_info.value)
        assert set(exc_info.value.matching_providers) == {"provider1", "provider2"}

    def test_alias_unknown_raises(self):
        p1 = _MockProvider("provider1", models=[ModelInfo(id="m1")])
        router = _build_router([p1])

        with pytest.raises(InvalidModelError, match="not found in any registered provider"):
            router.resolve("unknown-alias")
