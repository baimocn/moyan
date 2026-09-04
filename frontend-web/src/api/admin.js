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
