// 第二批搜索：放慢节奏避开限流
const queries = [
  "quiz question generation LLM",
  "AI tutor open source",
  "adaptive learning chatbot LLM",
  "constrained generation grammar JSON",
  "LLM JSON schema validation",
  "automatic grading free response LLM",
  "in:name,description tutor dialogue",
  "in:name,description quiz generator AI",
  "in:name,description question generation",
  "in:name,description exam grading",
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const q of queries) {
  try {
    const url =
      "https://api.github.com/search/repositories?q=" +
      encodeURIComponent(q) +
      "&sort=stars&order=desc&per_page=6";
    const res = await fetch(url, {
      headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" },
    });
    if (!res.ok) {
      console.log(`\n### q=${q} HTTP ${res.status}`);
      await sleep(9000);
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
  await sleep(8500);
}