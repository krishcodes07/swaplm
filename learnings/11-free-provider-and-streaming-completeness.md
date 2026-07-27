# 11 — Free Provider & Streaming Completeness (Phase 11 / v0.3.0)

**Phase:** 11  
**Date:** 2026-07-27  

---

## What Was Done

Implemented Phase 11 (Release `v0.3.0`), focusing on replacing legacy router special cases with a first-class `free` provider package, completing protocol-level streaming tool call deltas across OpenAI and Anthropic formats, providing explicit HTTP connection lifecycle management via `Client`/`AsyncClient`, and enforcing PEP 561 type checking compliance.

---

## Deliverables & Enhancements

1. **First-Class Free Provider (`swaplm/providers/free/`)**:
   - Created a real provider package with `provider.py` and `models.json`.
   - Uses OpenRouter's free-tier API endpoints (`https://openrouter.ai/api/v1`) with `requires_api_key=False`.
   - Populated 8 curated free models (`meta-llama/llama-3.3-70b-instruct:free`, `deepseek/deepseek-r1-0528:free`, `qwen/qwen3-30b-a3b:free`, `google/gemma-3-27b-it:free`, `mistralai/mistral-small-3.1-24b-instruct:free`, `google/gemini-2.5-pro-exp-03-25:free`, `meta-llama/llama-4-maverick:free`, `deepseek/deepseek-chat-v3-0324:free`).
   - Removed all virtual `free/` routing hacks from `Router` — resolution order simplified to a clean 2-step pipeline (explicit `provider/model` → alias lookup).

2. **OpenAI Protocol Streaming Tool Calls**:
   - Updated `OpenAIProtocol.parse_stream_chunk()` to extract `delta.tool_calls` (index, id, type, function name, and incremental JSON argument chunks).
   - Mapped tool call deltas to unified `ToolCallDelta` objects surfaced via `StreamChunk.tool_calls`.

3. **Anthropic Protocol Streaming Tool Use**:
   - Extended `AnthropicProtocol.parse_stream_chunk()` to handle:
     - `content_block_start` with `type="tool_use"` → emits `ToolCallDelta` with block `id` and function `name`.
     - `content_block_delta` with `type="input_json_delta"` → emits `ToolCallDelta` with partial JSON arguments.
     - `message_delta` with `stop_reason="tool_use"` → maps stop reason to normalized finish reason `"tool_calls"`.

4. **Connection Lifecycle (`Client` & `AsyncClient`)**:
   - Added public `Client` (sync) and `AsyncClient` (async) context-managed wrappers in `swaplm/client.py`.
   - Each client manages an isolated `HTTPTransport` instance, supporting `with Client() as client:` and `async with AsyncClient() as client:` for leak-free HTTP connection pool teardown.

5. **PEP 561 Support (`py.typed`)**:
   - Added `swaplm/py.typed` marker file and verified static type checking integration in package distribution builds.

6. **Pre-Yield Streaming Retry Safety**:
   - Updated `HTTPTransport.send_stream()` and `asend_stream()` to execute retries on HTTP 5xx/429/timeout errors strictly **before** yielding the first SSE data chunk to user generators.

7. **Executable Examples & Tests**:
   - Added 3 new executable examples (`11_free_provider.py`, `12_streaming_tools.py`, `13_client_context_manager.py`).
   - Created `tests/test_free_provider.py`, `tests/test_streaming_tools.py`, `tests/test_client_lifecycle.py`, and updated `tests/test_openai_providers_expansion.py` & `tests/test_version.py`.
   - Expanded test suite from 175 to **193 passed tests** in 0.54s.

---

## Architectural & Technical Takeaways

1. **First-Class Providers over Virtual Router Hacks**:
   Virtual router shortcuts (like checking `if provider_id == "free":` inside `Router.resolve()`) create hidden control flow paths and tight coupling. Treating `free` as a standard `BaseProvider` subclass with its own `models.json` allows the dynamic registry to auto-discover it cleanly without modifying routing logic.

2. **Protocol Delta Normalization**:
   Different LLM APIs structure streaming tool calls differently. OpenAI sends `delta.tool_calls` arrays, while Anthropic splits tool calls across discrete `content_block_start` and `content_block_delta` events. Normalizing both into `ToolCallDelta` objects allows end-user code to use `chunk.tool_calls` uniformly.

3. **Pre-Yield Retry Safety in SSE Generators**:
   Retrying network requests in a generator is safe *only before* any data has been yielded to the caller. Once a chunk is yielded, attempting a retry on network failure would corrupt application state or produce duplicate output.

4. **Context Manager Resource Scoping**:
   While top-level `swaplm.chat()` and `swaplm.achat()` functions use a shared transport singleton for zero-boilerplate convenience, high-throughput or batch applications benefit from explicit `Client()` and `AsyncClient()` instances whose connection pools close deterministically upon block exit.

---

## Release Audit Summary

| Check | Result |
|---|---|
| Supported Production Providers | **17 Registered Providers** (includes `free`) |
| Total Test Count | ✅ **193 passed** in 0.54s |
| `ruff check .` | ✅ All checks passed |
| `ruff format --check .` | ✅ All 121 files formatted |
| Package Build (`py.typed` included) | ✅ Validated |
