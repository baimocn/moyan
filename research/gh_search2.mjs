// Supplemental GitHub searches: EduChat / TutorLM / Khanmigo / Chinese education LLMs
await new Promise((r) => setTimeout(r, 45000)); // let search quota reset
const queries = [
  "EduChat education LLM",
  "tutorglm OR TutorLM tutor",
  "Khanmigo OR khan academy LLM tutor",
  "教育大模型 智能 教学",
  "socratic math tutor",
];
async function search(q) {
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=8`;
  const res = await fetch(url, { headers: { "User-Agent": "moyan-research", "Accept": "application/vnd.github+json" } });
  if (!res.ok) { console.error(`[${res.status}] ${q}`); return []; }
  const data = await res.json();
  return data.items.map((r) => ({
    full_name: r.full_name, stars: r.stargazers_count,
    description: (r.description || "").slice(0, 160), language: r.language,
    pushed_at: r.pushed_at, html_url: r.html_url,
  }));
}
const out = {};
for (const q of queries) {
  out[q] = await search(q);
  console.log(`\n===== ${q} =====`);
  for (const it of out[q]) console.log(`${it.stars}\t${it.full_name}\t${(it.description || "").slice(0, 90)}`);
  await new Promise((r) => setTimeout(r, 7000));
}
const fs = await import("node:fs");
fs.writeFileSync("research/github_search2.json", JSON.stringify(out, null, 2));