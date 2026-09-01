// 抓取 ar5iv 论文 HTML 文本，定位关键段落
const fs = await import('node:fs');
fs.mkdirSync(new URL('./papers/', import.meta.url), { recursive: true });
const targets = [
  ['2412.09416', 'tutor-eval-taxonomy'],   // 8 维度
  ['2607.19371', 'scaffolding-collapse'],  // 症状与对抗策略
  ['2303.08769', 'socratic-prompts'],      // 六种苏格拉底技巧
  ['2402.09216', 'autotutor-mwptutor'],    // 守卫/状态机教学方法
];
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 30000);
for (const [id, name] of targets) {
  try {
    const res = await fetch(`https://ar5iv.labs.arxiv.org/html/${id}`, { headers: { 'User-Agent': UA }, signal: ac.signal, redirect: 'follow' });
    const html = await res.text();
    const clean = html
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<(?:h[1-6]|p|li|div|span|section|table|tr|td|th)[^>]*>/gi, '\n')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'").replace(/&nbsp;/g, ' ')
      .replace(/[ \t]+/g, ' ')
      .replace(/\n{2,}/g, '\n')
      .trim();
    fs.writeFileSync(new URL(`./papers/${name}.txt`, import.meta.url), clean, 'utf8');
    console.log(`OK ${id} ${name}: status=${res.status} chars=${clean.length}`);
  } catch (e) {
    console.log(`FAIL ${id}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 1500));
}
clearTimeout(timer);
console.log('DONE');