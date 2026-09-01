// 通过 GitHub API /contents 抓取指定仓库内文件（base64 解码），避免 raw 重定向
const fs = await import('node:fs');
fs.mkdirSync(new URL('./files/', import.meta.url), { recursive: true });
const targets = [
  ['JushBJJ/Mr.-Ranedeer-AI-Tutor', 'Mr_Ranedeer.txt', 'ranedeer-prompt.txt'],
  ['lmonkt/ostep-socratic-tutor', 'prompt.md', 'ostep-prompt.md'],
  ['lmonkt/ostep-socratic-tutor', 'p1.md', 'ostep-p1.md'],
  ['lmonkt/ostep-socratic-tutor', 'p2.md', 'ostep-p2.md'],
];
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 25000);
for (const [repo, path, out] of targets) {
  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${encodeURIComponent(path)}`, {
      headers: { 'User-Agent': 'moyan-research', 'Accept': 'application/vnd.github+json' },
      signal: ac.signal,
    });
    if (res.ok) {
      const data = await res.json();
      if (data.content) {
        const text = Buffer.from(data.content, 'base64').toString('utf8');
        fs.writeFileSync(new URL(`./files/${out}`, import.meta.url), text, 'utf8');
        console.log(`OK ${repo}/${path}: ${text.length} chars`);
      } else {
        console.log(`NO-CONTENT ${repo}/${path}`);
      }
    } else {
      console.log(`FAIL ${repo}/${path}: status ${res.status}`);
    }
  } catch (e) {
    console.log(`FAIL ${repo}/${path}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 600));
}
clearTimeout(timer);
console.log('DONE');