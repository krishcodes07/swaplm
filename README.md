<div align="center">

<table align="center">
<tr><td align="center">

```
                                                                  
 ▄▄▄▄▄▄▄ ▄▄▄▄  ▄▄▄  ▄▄▄▄   ▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄      ▄▄▄      ▄▄▄ 
█████▀▀▀ ▀███  ███  ███▀ ▄██▀▀██▄ ███▀▀███▄ ███      ████▄  ▄████ 
 ▀████▄   ███  ███  ███  ███  ███ ███▄▄███▀ ███      ███▀████▀███ 
   ▀████  ███▄▄███▄▄███  ███▀▀███ ███▀▀▀▀   ███      ███  ▀▀  ███ 
███████▀   ▀████▀████▀   ███  ███ ███       ████████ ███      ███ 
                                                                                                                              
```

</td></tr>
</table>

<p align="center"><b>The universal Python SDK for every LLM provider.</b></p>
<p align="center"><b>One interface. 16 providers. Zero vendor lock-in.</b></p>

<p align="center">
  <a href="https://pypi.org/project/swaplm"><img alt="PyPI" src="https://img.shields.io/pypi/v/swaplm?style=for-the-badge&label=PyPI&color=blue" /></a>
  <a href="https://pypi.org/project/swaplm"><img alt="Downloads" src="https://img.shields.io/pypi/dm/swaplm?style=for-the-badge&color=green" /></a>
  <a href="https://pypi.org/project/swaplm"><img alt="Python" src="https://img.shields.io/pypi/pyversions/swaplm?style=for-the-badge" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" /></a>
  <a href="https://github.com/krishcodes07/swaplm/actions"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/krishcodes07/swaplm/ci.yml?style=for-the-badge&label=CI" /></a>
</p>

</div>

---

## Why SwapLM?

Most LLM applications are tightly coupled to a single provider. Switching from Groq to OpenAI to Anthropic means rewriting your API calls, error handling, streaming logic, and auth management. **SwapLM eliminates that lock-in.**

Write your code once. Swap providers by changing a single string.

```python
from swaplm import chat

# Groq
response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)

# OpenAI — same interface, different provider
response = chat(
    provider="openai",
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Anthropic — still the same interface
response = chat(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

---

## Features

- **🔌 16 Production Providers** — Groq, Anthropic, Google Gemini, OpenAI, OpenRouter, GitHub Models, NVIDIA NIM, Cerebras, SambaNova, Mistral, xAI, DeepInfra, Fireworks, Cloudflare, Perplexity, Cohere.
- **⚡ Sync & Async** — `chat()` for synchronous code, `achat()` for `async/await` workflows.
- **📡 Streaming** — Real-time token-by-token responses with `stream=True`. Works sync and async.
- **🛠️ Tool / Function Calling** — Define tools with JSON schemas. SwapLM handles provider-specific translation automatically.
- **🔄 Retries with Exponential Backoff** — Built-in retry on 5xx, 429 rate limits, and timeouts. Configurable per-request or globally.
- **🧩 Middleware Pipeline** — Intercept and modify requests/responses with `BaseMiddleware`. Supports both sync and async.
- **🪝 Lifecycle Hooks** — Listen for `before_request`, `after_request`, `before_retry`, `on_error` events.
- **🔌 Custom Transport** — Replace the HTTP layer entirely with `BaseTransport` for proxies, caching, mocks, or enterprise security.
- **🔍 Provider & Model Discovery** — Query available providers and their models programmatically.
- **🧠 Model Capability Awareness** — SDK automatically omits unsupported parameters (e.g., `seed`, `tool_choice`) based on model metadata.
- **🔒 Secure Debug Logging** — `configure(debug=True)` redacts API keys and authorization headers.
- **📦 Zero Heavy Dependencies** — Only `pydantic>=2.11` and `httpx>=0.27.0`.

---

## Installation

```bash
pip install swaplm
```

Requires **Python 3.10+**.

---

## Quick Start

### 1. Set Your API Key

```bash
export GROQ_API_KEY=gsk_...    # or any provider's env var
```

### 2. Make Your First Call

```python
from swaplm import chat

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the meaning of life?"},
    ],
    temperature=0.7,
    max_tokens=256,
)

print(response.content)
# => "The meaning of life is a philosophical question..."
```

### 3. Async Version

```python
import asyncio
from swaplm import achat

