# Free LLM Gateway

A unified OpenAI-compatible API server that aggregates **24+ free LLM providers** into one endpoint. Configure your free API keys in `.env`, then use **one base URL + one master key** to access every model.

[**العربية**](README_AR.md) | **English**

## Features

### Core
- **Single endpoint** — `http://localhost:8080/v1` (OpenAI SDK-compatible)
- **24+ providers** — OpenRouter, GitHub Models, Groq, Cerebras, Cloudflare, HuggingFace, NVIDIA, SiliconFlow, Cohere, Google Gemini, Mistral, Kilo, LLM7, Ollama Cloud, DeepSeek, Together AI, Fireworks AI, SambaNova, Chutes, Anthropic, OpenAI, Perplexity, xAI, Novita AI, Z AI, ModelScope
- **260+ free models** — auto-discovered from all providers
- **Automatic fallback** — if one provider fails (rate limit, error, timeout), tries the next
- **Round-robin load balancing** — distributes requests across providers
- **Streaming support** — full SSE passthrough with mid-stream error handling
- **Smart routing** — 60+ model aliases (type "gpt-4" → best available model)
- **Batch requests** — fan out multiple requests in parallel

### Security & Access Control
- **AES-256-GCM encrypted key storage** — API keys encrypted at rest with authenticated encryption
- **Unified gateway API keys** — `fgk-...` prefixed keys with per-key model/provider restrictions and admin roles
- **Per-key rate tracking** — RPM/RPD/TPM/TPD monitoring with rolling time windows and provider free-tier limits
- **Token estimation** — pre-flight TPM/TPD checks before routing to avoid hitting limits
- **Key health validation** — one-click test all API keys
- **Timing-safe key comparison** — constant-time auth to prevent timing attacks

### Routing & Reliability
- **Sticky sessions** — 30-minute provider affinity for conversation continuity
- **Routing headers** — `X-Routed-Via`, `X-Fallback-Attempts`, `X-Sticky-Session` on every response
- **Tool/function calling translation** — automatic OpenAI ↔ Gemini functionDeclarations conversion
- **Dynamic penalty routing** — providers returning 429s sink in priority; penalties decay over time
- **Per-key cooldown** — rate-limited keys are temporarily skipped until cooldown expires
- **Retry with backoff** — exponential backoff on 500/502/503 errors, Retry-After support on 429s
- **Runtime fallback editing** — reorder, enable/disable fallbacks via API without restart
- **Sort presets** — sort fallbacks by priority, penalty score, or health status
- **Model size labels** — automatic `small`/`medium`/`large`/`xl` tagging from model names

### Analytics & Persistence
- **SQLite request log** — every routed request persisted to disk, survives restarts
- **Rich analytics API** — 5 dedicated endpoints: summary, by-model, by-provider, timeline, errors
- **Time range filtering** — query analytics for 24h, 7d, or 30d windows
- **Error categorization** — rate-limited, timeout, auth, server errors auto-categorized
- **Estimated cost savings** — GPT-4o pricing comparison ($3/M input, $15/M output)
- **Usage analytics** — usage tracking, token counts, provider success rates

### Dashboard
- **Web dashboard** — 18 tabs: Models, Providers, Usage, Analytics, Rich Analytics, Benchmarks, Cache, Combos, Quotas, OAuth, Setup, Keys, Logs, Playground, Rate Tracking, Sessions, Gateway Keys, Fallbacks
- **Interactive playground** — test models directly from the dashboard with real-time responses
- **Fallback editor** — visually reorder and toggle fallback chains from the dashboard
- **Auto-sync** — pulls new free models from [awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)
- **Docker support** — one command to deploy

## Quick Start

```bash
# 1. Clone
git clone https://github.com/MrFadiAi/free-llm-gateway.git
cd free-llm-gateway

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env — add at least one provider API key

# 4. Start the gateway
python main.py
```

Open `http://127.0.0.1:8080/` for the dashboard.

## Configuration

### Environment Variables (`.env`)

