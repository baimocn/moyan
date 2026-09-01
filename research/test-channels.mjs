// 测试替代联网通道：DuckDuckGo lite / arXiv / Semantic Scholar
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36';

// 1. DuckDuckGo lite
try {
  const res = await fetch('https://lite.duckduckgo.com/lite/?q=' + encodeURIComponent('socratic method AI tutor large language models'), {
    headers: { 'User-Agent': UA, 'Accept': 'text/html' },
  });
  const html = await res.text();
  console.log('DDG lite status:', res.status, 'len:', html.length);
  const links = [...html.matchAll(/href="(https?:\/\/[^"]+)"[^>]*>(.{0,120}?)<\/a>/g)].slice(0, 10);
  for (const m of links) console.log('  -', m[1].slice(0, 110), '|', m[2].replace(/<[^>]+>/g, '').slice(0, 80));
} catch (e) { console.log('DDG lite error:', e.message); }

// 2. arXiv API
try {
  const res = await fetch('http://export.arxiv.org/api/query?search_query=all:%22socratic%22+AND+all:%22tutor%22&start=0&max_results=5&sortBy=relevance');
  const xml = await res.text();
  console.log('\narXiv status:', res.status, 'len:', xml.length);
  const titles = [...xml.matchAll(/<entry>[\s\S]*?<title>([\s\S]*?)<\/title>[\s\S]*?<id>(.*?)<\/id>/g)].slice(0, 5);
  for (const t of titles) console.log('  -', t[1].replace(/\s+/g, ' ').slice(0, 100), '|', t[2]);
} catch (e) { console.log('\narXiv error:', e.message); }

// 3. Semantic Scholar
try {
  const res = await fetch('https://api.semanticscholar.org/graph/v1/paper/search?query=socratic%20tutoring%20large%20language%20models&fields=title,year,url,abstract&limit=5');
  const data = await res.json();
  console.log('\nS2 status:', res.status, 'total:', data.total);
  for (const p of data.data || []) console.log('  -', p.title, '|', p.year, '|', p.url);
} catch (e) { console.log('\nS2 error:', e.message); }