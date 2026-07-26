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
response = chat(model="groq/llama-3.3-70b-versatile", messages=[{"role": "user", "content": "Hello!"}])

# Async
response = await achat(model="openai/gpt-4o", messages=[{"role": "user", "content": "Hello!"}])
```

---

## Provider Capability Matrix (17 Supported Providers)

| Provider | Slug | Protocol | Default Env Var | Free Tier | Streaming | Tool Calling | Structured Output | Reasoning |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|
| **Groq** | `groq` | OpenAI | `GROQ_API_KEY` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Anthropic** | `anthropic` | Anthropic | `ANTHROPIC_API_KEY` | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Google Gemini** | `google` | Google | `GEMINI_API_KEY` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAI** | `openai` | OpenAI | `OPENAI_API_KEY` | ❌ | ✅ | ✅ | ✅ | ✅ |
| **OpenRouter** | `openrouter` | OpenAI | `OPENROUTER_API_KEY` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Together AI** | `together` | OpenAI | `TOGETHER_API_KEY` | ❌ | ✅ | ✅ | ✅ | ✅ |
| **GitHub Models** | `github` | OpenAI | `GITHUB_TOKEN` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **NVIDIA NIM** | `nvidia` | OpenAI | `NVIDIA_API_KEY` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cerebras** | `cerebras` | OpenAI | `CEREBRAS_API_KEY` | ✅ | ✅ | ✅ | ✅ | ❌ |
| **SambaNova** | `sambanova` | OpenAI | `SAMBANOVA_API_KEY` | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Mistral AI** | `mistral` | OpenAI | `MISTRAL_API_KEY` | ✅ | ✅ | ✅ | ✅ | ❌ |
| **xAI** | `xai` | OpenAI | `XAI_API_KEY` | ❌ | ✅ | ✅ | ✅ | ❌ |
| **DeepInfra** | `deepinfra` | OpenAI | `DEEPINFRA_API_KEY` | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Fireworks AI** | `fireworks` | OpenAI | `FIREWORKS_API_KEY` | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Cloudflare** | `cloudflare` | OpenAI | `CLOUDFLARE_API_KEY` | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Perplexity** | `perplexity` | OpenAI | `PERPLEXITY_API_KEY` | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Cohere** | `cohere` | OpenAI | `COHERE_API_KEY` | ❌ | ✅ | ✅ | ✅ | ❌ |

---

## Features

- [x] 17 Production Provider Integrations (Groq, Anthropic, Gemini, OpenAI, OpenRouter, Together, GitHub, NVIDIA, Cerebras, SambaNova, Mistral, xAI, DeepInfra, Fireworks, Cloudflare, Perplexity, Cohere)
- [x] Zero-Code Provider Scaling via Metadata-Only Adapters
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

## Code Examples

### Explicit Provider Selection

```python
from swaplm import chat

# OpenAI
res_openai = chat(model="openai/gpt-4o", messages=[{"role": "user", "content": "Hello!"}])

# GitHub Models (Free)
res_github = chat(model="github/gpt-4o", messages=[{"role": "user", "content": "Hello!"}])

# OpenRouter (Free)
res_free = chat(model="free/qwen-2.5-72b-instruct:free", messages=[{"role": "user", "content": "Hello!"}])
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
| **6** | SDK Runtime & Developer Experience (Async, Retries, Middleware, Hooks) | ✅ Completed |
| **7** | OpenAI-Compatible Provider Expansion (17 Providers Integrated) | ✅ Current |
| **8** | Enterprise resilience (fallbacks, circuit breakers) | 🔜 Next |
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
