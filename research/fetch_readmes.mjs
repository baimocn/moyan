// Fetch READMEs of candidate repos via raw.githubusercontent.com (no API quota)
const repos = [
  ["JushBJJ", "Mr.-Ranedeer-AI-Tutor"],
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
];
const fs = await import("node:fs");
fs.mkdirSync("research/readmes", { recursive: true });
for (const [owner, repo] of repos) {
  const candidates = ["README.md", "README.MD", "readme.md", "Readme.md"];
  let got = false;
  for (const file of candidates) {
    const url = `https://raw.githubusercontent.com/${owner}/${repo}/HEAD/${file}`;
    try {
      const res = await fetch(url, { headers: { "User-Agent": "moyan-research" } });
      if (res.ok) {
        const text = await res.text();
        const safe = `${owner}__${repo}`.replace(/[^A-Za-z0-9._-]/g, "_");
        fs.writeFileSync(`research/readmes/${safe}.md`, text);
        console.log(`OK ${owner}/${repo} (${file}) ${text.length} bytes`);
        got = true;
        break;
      }
    } catch (e) { /* keep trying */ }
  }
  if (!got) console.log(`MISS ${owner}/${repo}`);
  await new Promise((r) => setTimeout(r, 1500));
}