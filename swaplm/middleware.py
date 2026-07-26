"""SwapLM Middleware system."""

from __future__ import annotations

from swaplm.exceptions import SwapLMError
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse


class BaseMiddleware:
    """Base class for SwapLM request/response middleware."""

    def process_request(self, request: ChatRequest) -> ChatRequest:
        """Inspect or modify the request before execution."""
        return request

    async def aprocess_request(self, request: ChatRequest) -> ChatRequest:
        """Inspect or modify the request before async execution."""
        return self.process_request(request)

    def process_response(self, response: ChatResponse) -> ChatResponse:
        """Inspect or modify the response after execution."""
        return response

    async def aprocess_response(self, response: ChatResponse) -> ChatResponse:
        """Inspect or modify the response after async execution."""
        return self.process_response(response)

    def process_error(self, error: SwapLMError) -> SwapLMError:
        """Inspect or modify exceptions raised during execution."""
        return error

    async def aprocess_error(self, error: SwapLMError) -> SwapLMError:
        """Inspect or modify exceptions raised during async execution."""
        return self.process_error(error)


_GLOBAL_MIDDLEWARES: list[BaseMiddleware] = []


def add_middleware(middleware: BaseMiddleware) -> None:
    """Register a middleware instance into the pipeline."""
    if middleware not in _GLOBAL_MIDDLEWARES:
        _GLOBAL_MIDDLEWARES.append(middleware)


def remove_middleware(middleware: BaseMiddleware) -> None:
    """Remove a middleware instance from the pipeline."""
    if middleware in _GLOBAL_MIDDLEWARES:
        _GLOBAL_MIDDLEWARES.remove(middleware)


def reset_middlewares() -> None:
    """Clear all registered middlewares."""
    _GLOBAL_MIDDLEWARES.clear()


def get_middlewares() -> list[BaseMiddleware]:
    """Return a list of all currently registered middlewares."""
    return list(_GLOBAL_MIDDLEWARES)