| Variable | Description | Get Free Key |
|---|---|---|
| `MASTER_KEY` | Your gateway API key | Set anything you want |
| `OPENROUTER_KEY` | 35+ free models | [openrouter.ai ↗](https://openrouter.ai/keys) |
| `NVIDIA_KEY` | 100+ models, no daily cap | [build.nvidia.com ↗](https://build.nvidia.com/) |
| `GITHUB_KEY` | OpenAI, Meta, Mistral models | [GitHub Models ↗](https://github.com/marketplace/models) |
| `GROQ_KEY` | Ultra-fast inference | [console.groq.com ↗](https://console.groq.com/) |
| `CEREBRAS_KEY` | Fastest Llama inference (~2,600 tok/s) | [cloud.cerebras.ai ↗](https://cloud.cerebras.ai/) |
| `GOOGLE_GEMINI_KEY` | Gemini 2.5 Flash, 1M context | [aistudio.google.com ↗](https://aistudio.google.com/apikey) |
| `MISTRAL_KEY` | Mistral Small/Large/Codestral | [console.mistral.ai ↗](https://console.mistral.ai/) |
| `COHERE_KEY` | Command R+ (1K calls/month) | [dashboard.cohere.com ↗](https://dashboard.cohere.com/) |
| `SILICONFLOW_KEY` | Qwen, DeepSeek, GLM | [siliconflow.cn ↗](https://cloud.siliconflow.cn/) |
| `HUGGINGFACE_KEY` | Thousands of community models | [huggingface.co ↗](https://huggingface.co/settings/tokens) |
| `CLOUDFLARE_KEY` | 50+ models, 10K neurons/day | [Cloudflare Workers AI ↗](https://dash.cloudflare.com/) |
| `KILO_KEY` | Free model gateway | [kilo.ai ↗](https://kilo.ai/) |
| `LLM7_KEY` | No registration needed | [llm7.io ↗](https://token.llm7.io/) |
| `DEEPSEEK_KEY` | DeepSeek-R1 reasoning models | [platform.deepseek.com ↗](https://platform.deepseek.com/api_keys) |
| `TOGETHER_KEY` | 100+ open-source models, $5 free credits | [together.ai ↗](https://api.together.xyz/settings/api-keys) |
| `FIREWORKS_KEY` | Fast open-source inference | [fireworks.ai ↗](https://app.fireworks.ai/) |
| `SAMBANOVA_KEY` | Fast Llama inference | [sambanova.ai ↗](https://cloud.sambanova.ai/apis) |
| `CHUTES_KEY` | Community-driven model hosting | [chutes.ai ↗](https://chutes.ai) |
| `NVIDIA_NIM_KEY` | 100+ models via NVIDIA NIM | [build.nvidia.com ↗](https://build.nvidia.com/) |
| `NOVITA_KEY` | GPU cloud for open-source LLMs | [novita.ai ↗](https://novita.ai) |
| `Z_AI_KEY` | Zhipu AI permanent free models | [bigmodel.cn ↗](https://open.bigmodel.cn/) |
| `MODELSCOPE_KEY` | Alibaba ModelScope models | [modelscope.cn ↗](https://modelscope.cn/) |
| `ANTHROPIC_KEY` | Claude models (paid) | [anthropic.com ↗](https://console.anthropic.com/) |
| `OPENAI_KEY` | GPT-4, GPT-4o (paid) | [platform.openai.com ↗](https://platform.openai.com/api-keys) |
| `PERPLEXITY_KEY` | Sonar search-augmented models (paid) | [perplexity.ai ↗](https://perplexity.ai/settings/api) |
| `XAI_KEY` | Grok models (paid) | [x.ai ↗](https://console.x.ai) |

You only need **at least one** provider key to get started.

### Model Configuration (`models.yaml`)

Models are defined with ordered fallback chains:

```yaml
models:
  llama-3.3-70b:
    - provider: openrouter
      model: meta-llama/llama-3.3-70b-instruct:free
    - provider: nvidia
      model: meta/llama-3.1-405b-instruct
```

## Usage

### With OpenAI SDK (Python)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="your-master-key",
)

response = client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### With curl

```bash
# List available models
curl http://localhost:8080/v1/models \
  -H "Authorization: Bearer your-master-key"

# Chat completion
curl http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer your-master-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.3-70b", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### With Gateway API Keys

Create a gateway key for per-user access control:

```bash
# Create a gateway key via API
curl -X POST http://localhost:8080/api/gateway-keys \
  -H "Authorization: Bearer your-master-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-user", "is_admin": false}'

# Response: {"raw_key": "fgk-xxxx...", ...}
# Use the fgk- key as your API key
```

```python
# Use gateway key in any OpenAI-compatible tool
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="fgk-your-gateway-key-here",
)
```

### With any OpenAI-compatible tool

Point any tool that supports custom OpenAI base URLs to `http://localhost:8080/v1` with your master key as the API key. Works with Cursor, LibreChat, Open WebUI, OpenClaw, and more.

## API Endpoints

### Chat & Models

| Endpoint | Method | Description |
|---|---|---|
| `/v1/chat/completions` | POST | Chat completions (with streaming) |
| `/v1/models` | GET | List all available models |
| `/v1/batch` | POST | Batch requests (parallel) |
| `/v1/embeddings` | POST | Text embeddings |
| `/` | GET | Web dashboard |

### Gateway & Analytics

| Endpoint | Method | Description |
|---|---|---|
| `/api/ping` | GET | Lightweight liveness probe (no auth required) |
| `/api/status` | GET | JSON status |
| `/api/analytics` | GET | Usage analytics + savings |
| `/api/keys/validate-all` | POST | Validate all API keys |
| `/api/auto-update` | GET | Re-scan providers for new models |
| `/api/sync-providers` | POST | Sync from awesome-free-llm-apis |
| `/api/playground` | POST | Interactive model testing |
| `/api/translate-tools` | POST | Tool format translation |

### Rich Analytics (SQLite-backed)

| Endpoint | Method | Description |
|---|---|---|
| `/api/analytics/summary?range=7d` | GET | Total requests, success rate, tokens, latency, savings |
| `/api/analytics/by-model?range=7d` | GET | Stats grouped by provider+model |
| `/api/analytics/by-provider?range=7d` | GET | Stats grouped by provider |
| `/api/analytics/timeline?range=7d&interval=day` | GET | Time-bucketed request counts |
| `/api/analytics/errors?range=7d` | GET | Error distribution by category + recent errors |

Ranges: `24h`, `7d`, `30d`

### Fallback Management

| Endpoint | Method | Description |
|---|---|---|
| `/api/fallbacks` | GET | Get all fallback chains with penalty info |
| `/api/fallbacks/{model}` | PUT | Reorder or toggle fallbacks for a model |
| `/api/fallbacks/{model}/sort/{preset}` | POST | Sort by preset: `priority`, `penalty`, `health` |

### Rate Tracking

| Endpoint | Method | Description |
|---|---|---|
| `/api/rate-tracking` | GET | All per-key rate tracking data |
| `/api/rate-tracking/{provider}` | GET | Rate tracking for specific provider |
| `/api/rate-tracking/set-limits` | POST | Set custom rate limits |
| `/api/rate-tracking/cleanup` | POST | Clean up stale tracking data |

### Sessions

| Endpoint | Method | Description |
|---|---|---|
| `/api/sessions` | GET | List active sticky sessions |
| `/api/sessions/{id}` | DELETE | Remove a session |
| `/api/sessions/cleanup` | POST | Clean up expired sessions |

### Gateway Keys

| Endpoint | Method | Description |
|---|---|---|
| `/api/gateway-keys` | GET | List gateway API keys |
| `/api/gateway-keys` | POST | Create a new gateway key |
| `/api/gateway-keys/{name}` | DELETE | Revoke a gateway key |
| `/api/gateway-keys/{name}/toggle` | PUT | Enable/disable a key |

### Encrypted Key Store

| Endpoint | Method | Description |
|---|---|---|
| `/api/encrypted-keys` | GET | List encrypted keys |
| `/api/encrypted-keys` | POST | Add encrypted key |
| `/api/encrypted-keys/{provider}/{index}` | DELETE | Remove encrypted key |

## Auto-Updates

Keep models fresh with zero effort:

1. **Dashboard** → Setup tab → "Sync Providers" button
2. **Terminal** → `python3 sync_providers.py`
3. **Auto-cron** → weekly sync from awesome-free-llm-apis

New providers and models appear automatically.

## Docker

```bash
docker-compose up -d
```

## Architecture

```
Any AI Tool → Gateway (localhost:8080)
               ├── Auth check (timing-safe, MASTER_KEY or fgk- gateway keys)
               ├── Per-key rate limiting (RPM/RPD/TPM/TPD)
               ├── Token estimation with TPM/TPD pre-checks
               ├── AES-256-GCM encrypted key storage
               ├── Smart routing with 60+ aliases
               ├── Model size labels (auto-inferred from names)
               ├── Round-robin load balancing
               ├── Dynamic penalty routing (429s sink priority)
               ├── Per-key cooldown on rate limits
               ├── Retry with exponential backoff (500/502/503)
               ├── Sticky sessions (30-min affinity)
               ├── Tool calling translation (OpenAI ↔ Gemini)
               ├── Streaming with mid-stream error handling
               ├── Liveness probe (/api/ping health checks)
               ├── Rate limit tracking per provider
               ├── Auto-fallback on failure
               ├── Runtime fallback chain editing (API)
               ├── Response caching (LRU + TTL)
               ├── Request queuing with backoff
               ├── SQLite persistent request log
               ├── Rich analytics API (5 endpoints)
               ├── Routing headers (X-Routed-Via, X-Fallback-Attempts)
               └── Usage analytics + savings tracker
```

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

130 tests covering rate tracking, sticky sessions, gateway auth, tool translation, key encryption, health checks, SQLite request logging, safe streaming, fallback editing, analytics endpoints, and more.

## License

MIT
