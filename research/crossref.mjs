// CrossRef 抓取两篇 RCT 论文元数据 + SSRN 页面
const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 25000);
for (const doi of ['10.1073/pnas.2422633122', '10.1038/s41598-025-97652-6', '10.21203/rs.3.rs-4243877/v1']) {
  try {
    const res = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, { signal: ac.signal });
    const d = await res.json();
    const m = d.message;
    console.log(`\n=== ${doi} ===`);
    console.log('title:', (m.title || ['?'])[0]);
    console.log('authors:', (m.author || []).map(a => `${a.given || ''} ${a.family || ''}`.trim()).slice(0, 8).join(', ') || '?');
    console.log('journal:', (m['container-title'] || ['?'])[0], '| year:', m.issued && m.issued['date-parts'] ? m.issued['date-parts'][0][0] : '?');
    if (m.abstract) console.log('abstract:', m.abstract.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 900));
  } catch (e) { console.log(`=== ${doi} ERROR: ${e.message}`); }
  await new Promise(r => setTimeout(r, 800));
}
clearTimeout(timer);
console.log('\nDONE');