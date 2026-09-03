import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import fs from 'node:fs'
import path from 'node:path'

// H5 开发代理：/api 直连本地后端（免 CORS）；小程序直接请求 MOYAN_HOST 地址
export default defineConfig({
  plugins: [
    uni(),
    // uni-app 不支持在 pages.json/manifest.json 声明 app.json 顶层字段，
    // build 收尾时把 lazyCodeLoading 注入小程序产物 app.json（按需注入，过微信代码质量检查）
    {
      name: 'inject-lazy-code-loading',
      apply: 'build',
      closeBundle() {
        const outDir = process.env.UNI_OUTPUT_DIR
        if (!outDir) return
        const file = path.resolve(outDir, 'app.json')
        try {
          const app = JSON.parse(fs.readFileSync(file, 'utf-8'))
          if (app.lazyCodeLoading !== 'requiredComponents') {
            app.lazyCodeLoading = 'requiredComponents'
            fs.writeFileSync(file, JSON.stringify(app, null, 2) + '\n')
            console.log('[inject] app.json += lazyCodeLoading: requiredComponents')
          }
        } catch (e) {
          console.warn('[inject] skip app.json patch:', e.message)
        }
      }
    }
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:5001', changeOrigin: true }
    }
  }
})
