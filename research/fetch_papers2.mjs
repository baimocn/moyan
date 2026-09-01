// Fetch remaining paper abstracts (Khan dataset, TutorLM, tutorbot)
const ids = ["2503.06424"]; // tutorbot DPO paper
const searches = [
  ['Khan', 'ti:"LLM Based Math Tutoring"'],
  ['TutorLM', 'ti:"TutorLM" OR all:"TutorLM tutoring"'],
  ['Khanmigo', 'all:"Khanmigo"'],
];
const fs = await import("node:fs");
async function byId(id) {
  const res = await fetch(`http://export.arxiv.org/api/query?id_list=${id}`);
  const xml = await res.text();
  const entry = xml.split("<entry>")[1] || "";
  const title = (entry.match(/<title>(.*?)<\/title>/s) || [])[1]?.trim().replace(/\s+/g, " ");
  const summary = (entry.match(/<summary>(.*?)<\/summary>/s) || [])[1]?.trim().replace(/\s+/g, " ");
  const authors = [...entry.matchAll(/<name>(.*?)<\/name>/g)].map((m) => m[1]).join(", ");
  const published = (entry.match(/<published>(.*?)<\/published>/s) || [])[1]?.trim().slice(0, 10);
  fs.writeFileSync(`research/papers/${id}.txt`, `TITLE: ${title}\nAUTHORS: ${authors}\nPUBLISHED: ${published}\nID: http://arxiv.org/abs/${id}\n\nABSTRACT:\n${summary}\n`);
  console.log(`saved ${id}: ${title?.slice(0, 90)}`);
}
async function search(label, query) {
  const url = `http://export.arxiv.org/api/query?search_query=${encodeURIComponent(query)}&start=0&max_results=4&sortBy=relevance`;
  const res = await fetch(url);
  const xml = await res.text();
  const entries = xml.split("<entry>").slice(1);
  console.log(`\n===== ${label} =====`);
  for (const e of entries) {
    const title = (e.match(/<title>(.*?)<\/title>/s) || [])[1]?.trim().replace(/\s+/g, " ");
    const id = (e.match(/<id>(.*?)<\/id>/s) || [])[1]?.trim();
    const published = (e.match(/<published>(.*?)<\/published>/s) || [])[1]?.trim().slice(0, 10);
    console.log(`${published}\t${id}\t${title?.slice(0, 100)}`);
  }
  await new Promise((r) => setTimeout(r, 3000));
}
await byId(ids[0]);
for (const [label, q] of searches) await search(label, q);
console.log("\nDONE");