// Fetch full abstracts for key papers by arXiv id
const ids = ["2410.03017", "2512.23633", "2607.22996", "2409.05511", "2309.08112", "2504.05570", "2404.06762"];
const fs = await import("node:fs");
fs.mkdirSync("research/papers", { recursive: true });
for (const id of ids) {
  const url = `http://export.arxiv.org/api/query?id_list=${id}`;
  try {
    const res = await fetch(url);
    const xml = await res.text();
    const entry = xml.split("<entry>")[1] || "";
    const title = (entry.match(/<title>(.*?)<\/title>/s) || [])[1]?.trim().replace(/\s+/g, " ");
    const summary = (entry.match(/<summary>(.*?)<\/summary>/s) || [])[1]?.trim().replace(/\s+/g, " ");
    const authors = [...entry.matchAll(/<name>(.*?)<\/name>/g)].map((m) => m[1]).join(", ");
    fs.writeFileSync(`research/papers/${id}.txt`, `TITLE: ${title}\nAUTHORS: ${authors}\nID: http://arxiv.org/abs/${id}\n\nABSTRACT:\n${summary}\n`);
    console.log(`saved ${id}: ${title?.slice(0, 80)}`);
  } catch (e) { console.log(`ERR ${id}: ${e.message}`); }
  await new Promise((r) => setTimeout(r, 2500));
}