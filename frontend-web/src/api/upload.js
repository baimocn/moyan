// 墨衍网页版 · 上传 + 任务轮询 API
import { request, authHeader, getDeviceId } from './client.js'

export async function uploadFile(file, displayName) {
  const fd = new FormData()
  fd.append('file', file)
  if (displayName) fd.append('display_name', displayName)
  const resp = await fetch('/api/upload', {
    method: 'POST',
    body: fd,
    headers: { 'X-Device-Id': getDeviceId(), ...authHeader() }, // fetch + FormData 不手动设 Content-Type（浏览器自动带 boundary）
  })
  if (!resp.ok) {
    let detail = ''
    try { detail = (await resp.json()).detail || '' } catch (e) { /* ignore */ }
    const err = new Error(detail || `HTTP ${resp.status}`)
    err.status = resp.status
    throw err
  }
  return resp.json()
}

export function getTask(taskId) {
  return request('GET', `/api/tasks/${taskId}`)
}

export function hasToken() {
  return !!getToken()
}
