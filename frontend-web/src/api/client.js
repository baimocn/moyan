// 墨衍网页版 · fetch 封装：Bearer(可选) + X-Device-Id(免登录设备身份) + 401 静默降级重试
const BASE = ''

export function getToken() {
  return localStorage.getItem('moyan:web:token') || ''
}

export function setAuth(token) {
  localStorage.setItem('moyan:web:token', token)
}

export function clearAuth() {
  localStorage.removeItem('moyan:web:token')
  localStorage.removeItem('moyan:web:user')
}

// 免登录设备身份：首次访问生成 uuid，之后所有请求带上（后端映射 web_<did>，进度按浏览器隔离）
export function getDeviceId() {
  let d = localStorage.getItem('moyan:web:device')
  if (!d) {
    d = (crypto.randomUUID)
      ? crypto.randomUUID()
      : 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 12)
    localStorage.setItem('moyan:web:device', d)
  }
  return d
}

export function authHeader() {
  const t = getToken()
  return t ? { Authorization: 'Bearer ' + t } : {}
}

// 统一 JSON 请求；非 2xx 抛 Error(message)。
// 401（token 过期）：清凭证后原样重试一次（匿名身份继续可用），不再强制跳登录页。
export async function request(method, url, { data, raw } = {}, _retried = false) {
  const resp = await fetch(BASE + url, {
    method,
    headers: { 'Content-Type': 'application/json', 'X-Device-Id': getDeviceId(), ...authHeader() },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  })
  if (resp.status === 401) {
    if (!_retried && getToken()) {
      clearAuth()
      return request(method, url, { data, raw }, true)
    }
    throw new Error('请重新登录后再试')
  }
  if (!resp.ok) {
    let detail = ''
    try { detail = (await resp.json()).detail || '' } catch (e) { /* 非 JSON 错误体 */ }
    const err = new Error(detail || `HTTP ${resp.status}`)
    err.status = resp.status
    throw err
  }
  if (raw) return resp
  return resp.json()
}
