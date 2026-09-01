// 从 GitHub blob 页面 HTML 提取代码行（LC{n}）为纯文本
const fs = await import('node:fs');
for (const [inp, out] of [
  ['files/ranedeer-from-blob.txt', 'files/ranedeer-prompt-extracted.txt'],
]) {
  const html = fs.readFileSync(new URL('./' + inp, import.meta.url), 'utf8');
  const lines = [];
  const re = /id="LC(\d+)"[^>]*>([\s\S]*?)<\/div><\/div><\/div>/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const n = parseInt(m[1], 10);
    let content = m[2]
      .replace(/<[^>]+>/g, '')
      .replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ');
    lines.push([n, content]);
  }
  lines.sort((a, b) => a[0] - b[0]);
  const text = lines.map(l => l[1]).join('\n');
  fs.writeFileSync(new URL('./' + out, import.meta.url), text, 'utf8');
  console.log(`${out}: ${lines.length} lines, ${text.length} chars`);
  console.log('--- head ---');
  console.log(text.slice(0, 400));
}