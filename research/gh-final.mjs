const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u, headers = { "User-Agent": "Mozilla/5.0" }) {
  for (let i = 1; i <= 4; i++) {
    try {
      const res = await fetch(u, { headers, signal: AbortSignal.timeout(20000) });
      return { ok: res.ok, status: res.status, text: await res.text() };
    } catch (e) {
      if (i === 4) return { ok: false, status: "ERR", text: "", err: e.message };
      await sleep(2500);
    }
  }
}
function grep(text, kws, max = 4, width = 300) {
  const low = text.toLowerCase();
  const out = [];
  for (const kw of kws) {
    let idx = 0, count = 0;
    while (count < max) {
      idx = low.indexOf(kw, idx);
      if (idx < 0) break;
      out.push("[kw] ..." + text.slice(Math.max(0, idx - 80), idx + width).replace(/\s+/g, " ").slice(0, 380) + "...");
      idx += kw.length; count++;
    }
  }
  return out.slice(0, 8).join("\n");
}

console.log("########## openai-python README (structured outputs) ##########");
let r = await get("https://raw.githubusercontent.com/openai/openai-python/main/README.md");
console.log(r.ok ? grep(r.text, ["structured outputs", "response_format", "json_schema", "strict"]).slice(0, 1800) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## Coding-Tutor README (workflow 细节) ##########");
r = await get("https://raw.githubusercontent.com/iwangjian/Coding-Tutor/main/README.md");
if (r.ok) {
  const lines = r.text.replace(/\r/g, "").split("\n");
  console.log(lines.slice(8, 26).join("\n").slice(0, 1800));
} else console.log("(fail " + r.status + ")");
await sleep(400);

console.log("\n########## Rasa README (dialogue management) ##########");
r = await get("https://raw.githubusercontent.com/RasaHQ/rasa/main/README.md");
console.log(r.ok ? grep(r.text, ["dialogue management", "stories", "rules", "forms", "conversation-driven"]).slice(0, 1500) : "(fail " + r.status + ")");
await sleep(400);

console.log("\n########## anthropics/claude-docs 更多路径 ##########");
for (const p of [
  "main/en/docs/build-with-claude/structured-outputs.mdx",
  "main/docs/build-with-claude/structured-outputs.mdx",
  "main/en/docs/structured-outputs.mdx",
  "main/en/docs/build-with-claude/structured-outputs/index.mdx",
]) {
  const rr = await get(`https://raw.githubusercontent.com/anthropics/claude-docs/${p}`);
  console.log(`${rr.ok ? "OK len=" + rr.text.length : "FAIL " + rr.status} :: ${p}`);
  await sleep(300);
}

console.log("\n########## Eedi org repos (search API) ##########");
const sres = await fetch(
  "https://api.github.com/search/repositories?q=org:Eedi&sort=stars&order=desc&per_page=5",
  { headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" } }
);
if (sres.ok) {
  const j = await sres.json();
  for (const it of j.items) console.log(`${it.full_name} | ★${it.stargazers_count} | ${(it.description || "").slice(0, 120)}`);
} else console.log("search HTTP " + sres.status);