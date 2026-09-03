// 墨衍网页版 · 认证 store（token / user 持久化 localStorage）
import { defineStore } from 'pinia'
import { clearAuth, getToken, setAuth } from '../api/client.js'
import * as authApi from '../api/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: JSON.parse(localStorage.getItem('moyan:web:user') || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
  },
  actions: {
    async login(email, password) {
      const r = await authApi.login(email, password)
      this._accept(r)
      return r
    },
    async register(email, password, nickName) {
      const r = await authApi.register(email, password, nickName)
      this._accept(r)
      return r
    },
    _accept(r) {
      this.token = r.token
      setAuth(r.token)
      // user_id 即唯一标识；昵称后端暂无回读接口，先本地记
      this.user = { user_id: r.user_id, is_new: r.is_new }
      localStorage.setItem('moyan:web:user', JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      clearAuth()
    },
  },
})
