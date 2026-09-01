// 提取 ipynb 中的 markdown + code 单元格文本: node ipynb2md.mjs <in.json> <out.md>
import { readFileSync, writeFileSync } from 'node:fs';
const [infile, outfile] = process.argv.slice(2);
const nb = JSON.parse(readFileSync(infile, 'utf-8'));
const parts = [];
for (const cell of nb.cells || []) {
  const src = (cell.source || []).join('');
  if (cell.cell_type === 'markdown') {
    parts.push(src + '\n');
  } else if (cell.cell_type === 'code') {
    parts.push('```python\n' + src + '\n```\n');
  }
}
const text = parts.join('\n\n');
writeFileSync(outfile, text);
console.log(`EXTRACTED cells=${(nb.cells||[]).length} bytes=${text.length} -> ${outfile}`);