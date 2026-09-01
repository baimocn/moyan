// 尝试多种方式拿到 Ranedeer 的 prompt 文件内容
const fs = await import('node:fs');
fs.mkdirSync(new URL('./files/', import.meta.url), { recursive: true });
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const attempts = [
  ['blob', 'https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor/blob/main/Mr_Ranedeer.txt', { 'User-Agent': UA, 'Accept': 'text/html' }],
  ['jina', 'https://r.jina.ai/https://raw.githubusercontent.com/JushBJJ/Mr.-Ranedeer-AI-Tutor/main/Mr_Ranedeer.txt', { 'User-Agent': UA, 'Accept': 'text/plain' }],
  ['jsdelivr', 'https://cdn.jsdelivr.net/gh/JushBJJ/Mr.-Ranedeer-AI-Tutor@main/Mr_Ranedeer.txt', { 'User-Agent': UA }],
];
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 27000);
for (const [name, url, headers] of attempts) {
  try {
    const res = await fetch(url, { headers, signal: ac.signal, redirect: 'follow' });
    const text = await res.text();
    console.log(`${name}: status=${res.status} len=${text.length} starts=${JSON.stringify(text.slice(0, 80))}`);
    if (res.ok && text.length > 2000) {
      // blob 页面：prompt 文本在 <textarea> 或 js blob 里；直接存原始
      fs.writeFileSync(new URL(`./files/ranedeer-from-${name}.txt`, import.meta.url), text, 'utf8');
      console.log(`${name}: SAVED`);
      break;
    }
  } catch (e) {
    console.log(`${name}: ${e.name === 'AbortError' ? 'timeout' : e.message}`);
  }
  await new Promise(r => setTimeout(r, 1500));
}
clearTimeout(timer);
console.log('DONE');