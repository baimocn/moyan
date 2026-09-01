// Bing HTML 搜索封装：node bing-search.mjs "query" [n]
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const query = process.argv[2];
const n = parseInt(process.argv[3] || '12', 10);
if (!query) { console.log('usage: node bing-search.mjs "query" [n]'); process.exit(0); }

const res = await fetch('https://www.bing.com/search?q=' + encodeURIComponent(query) + '&count=30&mkt=en-US&ensearch=1&setlang=en-US', {
  headers: { 'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-US,en;q=0.9' },
});
const html = await res.text();
console.log('status:', res.status, 'len:', html.length);
// Bing: <li class="b_algo"> ... <h2><a href="...">Title</a></h2> ... <p>snippet</p>
const blocks = html.split('<li class="b_algo"').slice(1);
let count = 0;
for (const b of blocks) {
  if (count >= n) break;
  const hrefM = b.match(/<h2[^>]*>\s*<a[^>]+href="(https?:\/\/[^"]+)"/);
  const titleM = b.match(/<h2[^>]*>\s*<a[^>]+>(.*?)<\/a>/);
  const snipM = b.match(/<p[^>]*>([\s\S]*?)<\/p>/);
  const title = titleM ? titleM[1].replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').trim() : '(no title)';
  const snip = snipM ? snipM[1].replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim() : '';
  console.log(`${count + 1}. ${title}`);
  console.log(`   ${hrefM ? hrefM[1] : '(no url)'}`);
  if (snip) console.log(`   ${snip.slice(0, 220)}`);
  console.log();
  count++;
}
if (!count) {
  console.log('(no b_algo blocks parsed)');
  const capM = html.match(/<title>([^<]*)<\/title>/);
  console.log('page title:', capM ? capM[1] : '?');
}