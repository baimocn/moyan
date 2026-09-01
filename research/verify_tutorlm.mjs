// Verify TutorLM paper via Semantic Scholar + arXiv generic query
const sleeps = (ms) => new Promise((r) => setTimeout(r, ms));
try {
  const r = await fetch(
    "https://api.semanticscholar.org/graph/v1/paper/search?query=TutorLM%20tutoring%20student%20learning%20language%20models&fields=title,year,externalIds,venue&limit=5",
    { headers: { "User-Agent": "moyan-research" }, signal: AbortSignal.timeout(20000) }
  );
  const j = await r.json();
  console.log("S2 status", r.status, "total", j.total);
  for (const p of j.data || []) console.log(" ", p.year, p.venue?.slice(0, 40), p.externalIds?.ArXiv ? "arXiv:" + p.externalIds.ArXiv : "", "-", p.title);
} catch (e) { console.log("S2 ERR", e.message); }
await sleeps(4000);
try {
  const r = await fetch(
    "http://export.arxiv.org/api/query?search_query=all:%22TutorLM%22+OR+all:%22tutoring+student+learning%22&start=0&max_results=8&sortBy=relevance",
    { headers: { "User-Agent": "moyan-research" }, signal: AbortSignal.timeout(20000) }
  );
  const xml = await r.text();
  const entries = xml.split("<entry>").slice(1);
  console.log("arxiv status", r.status, "entries", entries.length);
  for (const e of entries) {
    const title = (e.match(/<title>(.*?)<\/title>/s) || [])[1]?.trim().replace(/\s+/g, " ");
    const id = (e.match(/<id>(.*?)<\/id>/s) || [])[1]?.trim();
    console.log(" ", id, "-", title?.slice(0, 110));
  }
} catch (e) { console.log("arxiv ERR", e.message); }