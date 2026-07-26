"""Tests for the provider registry."""

import pytest

from swaplm.exceptions import InvalidProviderError
from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import ProviderRegistry


class _ProviderA(BaseProvider):
    info = ProviderInfo(
        id="alpha",
        name="Alpha",
        protocol="openai",
        base_url="https://api.alpha.com/v1",
        env_var="ALPHA_API_KEY",
    )


class _ProviderB(BaseProvider):
    info = ProviderInfo(
        id="beta",
        name="Beta",
        protocol="anthropic",
        base_url="https://api.beta.com/v1",
        env_var="BETA_API_KEY",
    )


class TestProviderRegistry:
    def _make_registry(self) -> ProviderRegistry:
        reg = ProviderRegistry()
        reg._discovered = True  # skip auto-discover
        return reg

    def test_register_and_get(self):
        reg = self._make_registry()
        provider = _ProviderA()
        reg.register(provider)
        assert reg.get("alpha") is provider

    def test_unknown_provider_raises(self):
        reg = self._make_registry()
        with pytest.raises(InvalidProviderError, match="Unknown provider"):
            reg.get("nonexistent")

    def test_list_providers(self):
        reg = self._make_registry()
        reg.register(_ProviderA())
        reg.register(_ProviderB())
        ids = reg.list_providers()
        assert "alpha" in ids
        assert "beta" in ids

    def test_register_overwrites(self):
        reg = self._make_registry()
        p1 = _ProviderA()
        p2 = _ProviderA()
        reg.register(p1)
        reg.register(p2)
        assert reg.get("alpha") is p2

    def test_empty_registry(self):
        reg = self._make_registry()
        assert reg.list_providers() == []