async def main():
    response = await achat(
        provider="groq",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.content)

asyncio.run(main())
```

---

## API Reference

### `chat()` / `achat()` Parameters

Both functions accept the same parameters (keyword-only). `achat()` is the async equivalent.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `str` | **required** | Model identifier. When `provider` is set, this is the raw model ID. Otherwise `"provider/model"` format (e.g., `"groq/llama-3.3-70b-versatile"`). |
| `messages` | `list[dict \| Message]` | **required** | Conversation history. Each dict needs `"role"` and `"content"`. |
| `provider` | `str \| None` | `None` | Explicit provider slug (e.g., `"groq"`). When set, bypasses model-string parsing. |
| `stream` | `bool` | `False` | If `True`, returns a `StreamResponse` that yields `StreamChunk` objects. |
| `api_key` | `str \| None` | `None` | Explicit API key. Overrides the provider's environment variable. |
| `base_url` | `str \| None` | `None` | Override the provider's default API base URL. |
| `max_tokens` | `int \| None` | `None` | Maximum tokens to generate in the response. |
| `temperature` | `float \| None` | `None` | Sampling temperature (0.0–2.0). Higher = more random. |
| `top_p` | `float \| None` | `None` | Nucleus sampling threshold (0.0–1.0). |
| `response_format` | `dict \| None` | `None` | Structured output format. Use `{"type": "json_object"}` for JSON mode. |
| `tools` | `list[Tool \| dict] \| None` | `None` | List of tools the model can call. |
| `tool_choice` | `str \| dict \| None` | `None` | Controls tool usage: `"auto"`, `"none"`, `"required"`, or a specific tool dict. |
| `stop` | `str \| list[str] \| None` | `None` | Stop sequence(s) that halt generation. |
| `seed` | `int \| None` | `None` | Seed for reproducible outputs (provider-dependent). |
| `timeout` | `float \| None` | `None` | Request timeout in seconds. Falls back to `configure()` default. |
| `retries` | `int` | `0` | Number of retries on transient failures (5xx, 429, timeouts). |
| `extra_headers` | `dict[str, str] \| None` | `None` | Additional HTTP headers merged into the request. |
| `provider_options` | `dict[str, Any] \| None` | `None` | Provider-specific options passed through verbatim (escape hatch). |

### Model String Format

**Recommended** — explicit provider:

```python
chat(provider="groq", model="llama-3.3-70b-versatile")
```

**Still supported** — combined model string:

```python
chat(model="groq/llama-3.3-70b-versatile")
```

| Format | Example | Description |
|---|---|---|
| Explicit provider | `provider="groq", model="llama-3.3-70b-versatile"` | Bypasses model-string parsing. Recommended. |
| Combined string | `"groq/llama-3.3-70b-versatile"` | Routes directly to the named provider. |
| Nested model ID | `provider="nvidia", model="deepseek-ai/deepseek-v4-flash"` | Handles model IDs with slashes cleanly. |
| Alias | `"llama-3.3-70b-versatile"` | Searches all providers. Raises `AmbiguousModelError` if multiple match. |
| Free tier | `"free/qwen-2.5-72b"` | Searches providers marked as free or requiring no API key. |

---

## Return Types

### `ChatResponse`

Returned by `chat()` / `achat()` when `stream=False`.

```python
from swaplm import chat

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hi"}],
)

# Convenience shortcuts
response.content          # str | None — text of first choice
response.tool_calls       # list[ToolCall] | None — tool calls from first choice
response.finish_reason    # str | None — "stop", "length", "tool_calls", etc.
response.reasoning        # str | None — reasoning/thinking content (if present)

# Full fields
response.id               # str — unique response ID
response.model            # str — model that generated the response
response.provider         # str — provider slug (e.g., "groq")
response.choices          # list[Choice] — all choices
response.usage            # Usage | None — token counts
response.usage.prompt_tokens     # int
response.usage.completion_tokens # int
response.usage.total_tokens      # int
response.created          # int | None — Unix timestamp
```

### `StreamResponse`

Returned by `chat()` / `achat()` when `stream=True`.

```python
from swaplm import chat

stream = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a poem."}],
    stream=True,
)

# Sync iteration — use convenience properties
for chunk in stream:
    print(chunk.content, end="", flush=True)

# Access full text after iteration
print(stream.text)              # alias for accumulated_content
print(stream.accumulated_content)  # same thing
```

```python
# Async iteration
async for chunk in stream:
    print(chunk.content, end="", flush=True)
