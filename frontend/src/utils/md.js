// 墨衍 · 轻量 Markdown → HTML（教学流子集：标题/粗斜体/行内码/代码块/列表/引用/链接）
// 先整体转义 HTML，再按行解析块级结构——输出可信 HTML 交给 mp-html/rich-text 渲染

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function inline(s) {
  let out = esc(s)
  out = out.replace(/`([^`]+)`/g, '<code class="mi">$1</code>')
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
  out = out.replace(/~~([^~]+)~~/g, '<del>$1</del>')
  out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<span class="lnk">$1</span>')
  return out
}

export function mdToHtml(src) {
  if (!src) return ''
  const lines = String(src).split('\n')
  const html = []
  let i = 0
  let para = []

  const flushPara = () => {
    if (para.length) { html.push('<p>' + inline(para.join(' ')) + '</p>'); para = [] }
  }

  while (i < lines.length) {
    const line = lines[i]

    if (/^```/.test(line)) {                       // 代码块
      flushPara()
      const buf = []
      i++
      while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++ }
      i++                                          // 跳过收尾 ```
      html.push('<pre class="cb"><code>' + esc(buf.join('\n')) + '</code></pre>')
      continue
    }

    const h = line.match(/^(#{1,6})\s+(.*)$/)      // 标题
    if (h) { flushPara(); html.push(`<h${h[1].length + 2} class="mh">` + inline(h[2]) + '</h>'); i++; continue }

    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) { flushPara(); html.push('<hr/>'); i++; continue }

    if (/^\s*>\s?/.test(line)) {                   // 引用
      flushPara()
      const buf = []
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^\s*>\s?/, '')); i++ }
      html.push('<blockquote class="mq">' + inline(buf.join(' ')) + '</blockquote>')
      continue
    }

    if (/^\s*[-*]\s+/.test(line)) {                // 无序列表
      flushPara()
      const buf = []
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) { buf.push('<li>' + inline(lines[i].replace(/^\s*[-*]\s+/, '')) + '</li>'); i++ }
      html.push('<ul>' + buf.join('') + '</ul>')
      continue
    }

    if (/^\s*\d+[.、]\s+/.test(line)) {            // 有序列表
      flushPara()
      const buf = []
      while (i < lines.length && /^\s*\d+[.、]\s+/.test(lines[i])) { buf.push('<li>' + inline(lines[i].replace(/^\s*\d+[.、]\s+/, '')) + '</li>'); i++ }
      html.push('<ol>' + buf.join('') + '</ol>')
      continue
    }

    if (line.trim() === '') { flushPara(); i++; continue }

    para.push(line.trim())
    i++
  }
  flushPara()
  return html.join('\n')
}
