// 墨衍网页版 · 管理台 API（Phase 4，require_admin 保护）
import { request } from './client.js'

// 口令换管理员 token（30 天长效；非用户登录层，只是管理员开门锁）
export function adminLogin(password) {
  return request('POST', '/api/admin/login', { data: { password } })
}

export function getAdminStats() {
  return request('GET', '/api/admin/stats')
}

export function getAdminUsage(days = 30) {
  return request('GET', `/api/admin/usage?days=${days}`)
}

// ---- M5 Phase 11：向量管理 UI（VECUI-01）----
export function getVecConfig() {
  return request('GET', '/api/admin/vec/config')
}
export function setVecConfig(vecInject) {
  return request('POST', '/api/admin/vec/config', { data: { vec_inject: vecInject } })
}
export function vecBuildIndex(docId) {
  return request('POST', `/api/admin/vec/index/${docId}`)
}
export function vecIndexStatus(docId) {
  return request('GET', `/api/admin/vec/status/${docId}`)
}
export function vecSearch(docId, q, topK = 4) {
  return request('GET', `/api/admin/vec/search?doc_id=${encodeURIComponent(docId)}&q=${encodeURIComponent(q)}&top_k=${topK}`)
}
