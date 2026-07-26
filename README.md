<p align="center">
  <h1 align="center">SwapLM</h1>
  <p align="center">
    <strong>One SDK. Every LLM.</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/swaplm"><img src="https://img.shields.io/pypi/v/swaplm?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/swaplm"><img src="https://img.shields.io/pypi/pyversions/swaplm" alt="Python"></a>
    <a href="https://github.com/krishcodes07/swaplm/blob/main/LICENSE"><img src="https://img.shields.io/github/license/krishcodes07/swaplm" alt="License"></a>
    <a href="https://github.com/krishcodes07/swaplm/actions"><img src="https://img.shields.io/github/actions/workflow/status/krishcodes07/swaplm/ci.yml?label=CI" alt="CI"></a>
  </p>
</p>

---

**SwapLM** is a modern, open-source Python SDK that provides a **unified interface** for interacting with Large Language Model providers.

Write your code once. Swap providers with a single line change.

```python
from swaplm import chat, achat

# Sync
response = chat(
    model="groq/llama-3.3-70b-versatile", messages=[{"role": "user", "content": "Hello!"}]
)

# Async
response = await achat(
    model="anthropic/claude-3-5-sonnet-20241022", messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## Supported Providers

| Provider | Status | Example Model | Default Env Var |
|---|---|---|---|
| **Groq** | ✅ Active | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| **Anthropic** | ✅ Active | `anthropic/claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| **Google Gemini** | ✅ Active | `google/gemini-2.5-pro` | `GEMINI_API_KEY` |

---

## Features

- [x] Complete Async API (`achat()`) & Async Streaming (`async for chunk in stream:`)
- [x] Configurable Transport Retries with Exponential Backoff (5xx, timeouts, 429 rate limits)
- [x] Interceptor Middleware Pipeline (`BaseMiddleware`, `add_middleware()`)
- [x] Lifecycle Hooks (`on("before_request")`, `on("after_request")`, `on("before_retry")`)
- [x] Structured Debug Mode & Token Redaction (`configure(debug=True)`)
- [x] Pluggable Custom Transport Injection (`BaseTransport`, `configure(transport=...)`)
- [x] HTTP Execution Engine (`httpx.Client` & `httpx.AsyncClient`)
- [x] Server-Sent Events (SSE) streaming support across all protocols
- [x] Model capability registry & automatic parameter omission
- [x] Advanced router: explicit model strings, aliases, `free/` virtual provider
- [x] Public provider & model discovery APIs (`providers()`, `models()`, `provider()`, `model()`)
- [x] Global configuration system (`configure()`)
- [x] Automatic API key management
- [x] Tool / Function calling support
- [x] Unified exception hierarchy

---

## Usage Guide

### Global Configuration & Debug Mode

Set SDK-wide default options across all `chat()` and `achat()` calls:

```python
from swaplm import configure

configure(
    timeout=45.0,
    retries=3,
    debug=True,  # Expose normalized request/response payloads with redacted credentials
)
```

### Async API (`achat`)

```python
import asyncio
from swaplm import achat


async def main():
    response = await achat(
        model="anthropic/claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": "Async Hello!"}],
    )
    print(response.content)


asyncio.run(main())
```

### Async Streaming

```python
stream = await achat(
    model="google/gemini-2.5-pro",
    messages=[{"role": "user", "content": "Write a short poem."}],
    stream=True,
)

async for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\nFull text:\n", stream.accumulated_content)
```

### Middleware Pipeline

Intercept and modify requests, responses, or exceptions:

```python
from swaplm import BaseMiddleware, add_middleware, ChatRequest, ChatResponse


class LoggingMiddleware(BaseMiddleware):
    def process_request(self, request: ChatRequest) -> ChatRequest:
        print(f"[Middleware] Outgoing request to {request.model}")
        return request

    def process_response(self, response: ChatResponse) -> ChatResponse:
        print(f"[Middleware] Incoming response from {response.provider}")
        return response


add_middleware(LoggingMiddleware())
```

### Lifecycle Hooks

Register lightweight event listeners:

```python
from swaplm import on


@on("before_request")
def handle_before_req(request):
    print(f"Sending request to {request.model}")


@on("before_retry")
def handle_retry(url, error_or_status, attempt):
    print(f"Retry attempt {attempt} for {url} due to {error_or_status}")
```

### Custom Transport Injection

Inject a custom transport for testing, caching, or enterprise proxies:

```python
from swaplm import BaseTransport, configure


class MyCustomTransport(BaseTransport):
    def send(self, method, url, **kwargs):
        # Custom proxying or mock response
        return 200, {"choices": [{"message": {"role": "assistant", "content": "Mocked!"}}]}

    async def asend(self, method, url, **kwargs):
        return 200, {"choices": [{"message": {"role": "assistant", "content": "Mocked!"}}]}


configure(transport=MyCustomTransport())
```

---

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ Completed |
| **2** | Provider architecture & protocol system | ✅ Completed |
| **3** | First production provider (Groq) & HTTP execution | ✅ Completed |
| **4** | Core SDK Infrastructure (Routing, Discovery, Config) | ✅ Completed |
| **5** | Multi-Protocol Validation (Anthropic & Google Gemini) | ✅ Completed |
| **6** | SDK Runtime & Developer Experience (Async, Retries, Middleware, Hooks) | ✅ Current |
| **7** | OpenAI provider & remaining OpenAI-compatible providers | 🔜 Next |
| **8** | Enterprise resilience (fallbacks, circuit breakers) | Planned |
| **9** | Documentation site & v1.0 release | Planned |

---

## Contributing

```bash
git clone https://github.com/krishcodes07/swaplm.git
cd swaplm
pip install -e ".[dev]"

ruff check .
ruff format .
pytest
```

## License

SwapLM is released under the [MIT License](LICENSE).
