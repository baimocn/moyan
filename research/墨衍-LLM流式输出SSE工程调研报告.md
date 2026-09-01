# 墨衍 · LLM 流式输出（SSE/打字机）工程调研报告

> 调研方式说明：本报告所有事实均来自 2025 年真实联网抓取的一手来源（官方文档、官方 SDK 源码、GitHub 真实项目源码/README），注明出处；设计建议单独标注为"推荐"。未使用任何搜索引擎摘要，未凭记忆编造。

---

## 0. 结论速览（TL;DR）

| 决策点 | 推荐 |
|---|---|
| 流式传输载体 | HTTP SSE（`text/event-stream`），不用 WebSocket（h5/小程序可后端兼容双通道，见 §6） |
| FastAPI 实现 | 裸 `StreamingResponse` + 异步生成器（官方推荐），或直接上 `sse-starlette.EventSourceResponse`（断连/ping 开箱即用） |
| 事件格式 | **类型化 SSE**：每行 `data: {json}\n\n`，JSON 内用 `type` 字段判别（借鉴 Vercel AI SDK Data Stream Protocol + Anthropic 事件模型），末尾 `data: [DONE]` |
| 上游协议 | OpenAI 兼容 SDK（`stream=True` → 逐块 `delta`）+ DeepSeek 官方兼容；Anthropic 走其自身 SDK（或兼容层） |
| 断连处理 | `await request.is_disconnected()` + `except asyncio.CancelledError` 清理 + 主动关闭上游流 |
| token 成本 | `stream_options={"include_usage": True}` 拿 usage 块 + 失败/中断兜底估算并记账（§2.1） |
| 结构化判定 | 推荐"类型化事件并存"：文本走 `text-delta`，结束前发 `judge`/`meta` 类型事件携带 JSON（§4） |
| 降级 | 手写轻量 Router（约 150 行）：同端点重试 1–2 次 → 跨引擎 failover → 熔断冷却；暂不引入 litellm（§5） |
| 生产部署 | nginx `proxy_buffering off` + `X-Accel-Buffering: no` + 心跳（§1.3） |

---

## 1. 【SSE 工程要点】

### 1.1 SSE 事件格式约定（W3C + 生态惯例）

- 每条 SSE 事件由若干 `字段: 值` 行组成，字段有 `data:`、`event:`、`id:`、`retry:` 与注释行（仅含 `:`），两条事件之间用**空行**分隔；字符串需 UTF-8，`data:` 可以多行，浏览器端会以换行拼接（sse-starlette 默认分隔符是 `\r\n`）。
- HTTP 头：`Content-Type: text/event-stream`、`Cache-Control: no-cache`、可选 `X-Accel-Buffering: no`（禁反向代理缓冲）、`Connection: keep-alive`。
- **OpenAI/DeepSeek 生态惯例**：每条 SSE **只发 `data: {json}\n\n`，不写 `event:` 行**，靠 JSON 内的 `object`/`finish_reason` 等字段区分；流以最后一个 `data: [DONE]`（字面量，非 JSON）结束。
- **Anthropic 生态惯例**：事件类型化——其官方 SDK 把流事件建模为按 **data JSON 内 `type` 字段判别**的联合类型（`message_start` / `content_block_start` / `content_block_delta` / `content_block_stop` / `message_delta` / `message_stop`），线协议另有 `event:` 行标注事件名（已验证 SDK 源码 `RawMessageStreamEvent` 的 `discriminator="type"`）。
- **心跳**：代理/负载均衡器会掐掉"没动静"的连接。sse-starlette 默认每 15s 自动发一个 ping 注释行；自己实现时也要发 `: ping\n\n`（或空 `data:`）。HAProxy 等超时配置必须大于 ping 间隔（README 示例：ping 45s → timeout client/server 60s）。
- **客户端重连**：浏览器 `EventSource` 原生自动重连；服务端可用 `retry:` 字段控制重连等待。sse-starlette 建议对 server 端也实现带退避的手动重连（onerror → setTimeout 重开）。

### 1.2 FastAPI 里的实现模式

