// 用 raw.githubusercontent 抓 README，按关键词提取关键事实（不消耗 API 配额）
const targets = [
  { repo: "567-labs/instructor", kw: ["fastapi", "retry", "reask", "validation", "pydantic", "schema"] },
  { repo: "dottxt-ai/outlines", kw: ["json", "schema", "fsm", "regex", "fastapi", "constrained"] },
  { repo: "guidance-ai/guidance", kw: ["json", "grammar", "regex", "fncall", "tool"] },
  { repo: "noamgat/lm-format-enforcer", kw: ["json", "schema", "regex", "fsm", "beam"] },
  { repo: "guardrails-ai/guardrails", kw: ["validator", "retry", "json", "schema", "reask"] },
  { repo: "langchain-ai/langgraph", kw: ["state", "graph", "agent", "node", "edge"] },
  { repo: "iwangjian/Coding-Tutor", kw: ["verifier", "dialogue", "tutor", "feedback", "state"] },
  { repo: "umass-ml4ed/dialogue-kt", kw: ["knowledge", "tracing", "dialogue", "student", "kt"] },
  { repo: "deshwalmahesh/PHUDGE", kw: ["rubric", "rubrics", "grade", "judge", "reference"] },
  { repo: "tanchongmin/strictjson", kw: ["retry", "json", "repair", "schema"] },
  { repo: "quentin-mckay/AI-Quiz-Generator", kw: ["json", "schema", "quiz", "question", "answer", "option"] },
  { repo: "code-with-Aaryan/content-ingestion-quiz-engine", kw: ["fastapi", "quiz", "schema", "question", "json"] },
  { repo: "UFV-INGINF/JorGPT", kw: ["deepseek", "grade", "schema", "json", "rubric"] },
];

async function fetchReadme(repo) {
  const branches = ["HEAD", "main", "master"];
  for (const b of branches) {
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${repo}/${b}/README.md`, {
        headers: { "User-Agent": "mo-yan-research" },
      });
      if (res.ok) return (await res.text()).replace(/\r/g, "");
    } catch {}
  }
  return null;
}

for (const t of targets) {
  const txt = await fetchReadme(t.repo);
  console.log(`\n========== ${t.repo} ==========`);
  if (!txt) {
    console.log("(README 获取失败)");
    continue;
  }
  const lines = txt.split("\n");
  const hits = [];
  lines.forEach((l, i) => {
    const low = l.toLowerCase();
    if (t.kw.some((k) => low.includes(k)) && l.trim().length > 0) {
      hits.push(`${i + 1}: ${l.trim().slice(0, 200)}`);
    }
  });
  // 打印前 15 个命中；若 README 很短则打印全部
  const slice = hits.slice(0, 15);
  if (slice.length === 0) {
    console.log(`(README ${txt.length} chars, 无关键词命中)`);
    console.log(lines.slice(0, 10).join("\n").slice(0, 600));
  } else {
    console.log(slice.join("\n"));
  }
  await new Promise((r) => setTimeout(r, 500));
}