```

### `StreamChunk`

Each yielded chunk during streaming. Provides convenience properties that proxy the first choice:

| Property | Type | Description |
|---|---|---|
| `content` | `str` | Incremental text content (empty string if none) |
| `reasoning` | `str` | Incremental reasoning/thinking content (empty string if none) |
| `tool_calls` | `list[ToolCallDelta] \| None` | Incremental tool call data |
| `finish_reason` | `str \| None` | `"stop"`, `"length"`, `"tool_calls"`, etc. |

Full access to underlying structure is still available:

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Response ID |
| `choices` | `list[ChunkChoice] \| None` | Choice deltas |
| `usage` | `Usage \| None` | Token usage (if provided by provider) |
| `model` | `str \| None` | Model identifier |
| `provider` | `str \| None` | Provider slug |

### `ChunkChoice`

| Field | Type | Description |
|---|---|---|
| `index` | `int` | Choice index |
| `delta` | `ChoiceDelta` | Incremental content |
| `finish_reason` | `str \| None` | `"stop"`, `"length"`, `"tool_calls"`, etc. |

### `ChoiceDelta`

| Field | Type | Description |
|---|---|---|
| `role` | `str \| None` | Message role (usually `"assistant"`) |
| `content` | `str \| None` | Incremental text content |
| `tool_calls` | `list[ToolCallDelta] \| None` | Incremental tool call data |

---

## Supported Providers

| Provider | Slug | Protocol | Env Variable | Free Tier | Streaming | Tools | Reasoning |
|---|---|---|---|:---:|:---:|:---:|:---:|
| **Groq** | `groq` | OpenAI | `GROQ_API_KEY` | ✅ | ✅ | ✅ | ✅ |
| **OpenAI** | `openai` | OpenAI | `OPENAI_API_KEY` | ❌ | ✅ | ✅ | ✅ |
| **Anthropic** | `anthropic` | Anthropic | `ANTHROPIC_API_KEY` | ❌ | ✅ | ✅ | ✅ |
| **Google Gemini** | `google` | Google | `GEMINI_API_KEY` | ✅ | ✅ | ✅ | ✅ |
| **OpenRouter** | `openrouter` | OpenAI | `OPENROUTER_API_KEY` | ✅ | ✅ | ✅ | ✅ |
| **GitHub Models** | `github` | OpenAI | `GITHUB_TOKEN` | ✅ | ✅ | ✅ | ✅ |
| **NVIDIA NIM** | `nvidia` | OpenAI | `NVIDIA_API_KEY` | ✅ | ✅ | ✅ | ✅ |
| **Cerebras** | `cerebras` | OpenAI | `CEREBRAS_API_KEY` | ✅ | ✅ | ✅ | ❌ |
| **SambaNova** | `sambanova` | OpenAI | `SAMBANOVA_API_KEY` | ✅ | ✅ | ✅ | ✅ |
| **Mistral AI** | `mistral` | OpenAI | `MISTRAL_API_KEY` | ✅ | ✅ | ✅ | ❌ |
| **xAI** | `xai` | OpenAI | `XAI_API_KEY` | ❌ | ✅ | ✅ | ❌ |
| **DeepInfra** | `deepinfra` | OpenAI | `DEEPINFRA_API_KEY` | ❌ | ✅ | ✅ | ✅ |
| **Fireworks AI** | `fireworks` | OpenAI | `FIREWORKS_API_KEY` | ❌ | ✅ | ✅ | ✅ |
| **Cloudflare** | `cloudflare` | OpenAI | `CLOUDFLARE_API_KEY` | ✅ | ✅ | ✅ | ❌ |
| **Perplexity** | `perplexity` | OpenAI | `PERPLEXITY_API_KEY` | ❌ | ✅ | ❌ | ✅ |
| **Cohere** | `cohere` | OpenAI | `COHERE_API_KEY` | ✅ | ✅ | ✅ | ❌ |

> **OpenAI-compatible providers** share the same protocol. Any provider using the `/v1/chat/completions` endpoint works automatically.

---

## Tool / Function Calling

Define tools with JSON Schema parameters. SwapLM translates them to each provider's native format.

```python
from swaplm import Tool, chat

tools = [
    Tool(
        function={
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    )
]

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto",
)

