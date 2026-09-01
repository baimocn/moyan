const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function getText(url, headers = { "User-Agent": "Mozilla/5.0" }) {
  try {
    const res = await fetch(url, { headers, signal: AbortSignal.timeout(25000) });
    if (!res.ok) return null;
    return await res.text();
  } catch { return null; }
}
function grep(text, kws, max = 5, width = 300) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0, count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      const start = Math.max(0, idx - 100);
      out.push(`[${kw}] ...${text.slice(start, idx + width).replace(/\s+/g, " ")}...`);
      idx += kw.length; count++;
    }
  }
  return out.slice(0, 10).join("\n");
}

console.log("########## Anthropic claude-docs (structured-outputs.mdx) ##########");
let t = await getText("https://raw.githubusercontent.com/anthropics/claude-docs/main/en/docs/build-with-claude/structured-outputs.mdx");
console.log(t ? grep(t, ["output_format", "json_schema", "structured outputs", "retry", "additionalProperties", "function"]).slice(0, 2500) : "(fail)");
await sleep(600);

console.log("\n########## OpenAI cookbook structured outputs ##########");
t = await getText("https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/structured_outputs/how_to_structured_outputs.ipynb");
console.log(t ? grep(t, ["strict", "json_schema", "additionalProperties", "response_format", "function"]).slice(0, 2200) : "(fail)");
await sleep(600);

console.log("\n########## JorGPT jsdelivr file list ##########");
t = await getText("https://data.jsdelivr.com/v1/packages/gh/UFV-INGINF/JorGPT@main");
const files = t ? JSON.parse(t).files.map((f) => f.name).join(", ") : "(fail)";
console.log(files);

console.log("\n########## AI-Quiz-Generator jsdelivr file list ##########");
t = await getText("https://data.jsdelivr.com/v1/packages/gh/quentin-mckay/AI-Quiz-Generator@main");
const files2 = t ? JSON.parse(t).files.map((f) => f.name).join(", ") : "(fail)";
console.log(files2);