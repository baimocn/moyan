// 批量 GitHub 仓库搜索（真实数据）
const queries = [
  "structured output llm",
  "in:name,description structured outputs",
  "function calling evaluation",
  "LLM grading student answers",
  "rubric LLM grading",
  "AI grade student answer",
  "quiz question generation LLM",
  "AI tutor open source",
  "adaptive learning chatbot",
  "constrained generation grammar",
  "LLM JSON schema",
  "automatic grading FREE RESPONSE LLM",
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const q of queries) {
  try {
    const url =
      "https://api.github.com/search/repositories?q=" +
      encodeURIComponent(q) +
      "&sort=stars&order=desc&per_page=8";
    const res = await fetch(url, {
      headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" },
    });
    if (!res.ok) {
      console.log(`\n### q=${q} HTTP ${res.status}`);
      await sleep(3000);
      continue;
    }
    const j = await res.json();
    console.log(`\n### q=${q} (total=${j.total_count})`);
    for (const it of j.items) {
      console.log(
        `${it.full_name} | ★${it.stargazers_count} | ${(it.description || "").slice(0, 140)}`
      );
    }
  } catch (e) {
    console.log(`\n### q=${q} ERR ${e.message}`);
  }
  await sleep(1500);
}