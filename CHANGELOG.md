# Changelog

All notable changes to **SwapLM** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1] - 2026-07-26

### Fixed
- `StreamChunk.content` and `StreamChunk.reasoning` return empty string `""` instead of `None` when no content is present. `print(chunk.content, end="")` now works without guard clauses.

---

## [0.2.0] - 2026-07-26

### Added
- **Explicit Provider Routing**: New `provider` parameter for `chat()` and `achat()` — bypasses model-string parsing.
- **Stream Convenience Properties**: `StreamChunk.content`, `StreamChunk.reasoning`, `StreamChunk.tool_calls`, `StreamChunk.finish_reason` — no more `chunk.choices[0].delta.content`.
- **Stream Response Alias**: `StreamResponse.text` — alias for `accumulated_content` for brevity.
- **Chat Response Reasoning**: `ChatResponse.reasoning` property — extracts reasoning from structured responses.
- **ChoiceDelta Reasoning**: `ChoiceDelta.reasoning` field — supports reasoning traces from thinking models (Claude, DeepSeek, Qwen).
- **Router.resolve_explicit()**: Dedicated routing path for explicit provider+model pairs.

### Changed
- Recommended API style: `chat(provider="groq", model="llama-3.3-70b-versatile")` over combined string.
- Streaming examples: `chunk.content` replaces `chunk.choices[0].delta.content`.
- All 7 example files updated to use explicit provider routing.

---

## [0.1.0] - 2026-07-26

### Added
- **Unified SDK API**: High-level `chat(...)` (sync) and `achat(...)` (async) entrypoints.
- **16 Production Providers**:
  - OpenAI (`openai`)
  - Anthropic (`anthropic`)
  - Google Gemini (`google`)
  - Groq (`groq`)
  - OpenRouter (`openrouter`, 345+ models)
  - GitHub Models (`github`)
  - NVIDIA NIM (`nvidia`)
  - Cerebras (`cerebras`)
  - SambaNova (`sambanova`)
  - Mistral AI (`mistral`)
  - xAI Grok (`xai`)
  - DeepInfra (`deepinfra`)
  - Fireworks AI (`fireworks`)
  - Cloudflare Workers AI (`cloudflare`)
  - Perplexity AI (`perplexity`)
  - Cohere (`cohere`)
- **Protocol System**: Robust request/response translation layers for OpenAI, Anthropic, and Google Gemini protocols.
- **Transport Engine**: `BaseTransport` interface with `HTTPTransport` implementation using `httpx.Client` & `httpx.AsyncClient` connection pooling, SSE streaming, and exponential backoff retries.
- **Middleware Interceptors**: `BaseMiddleware` class and pipeline execution (`add_middleware()`, `remove_middleware()`, `reset_middlewares()`).
- **Lifecycle Event Hooks**: `on()` and `off()` listeners supporting `before_request`, `after_request`, `before_retry`, `after_retry`, `on_error`.
- **Advanced Router**: Deterministic resolution supporting explicit provider prefixes (`openai/gpt-4o`), alias matching (`llama-3.3-70b`), virtual `free/` provider routing, and `AmbiguousModelError` detection.
- **Discovery APIs**: `providers()`, `provider()`, `models()`, `model()` public discovery helpers.
- **Structured Debug Logging**: `configure(debug=True)` with sensitive API token & header redaction.
