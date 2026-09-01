// 抓取官方文档 + 真实项目源码模板
async function getText(url, headers = { "User-Agent": "Mozilla/5.0" }) {
  const res = await fetch(url, { headers });
  if (!res.ok) return null;
  return await res.text();
}

function stripHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function grep(text, kws, max = 6, width = 260) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0;
    let count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      const start = Math.max(0, idx - 90);
      const seg = text.slice(start, idx + width).replace(/\s+/g, " ");
      out.push(`[${kw}] ...${seg}...`);
      idx += kw.length;
      count++;
      if (out.length >= max * 2) break;
    }
    if (out.length >= max * 2) break;
  }
  return out.slice(0, 12);
}

// ---- DeepSeek JSON mode ----
console.log("########## DeepSeek JSON mode ##########");
let t = await getText("https://api-docs.deepseek.com/guides/json_mode");
if (t) console.log(grep(stripHtml(t), ["json_object", "response_format", "strict", "schema", "JSON Mode"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- Anthropic structured outputs ----
console.log("\n########## Anthropic Structured Outputs ##########");
t = await getText("https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs");
if (t) console.log(grep(stripHtml(t), ["output_format", "structured outputs", "json_schema", "tools", "error", "retry"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- OpenAI Structured Outputs ----
console.log("\n########## OpenAI Structured Outputs ##########");
t = await getText("https://platform.openai.com/docs/guides/structured-outputs");
if (!t || t.length < 2000) {
  // 尝试 jina 渲染
  t = await getText("https://r.jina.ai/https://platform.openai.com/docs/guides/structured-outputs");
}
if (t) console.log(grep(stripHtml(t), ["strict", "json_schema", "additionalProperties", "function calling", "structured outputs", "tokens"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- instructor README: 供应商与 FastAPI ----
console.log("\n########## instructor README (providers/fastapi) ##########");
t = await getText("https://raw.githubusercontent.com/567-labs/instructor/HEAD/README.md");
if (t) console.log(grep(t.replace(/\r/g, ""), ["DeepSeek", "FastAPI", "Anthropic", "function calling", "streaming", "100+ different LLMs", "supported"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- outlines README: 后端/集成 ----
console.log("\n########## outlines README (backends) ##########");
t = await getText("https://raw.githubusercontent.com/dottxt-ai/outlines/HEAD/README.md");
if (t) console.log(grep(t.replace(/\r/g, ""), ["vLLM", "llama.cpp", "transformers", "FastAPI", "OpenAI", "JSON Schema", "structured", "Pydantic"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- Rasa README: dialogue management ----
console.log("\n########## Rasa README (dialogue management) ##########");
t = await getText("https://raw.githubusercontent.com/RasaHQ/rasa/HEAD/README.md");
if (t) console.log(grep(t.replace(/\r/g, ""), ["dialogue management", "stories", "rules", "forms", "conversation", "ML-policy", "state"]).join("\n"));
else console.log("(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- JorGPT 源码 (DeepSeek 评分 prompt/输出) ----
console.log("\n########## JorGPT source ##########");
const jgFiles = await getText("https://data.jsdelivr.com/v1/packages/gh/UFV-INGINF/JorGPT@main");
console.log("jsdelivr files:", jgFiles ? jgFiles.slice(0, 400) : "(fail)");
await new Promise((r) => setTimeout(r, 800));

// ---- AI-Quiz-Generator 文件列表 ----
console.log("\n########## AI-Quiz-Generator files ##########");
const qgFiles = await getText("https://data.jsdelivr.com/v1/packages/gh/quentin-mckay/AI-Quiz-Generator@main");
console.log("jsdelivr files:", qgFiles ? qgFiles.slice(0, 600) : "(fail)");