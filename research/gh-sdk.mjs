const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u) {
  for (let i = 1; i <= 4; i++) {
    try {
      const res = await fetch(u, { headers: { "User-Agent": "Mozilla/5.0" }, signal: AbortSignal.timeout(20000) });
      return { ok: res.ok, status: res.status, text: await res.text() };
    } catch (e) { if (i === 4) return { ok: false, status: "ERR", text: "" }; await sleep(2200); }
  }
}
function grep(text, kws, max = 3, width = 220) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0, count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      out.push("[kw] ..." + text.slice(Math.max(0, idx - 60), idx + width).replace(/\s+/g, " ").slice(0, 280) + "...");
      idx += kw.length; count++;
    }
  }
  return out.slice(0, 6).join("\n") || "(无命中 len=" + text.length + ")";
}

for (const p of [
  "src/openai/types/chat/response_format_json_schema.py",
  "src/openai/types/chat/completion_create_params.py",
  "src/openai/types/responses/response_format_json_schema.py",
]) {
  console.log(`########## ${p} ##########`);
  const r = await get(`https://raw.githubusercontent.com/openai/openai-python/main/${p}`);
  if (r.ok) console.log(grep(r.text, ["strict", "json_schema", "additionalProperties"]).slice(0, 1200));
  else console.log("(fail " + r.status + ")");
  await sleep(400);
}