// Bing 搜索助手：node bing.mjs "query" [n]
// 打印前 n 条结果标题+URL
const q = process.argv[2];
const n = parseInt(process.argv[3] || '10', 10);
const res = await fetch('https://www.bing.com/search?q=' + encodeURIComponent(q), {
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
  }
});
const t = await res.text();
console.log(`STATUS ${res.status} LEN ${t.length}`);
// b_algo 结构
const items = [...t.matchAll(/<li class="b_algo"[\s\S]*?<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a><\/h2>/g)];
items.slice(0, Math.max(n, items.length)).forEach((x, i) => {
  const title = x[2].replace(/<[^>]+>/g, '').trim();
  console.log(`${i + 1}. ${title} | ${x[1]}`);
});
if (items.length === 0) {
  // 备选：提取所有 https 链接
  const links = [...t.matchAll(/href="(https?:\/\/[^"]+)"/g)].map((m) => m[1]);
  [...new Set(links)].slice(0, 15).forEach((l, i) => console.log(`${i + 1}. ${l}`));
}