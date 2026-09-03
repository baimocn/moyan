// 墨衍网页版 · 书架/文档 API（与小程序同协议）
import { request } from './client.js'

// q：共享书库搜索（多词 AND，大小写不敏感）；空 = 全量
export function getDocuments(q) {
  const query = (q || '').trim()
  return request('GET', '/api/documents' + (query ? `?q=${encodeURIComponent(query)}` : ''))
}

export function getDocument(docId) {
  return request('GET', `/api/documents/${docId}`)
}

export function renameDocument(docId, title) {
  return request('PATCH', `/api/documents/${docId}`, { data: { title } })
}

export function getStats(docId) {
  return request('GET', `/api/study/${docId}/stats`)
}
