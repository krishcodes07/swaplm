"""Unit tests for middleware system and pipeline execution order."""

import httpx
import pytest

from swaplm import (
    BaseMiddleware,
    ChatRequest,
    ChatResponse,
    achat,
    add_middleware,
    chat,
    reset_middlewares,
)
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


class OrderTrackingMiddleware(BaseMiddleware):
    def __init__(self, name: str, tracker: list[str]):
        self.name = name
        self.tracker = tracker

    def process_request(self, request: ChatRequest) -> ChatRequest:
        self.tracker.append(f"{self.name}:req")
        return request

    async def aprocess_request(self, request: ChatRequest) -> ChatRequest:
        self.tracker.append(f"{self.name}:areq")
        return request

    def process_response(self, response: ChatResponse) -> ChatResponse:
        self.tracker.append(f"{self.name}:res")
        return response

    async def aprocess_response(self, response: ChatResponse) -> ChatResponse:
        self.tracker.append(f"{self.name}:ares")
        return response


def _create_mock_client(handler) -> _Client:
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    mock_async_httpx = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx, async_client=mock_async_httpx)
    return _Client(http_transport=transport)


class TestMiddlewarePipeline:
    def setup_method(self):
        reset_middlewares()

    def teardown_method(self):
        reset_middlewares()

    def test_sync_middleware_pipeline_execution_order(self, monkeypatch):
        tracker: list[str] = []
        add_middleware(OrderTrackingMiddleware("M1", tracker))
        add_middleware(OrderTrackingMiddleware("M2", tracker))

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"role": "assistant", "content": "OK"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
        )

        assert tracker == ["M1:req", "M2:req", "M2:res", "M1:res"]

    @pytest.mark.asyncio
    async def test_async_middleware_pipeline_execution_order(self, monkeypatch):
        tracker: list[str] = []
        add_middleware(OrderTrackingMiddleware("M1", tracker))
        add_middleware(OrderTrackingMiddleware("M2", tracker))

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"role": "assistant", "content": "OK"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                },
            )

        client = _create_mock_client(handler)
        monkeypatch.setattr("swaplm._client._default_client", client)

        await achat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
        )

        assert tracker == ["M1:areq", "M2:areq", "M2:ares", "M1:ares"]
