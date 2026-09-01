// arXiv API queries for LLM tutor effectiveness research
const queries = [
  '"Tutor CoPilot"',
  'all:"large language models" AND all:tutoring AND all:effectiveness',
  'all:"socratic" AND all:LLM AND all:education',
  'all:"AI tutor" AND all:"randomized"',
  'all:"TutorLM"',
  'all:"intelligent tutoring" AND all:"language models"',
];

async function q(query) {
  const url = `http://export.arxiv.org/api/query?search_query=${encodeURIComponent(query)}&start=0&max_results=6&sortBy=relevance`;
  const res = await fetch(url);
  if (!res.ok) { console.error(`ERR ${res.status} for ${query}`); return; }
  const xml = await res.text();
  // crude parsing of entry blocks
  const entries = xml.split("<entry>").slice(1);
  const out = entries.map((e) => {
    const title = (e.match(/<title>(.*?)<\/title>/s) || [])[1]?.trim().replace(/\s+/g, " ");
    const id = (e.match(/<id>(.*?)<\/id>/s) || [])[1]?.trim();
    const published = (e.match(/<published>(.*?)<\/published>/s) || [])[1]?.trim().slice(0, 10);
    const summary = (e.match(/<summary>(.*?)<\/summary>/s) || [])[1]?.trim().replace(/\s+/g, " ").slice(0, 400);
    const authors = [...e.matchAll(/<name>(.*?)<\/name>/g)].map((m) => m[1]).slice(0, 6).join(", ");
    return { title, id, published, authors, summary };
  }).filter((x) => x.title);
  console.log(`\n===== ${query} =====`);
  for (const o of out) console.log(`${o.published}\t${o.id}\t${o.title}\n   authors: ${o.authors}\n   ${o.summary?.slice(0, 250)}...`);
  return out;
}

const fs = await import("node:fs");
const all = {};
for (const query of queries) {
  all[query] = await q(query);
  await new Promise((r) => setTimeout(r, 3000));
}
fs.writeFileSync("research/arxiv_results.json", JSON.stringify(all, null, 2));