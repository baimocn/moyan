const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u, headers = { "User-Agent": "Mozilla/5.0" }) {
  for (let i = 1; i <= 4; i++) {
    try {
      const res = await fetch(u, { headers, signal: AbortSignal.timeout(20000) });
      return { ok: res.ok, status: res.status, text: await res.text() };
    } catch (e) { if (i === 4) return { ok: false, status: "ERR", text: "" }; await sleep(2500); }
  }
}
function grep(text, kws, max = 3, width = 280) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0, count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      out.push("[kw] ..." + text.slice(Math.max(0, idx - 70), idx + width).replace(/\s+/g, " ").slice(0, 340) + "...");
      idx += kw.length; count++;
    }
  }
  return out.slice(0, 6).join("\n");
}

console.log("########## anthropic SDK README ##########");
let r = await get("https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md");
console.log(r.ok ? grep(r.text, ["structured outputs", "output_format", "json_schema"]).slice(0, 1400) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## anthropic.com/news/structured-outputs ##########");
r = await get("https://www.anthropic.com/news/structured-outputs");
console.log(r.ok ? grep(r.text, ["structured outputs", "json_schema", "guarantee", "constraint"]).slice(0, 1200) || "OK len=" + r.text.length : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## help.openai.com structured outputs FAQ ##########");
r = await get("https://help.openai.com/en/articles/10555781-structured-outputs-faq-and-guide");
console.log(r.ok ? grep(r.text, ["json_schema", "strict", "additionalProperties", "guarantee"]).slice(0, 1400) || "OK len=" + r.text.length : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## instructor README (DeepSeek/Anthropic/FastAPI/retry) ##########");
r = await get("https://raw.githubusercontent.com/567-labs/instructor/HEAD/README.md");
console.log(r.ok ? grep(r.text, ["deepseek", "anthropic", "fastapi", "retry", "function calling"]).slice(0, 1600) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## Eedi/qatd-2k-anonymous-clone README ##########");
r = await get("https://raw.githubusercontent.com/Eedi/qatd-2k-anonymous-clone/main/README.md");
if (r.ok) console.log(r.text.replace(/\r/g, "").slice(0, 1500));
else console.log("(fail " + r.status + ")");
await sleep(400);

console.log("\n########## search: 1.1 Math Primers ##########");
const sres = await fetch("https://api.github.com/search/repositories?q=1.1-math-primers&per_page=5", {
  headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" },
});
if (sres.ok) {
  const j = await sres.json();
  for (const it of j.items) console.log(`${it.full_name} | ★${it.stargazers_count} | ${(it.description || "").slice(0, 110)}`);
} else console.log("search HTTP " + sres.status);