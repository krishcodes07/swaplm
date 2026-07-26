"""Tests for Pydantic models: construction, validation, serialization, computed properties."""

from swaplm.models import (
    ChatRequest,
    ChatResponse,
    Choice,
    ChoiceDelta,
    ChunkChoice,
    FunctionCall,
    FunctionDefinition,
    Message,
    ModelInfo,
    ProviderInfo,
    StreamChunk,
    Tool,
    ToolCall,
    Usage,
)

# ---------------------------------------------------------------------------
# Message models
# ---------------------------------------------------------------------------


class TestMessage:
    def test_basic_user_message(self):
        msg = Message(role="user", content="Hello!")
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert msg.tool_calls is None

    def test_assistant_message_with_tool_calls(self):
        tc = ToolCall(
            id="call_1",
            type="function",
            function=FunctionCall(name="get_weather", arguments='{"city": "SF"}'),
        )
        msg = Message(role="assistant", content=None, tool_calls=[tc])
        assert msg.role == "assistant"
        assert msg.content is None
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].function.name == "get_weather"

    def test_tool_response_message(self):
        msg = Message(role="tool", content="Sunny, 72°F", tool_call_id="call_1")
        assert msg.role == "tool"
        assert msg.tool_call_id == "call_1"

    def test_message_extra_fields_allowed(self):
        msg = Message(role="user", content="Hi", custom_field="value")
        assert msg.model_extra.get("custom_field") == "value"


class TestTool:
    def test_tool_construction(self):
        tool = Tool(
            function=FunctionDefinition(
                name="search",
                description="Search the web",
                parameters={"type": "object", "properties": {"q": {"type": "string"}}},
            )
        )
        assert tool.type == "function"
        assert tool.function.name == "search"
        assert tool.function.description == "Search the web"

    def test_tool_serialization(self):
        tool = Tool(function=FunctionDefinition(name="ping", description=None, parameters=None))
        data = tool.model_dump(exclude_none=True)
        assert data["function"]["name"] == "ping"
        assert "description" not in data["function"]


# ---------------------------------------------------------------------------
# ChatRequest
# ---------------------------------------------------------------------------


class TestChatRequest:
    def test_minimal_request(self):
        req = ChatRequest(
            model="openai/gpt-5",
            messages=[Message(role="user", content="Hi")],
        )
        assert req.model == "openai/gpt-5"
        assert req.stream is False
        assert req.retries == 0

    def test_computed_provider_id(self):
        req = ChatRequest(
            model="groq/llama-4",
            messages=[Message(role="user", content="Hi")],
        )
        assert req.provider_id == "groq"
        assert req.model_id == "llama-4"

    def test_computed_provider_id_no_slash(self):
        req = ChatRequest(
            model="gpt-5",
            messages=[Message(role="user", content="Hi")],
        )
        assert req.provider_id == ""
        assert req.model_id == "gpt-5"

    def test_full_request(self):
        req = ChatRequest(
            model="openai/gpt-5",
            messages=[Message(role="user", content="Hi")],
            stream=True,
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            stop=["END"],
            seed=42,
            response_format={"type": "json_object"},
            timeout=30.0,
            retries=3,
            extra_headers={"X-Custom": "value"},
            provider_options={"logprobs": True},
        )
        assert req.stream is True
        assert req.response_format == {"type": "json_object"}
        assert req.max_tokens == 100
        assert req.seed == 42

    def test_api_key_excluded_from_serialization(self):
        req = ChatRequest(
            model="openai/gpt-5",
            messages=[Message(role="user", content="Hi")],
            api_key="sk-secret",
        )
        data = req.model_dump()
        assert "api_key" not in data


# ---------------------------------------------------------------------------
# ChatResponse
# ---------------------------------------------------------------------------


class TestChatResponse:
    def _make_response(self, content: str = "Hello!", finish_reason: str = "stop"):
        return ChatResponse(
            id="resp_1",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=content),
                    finish_reason=finish_reason,
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-5",
            provider="openai",
            created=1700000000,
        )

    def test_basic_response(self):
        resp = self._make_response()
        assert resp.id == "resp_1"
        assert resp.provider == "openai"

    def test_content_shortcut(self):
        resp = self._make_response("World!")
        assert resp.content == "World!"

    def test_finish_reason_shortcut(self):
        resp = self._make_response(finish_reason="length")
        assert resp.finish_reason == "length"

    def test_tool_calls_shortcut(self):
        tc = ToolCall(
            id="call_1",
            function=FunctionCall(name="fn", arguments="{}"),
        )
        resp = ChatResponse(
            id="resp_2",
            choices=[
                Choice(
                    message=Message(role="assistant", tool_calls=[tc]),
                    finish_reason="tool_calls",
                )
            ],
            model="gpt-5",
            provider="openai",
        )
        assert resp.tool_calls is not None
        assert resp.tool_calls[0].function.name == "fn"

    def test_empty_choices(self):
        resp = ChatResponse(id="resp_3", choices=[], model="gpt-5", provider="openai")
        assert resp.content is None
        assert resp.tool_calls is None
        assert resp.finish_reason is None


# ---------------------------------------------------------------------------
# StreamChunk
# ---------------------------------------------------------------------------


class TestStreamChunk:
    def test_content_chunk(self):
        chunk = StreamChunk(
            id="chunk_1",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(content="Hello"),
                    finish_reason=None,
                )
            ],
            provider="openai",
        )
        assert chunk.choices[0].delta.content == "Hello"

    def test_empty_chunk(self):
        chunk = StreamChunk()
        assert chunk.choices is None
        assert chunk.usage is None


# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------


class TestUsage:
    def test_defaults(self):
        usage = Usage()
        assert usage.prompt_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.total_tokens == 150


# ---------------------------------------------------------------------------
# ProviderInfo & ModelInfo
# ---------------------------------------------------------------------------


class TestProviderInfo:
    def test_construction(self):
        info = ProviderInfo(
            id="openai",
            name="OpenAI",
            protocol="openai",
            base_url="https://api.openai.com/v1",
            env_var="OPENAI_API_KEY",
        )
        assert info.id == "openai"
        assert info.requires_api_key is True
        assert info.supports_byok is True


class TestModelInfo:
    def test_minimal(self):
        info = ModelInfo(id="gpt-5")
        assert info.id == "gpt-5"
        assert info.type == "chat"
        assert info.supports_streaming is True
        assert info.supports_tool_calling is False

    def test_full(self):
        info = ModelInfo(
            id="gpt-5",
            display_name="GPT-5",
            context_window=128000,
            max_tokens=16384,
            supports_tool_calling=True,
            supports_structured_output=True,
            supports_json_mode=True,
            supports_seed=True,
            default_temperature=1.0,
        )
        assert info.context_window == 128000
        assert info.supports_tool_calling is True
        assert info.default_temperature == 1.0
