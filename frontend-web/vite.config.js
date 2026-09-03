import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 墨衍网页版（独立 Vue3 工程，2026-09-03）
// 端口 5174：避免与 uni-app H5 的 5173 冲突
// 代理 /api → 5001：开发期同源，免 CORS；生产由 nginx 同域托管
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
    },
  },
})
