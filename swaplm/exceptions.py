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
# Configuration / validation / routing errors
# ---------------------------------------------------------------------------


class InvalidModelError(SwapLMError):
    """The requested model does not exist or is not supported."""

    def __init__(self, message: str = "", *, model: str | None = None) -> None:
        self.model = model
        super().__init__(message)


class AmbiguousModelError(InvalidModelError):
    """Multiple providers contain the requested model alias."""

    def __init__(
        self,
        message: str = "",
        *,
        model: str | None = None,
        matching_providers: list[str] | None = None,
    ) -> None:
        self.matching_providers = matching_providers or []
        if not message and model and self.matching_providers:
            providers_str = ", ".join(self.matching_providers)
            message = (
                f"Model alias '{model}' is ambiguous and matches multiple providers: {providers_str}. "
                f"Please specify explicit 'provider/model' (e.g. '{self.matching_providers[0]}/{model}')."
            )
        super().__init__(message, model=model)


class InvalidProviderError(SwapLMError):
    """The requested provider does not exist or is not registered."""

    def __init__(self, message: str = "", *, provider: str | None = None) -> None:
        self.provider = provider
        super().__init__(message)


class ConfigurationError(SwapLMError):
    """SDK or provider configuration is invalid."""


class RegistryValidationError(ConfigurationError):
    """Validation error when parsing a provider's models.json."""

    def __init__(
        self,
        message: str = "",
        *,
        provider_id: str | None = None,
        details: str | None = None,
    ) -> None:
        self.provider_id = provider_id
        self.details = details
        super().__init__(message)


class ModelCapabilityError(SwapLMError):
    """Requested operation is not supported by the model's capabilities."""

    def __init__(
        self,
        message: str = "",
        *,
        model: str | None = None,
        capability: str | None = None,
    ) -> None:
        self.model = model
        self.capability = capability
        super().__init__(message)


class ToolCallError(SwapLMError):
    """Error related to tool / function calling."""
