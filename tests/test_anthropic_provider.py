"""Tests for the Anthropic provider metadata and model registry."""

from swaplm.providers.anthropic import AnthropicProvider
from swaplm.providers.base import BaseProvider
from swaplm.providers.registry import default_provider_registry


class TestAnthropicProvider:
    def test_provider_metadata(self):
        provider = AnthropicProvider()
        assert provider.info.id == "anthropic"
        assert provider.info.name == "Anthropic"
        assert provider.info.protocol == "anthropic"
        assert provider.info.base_url == "https://api.anthropic.com/v1"
        assert provider.info.env_var == "ANTHROPIC_API_KEY"

    def test_models_json_loading(self):
        provider = AnthropicProvider()
        models = provider.get_models()
        assert len(models) > 0

        model_ids = [m.id for m in models]
        assert "claude-3-7-sonnet-20250219" in model_ids
        assert "claude-3-5-sonnet-20241022" in model_ids

    def test_thinking_capability(self):
        provider = AnthropicProvider()
        model_info = provider.get_model("claude-3-7-sonnet-20250219")
        assert model_info is not None
        assert model_info.supports_thinking is True

    def test_auto_discovery(self):
        default_provider_registry.auto_discover()
        provider = default_provider_registry.get("anthropic")
        assert isinstance(provider, BaseProvider)
        assert provider.info.id == "anthropic"