**模式 A：裸 `StreamingResponse`（FastAPI 官方文档推荐）**

FastAPI 官方 `custom-response` 文档明确建议：不要直接裸返回 StreamingResponse，而应遵循 **Stream Data** 教程的模式——声明 `response_class=StreamingResponse` 后在路径函数里用 `yield` 逐块产出，"更便捷且**在后台处理了取消（cancellation）**"。要点：

```python
from fastapi.responses import StreamingResponse

@app.post("/chat", response_class=StreamingResponse)
async def chat(req: ChatRequest):
    async def event_stream():
        async for chunk in llm_stream(...):          # 上游 OpenAI/DeepSeek 增量
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

官方要点：async 生成器与普通生成器都支持；每个 `yield` 原样给到响应体，需要自己完成字节编码；可继承 `StreamingResponse` 设 `media_type` 定制 Content-Type（文档里的 `PNGStreamingResponse` 就是范例）。

**模式 B：`sse-starlette`（848★，Starlette 生态事实标准）**

`sse_starlette.EventSourceResponse(content_stream)` 开箱提供：自动断连检测、每 N 秒 ping（默认 15s）、`send_timeout` 兜死连接、服务器优雅关闭（`shutdown_event` + `shutdown_grace_period`）、内存通道（anyio memory channel）替代生成器、多线程/多事件循环支持。结构化事件：

```python
from sse_starlette import EventSourceResponse, ServerSentEvent, JSONServerSentEvent

event = ServerSentEvent(data="...", event="text", id="msg-1", retry=5000)  # 带上 event 名
event = JSONServerSentEvent(data={"type": "text-delta", "delta": "你好"})  # data 自动 json.dumps
return EventSourceResponse(gen(), ping=15, send_timeout=30,
                           headers={"Cache-Control": "no-cache"})
