"""Tests for the Google Gemini provider metadata and model registry."""

from swaplm.providers.base import BaseProvider
from swaplm.providers.google import GoogleProvider
from swaplm.providers.registry import default_provider_registry


class TestGoogleProvider:
    def test_provider_metadata(self):
        provider = GoogleProvider()
        assert provider.info.id == "google"
        assert provider.info.name == "Google"
        assert provider.info.protocol == "google"
        assert provider.info.base_url == "https://generativelanguage.googleapis.com/v1beta"
        assert provider.info.env_var == "GEMINI_API_KEY"

    def test_models_json_loading(self):
        provider = GoogleProvider()
        models = provider.get_models()
        assert len(models) > 0

        model_ids = [m.id for m in models]
        assert "gemini-2.5-pro" in model_ids
        assert "gemini-2.5-flash" in model_ids
        assert "gemini-2.0-flash" in model_ids

    def test_context_window(self):
        provider = GoogleProvider()
        model_info = provider.get_model("gemini-2.5-pro")
        assert model_info is not None
        assert model_info.context_window == 2000000

    def test_auto_discovery(self):
        default_provider_registry.auto_discover()
        provider = default_provider_registry.get("google")
        assert isinstance(provider, BaseProvider)
        assert provider.info.id == "google"
