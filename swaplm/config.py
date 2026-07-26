"""Global SDK configuration system."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SDKConfig(BaseModel):
    """Global configuration defaults for SwapLM."""

    timeout: float | None = None
    retries: int = 0
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None


# Default global instance
_global_config = SDKConfig()


def configure(
    *,
    timeout: float | None = None,
    retries: int | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    **extra: Any,
) -> SDKConfig:
    """Configure global SDK default options.

    Example::

        from swaplm import configure

        configure(timeout=60.0, retries=3, max_tokens=4096)
    """
    global _global_config
    current = _global_config.model_dump()

    updates: dict[str, Any] = {}
    if timeout is not None:
        updates["timeout"] = timeout
    if retries is not None:
        updates["retries"] = retries
    if max_tokens is not None:
        updates["max_tokens"] = max_tokens
    if temperature is not None:
        updates["temperature"] = temperature
    if top_p is not None:
        updates["top_p"] = top_p

    current.update(updates)
    _global_config = SDKConfig.model_validate(current)
    return _global_config


def reset_config() -> SDKConfig:
    """Reset global configuration to defaults (useful in tests)."""
    global _global_config
    _global_config = SDKConfig()
    return _global_config


def get_config() -> SDKConfig:
    """Return the current global SDK configuration."""
    return _global_config