```

**真实项目实例（可对照学习）**：GitHub 教育 RAG 项目 `Happy-Chen-CH/Educational_RAG_System`（FastAPI）的 `/api/chat` 就是"裸 StreamingResponse + 每块 JSON"的完整实现：`data: {"token": "...", "session_id": "...", "done": false}\n\n` 逐块推送，`done: true` 收尾，`except Exception` 时把错误塞进 `done: true` 事件而不是中断连接，响应头带 `X-Accel-Buffering: no`。它还做了 `chunk_size=3 + sleep(0.015)` 的伪逐字切分来制造"打字机"观感——**墨衍建议把节奏控制放前端**（delta 驱动渲染），后端保持真实增量，避免人为 sleep 抬高延迟（除非要限速降负载）。

**生产注意**：长连接会占住 uvicorn worker 的并发槽，需按业务上限做并发控制（文档示例给了一个 `asyncio.Semaphore` 连接的 ConnectionLimiter）；每个连接有输出缓冲，注意内存；worker 数与 SSE 长连接数匹配（H5 端一个页面通常只有 1 条活跃 SSE）。

### 1.3 nginx 生产配置（防缓冲）

sse-starlette README 明确警告：**nginx 默认缓冲响应，会把 SSE 事件攒到 ~16KB 才吐给客户端**，直接破坏打字机体验。两种解法（文档原文整理）：

```nginx
location /api/chat {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_buffering off;            # 关键：本 location 关闭缓冲
    chunked_transfer_encoding off;
    proxy_read_timeout 300s;        # 大于一次最长生成时长，靠 ping 保活
}
```

优先级最高的做法是**应用层带头**：`X-Accel-Buffering: no`，nginx/OpenResty 会尊重它对该响应关闭缓冲（Educational_RAG_System 就是这么做的，可直接抄）。其他中间层：Cloudflare 约缓冲 100KB 才 flush、Akamai/F5 默认缓冲——小程序的域名若走 CDN 也要注意。

### 1.4 断连（client disconnect）处理

- 检测手段（sse-starlette 文档 + FastAPI issue #3766 的结论一致）：
  - 循环内 `if await request.is_disconnected(): break`——从"客户端断开"感知到下一次 yield 之间可能有延迟，所以小间隔事件流更灵敏；
  - 生成器内 `except asyncio.CancelledError:`——客户端断开时 uvicorn/anyio 会取消该任务，捕获它做清理（关 DB 会话、关上游流、记账）后**必须 re-raise**；
  - `send_timeout`——TCP 半开等"写不进去"的死连接，靠发送超时兜底。
- 主动中断（用户点"停止"）：中断本质是客户端行为（关掉 EventSource/AbortController），服务端据此收 CancelledError；也可在服务端用 `asyncio.Event` 作为取消信号。
- 上游流清理：OpenAI 异步客户端 `async for chunk in stream` 被取消时，`finally` 里 `await stream.close()`，避免上游继续生成扣费（OpenAI 文档也提示：流被中断时可能收不到 usage 块）。

---

## 2. 【OpenAI 兼容 SDK 流式接口标准 + 中断】

### 2.1 `chat.completions` with `stream=True`（SDK 源码验证）

- `client.chat.completions.create(..., stream=True)` 返回 `Stream[ChatCompletionChunk]`（异步为 `AsyncStream`），逐块迭代即得增量。
- **每一块的 JSON 结构**（openai-python 官方类型 `ChatCompletionChunk` 源码）：`object: "chat.completion.chunk"`；`id`/`created` 各块相同；`choices[0].delta.content` 为本块新增文本（**增量**，不是累计）；首块 `delta.role`；工具调用走 `delta.tool_calls[i].function.arguments`——**也是增量 JSON 片段**，需要自行拼接后再 `json.loads`。
- **结束语义**：最后一个内容块 `delta` 无新增，`choices[0].finish_reason` 变非空（`stop | length | tool_calls | content_filter`），随后是字面量 `data: [DONE]`。DeepSeek 文档也确认同样惯例："最后一块（`[DONE]` 之前）携带整个请求的 token usage，`choices` 恰含一个元素、无新内容、`finish_reason` 非空"。
- **token 成本控制要点**：`stream_options={"include_usage": True}` 时 usage 只出现在**最后一个块**（`choices` 为空的那种块）；**如果流被中断/取消，可能收不到 usage 块**（openai-python 源码注记原文）→ 墨衍的计费侧必须：① 优先解析 usage 块；② 拿不到时用"已收 delta 字符数 + tiktoken/分词器估算"兜底记账；③ 把实际 usage 与估算一并落日志。
- DeepSeek 思考模型另发 `reasoning_content` 增量（非流时在 `message.reasoning_content`），主文本在 `delta.content`——墨衍教学"讲思路"场景可单独渲染思考过程。

### 2.2 DeepSeek / 中转站兼容性

- **DeepSeek 官方明示**（api-docs.deepseek.com 首页原文）："The DeepSeek API uses an API format compatible with OpenAI/Anthropic"，OpenAI 兼容 base_url 为 `https://api.deepseek.com`（另有 `/anthropic` 端点），可直接用 `openai` Python SDK `/` JS SDK 接入；流式行为与 OpenAI 一致（`data:` 块 + `[DONE]`）。
- **中转站（国内聚合网关/OpenAI 兼容代理）**：按 OpenAI 协议实现是事实现状（前文 free-llm-gateway 等网关都以 OpenAI 兼容导出）。接入时校验：模型名映射、是否回传 usage、`finish_reason` 是否可靠、限流错误码（420/429）与错误体结构——这些是"一个 SDK 兼容不代表计费/错误语义也兼容"的差异点。

### 2.3 断连正确姿势（FastAPI 侧，代码要点级）

```python
async def sse_gen(request: Request, ...):
    try:
        async for chunk in upstream_stream():        # openai AsyncStream
            if await request.is_disconnected():      # 客户端跑了
                break
            yield f"data: {json.dumps(chunk_ev(chunk), ensure_ascii=False)}\n\n"
    except asyncio.CancelledError:                   # uvicorn 取消（断连/关服）
        await upstream_stream.aclose()               # 关上游，停止计费
        log_usage_partial(...)                       # 兜底记账
        raise                                        # 必须继续抛，交给框架
    finally:
        ...                                          # 清理 session/连接池
```

