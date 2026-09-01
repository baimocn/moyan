// 解码 GitHub readme API 的 base64 content（含 mkdir）
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
const [infile, outfile] = process.argv.slice(2);
const data = JSON.parse(readFileSync(infile, 'utf-8'));
const text = Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf-8');
mkdirSync(path.dirname(outfile), { recursive: true });
writeFileSync(outfile, text);
console.log(`DECODED ${data.name} bytes=${text.length} -> ${outfile}`);