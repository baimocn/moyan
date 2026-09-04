// 墨衍网页版 · 路由（免登录：任何人打开即用；/login 保留但无入口）
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import TutorView from './views/TutorView.vue'
import AdminView from './views/AdminView.vue'
import { getDeviceId } from './api/client'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: HomeView },
    { path: '/tutor', component: TutorView },
    { path: '/admin', component: AdminView },
  ],
})

// 浏览量埋点（STATS-02）：每次路由切换上报一笔，sendBeacon 失败静默（fire-and-forget）
router.afterEach((to) => {
  try {
    const payload = JSON.stringify({
      source: 'web',
      page: (to.name && String(to.name)) || to.path || 'home',
      device_id: getDeviceId(),
    })
    const url = '/api/metrics/pv'
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, new Blob([payload], { type: 'application/json' }))
    } else {
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
      }).catch(() => {})
    }
  } catch (e) { /* 统计绝不影响主流程 */ }
})