参考一手来源：FastAPI issue #3766（"client disconnect 时如何优雅取消 handler"）、sse-starlette 的 client-disconnect 示例（README §Advanced）。

---

## 3. 【类型化事件方案 —— 给墨衍的推荐设计】

### 3.1 设计原则

1. **单通道、单格式**：整条流都是 `data: {json}\n\n`，事件类型写在 JSON 的 `type` 字段——不做多 `event:` 名（H5/小程序/各种解析器统一按 JSON 处理最简单），这正是 Vercel AI SDK Data Stream Protocol 的做法。
2. **文本用增量事件**（`text-delta`），前端据此驱动"打字机"渲染，天然支持打断/重放。
3. **结构数据是"事件"不是"附录"**：判定/评分等 JSON 作为带类型的事件在文本结束后发出（见 §4）。
4. **必须有 `[DONE]` 与 `error` 语义**，客户端才能区分"正常结束 / 出错 / 被中断"。
5. **带消息/会话上下文**（`messageId`、`sessionId`），方便会话历史与续期。

### 3.2 推荐事件类型与 JSON 规格（v0.1）

| type | 时机/频率 | data 字段（示意） | 说明 |
|---|---|---|---|
| `start` | 流开始 | `{type, messageId, sessionId, model, engine}` | 前端可立刻渲染"思考中…" |
| `reasoning-delta` | 可选，思考模型 | `{type, messageId, delta}` | DeepSeek `reasoning_content` 增量 |
| `text-delta` | 主文本逐块 | `{type, messageId, delta, seq}` | 打字机唯一数据源（借鉴 Vercel `text-delta`） |
| `judge` | 文本结束后 1 次 | `{type, messageId, data:{...判定 JSON...}, schema:"learn_judge_v1"}` | 教学判定/下一题等结构化数据（§4） |
| `meta` | 收尾前 1 次 | `{type, model, engine, usage:{prompt,completion,total}, latencyMs, fallbackUsed, provider}` | 成本与链路信息，供计费/调试 |
| `error` | 任意时点 | `{type, code, message, retriable}` | `retriable` 供前端决定是否"重试" |
| `finish` | 正常结束 | `{type, messageId, finishReason, usage}` | 等价 OpenAI `finish_reason` |
| `abort` | 服务端主动终止 | `{type, reason}` | 如熔断降级后 |
| 流终止 | 始终 | 字面量 `data: [DONE]` | 与 OpenAI/DeepSeek/Vercel 全兼容 |

实现样例（FastAPI + sse-starlette 风格）：

```python
def ev(t: str, **kw):
    return JSONServerSentEvent(data={"type": t, **kw})   # 或手工 f"data: {json.dumps(...)}\n\n"

# 流内：text-delta → judge → meta → finish → [DONE]
yield ev("text-delta", messageId=mid, delta="二次函数", seq=n)
yield ev("judge", messageId=mid, data=judge_payload)     # 教学判定 JSON
yield ev("meta", model="gpt-4o", engine="primary", usage=usage, latencyMs=ms)
yield ev("finish", messageId=mid, finishReason="stop", usage=usage)
yield ev("[DONE]") if manual else "data: [DONE]\n\n"
```

> 参考：Vercel AI SDK 的 `start/text-start/text-delta/text-end/reasoning-*/data-*/error/finish/abort` 全部以 `data:` JSON 表达并支持 `data-<custom>` 自定义类型、以 `[DONE]` 收尾——墨衍这套是它的教学场景裁剪版；Anthropic 的 `type` 判别事件模型同理可映射。

---

## 4. 【流式 + 结构化数据】组合方案

### 4.1 三种方案的取舍

**方案 A：先流式文本、末尾附 JSON（同一次响应内两段）**
- 做法：提示词里约定"先讲课，最后输出 `{"judge": ...}`"；或在最后单独跑一次判定调用。
- 优点：客户端简单，一次请求完事。缺点：文本与 JSON 混在流里，前端要"找最后一个 JSON"；`finish_reason=length` 截断时 JSON 不完整（DeepSeek 文档明确提示 json_object 模式下 content 可能因 `length` 截断）→ 需要兜底（parse 失败重试/降级为纯文本）。
- 结合点：DeepSeek/OpenAI 的 `response_format={"type":"json_object"}` 可保证模型输出合法 JSON（但必须在 prompt 里显式要求输出 JSON，否则可能空转）。
- 适用：判定简单、可容忍截断风险的早期版本。

