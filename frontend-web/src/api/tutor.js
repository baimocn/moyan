// 墨衍网页版 · 教学辅导 API：start（普通 JSON）+ turn（SSE 流式）
// SSE 解析逻辑与小程序 api.js::_streamTurnH5 同构：缓冲到 \n\n 分帧，data: JSON 逐事件回调
import { request, authHeader, clearAuth } from './client.js'

export function startTutor(docId, chapterIndex) {
  return request('POST', '/api/tutor/start', {
    data: { doc_id: docId, chapter_index: chapterIndex },
  })
}

export function streamTurn(payload, onEvent) {
  const doFetch = () => fetch('/api/tutor/turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(payload),
  })
  return doFetch().then(async resp => {
    if (resp.status === 401) {
      clearAuth()
      location.href = '/login'
      throw new Error('登录已失效')
    }
    if (!resp.ok) {
      let detail = ''
      try { detail = (await resp.json()).detail || '' } catch (e) { /* ignore */ }
      throw new Error(`HTTP ${resp.status}${detail ? ': ' + detail : ''}`)
    }
    const reader = resp.body.getReader()
    const dec = new TextDecoder()
    let buf = ''
    function pump() {
      return reader.read().then(({ done, value }) => {
        if (done) return
        buf += dec.decode(value, { stream: true })
        buf = parseFrame(buf, onEvent)
        return pump()
      })
    }
    return pump()
  })
}

function parseFrame(buf, onEvent) {
  let i
  while ((i = buf.indexOf('\n\n')) >= 0) {
    const blk = buf.slice(0, i)
    for (const line of blk.split('\n')) {
      if (!line.startsWith('data: ')) continue
      const p = line.slice(6).trim()
      if (p === '[DONE]') continue
      try { onEvent(JSON.parse(p)) } catch (e) { /* 单事件解析失败不中断 */ }
    }
    buf = buf.slice(i + 2)
  }
  return buf
}
