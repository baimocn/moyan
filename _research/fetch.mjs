// 通用抓取助手 v2：node fetch.mjs <url> <outfile> [--json] [--jina]
// --json: 期望 JSON，打印紧凑摘要；--jina: 通过 r.jina.ai 转 markdown
// 内置重试（最多 4 次，指数退避）
import { writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';

const [url, outfile] = process.argv.slice(2);
const useJson = process.argv.includes('--json');
const useJina = process.argv.includes('--jina');

const headers = { 'User-Agent': 'moyan-research/1.0' };
let target = url;
if (useJina) {
  target = 'https://r.jina.ai/' + url.replace(/^https?:\/\//, '');
}

async function doFetch() {
  const res = await fetch(target, { headers, redirect: 'follow' });
  const text = await res.text();
  return { status: res.status, text, finalUrl: res.url };
}

let result = null;
for (let attempt = 1; attempt <= 4; attempt++) {
  try {
    result = await doFetch();
    break;
  } catch (e) {
    if (attempt === 4) {
      console.log(`FETCH FAILED after 4 attempts: ${e.message}`);
      process.exit(2);
    }
    console.log(`attempt ${attempt} failed (${e.message}), retrying...`);
    await new Promise((r) => setTimeout(r, 1500 * attempt));
  }
}

const { status, text } = result;
console.log(`STATUS ${status} LEN ${text.length} URL ${result.finalUrl}`);

if (outfile) {
  mkdirSync(path.dirname(outfile), { recursive: true });
}

if (useJson) {
  try {
    const data = JSON.parse(text);
    if (Array.isArray(data)) {
      console.log(`JSON ARRAY len=${data.length}`);
      data.slice(0, 20).forEach((it, i) => {
        const name = it.full_name || it.name || '?';
        const stars = it.stargazers_count ?? '';
        const desc = (it.description || '').replace(/\s+/g, ' ').slice(0, 140);
        console.log(`${i + 1}. ${name} | stars=${stars} | ${desc}`);
      });
    } else if (data && typeof data === 'object') {
      console.log(`JSON OBJECT keys=${Object.keys(data).join(',')}`);
      ['full_name', 'stargazers_count', 'description', 'html_url', 'updated_at', 'subscribers_count', 'forks_count'].forEach((k) => {
        if (data[k] !== undefined) console.log(`  ${k}: ${data[k]}`);
      });
      if (data.items) {
        console.log(`  items len=${data.items.length}`);
        data.items.slice(0, 20).forEach((it, i) => {
          const s = it.stargazers_count ?? '';
          const d = (it.description || '').replace(/\s+/g, ' ').slice(0, 130);
          console.log(`  ${i + 1}. ${it.full_name} | stars=${s} | ${d}`);
        });
      }
    }
    if (outfile) {
      writeFileSync(outfile, text);
      console.log('SAVED ' + outfile);
    }
    process.exit(0);
  } catch (e) {
    console.log('NOT JSON: ' + e.message);
  }
}

if (outfile) {
  writeFileSync(outfile, text);
  console.log('SAVED ' + outfile);
}