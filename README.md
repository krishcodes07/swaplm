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
from swaplm import chat

# Groq
response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.content)
```

---

## Vision

LLM providers each ship their own SDK with different conventions, authentication flows, and response formats. Switching between providers — or supporting multiple — means rewriting integration code, handling edge cases per-vendor, and managing a growing dependency tree.

SwapLM eliminates this friction. A single, consistent API lets you target **any** provider while keeping your application code clean and portable.

## Supported Providers

| Provider | Status | Model Example | Default Env Var |
|---|---|---|---|
| **Groq** | ✅ Active | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |

---

## Features

- [x] Project foundation and repository structure
- [x] Provider architecture and protocol system
- [x] Groq production provider integration
- [x] HTTP execution engine (`httpx`)
- [x] Server-Sent Events (SSE) streaming support
- [x] Model capability registry
- [x] Automatic API key management
- [x] Tool / Function calling support
- [x] Unified exception hierarchy
- [ ] Additional providers (OpenAI, Anthropic, Google, etc.)
- [ ] Async client support (`achat`)
- [ ] Provider fallback and retry logic

---

## Quickstart

### Installation

```bash
pip install swaplm
```

### Authentication

Set the API key via environment variable:

```bash
export GROQ_API_KEY="gsk_..."
```

Or pass `api_key` explicitly:

```python
from swaplm import chat

response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Explain quantum computing in one sentence."}],
    api_key="gsk_...",
)
```

### Basic Chat Completion

```python
from swaplm import chat

response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.7,
    max_tokens=100,
)

print(response.content)
print(f"Tokens used: {response.usage.total_tokens}")
```

### Streaming Responses

```python
from swaplm import chat

stream = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a short poem about code."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Full accumulated content is also accessible:
print("\n\nFull Poem:\n", stream.accumulated_content)
```

### Tool / Function Calling

```python
from swaplm import Tool, chat

weather_tool = Tool.model_validate(
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "City name"}},
                "required": ["location"],
            },
        },
    }
)

response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=[weather_tool],
    tool_choice="auto",
)

if response.tool_calls:
    tool_call = response.tool_calls[0]
    print(f"Model requested tool: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
```

---

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ Completed |
| **2** | Provider architecture & protocol system | ✅ Completed |
| **3** | First production provider (Groq) & HTTP execution | ✅ Current |
| **4** | Additional core providers (OpenAI, Anthropic, Google) | 🔜 Next |
| **5** | Async support & streaming enhancements | Planned |
| **6** | Model registry & intelligent routing | Planned |
| **7** | Advanced features (fallbacks, retries) | Planned |
| **8** | Documentation site & v1.0 release | Planned |

---

## Architecture

```
┌──────────────────────────────────────────────┐
│              Public API (chat)               │
├──────────────────────────────────────────────┤
│                   Router                     │
│         Resolves model → provider            │
├──────────────────────────────────────────────┤
│                 Protocols                    │
│    OpenAI-compat · Anthropic · Google        │
├──────────────────────────────────────────────┤
│                 Providers                    │
│                Groq · ...                    │
├──────────────────────────────────────────────┤
│             HTTP Transport (httpx)           │
├──────────────────────────────────────────────┤
│              Auth · Models · Utils           │
└──────────────────────────────────────────────┘
```

---

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

```bash
# Clone and set up
git clone https://github.com/krishcodes07/swaplm.git
cd swaplm
pip install -e ".[dev]"

# Run checks
ruff check .
ruff format .
pytest
```

## License

SwapLM is released under the [MIT License](LICENSE).

---

<p align="center">
  Built with care by <a href="https://github.com/krishcodes07">Krish</a> and contributors.
</p>
