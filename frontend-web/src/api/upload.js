// 墨衍网页版 · 上传 + 任务轮询 API
import { request, authHeader, getToken } from './client.js'

export async function uploadFile(file, displayName) {
  const fd = new FormData()
  fd.append('file', file)
  if (displayName) fd.append('display_name', displayName)
  const resp = await fetch('/api/upload', {
    method: 'POST',
    body: fd,
    headers: authHeader(), // fetch + FormData 不手动设 Content-Type（浏览器自动带 boundary）
  })
  if (resp.status === 401) throw new Error('登录已失效，请重新登录')
  if (!resp.ok) {
    let detail = ''
    try { detail = (await resp.json()).detail || '' } catch (e) { /* ignore */ }
    throw new Error(detail || `HTTP ${resp.status}`)
  }
  return resp.json()
}

export function getTask(taskId) {
  return request('GET', `/api/tasks/${taskId}`)
}

export function hasToken() {
  return !!getToken()
}