if response.tool_calls:
    for tc in response.tool_calls:
        print(f"Calling: {tc.function.name}")
        print(f"Args: {tc.function.arguments}")
```

---

## Streaming

### Sync Streaming

```python
from swaplm import chat

stream = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    print(chunk.content, end="", flush=True)

# Full text available after iteration
print("\n\nFull:", stream.text)
```

### Async Streaming

```python
import asyncio
from swaplm import achat

async def main():
    stream = await achat(
        provider="groq",
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True,
    )

    async for chunk in stream:
        print(chunk.content, end="", flush=True)

asyncio.run(main())
```

---

## Configuration

Set global defaults that apply to all requests:

```python
from swaplm import configure, get_config, reset_config

configure(
    timeout=30.0,         # Request timeout in seconds
    retries=3,            # Retry on 5xx/429/timeout
    retry_delay=0.5,      # Initial retry delay (exponential backoff)
    max_tokens=1024,      # Default max tokens for all requests
    temperature=0.7,      # Default temperature
    top_p=0.9,            # Default top_p
    debug=True,           # Enable debug logging (redacts secrets)
    logging=True,         # Enable info-level logging
)

# Read current config
cfg = get_config()
print(cfg.timeout, cfg.retries)

# Reset to defaults
reset_config()
```

| Config Field | Type | Default | Description |
|---|---|---|---|
| `timeout` | `float \| None` | `None` | Global request timeout in seconds. |
| `retries` | `int` | `0` | Global retry count for transient failures. |
| `retry_delay` | `float` | `0.5` | Initial delay between retries (doubles each attempt). |
| `max_tokens` | `int \| None` | `None` | Default max tokens if not specified per-request. |
| `temperature` | `float \| None` | `None` | Default temperature if not specified per-request. |
| `top_p` | `float \| None` | `None` | Default top_p if not specified per-request. |
| `debug` | `bool` | `False` | Enable debug logging with secret redaction. |
| `logging` | `bool` | `False` | Enable info-level request logging. |
| `transport` | `BaseTransport \| None` | `None` | Custom transport implementation (see below). |

---

## Custom Transport

Replace the HTTP layer for proxies, caching, mocks, or enterprise security:

```python
from collections.abc import AsyncIterator, Iterator
from typing import Any

from swaplm import BaseTransport, chat, configure, reset_config


class MyTransport(BaseTransport):
    def send(self, method, url, *, headers=None, json=None, timeout=None, retries=0):
        print(f" intercepted: {url}")
        return 200, {"choices": [{"message": {"role": "assistant", "content": "Intercepted!"}}]}

    async def asend(self, method, url, *, headers=None, json=None, timeout=None, retries=0):
        return self.send(method, url, headers=headers, json=json, timeout=timeout, retries=retries)

    def send_stream(self, method, url, *, headers=None, json=None, timeout=None):
        yield {"choices": [{"delta": {"content": "Stream intercepted"}}]}

    async def asend_stream(self, method, url, *, headers=None, json=None, timeout=None):
        yield {"choices": [{"delta": {"content": "Async stream intercepted"}}]}


configure(transport=MyTransport())

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.content)  # => "Intercepted!"

reset_config()
```

### `BaseTransport` Interface

```python
class BaseTransport(ABC):
    def send(self, method, url, *, headers, json, timeout, retries) -> tuple[int, dict]: ...
    async def asend(self, method, url, *, headers, json, timeout, retries) -> tuple[int, dict]: ...
    def send_stream(self, method, url, *, headers, json, timeout) -> Iterator[dict]: ...
    async def asend_stream(self, method, url, *, headers, json, timeout) -> AsyncIterator[dict]: ...
    def close(self) -> None: ...
    async def aclose(self) -> None: ...
```

---

## Middleware

Intercept and transform requests and responses in a pipeline:

```python
from swaplm import BaseMiddleware, ChatRequest, ChatResponse, add_middleware, chat, reset_middlewares


class LoggingMiddleware(BaseMiddleware):
    def process_request(self, request: ChatRequest) -> ChatRequest:
        print(f"[REQ] {request.model} | {len(request.messages)} messages")
        return request

    def process_response(self, response: ChatResponse) -> ChatResponse:
        print(f"[RES] {response.provider} | {response.usage.total_tokens} tokens")
        return response


add_middleware(LoggingMiddleware())

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)
# Prints:
# [REQ] groq/llama-3.3-70b-versatile | 1 messages
# [RES] groq | 42 tokens

