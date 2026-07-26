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

# OpenAI
response = chat(
    model="openai/gpt-5",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Google
response = chat(
    model="google/gemini-2.5-pro",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Free tier
response = chat(
    model="free/qwen3-30b",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

> **Status:** SwapLM is in early development. The public API is not yet available.

---

## Vision

LLM providers each ship their own SDK with different conventions, authentication flows, and response formats. Switching between providers — or supporting multiple — means rewriting integration code, handling edge cases per-vendor, and managing a growing dependency tree.

SwapLM eliminates this friction. A single, consistent API lets you target **any** provider while keeping your application code clean and portable.

## Goals

| Goal | Description |
|---|---|
| **Unified API** | One function call to reach any provider |
| **Excellent DX** | Intuitive, strongly-typed, minimal boilerplate |
| **Clean Architecture** | Modular internals that are easy to read and extend |
| **Strong Typing** | Full type annotations and Pydantic models throughout |
| **Minimal Dependencies** | Only what's essential — `httpx` and `pydantic` |
| **Extensible Providers** | Add new providers without touching core code |
| **Open Source Standards** | CI, changelogs, semver, contributor guides |

## Planned Features

- [x] Project foundation and repository structure
- [ ] Provider architecture and protocol system
- [ ] OpenAI-compatible provider
- [ ] Anthropic-compatible provider
- [ ] Google Gemini provider
- [ ] Unified chat completions API
- [ ] Streaming support (SSE)
- [ ] Async support
- [ ] Model registry and routing
- [ ] Automatic API key management
- [ ] Provider fallback and retry logic
- [ ] Free-tier provider support (OpenRouter, Cerebras, etc.)
- [ ] Tool / function calling
- [ ] Multi-modal support (images, audio)
- [ ] CLI for quick testing
- [ ] Comprehensive documentation site

## Installation

> **Note:** SwapLM is not yet published to PyPI. The instructions below will work once the first release is available.

```bash
pip install swaplm
```

For development:

```bash
git clone https://github.com/krishcodes07/swaplm.git
cd swaplm
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Quick Example

```python
from swaplm import chat

response = chat(
    model="openai/gpt-5",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in one sentence."},
    ],
)

print(response.content)
```

Swap the model string to switch providers — no other code changes required:

```python
response = chat(model="anthropic/claude-4-sonnet", messages=[...])
response = chat(model="google/gemini-2.5-pro", messages=[...])
response = chat(model="groq/llama-4-scout", messages=[...])
```

## Roadmap

| Phase | Milestone | Status |
|---|---|---|
| **1** | Project foundation & repository structure | ✅ Current |
| **2** | Provider architecture & protocol system | 🔜 Next |
| **3** | First providers (OpenAI, Anthropic, Google) | Planned |
| **4** | Streaming & async support | Planned |
| **5** | Model registry & intelligent routing | Planned |
| **6** | Advanced features (fallbacks, retries, tools) | Planned |
| **7** | Free-tier providers & community providers | Planned |
| **8** | Documentation site & v1.0 release | Planned |

## Architecture

SwapLM is built around a modular, layered architecture:

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
│  OpenAI · Anthropic · Gemini · Groq · ...   │
├──────────────────────────────────────────────┤
│              Auth · Models · Utils           │
│     API keys · Pydantic models · Helpers     │
└──────────────────────────────────────────────┘
```

**Key concepts:**

- **Providers** — Vendor-specific implementations (one per service).
- **Protocols** — Shared API patterns (e.g., many providers use the OpenAI chat format).
- **Router** — Maps a `provider/model` string to the correct provider + protocol.
- **Models** — Pydantic schemas for requests, responses, and configuration.
- **Auth** — Manages API keys from environment variables, config files, or direct input.

## Project Structure

```
swaplm/
├── __init__.py          # Public API surface
├── version.py           # Single source of version truth
├── auth/                # API key management
├── protocols/           # Shared API protocol implementations
├── providers/           # Vendor-specific provider adapters
├── models/              # Pydantic request/response schemas
├── router/              # Model string → provider resolution
├── streaming/           # SSE and streaming utilities
├── utils/               # Shared helpers and constants
└── resources/           # Static assets (model lists, etc.)

docs/                    # Documentation
examples/                # Usage examples
tests/                   # Test suite
.github/workflows/       # CI/CD pipelines
```

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
