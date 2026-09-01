// 仓库搜索助手：node search.mjs "query" 标签 [per_page]
// 用 GitHub 搜索 API 按 star 排序，输出前 N 个仓库
const q = process.argv[2];
const label = process.argv[3] || q;
const perPage = parseInt(process.argv[4] || '12', 10);

const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=${perPage}`;
const res = await fetch(url, { headers: { 'User-Agent': 'moyan-research/1.0', 'Accept': 'application/vnd.github+json' } });
const data = await res.json();
console.log(`\n===== ${label} (q=${q}) status=${res.status} total=${data.total_count} =====`);
if (data.items) {
  data.items.forEach((it, i) => {
    const s = it.stargazers_count ?? '';
    const d = (it.description || '').replace(/\s+/g, ' ').slice(0, 120);
    console.log(`${i + 1}. ${it.full_name} | ${s}★ | ${d}`);
  });
} else {
  console.log(JSON.stringify(data).slice(0, 500));
}