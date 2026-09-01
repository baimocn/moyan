const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u, headers = { "User-Agent": "Mozilla/5.0" }) {
  for (let i = 1; i <= 4; i++) {
    try {
      const res = await fetch(u, { headers, signal: AbortSignal.timeout(20000) });
      return { ok: res.ok, status: res.status, text: await res.text() };
    } catch (e) { if (i === 4) return { ok: false, status: "ERR", text: "" }; await sleep(2200); }
  }
}
function grep(text, kws, max = 3, width = 260) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0, count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      out.push("[kw] ..." + text.slice(Math.max(0, idx - 70), idx + width).replace(/\s+/g, " ").slice(0, 320) + "...");
      idx += kw.length; count++;
    }
  }
  return out.slice(0, 6).join("\n") || "(无关键词命中，len=" + text.length + ")";
}

console.log("########## openai-cookbook structured_outputs 文件名探测 ##########");
for (const f of [
  "01-Structured-Outputs.ipynb",
  "02-Structured-Outputs.ipynb",
  "how_to_structured_outputs.ipynb",
  "structured_outputs.ipynb",
]) {
  const rr = await get(`https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/structured_outputs/${f}`);
  console.log(`${rr.ok ? "OK len=" + rr.text.length : "FAIL " + rr.status} :: ${f}`);
  if (rr.ok) {
    console.log(grep(rr.text, ["strict", "json_schema", "additionalProperties", "response_format"]).slice(0, 1100));
    break;
  }
  await sleep(300);
}

console.log("\n########## openai-agents-python README ##########");
let r = await get("https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md");
console.log(r.ok ? grep(r.text, ["structured outputs", "output_type", "Pydantic", "function calling"]).slice(0, 1300) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## openai-python README (直接诊断) ##########");
r = await get("https://raw.githubusercontent.com/openai/openai-python/main/README.md");
console.log(r.ok ? "len=" + r.text.length + "\n" + grep(r.text, ["structured", "json_schema", "response_format"]).slice(0, 1000) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## instructor docs/fastapi 探测 ##########");
for (const p of ["docs/fastapi.md", "docs/integrations/fastapi.md", "docs/concepts/streaming.md"]) {
  const rr = await get(`https://raw.githubusercontent.com/567-labs/instructor/HEAD/${p}`);
  console.log(`${rr.ok ? "OK len=" + rr.text.length : "FAIL " + rr.status} :: ${p}`);
  if (rr.ok) console.log(rr.text.replace(/\r/g, "").slice(0, 900));
  await sleep(300);
}