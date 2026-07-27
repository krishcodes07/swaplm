"""Tests for streaming tool call parsing across protocols."""

from swaplm.protocols.anthropic import AnthropicProtocol
from swaplm.protocols.openai import OpenAIProtocol


class TestStreamingToolCallsOpenAI:
    def setup_method(self):
        self.protocol = OpenAIProtocol()

    def test_openai_stream_chunk_tool_calls_start(self):
        raw_event = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": "",
                                },
                            }
                        ],
                    },
                    "finish_reason": None,
                }
            ],
        }

        chunk = self.protocol.parse_stream_chunk(raw_event, "openai")
        assert chunk is not None
        assert chunk.tool_calls is not None
        assert len(chunk.tool_calls) == 1

        tc = chunk.tool_calls[0]
        assert tc.id == "call_abc123"
        assert tc.function is not None
        assert tc.function.name == "get_weather"
        assert tc.function.arguments == ""

    def test_openai_stream_chunk_tool_calls_argument_delta(self):
        raw_event = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "function": {
                                    "arguments": '{"location": "Tokyo"}',
                                },
                            }
                        ]
                    },
                }
            ],
        }

        chunk = self.protocol.parse_stream_chunk(raw_event, "openai")
        assert chunk is not None
        assert chunk.tool_calls is not None
        tc = chunk.tool_calls[0]
        assert tc.function is not None
        assert tc.function.arguments == '{"location": "Tokyo"}'


class TestStreamingToolCallsAnthropic:
    def setup_method(self):
        self.protocol = AnthropicProtocol()

    def test_anthropic_content_block_start_tool_use(self):
        raw_event = {
            "type": "content_block_start",
            "index": 1,
            "content_block": {
                "type": "tool_use",
                "id": "toolu_01A09q906h5e1975fs35b11",
                "name": "get_weather",
                "input": {},
            },
        }

        chunk = self.protocol.parse_stream_chunk(raw_event, "anthropic")
        assert chunk is not None
        assert chunk.tool_calls is not None
        assert len(chunk.tool_calls) == 1

        tc = chunk.tool_calls[0]
        assert tc.id == "toolu_01A09q906h5e1975fs35b11"
        assert tc.function is not None
        assert tc.function.name == "get_weather"

    def test_anthropic_input_json_delta(self):
        raw_event = {
            "type": "content_block_delta",
            "index": 1,
            "delta": {
                "type": "input_json_delta",
                "partial_json": '{"location": "San Francisco"}',
            },
        }

        chunk = self.protocol.parse_stream_chunk(raw_event, "anthropic")
        assert chunk is not None
        assert chunk.tool_calls is not None
        tc = chunk.tool_calls[0]
        assert tc.function is not None
        assert tc.function.arguments == '{"location": "San Francisco"}'

    def test_anthropic_stop_reason_tool_use(self):
        raw_event = {
            "type": "message_delta",
            "delta": {"stop_reason": "tool_use", "stop_sequence": None},
            "usage": {"output_tokens": 25},
        }

        chunk = self.protocol.parse_stream_chunk(raw_event, "anthropic")
        assert chunk is not None
        assert chunk.finish_reason == "tool_calls"