**方案 B：SSE 类型化事件并存（推荐给墨衍）**
- 文本走 `text-delta` 事件流；判定等结构化数据走**独立类型事件**（`judge`），或在文本结束后追加一次判定调用再发 `judge` 事件。
- 优点：文本与结构在协议层分离，前端永远不猜；中途出错可发 `error` 事件且已有文本仍有效；`reset-step`/重试时只作废半截文本（Vercel 的 `reset-step` 正是为此设计）。Anthropic 原生就是这个模型（text block 与 tool use block 并存）。
- 缺点：事件 schema 需要前后端一起定（就是 §3 这套）。

**方案 C：文本流 + 独立接口取 JSON（解耦）**
- 文本 SSE 结束后前端再 GET/POST 一个 `/judge?message_id=` 拿结构化结果。
- 优点：最解耦、可缓存、可单独重试判定。缺点：多一次往返、判定结果与文本不同步（服务端要先把判定算完/存好）。

### 4.2 教学场景（墨衍）推荐落法

- 判定独立，但**时间上紧跟文本结束**：生成完文本（同一轮对话）立刻做第二次小调用（成本可控、judge 不参与流式），随后发 `judge` 事件 → 用户体验上是"讲完话紧跟着给判定/下一题"。
- 若想省一次调用：prompt 让模型"以 `<<JUDGE>>` 分隔讲课与 JSON"，后端切流：分隔符前 → `text-delta`，分隔符后 → 攒起来 parse 成 `judge` 事件；parse 失败走降级（视为纯文本或重新判定）。
- 真实例证：`Educational_RAG_System` 用的是"逐块 JSON + done 标志"的朴素方案（文本与状态合在一个 JSON 里）；`free-llm-gateway` 做 OpenAI 兼容 SSE 直通时实现了**流中间错误处理**（mid-stream error handling）——说明中间插错误/元信息事件是被业界接受且可行的。

---

## 5. 【降级 / 重试设计】（主备引擎切换、超时、熔断）

### 5.1 业界做法（一手来源）

- **liteLLM Router**（文档实测）：`model_list` 里可配多 deployment；`order` 字段做"优先顺序"，order=1 失败（连接错误/404/429 等）自动依次尝试 order=2、3…；`fallbacks` 做**跨模型组**兜底；`enable_weighted_failover` 先组内重选再跨组；总兜底步数 `max_fallbacks`（默认 5）。可靠性参数：**cooldown**（默认 `cooldown_time=5s`、`allowed_fails` 计数触发冷却，冷却期内该 deployment 移出可用池、到期自动恢复，生产可换 Redis 记录）；**num_retries**（优先级：请求体 > deployment 配置 > router 全局）；`RetryPolicy` 可**按错误类型**配重试（如 ContentPolicyViolation 重试 3 次、AuthenticationError 重试 0 次）。文档特别警示：**`num_retries` 与上游 SDK 的 `max_retries` 别叠加**，否则一次请求变 `(1+N)²` 次上游调用。
- **openai-python SDK**（源码实测）：默认 `max_retries=2`；退避算法 `min(0.5 * 2^n, 8.0)` 秒 + `1 - 0.25*random()` 抖动；尊重服务端 `Retry-After`（上限 120s）与 `x-should-retry` 头；默认超时 `DEFAULT_TIMEOUT=600s / connect=5s`。
- **free-llm-gateway**（README）：按 `models.yaml` 写**有序 fallback 链**；500/502/503 指数退避重试、429 尊重 Retry-After；**动态惩罚路由**——返 429 的 provider 优先级下沉且惩罚随时间衰减；**per-key cooldown** 临时跳过限流 key；30 分钟 sticky session 保持对话连续性；响应头 `X-Routed-Via` / `X-Fallback-Attempts` 透出实际路由（可观测性要点）。
- **9router**（README）：**分层 tier 降级**模型——订阅(Sub) → 便宜(Cheap) → 免费(Free)，quota 耗尽自动下探，零停机。

