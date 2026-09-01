const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u, headers = { "User-Agent": "Mozilla/5.0" }) {
  try {
    const res = await fetch(u, { headers, signal: AbortSignal.timeout(20000) });
    const t = await res.text();
    return { ok: res.ok, status: res.status, text: t };
  } catch (e) { return { ok: false, status: "ERR", text: "", err: e.message }; }
}

// 1) openai-python README 中的 structured outputs 说明
console.log("########## openai-python README (structured outputs) ##########");
let r = await get("https://raw.githubusercontent.com/openai/openai-python/main/README.md");
if (r.ok) {
  const low = r.text.toLowerCase();
  let idx = low.indexOf("structured");
  let shown = 0;
  while (idx >= 0 && shown < 6) {
    console.log("---- ..." + r.text.slice(Math.max(0, idx - 60), idx + 500).replace(/\s+/g, " ").slice(0, 560));
    idx = low.indexOf("structured", idx + 10);
    shown++;
  }
} else console.log("(fail)");
await sleep(400);

// 2) Anthropic claude-docs 路径探测
console.log("\n########## anthropics/claude-docs path probes ##########");
const paths = [
  "main/llms.txt",
  "main/llms-full.txt",
  "main/en/llms.txt",
  "main/en/docs/build-with-claude/structured-outputs.md",
  "main/en/docs/build-with-claude/structured-outputs.mdx",
];
for (const p of paths) {
  const rr = await get(`https://raw.githubusercontent.com/anthropics/claude-docs/${p}`);
  console.log(`${rr.ok ? "OK  len=" + rr.text.length : "FAIL " + rr.status} :: ${p}`);
  await sleep(300);
}

// 3) quentin-mckay/AI-Quiz-Generator prompt 路径探测
console.log("\n########## quentin-mckay/AI-Quiz-Generator prompt probes ##########");
const qpaths = [
  "HEAD/src/app/page.tsx",
  "HEAD/app/page.tsx",
  "HEAD/src/lib/prompts.ts",
  "HEAD/lib/prompts.ts",
  "HEAD/src/app/api/quiz/route.ts",
  "HEAD/app/api/quiz/route.ts",
  "HEAD/src/lib/openai.ts",
];
for (const p of qpaths) {
  const rr = await get(`https://raw.githubusercontent.com/quentin-mckay/AI-Quiz-Generator/${p}`);
  console.log(`${rr.ok ? "OK  len=" + rr.text.length : "FAIL " + rr.status} :: ${p}`);
  await sleep(300);
}