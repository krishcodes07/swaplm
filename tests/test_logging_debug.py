"""Unit tests for debug mode and sensitive token redaction."""

from swaplm.logging import redact_body, redact_headers


class TestLoggingDebug:
    def test_header_redaction(self):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": "secret_key_123",
            "Authorization": "Bearer token_456",
            "x-goog-api-key": "ai_key_789",
        }
        redacted = redact_headers(headers)
        assert redacted["Content-Type"] == "application/json"
        assert redacted["x-api-key"] == "***"
        assert redacted["Authorization"] == "***"
        assert redacted["x-goog-api-key"] == "***"

    def test_body_redaction(self):
        body = {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": "Secret text"}],
        }
        redacted_non_debug = redact_body(body, debug=False)
        assert redacted_non_debug["messages"] == "[1 message(s) redacted]"

        redacted_debug = redact_body(body, debug=True)
        assert redacted_debug["messages"] == [{"role": "user", "content": "Secret text"}]
