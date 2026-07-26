"""Unit tests for custom transport injection via configure(transport=...)."""

from collections.abc import AsyncIterator, Iterator
from typing import Any

from swaplm import BaseTransport, ChatResponse, chat, configure, reset_config


class CustomMockTransport(BaseTransport):
    def send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> tuple[int, dict[str, Any]]:
        return 200, {
            "choices": [
                {"message": {"role": "assistant", "content": "Custom Transport response!"}}
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    async def asend(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> tuple[int, dict[str, Any]]:
        return 200, {
            "choices": [{"message": {"role": "assistant", "content": "Async Custom Transport!"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    def send_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        yield {}

    async def asend_stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        yield {}


class TestCustomTransport:
    def setup_method(self):
        reset_config()

    def teardown_method(self):
        reset_config()

    def test_custom_transport_injection(self):
        custom = CustomMockTransport()
        configure(transport=custom)

        response = chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_mock",
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Custom Transport response!"
