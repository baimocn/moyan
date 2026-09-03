// 墨衍网页版 · 路由（页面流程与小程序一致：登录 → 书架 → 辅导）
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth.js'
import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import TutorView from './views/TutorView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', component: HomeView },
    { path: '/tutor', component: TutorView },
  ],
})

// 全局守卫：未登录 → /login；已登录访问 /login → /
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) return { path: '/login' }
  if (to.path === '/login' && auth.token) return { path: '/' }
  return true
})
