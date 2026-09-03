// 墨衍网页版 · 路由（免登录：任何人打开即用；/login 保留但无入口）
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'
import TutorView from './views/TutorView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: HomeView },
    { path: '/tutor', component: TutorView },
  ],
})
