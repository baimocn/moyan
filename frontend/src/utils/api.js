// 墨衍 · 前端 API 层（双前端：H5 fetch 流式 / 小程序 enableChunked，同一事件协议）
// BASE：H5 走 vite 代理（免 CORS）；小程序直连后端（开发者工具勾"不校验合法域名"）
//
// 鉴权（2026-09-02 部署前置）：所有请求自动带 Authorization: Bearer <token>。
// 401 自动重登一次（force=true），再 401 → 抛错给上层。
// token 来自 utils/auth.js 的 storage（App.vue onLaunch 已静默登录）。

// #ifdef H5
export const BASE = ''
// #endif
// #ifdef MP-WEIXIN
export const BASE = 'https://moyan.baimo7715.top'
// #endif

import { ensureLogin, getToken } from './auth.js'

function _authHeader() {
  const t = getToken()
  return t ? { Authorization: 'Bearer ' + t } : {}
}

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

// ---- 公共 uni.request 包装（401 自动重登一次）----

function _uniReq(method, url, { data, header, responseType } = {}) {
  return new Promise((resolve, reject) => {
    const opts = {
      url: BASE + url,
      method,
      header: { 'Content-Type': 'application/json', ..._authHeader(), ...(header || {}) },
      success: r => {
        if (r.statusCode === 401) {
          // 401 → 重登一次 + 重发
          ensureLogin({ force: true })
            .then(() => _uniReq(method, url, { data, header, responseType }))
            .then(resolve, reject)
          return
        }
        resolve(r)
      },
      fail: err => reject(new Error(err && err.errMsg ? err.errMsg : '请求失败')),
    }
    if (data !== undefined) opts.data = data
    if (responseType) opts.responseType = responseType
    uni.request(opts)
  })
}

function _extract(r) { return r && r.data }

// ---- API ----

export function getDocuments() {
  return _uniReq('GET', '/api/documents').then(_extract)
}

export function getDocument(docId) {
  return _uniReq('GET', `/api/documents/${docId}`).then(_extract)
}

// 书籍自定义命名（PATCH /api/documents/{id}）
export function renameDocument(docId, title) {
  return _uniReq('PATCH', `/api/documents/${docId}`, { data: { title } }).then(_extract)
}

// 上传资料（multipart）。小程序走 wx.uploadFile；H5 走 fetch + FormData
export function uploadFile(filePath, displayName) {
  return new Promise((resolve, reject) => {
    const _doUpload = () => {
      // #ifdef MP-WEIXIN
      wx.uploadFile({
        url: BASE + '/api/upload',
        filePath,
        name: 'file',
        header: _authHeader(),                       // ← Bearer
        formData: { display_name: displayName || '' },
        success: r => {
          try {
            const body = JSON.parse(r.data)
            // 401 兜底：wx.uploadFile 不像 uni.request 有 success 钩子
            if (r.statusCode === 401) {
              ensureLogin({ force: true })
                .then(() => uploadFile(filePath, displayName))
                .then(resolve, reject)
              return
            }
            resolve(body)
          } catch (e) { reject(new Error('响应解析失败: ' + r.data)) }
        },
        fail: reject,
      })
      // #endif
      // #ifdef H5
      const fd = new FormData()
      fd.append('file', filePath)
      if (displayName) fd.append('display_name', displayName)
      fetch(BASE + '/api/upload', {
        method: 'POST',
        body: fd,
        headers: _authHeader(),                       // ← Bearer（fetch 不会自动设 Content-Type）
      })
        .then(async r => {
          if (r.status === 401) {
            await ensureLogin({ force: true })
            return uploadFile(filePath, displayName)
          }
          return r.json()
        })
        .then(resolve, reject)
      // #endif
    }
    _doUpload()
  })
}

// 后台任务进度（扫描件/大文件异步解析）
export function getTask(taskId) {
  return _uniReq('GET', `/api/tasks/${taskId}`).then(_extract)
}

export function getStats(docId) {
  return _uniReq('GET', `/api/study/${docId}/stats`).then(_extract)
}

export function startTutor(docId, chapterIndex) {
  return _uniReq('POST', '/api/tutor/start', { data: { doc_id: docId, chapter_index: chapterIndex } }).then(_extract)
}

// 教学轮：流式读取（H5=fetch reader / 小程序=wx.request enableChunked），逐事件回调 onEvent
export function streamTurn(payload, onEvent) {
  // #ifdef H5
  return _streamTurnH5(payload, onEvent)
  // #endif
  // #ifdef MP-WEIXIN
  return _streamTurnMP(payload, onEvent)
  // #endif
}

function _streamTurnH5(payload, onEvent) {
  const doFetch = () => fetch(BASE + '/api/tutor/turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ..._authHeader() },
    body: JSON.stringify(payload),
  })
  return doFetch().then(async resp => {
    if (resp.status === 401) {
      await ensureLogin({ force: true })
      return _streamTurnH5(payload, onEvent)
    }
    if (!resp.ok) {
      // 业务错误（如 503 引擎未就绪）→ 解析 JSON 抛出
      let detail = ''
      try { detail = (await resp.json()).detail || '' } catch (e) {}
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

function _streamTurnMP(payload, onEvent) {
  // 微信小程序 wx.request + enableChunked 的已知必要参数：
  // - enableHttp2:false —— 真机上 chunked 与 HTTP/2 不兼容会收不到分块（需强制 HTTP/1.1）
  // - responseType:'arraybuffer' —— onChunkReceived 回调 res.data 是 ArrayBuffer
  // - timeout 300000 覆盖多模态/长文生成
  return new Promise((resolve, reject) => {
    let buf = ''
    let retried = false
    const doReq = () => {
      const task = wx.request({
        url: BASE + '/api/tutor/turn', method: 'POST',
        enableChunked: true, enableHttp2: false, responseType: 'arraybuffer', timeout: 300000,
        header: { 'Content-Type': 'application/json', ..._authHeader() },
        data: payload,
        success: res => {
            if (res.statusCode === 401 && !retried) {
              retried = true
              ensureLogin({ force: true }).then(() => doReq(), reject)
              return
            }
            try {
              const s = res && res.data != null ? String(res.data) : ''
              if (s.indexOf('data:') === 0) parseFrame(s, onEvent)
            } catch (e) { /* 兜底解析失败不致命 */ }
            resolve()
          },
          fail: err => reject(new Error(err && err.errMsg ? err.errMsg : '请求失败')),
        })
        task.onChunkReceived(res => {
          buf = parseFrame(buf + decodeAB(res.data), onEvent)
        })
    }
    doReq()
  })
}
