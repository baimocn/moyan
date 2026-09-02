// 墨衍 · 前端鉴权（双端：MP-WEIXIN 走 wx.login / H5 走 dev-login）
//
// 后端 /api/auth/wx-login 接收 code 换 openid 签发 JWT（生产）。
// 后端 /api/auth/dev-login 仅 MOYAN_AUTH_DISABLED=1 时接受（开发期）。
//
// storage key 统一 'moyan:token' / 'moyan:user_id' / 'moyan:openid'。
//
// 调用入口：App.vue onLaunch 静默调 ensureLogin()（失败仅 log，不阻塞首屏）。
// 调用出口：api.js 每次请求前调 getToken() 拼 Authorization: Bearer <token>。
// 401 重登：api.js 内部捕到 401 时调一次 ensureLogin({force: true}) 重登一次。

const KEY_TOKEN = 'moyan:token'
const KEY_USER = 'moyan:user_id'
const KEY_OPENID = 'moyan:openid'

// #ifdef H5
const BASE = ''
// #endif
// #ifdef MP-WEIXIN
const BASE = 'http://127.0.0.1:5001'
// #endif

function _setToken(token, userId, openid) {
  try {
    uni.setStorageSync(KEY_TOKEN, token || '')
    uni.setStorageSync(KEY_USER, userId || '')
    uni.setStorageSync(KEY_OPENID, openid || '')
  } catch (e) { /* storage 不可用忽略 */ }
}

export function getToken() {
  try { return uni.getStorageSync(KEY_TOKEN) || '' } catch (e) { return '' }
}

export function getUserId() {
  try { return uni.getStorageSync(KEY_USER) || '' } catch (e) { return '' }
}

export function clearToken() { _setToken('', '', '') }

function _wxLoginCode() {
  // 小程序：拿 jscode 走 /api/auth/wx-login
  // 微信开发者工具「游客模式」时 wx.login 仍可调，会返回临时 code；
  // 后端若没配真实 AppID 则返 503——按用户要求保证能跑通，所以先尝试一次：
  //   503 → 直接清空 token 退出，前端按未登录处理
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    wx.login({
      success: r => r && r.code ? resolve(r.code) : reject(new Error('wx.login 未返回 code')),
      fail: err => reject(new Error(err && err.errMsg ? err.errMsg : 'wx.login 失败')),
    })
    // #endif
    // #ifdef H5
    // H5 在浏览器里没有 wx.login,直接 reject 让外层 fallback 到 dev-login
    reject(new Error('H5 走 dev-login,不走 wx.login'))
    // #endif
  })
}

async function _postJSON(path, body) {
  // 用 uni.request 包一层（uni-app 跨端统一）
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE + path,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: body,
      success: r => {
        const d = r.data
        if (r.statusCode === 200 && d && d.token) resolve(d)
        else if (r.statusCode === 200) resolve(d)         // dev-login 等
        else reject(new Error(`HTTP ${r.statusCode}: ${(d && d.detail) || (d && d.errmsg) || '鉴权失败'}`))
      },
      fail: err => reject(new Error(err && err.errMsg ? err.errMsg : '请求失败')),
    })
  })
}

/**
 * 确保已登录：拿到 token。失败时清空已有 token 并抛错（不阻塞调用方）。
 * - MP-WEIXIN：wx.login → code → POST /api/auth/wx-login
 * - H5：直接 POST /api/auth/dev-login（仅开发期 AUTH_DISABLED=1 可用；生产 H5 登录方案待定）
 * - 已有 token 时 force=false 跳过（401 触发 force=true 重登）
 */
export async function ensureLogin({ force = false } = {}) {
  if (!force) {
    const t = getToken()
    if (t) return t
  }
  // MP 优先 wx-login；失败 fallback H5 dev-login（开发期 A/A 友好）
  // #ifdef MP-WEIXIN
  try {
    const code = await _wxLoginCode()
    const r = await _postJSON('/api/auth/wx-login', { code })
    if (r && r.token) { _setToken(r.token, r.user_id, r.openid); return r.token }
  } catch (e) {
    // wx-login 失败（游客模式/无 AppID/网络）：在开发期（AUTH_DISABLED=1）退化为 dev-login
    console.warn('[auth] wx-login 失败,试 dev-login:', e.message)
    try {
      const r2 = await _postJSON('/api/auth/dev-login', { dev_openid: 'mp_dev' })
      if (r2 && r2.token) { _setToken(r2.token, r2.user_id, r2.openid); return r2.token }
    } catch (e2) {
      console.error('[auth] dev-login 兜底失败:', e2.message)
    }
    clearToken()
    throw e
  }
  // #endif

  // #ifdef H5
  try {
    const r = await _postJSON('/api/auth/dev-login', { dev_openid: 'h5_dev' })
    if (r && r.token) { _setToken(r.token, r.user_id, r.openid); return r.token }
  } catch (e) {
    console.error('[auth] dev-login 失败:', e.message)
    clearToken()
    throw e
  }
  // #endif

  clearToken()
  throw new Error('ensureLogin 失败：未匹配任何平台分支')
}

/** 静默登录：失败仅 log 不抛。App.vue onLaunch 用。 */
export function silentLogin() {
  ensureLogin().catch(e => console.warn('[auth] 静默登录失败:', e && e.message))
}
