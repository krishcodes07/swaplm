"""SwapLM Logging and Debug Utilities."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("swaplm")

_SENSITIVE_HEADERS = {"authorization", "x-api-key", "x-goog-api-key", "api-key"}


def redact_headers(headers: dict[str, str] | None) -> dict[str, str]:
    """Return a copy of headers with sensitive authorization keys redacted."""
    if not headers:
        return {}
    redacted: dict[str, str] = {}
    for k, v in headers.items():
        if k.lower() in _SENSITIVE_HEADERS:
            redacted[k] = "***"
        else:
            redacted[k] = v
    return redacted


def redact_body(body: dict[str, Any] | None, *, debug: bool = False) -> dict[str, Any]:
    """Return a copy of request body with sensitive data redacted unless debug is enabled."""
    if not body:
        return {}
    if debug:
        return dict(body)
    redacted = dict(body)
    if "messages" in redacted:
        redacted["messages"] = f"[{len(redacted['messages'])} message(s) redacted]"
    return redacted


def log_debug(msg: str, *, debug: bool = False) -> None:
    """Log a debug message if debug or SDK logging is enabled."""
    if debug:
        logger.info(f"[SwapLM DEBUG] {msg}")
    else:
        logger.debug(msg)
