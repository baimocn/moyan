// GitHub repository search (unauthenticated, search API quota: 10 req/min)
const queries = [
  "socratic tutor",
  "AI tutor chatbot LLM",
  "LLM tutor education",
  "intelligent tutoring system",
  "socratic questioning LLM",
  "educational LLM assistant",
  "TutorLM tutoring",
  "tutoring LLM learning",
  "AI teacher chatgpt education",
  "math tutor LLM",
];

async function search(q) {
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=10`;
  const res = await fetch(url, { headers: { "User-Agent": "moyan-research", "Accept": "application/vnd.github+json" } });
  if (!res.ok) {
    console.error(`[${res.status}] query=${q}`);
    const body = await res.text();
    console.error(body.slice(0, 200));
    return [];
  }
  const data = await res.json();
  return data.items.map((r) => ({
    full_name: r.full_name,
    stars: r.stargazers_count,
    description: (r.description || "").slice(0, 160),
    language: r.language,
    pushed_at: r.pushed_at,
    html_url: r.html_url,
    topics: (r.topics || []).slice(0, 8),
  }));
}

const results = {};
for (const q of queries) {
  results[q] = await search(q);
  await new Promise((r) => setTimeout(r, 7000)); // stay under 10 req/min
}
const fs = await import("node:fs");
fs.writeFileSync("research/github_search_results.json", JSON.stringify(results, null, 2));
// compact console view
for (const [q, items] of Object.entries(results)) {
  console.log(`\n===== ${q} =====`);
  for (const it of items) console.log(`${it.stars}\t${it.full_name}\t${(it.description || "").slice(0, 90)}`);
}