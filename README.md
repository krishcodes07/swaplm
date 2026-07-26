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
response = chat(model="groq/llama-3.3-70b-versatile", messages=[{"role": "user", "content": "Hello!"}])

# Anthropic
response = chat(model="anthropic/claude-3-5-sonnet-20241022", messages=[{"role": "user", "content": "Hello!"}])

# Google Gemini
response = chat(model="google/gemini-2.5-pro", messages=[{"role": "user", "content": "Hello!"}])
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

- [x] Project foundation and repository structure
- [x] Provider architecture and protocol system
- [x] Production provider integrations (Groq, Anthropic, Google Gemini)
- [x] HTTP execution engine (`httpx`)
- [x] Server-Sent Events (SSE) streaming support across all protocols
- [x] Model capability registry & automatic parameter omission
- [x] Advanced router: explicit model strings, aliases, `free/` virtual provider
- [x] Public provider & model discovery APIs (`providers()`, `models()`, `provider()`, `model()`)
- [x] Global configuration system (`configure()`)
- [x] Automatic API key management
- [x] Tool / Function calling support
- [x] Unified exception hierarchy
- [ ] OpenAI provider integration
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

### Model Routing

#### 1. Explicit Provider & Model

```python
response = chat(model="groq/llama-3.3-70b-versatile", messages=[...])
response = chat(model="anthropic/claude-3-5-sonnet-20241022", messages=[...])
response = chat(model="google/gemini-2.5-pro", messages=[...])
```

#### 2. Alias Resolution

```python
response = chat(model="claude-3-5-sonnet-20241022", messages=[...])
response = chat(model="gemini-2.5-pro", messages=[...])
```

#### 3. Virtual Free Provider (`free/model`)

```python
response = chat(model="free/qwen3-30b", messages=[...])
```

---

## Code Examples

### Multi-Provider Completion

```python
from swaplm import chat

# Anthropic
res_claude = chat(
    model="anthropic/claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Explain relativity in one sentence."}],
)
print("Claude:", res_claude.content)

# Google Gemini
res_gemini = chat(
    model="google/gemini-2.5-pro",
    messages=[{"role": "user", "content": "Explain relativity in one sentence."}],
)
print("Gemini:", res_gemini.content)
```

### Streaming Across Providers

```python
from swaplm import chat

stream = chat(
    model="anthropic/claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Write a short poem."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\nFull text:\n", stream.accumulated_content)
```

### Tool Calling Across Providers

```python
from swaplm import Tool, chat

calculator_tool = Tool.model_validate({
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "Multiply two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    },
})

# Works identically on Gemini, Claude, or Groq
response = chat(
    model="google/gemini-2.5-pro",
    messages=[{"role": "user", "content": "Calculate 42 * 12"}],
    tools=[calculator_tool],
)

if response.tool_calls:
    tc = response.tool_calls[0]
    print(f"Tool call requested: {tc.function.name}({tc.function.arguments})")
```

---

## Public Discovery APIs

```python
import swaplm

# Inspect all providers
for p in swaplm.providers():
    print(f"{p.name} ({p.id}) - Base URL: {p.base_url}")

# Inspect model capabilities
p_info, m_info = swaplm.model("anthropic/claude-3-7-sonnet-20250219")
print("Supports thinking:", m_info.supports_thinking)
```

---

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ Completed |
| **2** | Provider architecture & protocol system | ✅ Completed |
| **3** | First production provider (Groq) & HTTP execution | ✅ Completed |
| **4** | Core SDK Infrastructure (Routing, Discovery, Config) | ✅ Completed |
| **5** | Multi-Protocol Validation (Anthropic & Google Gemini) | ✅ Current |
| **6** | OpenAI provider & remaining OpenAI-compatible providers | 🔜 Next |
| **7** | Async support & streaming enhancements | Planned |
| **8** | Advanced features (fallbacks, retries) | Planned |
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
