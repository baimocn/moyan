// 墨衍网页版 · 认证 API（register / login / me）
import { request } from './client.js'

export function register(email, password, nickName) {
  return request('POST', '/api/auth/register', {
    data: { email, password, nick_name: nickName || '' },
  })
}

export function login(email, password) {
  return request('POST', '/api/auth/login', { data: { email, password } })
}

export function me() {
  return request('GET', '/api/auth/me')
}
