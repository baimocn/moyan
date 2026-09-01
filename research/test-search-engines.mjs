const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const q = 'why students dislike AI tutors chatbot teaching style';

// Bing HTML
try {
  const res = await fetch('https://www.bing.com/search?q=' + encodeURIComponent(q) + '&count=20', {
    headers: { 'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-US,en;q=0.9' },
  });
  const html = await res.text();
  console.log('BING status:', res.status, 'len:', html.length);
  const links = [...html.matchAll(/<h2><a href="(https?:\/\/[^"]+)"[^>]*>([\s\S]*?)<\/a><\/h2>/g)].slice(0, 12);
  for (const m of links) {
    const t = m[2].replace(/<[^>]+>/g, '').trim();
    console.log('  -', t.slice(0, 90), '|', m[1].slice(0, 120));
  }
  if (!links.length) console.log('  (no h2 links parsed)');
} catch (e) { console.log('BING error:', e.message); }

// DDG html endpoint
try {
  const res = await fetch('https://html.duckduckgo.com/html/?q=' + encodeURIComponent(q), {
    headers: { 'User-Agent': UA, 'Accept': 'text/html' },
  });
  const html = await res.text();
  console.log('\nDDG html status:', res.status, 'len:', html.length);
  const links = [...html.matchAll(/class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)].slice(0, 12);
  for (const m of links) {
    const t = m[2].replace(/<[^>]+>/g, '').trim();
    console.log('  -', t.slice(0, 90), '|', decodeURIComponent(m[1]).slice(0, 120));
  }
  if (!links.length) console.log('  (no results parsed)');
} catch (e) { console.log('\nDDG html error:', e.message); }