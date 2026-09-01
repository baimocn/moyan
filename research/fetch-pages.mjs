// 抓取关键一手页面到 research/pages/
const fs = await import('node:fs');
fs.mkdirSync(new URL('./pages/', import.meta.url), { recursive: true });
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const targets = [
  ['khanmigo.ai', 'https://www.khanmigo.ai/'],
  ['openai-khan-case', 'https://openai.com/index/khan-academy/'],
  ['sohu-rip-khanmigo', 'https://www.sohu.com/a/1018265291_100934'],
  ['khanacademy-khanmigo-about', 'https://www.khanacademy.org/khanmigo'],
  ['khanacademy-blog-ai', 'https://blog.khanacademy.org/tag/ai/'],
];
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 25000);
for (const [name, url] of targets) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml' }, signal: ac.signal, redirect: 'follow' });
    const text = await res.text();
    const clean = text
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
      .replace(/\s+/g, ' ')
      .trim();
    fs.writeFileSync(new URL(`./pages/${name}.txt`, import.meta.url), clean, 'utf8');
    console.log(`OK ${name}: status=${res.status} final=${res.url} textLen=${clean.length}`);
  } catch (e) {
    console.log(`FAIL ${name}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 800));
}
clearTimeout(timer);
console.log('\nDONE');