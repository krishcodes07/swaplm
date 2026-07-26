"""Tests for public provider and model discovery APIs."""

import swaplm
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.providers.groq import GroqProvider
from swaplm.providers.registry import default_provider_registry


class TestDiscoveryAPIs:
    def setup_method(self):
        default_provider_registry.register(GroqProvider())

    def test_providers_api(self):
        provs = swaplm.providers()
        assert len(provs) > 0
        groq_info = next((p for p in provs if p.id == "groq"), None)
        assert groq_info is not None
        assert isinstance(groq_info, ProviderInfo)
        assert groq_info.name == "Groq"

    def test_models_api(self):
        all_models = swaplm.models()
        assert len(all_models) > 0

        p_info, m_info = all_models[0]
        assert isinstance(p_info, ProviderInfo)
        assert isinstance(m_info, ModelInfo)

    def test_single_provider_api(self):
        p_info = swaplm.provider("groq")
        assert isinstance(p_info, ProviderInfo)
        assert p_info.id == "groq"
        assert p_info.base_url == "https://api.groq.com/openai/v1"

    def test_single_model_api(self):
        p_info, m_info = swaplm.model("groq/llama-3.3-70b-versatile")
        assert p_info.id == "groq"
        assert m_info.id == "llama-3.3-70b-versatile"
        assert m_info.context_window == 128000

    def test_single_model_api_by_alias(self):
        p_info, m_info = swaplm.model("llama-3.3-70b-versatile")
        assert p_info.id == "groq"
        assert m_info.id == "llama-3.3-70b-versatile"
