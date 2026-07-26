"""Tests for the exception hierarchy."""

import pytest

from swaplm.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidModelError,
    InvalidProviderError,
    ProviderError,
    RateLimitError,
    SwapLMError,
    TimeoutError,
    ToolCallError,
)


class TestExceptionHierarchy:
    """All exceptions should inherit from SwapLMError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ProviderError,
            AuthenticationError,
            RateLimitError,
            TimeoutError,
            InvalidModelError,
            InvalidProviderError,
            ConfigurationError,
            ToolCallError,
        ],
    )
    def test_inherits_from_swaplm_error(self, exc_class):
        assert issubclass(exc_class, SwapLMError)

    def test_provider_error_subtypes(self):
        assert issubclass(AuthenticationError, ProviderError)
        assert issubclass(RateLimitError, ProviderError)
        assert issubclass(TimeoutError, ProviderError)


class TestProviderError:
    def test_attributes(self):
        err = ProviderError(
            "Something went wrong",
            provider="openai",
            model="gpt-5",
            status_code=500,
        )
        assert err.message == "Something went wrong"
        assert err.provider == "openai"
        assert err.model == "gpt-5"
        assert err.status_code == 500

    def test_str_representation(self):
        err = ProviderError("Bad request", provider="groq", status_code=400)
        s = str(err)
        assert "Bad request" in s
        assert "groq" in s
        assert "400" in s

    def test_catchable_as_swaplm_error(self):
        with pytest.raises(SwapLMError):
            raise ProviderError("test", provider="x", status_code=500)


class TestAuthenticationError:
    def test_attributes(self):
        err = AuthenticationError("Invalid key", provider="openai", status_code=401)
        assert err.status_code == 401
        assert isinstance(err, ProviderError)


class TestInvalidModelError:
    def test_attributes(self):
        err = InvalidModelError("Not found", model="bad/model")
        assert err.model == "bad/model"
        assert isinstance(err, SwapLMError)


class TestInvalidProviderError:
    def test_attributes(self):
        err = InvalidProviderError("Unknown", provider="xyz")
        assert err.provider == "xyz"
        assert isinstance(err, SwapLMError)
