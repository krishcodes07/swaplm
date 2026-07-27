"""Tests for the first-class free provider."""

from swaplm.discovery import models, provider, providers
from swaplm.providers.registry import default_provider_registry
from swaplm.router.router import Router


class TestFreeProvider:
    def test_free_provider_registered(self):
        registered_ids = default_provider_registry.list_providers()
        assert "free" in registered_ids

    def test_free_provider_metadata(self):
        info = provider("free")
        assert info.id == "free"
        assert info.name == "Free"
        assert info.protocol == "openai"
        assert info.requires_api_key is False
        assert info.supports_byok is False

    def test_free_provider_models_loaded(self):
        free_prov = default_provider_registry.get("free")
        model_list = free_prov.get_models()
        assert len(model_list) >= 8

        model_ids = [m.id for m in model_list]
        assert "meta-llama/llama-3.3-70b-instruct:free" in model_ids
        assert "deepseek/deepseek-r1-0528:free" in model_ids

    def test_free_provider_router_explicit_resolution(self):
        router = Router()
        prov_inst, model_id = router.resolve_explicit(
            "free", "meta-llama/llama-3.3-70b-instruct:free"
        )
        assert prov_inst.info.id == "free"
        assert model_id == "meta-llama/llama-3.3-70b-instruct:free"

    def test_free_provider_router_combined_string_resolution(self):
        router = Router()
        prov_inst, model_id = router.resolve("free/meta-llama/llama-3.3-70b-instruct:free")
        assert prov_inst.info.id == "free"
        assert model_id == "meta-llama/llama-3.3-70b-instruct:free"

    def test_free_provider_in_providers_discovery(self):
        all_provs = providers()
        free_meta = next((p for p in all_provs if p.id == "free"), None)
        assert free_meta is not None
        assert free_meta.requires_api_key is False

    def test_free_provider_models_discovery(self):
        all_models = models()
        free_models = [m for p, m in all_models if p.id == "free"]
        assert len(free_models) >= 8
