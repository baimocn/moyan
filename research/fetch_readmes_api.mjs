// Fetch READMEs via GitHub API readme endpoint (raw accept) with timeouts
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
];
const fs = await import("node:fs");
fs.mkdirSync("research/readmes", { recursive: true });
let used = 0;
for (const [owner, repo] of repos) {
  const url = `https://api.github.com/repos/${owner}/${repo}/readme`;
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "moyan-research", "Accept": "application/vnd.github.raw+json" },
      signal: AbortSignal.timeout(20000),
    });
    if (res.ok) {
      const text = await res.text();
      const safe = `${owner}__${repo}`.replace(/[^A-Za-z0-9._-]/g, "_");
      fs.writeFileSync(`research/readmes/${safe}.md`, text);
      console.log(`OK ${owner}/${repo} ${text.length} bytes`);
    } else {
      console.log(`HTTP ${res.status} ${owner}/${repo}`);
    }
    used++;
  } catch (e) {
    console.log(`ERR ${owner}/${repo}: ${e.message}`);
  }
  await new Promise((r) => setTimeout(r, 1200));
}
console.log(`\nDONE, api calls used: ${used}`);