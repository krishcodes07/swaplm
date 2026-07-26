"""Global SDK configuration system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from swaplm.transport.base import BaseTransport


class SDKConfig(BaseModel):
    """Global configuration defaults for SwapLM."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    timeout: float | None = None
    retries: int = 0
    retry_delay: float = 0.5
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    debug: bool = False
    logging: bool = False
    transport: Any = None


_global_config = SDKConfig()


def configure(
    *,
    timeout: float | None = None,
    retries: int | None = None,
    retry_delay: float | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    debug: bool | None = None,
    logging: bool | None = None,
    transport: BaseTransport | None = None,
    **extra: Any,
) -> SDKConfig:
    """Configure global SDK default options.

    Example::

        from swaplm import configure

        configure(timeout=60.0, retries=3, debug=True)
    """
    global _global_config
    current = _global_config.model_dump(exclude={"transport"})

    updates: dict[str, Any] = {}
    if timeout is not None:
        updates["timeout"] = timeout
    if retries is not None:
        updates["retries"] = retries
    if retry_delay is not None:
        updates["retry_delay"] = retry_delay
    if max_tokens is not None:
        updates["max_tokens"] = max_tokens
    if temperature is not None:
        updates["temperature"] = temperature
    if top_p is not None:
        updates["top_p"] = top_p
    if debug is not None:
        updates["debug"] = debug
    if logging is not None:
        updates["logging"] = logging

    current.update(updates)
    new_config = SDKConfig.model_validate(current)
    if transport is not None:
        new_config.transport = transport
    elif _global_config.transport is not None:
        new_config.transport = _global_config.transport

    _global_config = new_config
    return _global_config


def reset_config() -> SDKConfig:
    """Reset global configuration to defaults (useful in tests)."""
    global _global_config
    _global_config = SDKConfig()
    return _global_config


def get_config() -> SDKConfig:
    """Return the current global SDK configuration."""
    return _global_config
