"""SwapLM exception hierarchy.

Every provider maps its native errors into these exceptions so
user code only needs to catch SwapLM types.
"""

from __future__ import annotations


class SwapLMError(Exception):
    """Base exception for all SwapLM errors."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------------------------
# Provider errors (HTTP / runtime)
# ---------------------------------------------------------------------------


class ProviderError(SwapLMError):
    """An error returned by an LLM provider."""

    def __init__(
        self,
        message: str = "",
        *,
        provider: str | None = None,
        model: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.provider:
            parts.append(f"provider={self.provider}")
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        return " | ".join(parts)


class AuthenticationError(ProviderError):
    """API key is missing, invalid, or expired."""


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""


class TimeoutError(ProviderError):
    """Request to the provider timed out."""


# ---------------------------------------------------------------------------
# Configuration / validation errors
# ---------------------------------------------------------------------------


class InvalidModelError(SwapLMError):
    """The requested model does not exist or is not supported."""

    def __init__(self, message: str = "", *, model: str | None = None) -> None:
        self.model = model
        super().__init__(message)


class InvalidProviderError(SwapLMError):
    """The requested provider does not exist or is not registered."""

    def __init__(self, message: str = "", *, provider: str | None = None) -> None:
        self.provider = provider
        super().__init__(message)


class ConfigurationError(SwapLMError):
    """SDK or provider configuration is invalid."""


class ToolCallError(SwapLMError):
    """Error related to tool / function calling."""
