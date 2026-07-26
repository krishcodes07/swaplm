"""Tests for the Groq provider metadata and model registry."""

from swaplm.providers.base import BaseProvider
from swaplm.providers.groq import GroqProvider
from swaplm.providers.registry import default_provider_registry


class TestGroqProvider:
    def test_provider_metadata(self):
        provider = GroqProvider()
        assert provider.info.id == "groq"
        assert provider.info.name == "Groq"
        assert provider.info.protocol == "openai"
        assert provider.info.base_url == "https://api.groq.com/openai/v1"
        assert provider.info.env_var == "GROQ_API_KEY"
        assert provider.info.requires_api_key is True
        assert provider.info.supports_byok is True

    def test_models_json_loading(self):
        provider = GroqProvider()
        models = provider.get_models()
        assert len(models) > 0

        model_ids = [m.id for m in models]
        assert "llama-3.3-70b-versatile" in model_ids
        assert "llama-3.1-8b-instant" in model_ids
        assert "deepseek-r1-distill-llama-70b" in model_ids

    def test_get_specific_model(self):
        provider = GroqProvider()
        model_info = provider.get_model("llama-3.3-70b-versatile")
        assert model_info is not None
        assert model_info.id == "llama-3.3-70b-versatile"
        assert model_info.context_window == 128000
        assert model_info.supports_streaming is True
        assert model_info.supports_tool_calling is True

    def test_thinking_model_capabilities(self):
        provider = GroqProvider()
        model_info = provider.get_model("deepseek-r1-distill-llama-70b")
        assert model_info is not None
        assert model_info.supports_thinking is True

    def test_auto_discovery(self):
        default_provider_registry.auto_discover()
        provider = default_provider_registry.get("groq")
        assert isinstance(provider, BaseProvider)
        assert provider.info.id == "groq"
