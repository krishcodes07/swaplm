"""Unit tests for lifecycle hooks execution."""

import httpx

from swaplm import chat, on, reset_hooks
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


def _create_mock_client(handler) -> _Client:
    mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPTransport(client=mock_httpx)
    return _Client(http_transport=transport)


class TestLifecycleHooks:
    def setup_method(self):
        reset_hooks()

    def teardown_method(self):
        reset_hooks()

    def test_before_and_after_request_hooks(self, monkeypatch):
        events: list[str] = []

        def on_before(req):
            events.append("before")

        def on_after(req, res):
            events.append("after")

        on("before_request", on_before)
        on("after_request", on_after)

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

        assert events == ["before", "after"]
