// 1) 抓取指定 arXiv 论文完整摘要  2) OpenAlex 检索关键研究
const ids = [
  '2607.19371', '2303.08769', '2407.17349', '2402.09216', '2412.09416',
  '2605.29582', '2508.03275', '2410.03017', '2401.03238', '2507.05795',
  '2504.06294', '2305.14999', '2406.10934', '2503.01859',
];
const url = `http://export.arxiv.org/api/query?id_list=${ids.join(',')}&max_results=30`;
const res = await fetch(url);
const xml = await res.text();
const entries = [...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)];
console.log('===== ARXIV ABSTRACTS =====');
for (const e of entries) {
  const t = (e[1].match(/<title>([\s\S]*?)<\/title>/) || [])[1];
  const id = (e[1].match(/<id>(.*?)<\/id>/) || [])[1];
  const sum = (e[1].match(/<summary>([\s\S]*?)<\/summary>/) || [])[1];
  console.log(`\n### ${t ? t.replace(/\s+/g, ' ').trim() : '?'}`);
  console.log(`ID: ${id || '?'}`);
  if (sum) console.log(`ABS: ${sum.replace(/\s+/g, ' ').trim()}`);
}

console.log('\n\n===== OPENALEX =====');
const openalexQueries = [
  'Generative AI Can Harm Learning',
  'AI tutoring outperforms active learning',
  'ChatGPT tutoring randomized experiment learning outcomes',
];
for (const q of openalexQueries) {
  try {
    const r = await fetch(`https://api.openalex.org/works?search=${encodeURIComponent(q)}&per-page=5&mailto=research@example.com`);
    const data = await r.json();
    console.log(`\n### OA: ${q} (count=${data.meta.count})`);
    for (const w of (data.results || []).slice(0, 5)) {
      console.log(`- ${w.display_name} | ${w.publication_year} | ${w.doi || 'no-doi'}`);
      console.log(`  ${(w.primary_location && w.primary_location.landing_page_url) || ''}`);
      if (w.abstract_inverted_index) {
        const pos = {};
        for (const [k, arr] of Object.entries(w.abstract_inverted_index)) for (const p of arr) pos[p] = k;
        const abs = Object.keys(pos).sort((a, b) => a - b).map(k => pos[k]).join(' ');
        console.log(`  abs: ${abs.slice(0, 400)}`);
      }
    }
  } catch (e) { console.log(`OA error: ${e.message}`); }
  await new Promise(r => setTimeout(r, 1500));
}
console.log('\nDONE');