### 5.2 给墨衍的推荐实现（手写轻量 Router，~150 行）

```python
PROVIDERS = [  # 依序：主引擎 → 备用引擎（如主 GPT/DeepSeek → 备用中转/开源）
    Provider(name="deepseek",   client=AsyncOpenAI(base_url="https://api.deepseek.com", ...),
             order=1, allowed_fails=4, cooldown_s=60),
    Provider(name="backup-gw",  client=AsyncOpenAI(base_url="https://xxx中转/v1", ...),
             order=2, allowed_fails=2, cooldown_s=30),
]

async def chat_with_failover(messages, *, request):
    for i, p in enumerate(available(PROVIDERS)):        # 过滤冷却中的
        try:
            stream = await p.client.chat.completions.create(model=..., messages=..., stream=True,
                                                            stream_options={"include_usage": True},
                                                            timeout=httpx.Timeout(600, connect=5, read=30))
            async for chunk in stream:
                if await request.is_disconnected():     # 断连立即停，不计费
                    await stream.aclose(); return
                yield chunk_to_event(chunk, engine=p.name)
            p.fail = 0                                  # 成功清零
            return
        except (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError) as e:
            p.fail += 1
            log(f"provider={p.name} attempt={i+1} error={type(e).__name__}")
            if i == len(available(PROVIDERS)) - 1:      # 全失败
                yield error_event(code="all_providers_failed", retriable=True)
                return
```

要点/参数建议（供默认值，可配置化）：

| 项 | 建议默认 | 依据 |
|---|---|---|
| 单供应商重试次数 | 1–2 次（同端点内） | openai 默认 2 |
| 跨引擎切换 | 每层最多 1 次，总尝试 ≤ 3–4 | litellm order/fallbacks 语义 |
| 连接超时 | 5s；首包(read) 30s；总时长 600s 上限 | openai 默认 connect=5/600 |
| 退避 | 0.5s×2^n 封顶 8s + 抖动 | openai SDK 源码 |
| 429 | 尊重 Retry-After；超 120s 不重试直接切换 | openai SDK |
| 熔断冷却 | 连续失败 4 次 → 冷却 60s；冷却期移出候选池 | litellm allowed_fails/cooldown |
| 路由可观测性 | `meta` 事件带 `provider`/`fallbackUsed`/`latencyMs` | free-llm-gateway 响应头思路 |
| 审计 | 每次 fallback 记日志（原因、次数、耗时、usage） | 成本核算必需 |

**避免的坑**：
- 上游 SDK `max_retries` 与自研重试**别同时开**（litellm 文档的 `(1+N)²` 警告）——二选一：用 SDK 内部重试（设 max_retries=1）做同端点，自研只做**跨引擎**切换。
- 流开始后才失败（中途断流）：已发的文本保留，发 `error` 或降级文本提示；**不建议**在用户已看到一半时无声切引擎重发（Vercel 用 `reset-step` 显式作废半截，墨衍教学场景可提示"已重试"）。
- 超时兜底：服务端生成要有总时长上限（如 300s），超出发 `error`/降级为非流式重试。

### 5.3 是否需要引入 litellm？（轻量依赖评估）

- **不建议现在就引**：墨衍只有 GPT/Claude/DeepSeek + 中转站 2–4 家，手写 Router（顺序尝试 + 计数熔断 + 冷却表）约 150 行、零新依赖（直接多实例 `AsyncOpenAI` 即可）；litellm 为覆盖几十家 provider 而做得重（大依赖树、版本波动风险），为 4 家引擎引入不划算。
- **何时再引**：模型/供应商扩充到 10+、需要 tpm/rpm 用量路由、Redis 级熔断共享、或需要 proxy 层给团队统一出口时，再评估 litellm Router 或同类网关（free-llm-gateway/9router 是现成对照实现）。
- Claude 接入提示：Anthropic 为独立协议，若手写 Router 建议给 Claude 配一层"OpenAI 兼容转换"（9router 的做法：格式互转），或直接双客户端（AsyncOpenAI + AsyncAnthropic）按引擎分派。

