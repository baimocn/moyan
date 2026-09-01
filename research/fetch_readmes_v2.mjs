// Fetch READMEs via jsDelivr CDN (works without GitHub API quota), fallback to github HTML
const repos = [
  ["CAHLR", "OATutor"],
  ["Khan", "tutoring-accuracy-dataset"],
  ["eth-lre", "mathtutorbench"],
  ["umass-ml4ed", "tutorbot-dpo"],
  ["zijinz456", "OpenTutor"],
  ["GeminiLight", "gen-mentor"],
  ["gpoesia", "socratic-tutor"],
  ["Li-Evan", "Bloom"],
  ["HugeCatLab", "ChatTutor"],
  ["sanjarbek404", "Socratic-Math-Tutor"],
  ["koofree", "research-aied"],
  ["ECNU-ICALK", "EduChat"],
  ["HKUDS", "DeepTutor"],
  ["Open-TutorAi", "open-tutor-ai-CE"],
  ["JushBJJ", "Mr.-Ranedeer-AI-Tutor"], // re-fetch full (already have)
  ["lmonkt", "ostep-socratic-tutor"],
  ["towardsai", "ai-tutor-app"],
];
const fs = await import("node:fs");
fs.mkdirSync("research/readmes", { recursive: true });
const UA = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36" };

for (const [owner, repo] of repos) {
  const safe = `${owner}__${repo}`.replace(/[^A-Za-z0-9._-]/g, "_");
  let done = false;
  // 1) jsDelivr
  for (const file of ["README.md", "readme.md", "Readme.md", "README.MD"]) {
    try {
      const r = await fetch(`https://cdn.jsdelivr.net/gh/${owner}/${repo}@HEAD/${file}`, { headers: UA, signal: AbortSignal.timeout(15000) });
      if (r.ok) {
        const t = await r.text();
        if (!t.startsWith("<!DOCTYPE") && !t.startsWith("<html")) {
          fs.writeFileSync(`research/readmes/${safe}.md`, t);
          console.log(`OK  jsdelivr ${owner}/${repo} ${t.length}`);
          done = true;
          break;
        }
      }
    } catch (e) { /* next */ }
  }
  // 2) github HTML article
  if (!done) {
    try {
      const r = await fetch(`https://github.com/${owner}/${repo}`, { headers: UA, signal: AbortSignal.timeout(20000) });
      const html = await r.text();
      const m = html.match(/<article[^>]*markdown-body[\s\S]*?<\/article>/);
      if (m) {
        fs.writeFileSync(`research/readmes/${safe}.html`, m[0]);
        console.log(`OK  github-html ${owner}/${repo} ${m[0].length}`);
        done = true;
      } else {
        console.log(`MISS ${owner}/${repo} (no article)`);
      }
    } catch (e) { console.log(`MISS ${owner}/${repo}: ${e.message}`); }
  }
  if (!done) console.log(`MISS ${owner}/${repo}`);
  await new Promise((r) => setTimeout(r, 1000));
}
console.log("DONE");