reset_middlewares()
```

### `BaseMiddleware` Methods

| Method | Description |
|---|---|
| `process_request(request)` | Modify request before execution (sync). |
| `aprocess_request(request)` | Modify request before execution (async). |
| `process_response(response)` | Modify response after execution (sync). |
| `aprocess_response(response)` | Modify response after execution (async). |
| `process_error(error)` | Intercept exceptions (sync). |
| `aprocess_error(error)` | Intercept exceptions (async). |

### Pipeline Management

```python
from swaplm import add_middleware, remove_middleware, get_middlewares, reset_middlewares

add_middleware(my_middleware)      # Register
remove_middleware(my_middleware)   # Unregister
get_middlewares()                  # List all registered
reset_middlewares()                # Clear all
```

---

## Lifecycle Hooks

Subscribe to SDK events for logging, metrics, or custom behavior:

```python
from swaplm import ChatRequest, ChatResponse, chat, on, off, reset_hooks


def log_request(request: ChatRequest):
    print(f"Sending to {request.model}")


def log_response(response: ChatResponse, request: ChatRequest):
    print(f"Got {response.usage.total_tokens} tokens from {response.provider}")


on("before_request", log_request)
on("after_request", log_response)

response = chat(
    provider="groq",
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hi"}],
)

off("before_request", log_request)  # Unregister
reset_hooks()                        # Clear all
```

### Available Events

| Event | Callback Signature | When |
|---|---|---|
| `before_request` | `(request: ChatRequest)` | Before the HTTP request is sent. |
| `after_request` | `(response: ChatResponse, request: ChatRequest)` | After a successful response. |
| `before_retry` | `(url, status_or_exc, attempt)` | Before a retry attempt. |
| `after_retry` | `(url, status_or_exc, attempt)` | After a retry attempt. |
| `before_stream` | `(request: ChatRequest)` | Before streaming begins. |
| `after_stream` | `(request: ChatRequest)` | After streaming ends. |
| `on_error` | `(request: ChatRequest, error: SwapLMError)` | When an error occurs. |

---

## Provider & Model Discovery

Query available providers and models programmatically:

```python
import swaplm

# List all providers
for p in swaplm.providers():
    print(f"{p.id}: {p.name} ({p.protocol})")

# Get a specific provider
groq = swaplm.provider("groq")
print(groq.base_url)  # => "https://api.groq.com/openai/v1"

# List all models across all providers
all_models = swaplm.models()
for provider_info, model_info in all_models:
    print(f"{provider_info.id}/{model_info.id}")

# Get a specific model's metadata
provider_info, model_info = swaplm.model("groq/llama-3.3-70b-versatile")
print(model_info.context_window)       # => 128000
print(model_info.supports_tool_calling) # => True
```

---

## Error Handling

SwapLM maps all provider-specific errors into a unified exception hierarchy:

```python
from swaplm import chat
from swaplm.exceptions import (
    SwapLMError,           # Base — catch everything
    ProviderError,         # Generic provider error
    AuthenticationError,   # 401 / invalid API key
    RateLimitError,        # 429 / rate limited
    TimeoutError,          # Request timed out
    InvalidModelError,     # Model not found (404)
    AmbiguousModelError,   # Alias matches multiple providers
    InvalidProviderError,  # Unknown provider slug
    ConfigurationError,    # SDK configuration issue
    ModelCapabilityError,  # Unsupported operation for model
    ToolCallError,         # Tool/function calling error
)

try:
    response = chat(
        provider="groq",
        model="nonexistent-model",
        messages=[{"role": "user", "content": "Hi"}],
        api_key="invalid",
    )
except AuthenticationError as e:
    print(f"Auth failed: {e}")
    print(f"Provider: {e.provider}")
    print(f"Status: {e.status_code}")
except InvalidModelError as e:
    print(f"Model not found: {e.model}")
except SwapLMError as e:
    print(f"SDK error: {e}")
```

---

## Tool Types Reference

### `Message`

```python
from swaplm import Message

msg = Message(
    role="user",                   # "system" | "user" | "assistant" | "tool"
    content="Hello!",              # str | list[dict] | None
    name="optional_name",         # str | None
    tool_calls=[...],             # list[ToolCall] | None
    tool_call_id="call_abc",      # str | None (for role="tool")
)
```

### `Tool`

```python
from swaplm import Tool

