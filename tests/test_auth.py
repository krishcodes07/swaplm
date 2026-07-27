"""Tests for the authentication manager."""

import os

import pytest

from swaplm.auth.manager import AuthManager
from swaplm.exceptions import AuthenticationError
from swaplm.models.provider import ProviderInfo
from swaplm.providers.base import BaseProvider


class _TestProvider(BaseProvider):
    info = ProviderInfo(
        id="test",
        name="Test Provider",
        protocol="openai",
        base_url="https://api.test.com",
        env_var="TEST_API_KEY",
    )


class _NoKeyProvider(BaseProvider):
    info = ProviderInfo(
        id="nokey",
        name="No-Key Provider",
        protocol="openai",
        base_url="https://api.nokey.com",
        env_var="NOKEY_API_KEY",
        requires_api_key=False,
    )


class TestAuthManager:
    def setup_method(self):
        self.auth = AuthManager()
        # Clean up env var before each test
        os.environ.pop("TEST_API_KEY", None)

    def teardown_method(self):
        os.environ.pop("TEST_API_KEY", None)

    def test_explicit_key_takes_priority(self):
        os.environ["TEST_API_KEY"] = "env-key"
        provider = _TestProvider()
        key = self.auth.resolve_api_key(provider, explicit_key="explicit-key")
        assert key == "explicit-key"

    def test_env_var_fallback(self):
        os.environ["TEST_API_KEY"] = "env-key"
        provider = _TestProvider()
        key = self.auth.resolve_api_key(provider)
        assert key == "env-key"

    def test_missing_key_raises(self):
        provider = _TestProvider()
        with pytest.raises(AuthenticationError, match="TEST_API_KEY"):
            self.auth.resolve_api_key(provider)

    def test_no_key_required(self):
        provider = _NoKeyProvider()
        key = self.auth.resolve_api_key(provider)
        assert key == ""

    def test_error_includes_provider_name(self):
        provider = _TestProvider()
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth.resolve_api_key(provider)
        assert exc_info.value.provider == "test"
