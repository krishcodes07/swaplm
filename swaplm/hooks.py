"""SwapLM Lifecycle Hooks system."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

_HOOKS: dict[str, list[Callable[..., Any]]] = {
    "before_request": [],
    "after_request": [],
    "before_retry": [],
    "after_retry": [],
    "before_stream": [],
    "after_stream": [],
    "on_error": [],
}


def on(event: str, callback: Callable[..., Any]) -> Callable[..., Any]:
    """Register a callback listener for a lifecycle event."""
    if event not in _HOOKS:
        _HOOKS[event] = []
    if callback not in _HOOKS[event]:
        _HOOKS[event].append(callback)
    return callback


def off(event: str, callback: Callable[..., Any]) -> None:
    """Unregister a callback listener for a lifecycle event."""
    if event in _HOOKS and callback in _HOOKS[event]:
        _HOOKS[event].remove(callback)


def reset_hooks() -> None:
    """Clear all registered event listeners."""
    for key in _HOOKS:
        _HOOKS[key].clear()


def emit(event: str, *args: Any, **kwargs: Any) -> None:
    """Emit a synchronous lifecycle event."""
    listeners = _HOOKS.get(event, [])
    for listener in listeners:
        try:
            if not inspect.iscoroutinefunction(listener):
                listener(*args, **kwargs)
        except Exception:
            pass  # Hooks should never crash execution


async def aemit(event: str, *args: Any, **kwargs: Any) -> None:
    """Emit an asynchronous lifecycle event."""
    listeners = _HOOKS.get(event, [])
    for listener in listeners:
        try:
            if inspect.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)
        except Exception:
            pass
