// 通过 GitHub API 的 /readme 端点抓取 README（base64），带超时
const fs = await import('node:fs');
const repos = [
  'JushBJJ/Mr.-Ranedeer-AI-Tutor',
  'Li-Evan/Bloom',
  'ktaletsk/learn-codebase',
  'gpoesia/socratic-tutor',
  'lmonkt/ostep-socratic-tutor',
  'SYuan03/Skill-Anything',
  'nagisanzenin/engram',
  'open-spaced-repetition/ts-fsrs',
  'open-spaced-repetition/free-spaced-repetition-scheduler',
  'open-spaced-repetition/awesome-fsrs',
  'nilsreichardt/AnkiGPT',
  'CaviraOSS/PageLM',
  'beltromatti/get-it',
  'thiswillbeyourgithub/AnkiAIUtils',
  'baturyilmaz/wordpecker-app',
  'samiahraf/study-dost-ai',
  'TovTechOrg/Tov-learn',
  'michael-borck/study-buddy',
  'artcc/freelingo',
  'ankimcp/anki-mcp-server',
];
fs.mkdirSync(new URL('./readmes/', import.meta.url), { recursive: true });
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 20000);
for (const repo of repos) {
  const [owner, name] = repo.split('/');
  const fname = `${owner}__${name}`;
  try {
    const res = await fetch(`https://api.github.com/repos/${owner}/${name}/readme`, {
      headers: { 'User-Agent': 'moyan-research', 'Accept': 'application/vnd.github.raw+json' },
      signal: ac.signal,
    });
    if (res.ok) {
      const text = await res.text();
      if (text && !text.includes('Not Found')) {
        fs.writeFileSync(new URL(`./readmes/${fname}.md`, import.meta.url), text, 'utf8');
        console.log(`OK ${repo}: ${text.length} bytes`);
        continue;
      }
    }
    console.log(`FAIL ${repo}: status ${res.status}`);
  } catch (e) {
    console.log(`FAIL ${repo}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 300));
}
clearTimeout(timer);
console.log('\nDONE');
console.log('FILES:');
for (const f of fs.readdirSync(new URL('./readmes/', import.meta.url))) console.log('  ' + f);