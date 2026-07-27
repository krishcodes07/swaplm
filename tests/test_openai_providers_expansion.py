"""Parameterized test suite for Phase 7 OpenAI-compatible provider expansion."""

import pytest

from swaplm import AmbiguousModelError
from swaplm.discovery import models, providers
from swaplm.providers.registry import default_provider_registry

ALL_EXPECTED_PROVIDERS = [
    "groq",
    "anthropic",
    "google",
    "openai",
    "openrouter",
    "github",
    "nvidia",
    "cerebras",
    "sambanova",
    "mistral",
    "xai",
    "deepinfra",
    "fireworks",
    "cloudflare",
    "perplexity",
    "cohere",
    "free",
]


class TestProviderExpansion:
    def setup_method(self):
        default_provider_registry.auto_discover()

    @pytest.mark.parametrize("provider_id", ALL_EXPECTED_PROVIDERS)
    def test_provider_registration_and_models(self, provider_id: str):
        p = default_provider_registry.get(provider_id)
        assert p is not None
        assert p.info.id == provider_id

        model_list = p.get_models()
        assert len(model_list) > 0, f"Provider {provider_id} has empty models.json"
        for m in model_list:
            assert m.id, f"Model in {provider_id} missing ID"
            assert m.context_window > 0

    def test_discovery_providers_count(self):
        prov_list = providers()
        prov_ids = [p.id for p in prov_list]
        for expected in ALL_EXPECTED_PROVIDERS:
            assert expected in prov_ids

    def test_discovery_models_list(self):
        all_models = models()
        assert len(all_models) >= 50

    def test_ambiguous_model_detection_across_providers(self):
        from swaplm.router.router import Router

        router = Router()
        # 'gpt-oss-120b' exists in openai, cerebras, and sambanova providers
        with pytest.raises(AmbiguousModelError) as exc_info:
            router.resolve("gpt-oss-120b")

        assert "openai" in exc_info.value.matching_providers
        assert "sambanova" in exc_info.value.matching_providers

    def test_explicit_routing_bypasses_ambiguity(self):
        from swaplm.router.router import Router

        router = Router()
        p_obj, m_id = router.resolve("openai/gpt-5.6-sol")
        assert p_obj.info.id == "openai"
        assert m_id == "gpt-5.6-sol"

        p_obj_gh, m_id_gh = router.resolve("github/phi-4")
        assert p_obj_gh.info.id == "github"
        assert m_id_gh == "phi-4"