tool = Tool(
    function={
        "name": "my_function",
        "description": "Does something useful",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    }
)
```

### `ChatRequest`

```python
from swaplm import ChatRequest, Message

request = ChatRequest(
    model="llama-3.3-70b-versatile",
    messages=[Message(role="user", content="Hi")],
    provider="groq",                   # explicit provider (recommended)
    stream=False,
    max_tokens=1024,
    temperature=0.7,
    top_p=0.9,
    stop=["\n\n"],
    seed=42,
    response_format={"type": "json_object"},
    tools=[...],
    tool_choice="auto",
    api_key="optional-explicit-key",
    base_url="https://custom-endpoint.com/v1",
    timeout=30.0,
    retries=3,
    extra_headers={"X-Custom": "value"},
    provider_options={"thinking": {"type": "enabled"}},
)

# Computed properties
request.provider_id  # => "groq"
request.model_id     # => "llama-3.3-70b-versatile"
```

### `ModelInfo`

```python
from swaplm import model

provider_info, model_info = swaplm.model("groq/llama-3.3-70b-versatile")

model_info.id                      # => "llama-3.3-70b-versatile"
model_info.display_name            # => "LLaMA 3.3 70B"
model_info.context_window          # => 128000
model_info.max_tokens              # => 32768
model_info.supports_streaming      # => True
model_info.supports_tool_calling   # => True
model_info.supports_json_mode      # => True
model_info.supports_thinking       # => True
model_info.supports_seed           # => False
model_info.supports_vision         # => False
model_info.default_temperature     # => None
model_info.default_max_tokens      # => None
```

---

## Architecture

```
chat() / achat()
    │
    ├─ Middleware Pipeline (request)
    │
    ├─ Router ─────────── Resolves "provider/model" string
    │     │
    │     ├─ ProviderRegistry ── Auto-discovers providers
    │     └─ Provider ────────── Metadata + models.json
    │
    ├─ AuthManager ────── Resolves API key (explicit → env var)
    │
    ├─ Protocol ───────── Translates to provider-native format
    │     │
    │     ├─ OpenAIProtocol ─── OpenAI, Groq, NVIDIA, etc.
    │     ├─ AnthropicProtocol  Anthropic Claude
    │     └─ GoogleProtocol ─── Google Gemini
    │
    ├─ Transport ──────── Executes HTTP (httpx / custom)
    │
    ├─ Protocol ───────── Parses response back to unified format
    │
    ├─ Middleware Pipeline (response)
    │
    └─ ChatResponse / StreamResponse
```

---

## Examples

| Example | Description |
|---|---|
| [`01_basic_chat.py`](examples/01_basic_chat.py) | Synchronous chat with Groq |
| [`02_async_chat.py`](examples/02_async_chat.py) | Async chat with `achat()` |
| [`03_streaming.py`](examples/03_streaming.py) | Real-time token streaming |
| [`04_tool_calling.py`](examples/04_tool_calling.py) | Function / tool calling |
| [`05_structured_output.py`](examples/05_structured_output.py) | JSON structured output |
| [`06_multi_provider.py`](examples/06_multi_provider.py) | Switching between providers |
| [`07_middleware.py`](examples/07_middleware.py) | Request/response middleware |
| [`08_hooks.py`](examples/08_hooks.py) | Lifecycle event hooks |
| [`09_custom_transport.py`](examples/09_custom_transport.py) | Custom transport injection |
| [`10_discovery.py`](examples/10_discovery.py) | Provider & model discovery |

---

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ |
| **2** | Provider architecture & protocol system | ✅ |
| **3** | First production provider (Groq) & HTTP execution | ✅ |
| **4** | Core SDK infrastructure (routing, discovery, config) | ✅ |
| **5** | Multi-protocol validation (Anthropic & Google Gemini) | ✅ |
| **6** | SDK runtime & developer experience (async, retries, middleware, hooks) | ✅ |
| **7** | OpenAI-compatible provider expansion (16 providers) | ✅ |
| **8** | Enterprise resilience (fallbacks, circuit breakers) | 🔜 |
| **9** | Documentation site & v1.0 release | Planned |

---

## Contributing

```bash
git clone https://github.com/krishcodes07/swaplm.git
cd swaplm
pip install -e ".[dev]"

# Lint & format
ruff check .
ruff format .

# Run tests
pytest
```

---

## License

SwapLM is released under the [MIT License](LICENSE).
