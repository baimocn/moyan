const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function get(u, headers = { "User-Agent": "Mozilla/5.0" }) {
  try {
    const res = await fetch(u, { headers, signal: AbortSignal.timeout(20000) });
    return { ok: res.ok, status: res.status, len: (await res.text()).length, u };
  } catch (e) {
    return { ok: false, status: "ERR", len: 0, u, err: e.message };
  }
}

const urls = [
  // Anthropic claude-docs 变体
  "https://cdn.statically.io/gh/anthropics/claude-docs/main/en/docs/build-with-claude/structured-outputs.mdx",
  "https://raw.githubusercontent.com/anthropics/claude-docs/main/en/docs/build-with-claude/structured-outputs.mdx",
  // openai-cookbook 变体
  "https://cdn.statically.io/gh/openai/openai-cookbook/main/examples/structured_outputs/how_to_structured_outputs.ipynb",
  "https://raw.githubusercontent.com/openai/openai-python/main/README.md",
  // JorGPT 源码
  "https://raw.githubusercontent.com/UFV-INGINF/JorGPT/HEAD/jorgpt_deepseek_v1.2.py",
  // AI-Quiz-Generator prompt 变体
  "https://raw.githubusercontent.com/quentin-mckay/AI-Quiz-Generator/HEAD/src/lib/prompt.ts",
  "https://raw.githubusercontent.com/quentin-mckay/AI-Quiz-Generator/HEAD/lib/prompt.ts",
  // codeload 探测
  "https://codeload.github.com/UFV-INGINF/JorGPT/tar.gz/refs/heads/main",
];
for (const u of urls) {
  const r = await get(u);
  console.log(`${r.ok ? "OK " + r.status + " len=" + r.len : "FAIL " + r.status + " " + (r.err || "")} :: ${u}`);
  await sleep(400);
}