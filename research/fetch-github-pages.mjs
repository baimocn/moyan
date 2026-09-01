// 直接抓取 github.com 仓库页 HTML，提取 README 正文(markdown-body)，保存为 md
const fs = await import('node:fs');
fs.mkdirSync(new URL('./readmes/', import.meta.url), { recursive: true });
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const repos = process.argv.slice(2);
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 30000);
for (const repo of repos) {
  const [owner, name] = repo.split('/');
  const fname = `${owner}__${name}`;
  try {
    const res = await fetch(`https://github.com/${owner}/${name}`, {
      headers: { 'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-US,en;q=0.9' },
      signal: ac.signal, redirect: 'follow',
    });
    const html = await res.text();
    // README 正文: <article class="markdown-body ...">...</article>
    let m = html.match(/<article class="markdown-body[^"]*"[\s\S]*?<div data-target="readme-toc.content">([\s\S]*?)<\/div>\s*<\/article>/i);
    if (!m) m = html.match(/<article class="markdown-body[^"]*"[^>]*>([\s\S]*?)<\/article>/i);
    if (m) {
      const body = m[1]
        .replace(/<script[\s\S]*?<\/script>/gi, ' ')
        .replace(/<style[\s\S]*?<\/style>/gi, ' ')
        .replace(/<[^>]+>/g, ' ')
        .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>')
        .replace(/[ \t]+/g, ' ')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
      fs.writeFileSync(new URL(`./readmes/${fname}.md`, import.meta.url), body, 'utf8');
      console.log(`OK ${repo}: status=${res.status} bodyLen=${body.length}`);
    } else {
      console.log(`NO-ARTICLE ${repo}: status=${res.status} htmlLen=${html.length}`);
    }
  } catch (e) {
    console.log(`FAIL ${repo}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 1000));
}
clearTimeout(timer);
console.log('\nDONE');