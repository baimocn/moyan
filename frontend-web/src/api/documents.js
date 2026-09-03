// 墨衍网页版 · 书架/文档 API（与小程序同协议）
import { request } from './client.js'

export function getDocuments() {
  return request('GET', '/api/documents')
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
