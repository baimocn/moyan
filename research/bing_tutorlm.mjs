// Bing search for TutorLM paper verification
const url = "https://www.bing.com/search?q=" + encodeURIComponent('"TutorLM: Tutoring Student Learning with Language Models"');
try {
  const r = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36", "Accept-Language": "en-US" },
    signal: AbortSignal.timeout(20000),
  });
  const h = await r.text();
  console.log("status", r.status, "len", h.length);
  const links = [...h.matchAll(/<h2><a href="(https?:\/\/[^"]+)"[^>]*>(.*?)<\/a><\/h2>/g)].slice(0, 8);
  for (const m of links) console.log(" -", m[2].replace(/<[^>]+>/g, "").slice(0, 110), "|", m[1].slice(0, 130));
  if (!links.length) {
    const clean = h.replace(/\s+/g, " ");
    const idx = clean.indexOf("TutorLM");
    console.log("no h2; context:", clean.slice(Math.max(0, idx - 100), idx + 300));
  }
} catch (e) { console.log("ERR", e.message); }