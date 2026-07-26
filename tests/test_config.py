"""Tests for global SDK configuration system."""

from typing import Any

import httpx

import swaplm
from swaplm import configure, get_config, reset_config
from swaplm._client import _Client
from swaplm.transport.http import HTTPTransport


class TestConfig:
    def setup_method(self):
        reset_config()

    def teardown_method(self):
        reset_config()

    def test_configure_sets_defaults(self):
        cfg = configure(timeout=45.0, retries=2, max_tokens=2048, temperature=0.5)
        assert cfg.timeout == 45.0
        assert cfg.retries == 2
        assert cfg.max_tokens == 2048
        assert cfg.temperature == 0.5

        active = get_config()
        assert active.timeout == 45.0

    def test_chat_inherits_global_config_defaults(self, monkeypatch):
        configure(timeout=30.0, max_tokens=1000, temperature=0.2)

        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_request["body"] = json.loads(request.read().decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "llama-3.3-70b-versatile",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}}],
                },
            )

        mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
        client = _Client(http_transport=HTTPTransport(client=mock_httpx))
        monkeypatch.setattr("swaplm._client._default_client", client)

        swaplm.chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_test",
        )

        body = captured_request["body"]
        assert body.get("max_tokens") == 1000
        assert body.get("temperature") == 0.2

    def test_explicit_call_param_overrides_global_config(self, monkeypatch):
        configure(max_tokens=1000, temperature=0.2)

        captured_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            captured_request["body"] = json.loads(request.read().decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "id": "c1",
                    "model": "llama-3.3-70b-versatile",
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"}}],
                },
            )

        mock_httpx = httpx.Client(transport=httpx.MockTransport(handler))
        client = _Client(http_transport=HTTPTransport(client=mock_httpx))
        monkeypatch.setattr("swaplm._client._default_client", client)

        swaplm.chat(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            api_key="gsk_test",
            max_tokens=500,
            temperature=0.9,
        )

        body = captured_request["body"]
        assert body.get("max_tokens") == 500
        assert body.get("temperature") == 0.9
