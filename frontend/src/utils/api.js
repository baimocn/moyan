// 墨衍 · 前端 API 层（双前端：H5 fetch 流式 / 小程序 enableChunked，同一事件协议）
// BASE：H5 走 vite 代理（免 CORS）；小程序直连后端（开发者工具勾"不校验合法域名"）

// #ifdef H5
export const BASE = ''
// #endif
// #ifdef MP-WEIXIN
export const BASE = 'http://127.0.0.1:5001'
// #endif

function decodeAB(ab) {
  // 小程序端 ArrayBuffer → UTF-8 文本；低端机无 TextDecoder 时的兜底（仅 ASCII 完整）
  try {
    return new TextDecoder('utf-8').decode(ab)
  } catch (e) {
    const u8 = new Uint8Array(ab)
    let s = ''
    for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i])
    return decodeURIComponent(escape(s))
  }
}

function parseFrame(buf, onEvent) {
  // SSE 分帧：缓冲到 \n\n 再解析（事件可能被拆在两个 chunk）
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

export function getDocuments() {
  return new Promise((resolve, reject) => {
    uni.request({ url: BASE + '/api/documents', method: 'GET', success: r => resolve(r.data), fail: reject })
  })
}

export function getDocument(docId) {
  return new Promise((resolve, reject) => {
    uni.request({ url: `${BASE}/api/documents/${docId}`, method: 'GET', success: r => resolve(r.data), fail: reject })
  })
}

export function getStats(docId) {
  return new Promise((resolve, reject) => {
    uni.request({ url: `${BASE}/api/study/${docId}/stats`, method: 'GET', success: r => resolve(r.data), fail: reject })
  })
}

export function startTutor(docId, chapterIndex) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE + '/api/tutor/start', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { doc_id: docId, chapter_index: chapterIndex },
      success: r => resolve(r.data), fail: reject
    })
  })
}

// 教学轮：流式读取（H5=fetch reader / 小程序=enableChunked），逐事件回调 onEvent
export function streamTurn(payload, onEvent) {
  // #ifdef H5
  return fetch(BASE + '/api/tutor/turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(resp => {
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
  // #endif
  // #ifdef MP-WEIXIN
  return new Promise((resolve, reject) => {
    let buf = ''
    const task = uni.request({
      url: BASE + '/api/tutor/turn', method: 'POST', enableChunked: true, timeout: 300000,
      header: { 'Content-Type': 'application/json' },
      data: payload, success: () => resolve(), fail: reject
    })
    task.onChunkReceived(res => {
      buf = parseFrame(buf + decodeAB(res.data), onEvent)
    })
  })
  // #endif
}
