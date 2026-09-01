// 批量抓取关键仓库 README 到 research/readmes/
const fs = await import('node:fs');
const repos = [
  ['JushBJJ/Mr.-Ranedeer-AI-Tutor'],
  ['Li-Evan/Bloom'],
  ['ktaletsk/learn-codebase'],
  ['gpoesia/socratic-tutor'],
  ['lmonkt/ostep-socratic-tutor'],
  ['SYuan03/Skill-Anything'],
  ['nagisanzenin/engram'],
  ['open-spaced-repetition/ts-fsrs'],
  ['open-spaced-repetition/free-spaced-repetition-scheduler'],
  ['open-spaced-repetition/awesome-fsrs'],
  ['nilsreichardt/AnkiGPT'],
  ['CaviraOSS/PageLM'],
  ['beltromatti/get-it'],
  ['thiswillbeyourgithub/AnkiAIUtils'],
  ['baturyilmaz/wordpecker-app'],
  ['samiahraf/study-dost-ai'],
  ['TovTechOrg/Tov-learn'],
  ['michael-borck/study-buddy'],
  ['artcc/freelingo'],
  ['ankimcp/anki-mcp-server'],
];

fs.mkdirSync(new URL('./readmes/', import.meta.url), { recursive: true });

for (const [repo] of repos) {
  const [owner, name] = repo.split('/');
  const fname = `${owner}__${name}`;
  let got = false;
  for (const branch of ['main', 'master']) {
    for (const file of ['README.md', 'README_CN.md', 'readme.md', 'README.MD']) {
      const url = `https://raw.githubusercontent.com/${owner}/${name}/${branch}/${file}`;
      try {
        const res = await fetch(url);
        if (res.ok) {
          const text = await res.text();
          fs.writeFileSync(new URL(`./readmes/${fname}.md`, import.meta.url), text, 'utf8');
          console.log(`OK ${repo} (${branch}/${file}) ${text.length} bytes`);
          got = true;
          break;
        }
      } catch (e) { /* continue */ }
    }
    if (got) break;
  }
  if (!got) {
    // 尝试 GitHub API 拿默认分支
    try {
      const res = await fetch(`https://api.github.com/repos/${owner}/${name}`);
      if (res.ok) {
        const meta = await res.json();
        console.log(`META ${repo}: default_branch=${meta.default_branch}, desc=${(meta.description||'').slice(0,90)}`);
      } else {
        console.log(`FAIL ${repo}: api ${res.status}`);
      }
    } catch (e) { console.log(`FAIL ${repo}: ${e.message}`); }
  }
  await new Promise(r => setTimeout(r, 400));
}
console.log('\nDONE');