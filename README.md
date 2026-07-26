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

## Features

- [x] Project foundation and repository structure
- [x] Provider architecture and protocol system
- [x] Groq production provider integration
- [x] HTTP execution engine (`httpx`)
- [x] Server-Sent Events (SSE) streaming support
- [x] Model capability registry & automatic parameter omission
- [x] Advanced router: model aliases, ambiguity detection, `free/` provider routing
- [x] Public provider & model discovery APIs (`providers()`, `models()`, `provider()`, `model()`)
- [x] Global configuration system (`configure()`)
- [x] Automatic API key management
- [x] Tool / Function calling support
- [x] Unified exception hierarchy
- [ ] Additional providers (OpenAI, Anthropic, Google, etc.)
- [ ] Async client support (`achat`)
- [ ] Provider fallback and retry logic

---

## Usage Guide

### Global Configuration

Set SDK-wide default options across all `chat()` calls:

```python
from swaplm import configure

configure(
    timeout=45.0,
    retries=3,
    max_tokens=4096,
    temperature=0.7,
)
```

### Advanced Model Routing

#### 1. Explicit Model String (`provider/model`)

```python
response = chat(model="groq/llama-3.3-70b-versatile", messages=[...])
```

#### 2. Alias Resolution

If a model alias uniquely exists in a registered provider, specify the alias directly:

```python
response = chat(model="llama-3.3-70b-versatile", messages=[...])
```

*If multiple providers contain the same model alias, SwapLM raises an `AmbiguousModelError` asking for an explicit `provider/model` string.*

#### 3. Virtual Free Provider (`free/model`)

Route automatically to free-tier or open-access providers:

```python
response = chat(model="free/qwen3-30b", messages=[...])
```

---

## Public Discovery APIs

Inspect registered providers and model capabilities without making network requests:

```python
import swaplm

# List all registered providers
for p in swaplm.providers():
    print(f"Provider: {p.name} ({p.id}) - Base URL: {p.base_url}")

# Inspect a single provider
groq_info = swaplm.provider("groq")
print("Supports BYOK:", groq_info.supports_byok)

# Inspect a model's capabilities
p_info, m_info = swaplm.model("groq/llama-3.3-70b-versatile")
print(f"Context Window: {m_info.context_window}")
print(f"Supports Tools: {m_info.supports_tool_calling}")

# Search all models across providers
for p_info, m_info in swaplm.models():
    print(f"{p_info.id}/{m_info.id} - Max Tokens: {m_info.max_tokens}")
```

---

## Examples

### Basic Completion

```python
from swaplm import chat

response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)

print(response.content)
```

### Streaming

```python
from swaplm import chat

stream = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a poem about open source."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Tool Calling

```python
from swaplm import Tool, chat

weather_tool = Tool.model_validate({
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
})

response = chat(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Weather in Tokyo?"}],
    tools=[weather_tool],
)

if response.tool_calls:
    print("Tool requested:", response.tool_calls[0].function.name)
```

---

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ Completed |
| **2** | Provider architecture & protocol system | ✅ Completed |
| **3** | First production provider (Groq) & HTTP execution | ✅ Completed |
| **4** | Core SDK Infrastructure (Routing, Discovery, Config) | ✅ Current |
| **5** | Additional core providers (OpenAI, Anthropic, Google) | 🔜 Next |
| **6** | Async support & streaming enhancements | Planned |
| **7** | Advanced features (fallbacks, retries) | Planned |
| **8** | Documentation site & v1.0 release | Planned |

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
