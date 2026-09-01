// arXiv 检索：多个主题并行
const subjects = [
  ['socratic_tutor', 'all:"socratic" AND all:"tutor"'],
  ['socratic_llm', 'all:"socratic" AND all:"large language model"'],
  ['ai_tutor_llm', 'all:"AI tutor" AND all:"large language model"'],
  ['tutor_copilot', 'all:"Tutor CoPilot"'],
  ['spaced_llm', 'all:"spaced repetition" AND all:"language model"'],
  ['llm_education', 'all:"learning" AND all:"large language model" AND all:"tutoring"'],
];

for (const [label, query] of subjects) {
  try {
    const url = `http://export.arxiv.org/api/query?search_query=${encodeURIComponent(query)}&start=0&max_results=6&sortBy=relevance`;
    const res = await fetch(url);
    const xml = await res.text();
    console.log(`\n===== ${label}: ${query} =====`);
    const entries = [...xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)];
    for (const e of entries) {
      const t = e[1].match(/<title>([\s\S]*?)<\/title>/);
      const id = e[1].match(/<id>(.*?)<\/id>/);
      const pub = e[1].match(/<published>(\d{4}-\d{2}-\d{2})/);
      const sum = e[1].match(/<summary>([\s\S]*?)<\/summary>/);
      console.log(`- ${t ? t[1].replace(/\s+/g, ' ').trim() : '?'} (${pub ? pub[1] : '?'})`);
      console.log(`  ${id ? id[1] : '?'}`);
      if (sum) console.log(`  abs: ${sum[1].replace(/\s+/g, ' ').trim().slice(0, 180)}`);
    }
    if (!entries.length) console.log('  (no results)');
  } catch (e) { console.log(`[${label}] error: ${e.message}`); }
  await new Promise(r => setTimeout(r, 1200));
}
console.log('\nDONE');