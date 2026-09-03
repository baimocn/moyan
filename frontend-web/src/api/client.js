// 墨衍网页版 · fetch 封装：Bearer 头 + 401 清凭证跳登录
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

export function authHeader() {
  const t = getToken()
  return t ? { Authorization: 'Bearer ' + t } : {}
}

// 统一 JSON 请求；非 2xx 抛 Error(message)。401 → 清凭证跳 /login
export async function request(method, url, { data, raw } = {}) {
  const resp = await fetch(BASE + url, {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  })
  if (resp.status === 401) {
    clearAuth()
    if (!location.pathname.startsWith('/login')) location.href = '/login'
    throw new Error('登录已失效，请重新登录')
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
