"""Tests for model capability filtering in protocol payload generation."""

from swaplm.models.messages import Message, Tool
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.protocols.openai import OpenAIProtocol


class TestCapabilityFiltering:
    def setup_method(self):
        self.protocol = OpenAIProtocol()
        self.provider_info = ProviderInfo(
            id="test",
            name="Test",
            protocol="openai",
            base_url="https://api.test.com",
            env_var="TEST_API_KEY",
        )

    def test_seed_omitted_when_unsupported(self):
        model_info = ModelInfo(id="m1", supports_seed=False)
        req = ChatRequest(
            model="test/m1",
            messages=[Message(role="user", content="Hi")],
            seed=42,
        )
        body = self.protocol.build_request_body(req, model_info=model_info)
        assert "seed" not in body

    def test_seed_included_when_supported(self):
        model_info = ModelInfo(id="m1", supports_seed=True)
        req = ChatRequest(
            model="test/m1",
            messages=[Message(role="user", content="Hi")],
            seed=42,
        )
        body = self.protocol.build_request_body(req, model_info=model_info)
        assert body.get("seed") == 42

    def test_tools_omitted_when_tool_calling_unsupported(self):
        model_info = ModelInfo(id="m1", supports_tool_calling=False)
        tool = Tool.model_validate(
            {"type": "function", "function": {"name": "fn", "description": "desc"}}
        )
        req = ChatRequest(
            model="test/m1",
            messages=[Message(role="user", content="Hi")],
            tools=[tool],
            tool_choice="auto",
        )
        body = self.protocol.build_request_body(req, model_info=model_info)
        assert "tools" not in body
        assert "tool_choice" not in body

    def test_thinking_and_response_format_filtered_from_provider_options(self):
        model_info = ModelInfo(
            id="m1",
            supports_thinking=False,
            supports_json_mode=False,
            supports_structured_output=False,
        )
        req = ChatRequest(
            model="test/m1",
            messages=[Message(role="user", content="Hi")],
            provider_options={
                "thinking": {"type": "enabled"},
                "response_format": {"type": "json_object"},
                "custom_option": 123,
            },
        )
        body = self.protocol.build_request_body(req, model_info=model_info)
        assert "thinking" not in body
        assert "response_format" not in body
        assert body.get("custom_option") == 123
