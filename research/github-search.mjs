// GitHub 仓库搜索：教学/学习类 AI 项目调研（真实数据，含 star）
const label = process.argv[2] || 'all';
const queries = [
  ['ai_learning', 'AI learning app'],
  ['llm_teaching', 'LLM teaching'],
  ['ai_tutor', 'AI tutor'],
  ['anki_gpt', 'anki gpt'],
  ['flashcards', 'flashcards AI'],
  ['study_buddy', 'study buddy AI'],
  ['socratic', 'socratic tutor'],
  ['spaced_repet', 'spaced repetition LLM'],
  ['fsrs', 'FSRS'],
  ['interactive_learning', 'interactive learning app LLM'],
  ['question_gen', 'flashcard question generation LLM'],
  ['education_ai', 'education AI LLM app'],
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const [l, q] of queries) {
  if (label !== 'all' && l !== label) continue;
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=8`;
  let tryN = 0;
  while (tryN < 3) {
    try {
      const res = await fetch(url, { headers: { 'User-Agent': 'moyan-research' } });
      if (res.status === 403 || res.status === 429) {
        const rl = res.headers.get('x-ratelimit-remaining');
        console.log(`[rate-limit remaining=${rl}] waiting 35s for ${l}...`);
        await sleep(35000);
        tryN++; continue;
      }
      const data = await res.json();
      console.log(`\n===== ${l}: "${q}" (total=${data.total_count}) =====`);
      for (const it of data.items) {
        const desc = (it.description || '').replace(/\s+/g, ' ').trim() || '(no desc)';
        console.log(`${it.full_name} | ${it.stargazers_count}★ | ${it.language} | pushed ${(it.pushed_at||'').slice(0,10)}`);
        console.log(`    ${desc}`);
        if (it.topics && it.topics.length) console.log(`    topics: ${it.topics.join(', ')}`);
      }
      break;
    } catch (e) {
      console.log(`[${l}] error: ${e.message}`);
      tryN++;
    }
  }
  await sleep(7000);
}
console.log('\nDONE');