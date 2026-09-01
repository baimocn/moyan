// 1) 补抓教育类仓库 README
const readmes = [
  { repo: "quentin-mckay/AI-Quiz-Generator", kw: ["json", "schema", "quiz", "question", "answer", "option", "difficulty"] },
  { repo: "code-with-Aaryan/content-ingestion-quiz-engine", kw: ["fastapi", "quiz", "schema", "question", "json", "difficulty", "adaptive"] },
  { repo: "UFV-INGINF/JorGPT", kw: ["deepseek", "grade", "schema", "json", "rubric", "score"] },
];

async function fetchReadme(repo) {
  for (const b of ["HEAD", "main", "master"]) {
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${repo}/${b}/README.md`, {
        headers: { "User-Agent": "mo-yan-research" },
      });
      if (res.ok) return (await res.text()).replace(/\r/g, "");
    } catch {}
  }
  return null;
}

for (const t of readmes) {
  const txt = await fetchReadme(t.repo);
  console.log(`\n========== ${t.repo} ==========`);
  if (!txt) { console.log("(README 获取失败)"); continue; }
  const lines = txt.split("\n");
  const hits = [];
  lines.forEach((l, i) => {
    const low = l.toLowerCase();
    if (t.kw.some((k) => low.includes(k)) && l.trim().length > 0) hits.push(`${i + 1}: ${l.trim().slice(0, 200)}`);
  });
  console.log((hits.slice(0, 18).length ? hits.slice(0, 18).join("\n") : "(无命中) " + lines.slice(0, 15).join("\n").slice(0, 700)));
  await new Promise((r) => setTimeout(r, 400));
}

// 2) 用页面 HTML 解析 star 数（GitHub 页面不含 API 配额限制）
console.log("\n\n########## STAR 解析 ##########");
const pages = [
  "guardrails-ai/guardrails",
  "noamgat/lm-format-enforcer",
  "pydantic/pydantic",
  "RasaHQ/rasa",
  "1rgs/jsonformer",
  "prefecthq/marvin",
  "ShishirPatil/gorilla",
  "teddysum/EduChat",
];
for (const p of pages) {
  try {
    const res = await fetch(`https://github.com/${p}`, { headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" } });
    const html = await res.text();
    // GitHub 页面里的 star 数： aria-label="... users starred this repository" 或 "stargazers"
    const m1 = html.match(/aria-label="([\d,\.k]+) users? starred this repository"/i);
    const m2 = html.match(/"starCount":(\d+)/);
    const m3 = html.match(/([\d,]+)\s+stars/i);
    const star = m1 ? m1[1] : m2 ? m2[1] : m3 ? m3[1] : "?";
    console.log(`${p} -> ★${star}`);
  } catch (e) {
    console.log(`${p} -> ERR ${e.message}`);
  }
  await new Promise((r) => setTimeout(r, 1500));
}