---

## 6. 【uni-app 前端提示】（含 H5/小程序差异）

- **H5**：标准 `EventSource` 即可；逐字打字机由 `text-delta` 事件驱动 + 前端 CSS/定时渲染节奏实现（后端不伪造节奏）。中断 = `es.close()`（服务端收 CancelledError）。
- **小程序端现实约束**（工程提示，非断言）：微信小程序**没有原生 EventSource**，`wx.request` 也不支持流式读取响应体；本次 GitHub 检索（uni-app × SSE × chat、wechat × miniprogram × streaming）均返回 0 个成熟项目，印证该生态比较薄。落地选项：
  1. 后端对流式提供 **WebSocket 通道**（同事件 JSON 复用，传输层抽象成"SSE/WS 双适配"）；
  2. 小程序分包引入 SSE polyfill（`fetch` 在部分平台可读流/或第三方库），兼容性逐一验证；
  3. 特例降级：小程序端回退"非流式 + 定时拉取"。
  建议墨衍把**事件协议与传输层解耦**（一套事件 JSON，两种 transport），前端库按平台注入。

---

## 7. 引用链接（全部为本次调研实际抓取的一手来源）

**FastAPI / Starlette / SSE**
- sse-starlette（README：EventSourceResponse、ping、断连、nginx/HAProxy/CDN 配置）：https://github.com/sysid/sse-starlette
- Starlette Responses 文档（StreamingResponse）：https://docs.starlette.io/responses/
- FastAPI 自定义响应（StreamingResponse + 推荐 stream-data 模式）：https://fastapi.tiangolo.com/advanced/custom-response/
- FastAPI 流式数据教程（yield、取消处理、自定义 media_type）：https://fastapi.tiangolo.com/advanced/stream-data/
- FastAPI issue #3766（客户端断连时优雅取消 handler）：https://github.com/fastapi/fastapi/issues/3766

**OpenAI 兼容流式标准 / SDK**
- openai-python `ChatCompletionChunk` 类型（delta/finish_reason/usage 块语义）：https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_chunk.py
- openai-python 重试/超时源码（`_base_client.py`、`_constants.py`：max_retries=2、0.5s→8s 抖动退避、Retry-After）：https://github.com/openai/openai-python/blob/main/src/openai/_base_client.py
- DeepSeek API 官方文档（首页 OpenAI/Anthropic 兼容声明 + base_url；Create Chat Completion 的 [DONE]/usage/reasoning_content）：https://api-docs.deepseek.com/
- Anthropic SDK 流事件类型（`RawMessageStreamEvent` 按 type 判别）：https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/raw_message_stream_event.py

**流式 + 结构化 / 类型化事件**
- Vercel AI SDK Stream Protocol（`start/text-delta/error/finish/abort/data-*` + `[DONE]` 类型化 SSE 协议）：https://ai-sdk.dev（源码：https://github.com/vercel/ai/blob/main/content/docs/04-ai-sdk-ui/50-stream-protocol.mdx）
- 教育 RAG 系统（FastAPI + StreamingResponse + 逐块 JSON + X-Accel-Buffering 真实实现）：https://github.com/Happy-Chen-CH/Educational_RAG_System
- LangChain 聊天流式（WebSocket 备选方案）：https://github.com/pors/langchain-chat-websockets

**降级 / 重试 / 熔断**
- liteLLM Router 官方文档（fallbacks/order/cooldown/num_retries/RetryPolicy/双重重试陷阱）：https://docs.litellm.ai/docs/routing
- free-llm-gateway（OpenAI 兼容网关：fallback 链、指数退避、429 惩罚路由、cooldown、流中间错误处理）：https://github.com/MrFadiAi/free-llm-gateway
- 9router（多供应商分层 tier 自动降级）：https://github.com/decolua/9router