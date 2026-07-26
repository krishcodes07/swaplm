"""Custom transport injection example using SwapLM."""

from collections.abc import AsyncIterator, Iterator
from typing import Any

from swaplm import BaseTransport, chat, configure, reset_config


class MockCustomTransport(BaseTransport):
    """Custom transport implementation mocking network requests."""

    def send(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> tuple[int, dict[str, Any] | str]:
        print(f"[Custom Transport] Mocking HTTP POST to: {url}")
        return 200, {
            "id": "chatcmpl-mock123",
            "object": "chat.completion",
            "model": json_body.get("model", "mock-model") if json_body else "mock-model",
            "choices": [
                {"message": {"role": "assistant", "content": "Hello from custom transport!"}}
            ],
        }

    async def asend(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> tuple[int, dict[str, Any] | str]:
        return self.send(url, headers, json_body, timeout)

    def send_stream(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> Iterator[str]:
        yield 'data: {"choices":[{"delta":{"content":"Mock stream chunk"}}\n\n'

    async def asend_stream(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> AsyncIterator[str]:
        yield 'data: {"choices":[{"delta":{"content":"Mock stream chunk"}}\n\n'

    def close(self) -> None:
        pass

    async def aclose(self) -> None:
        pass


def main():
    # Inject custom transport globally
    configure(transport=MockCustomTransport())

    response = chat(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Test prompt"}],
    )

    print("Response:", response.content)

    reset_config()


if __name__ == "__main__":
    main()
