<script setup>
// 墨衍 · 错题本（M5 Phase 11 PRAC-02）：跨文档薄弱点列表 + 发起重练
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../api/client.js'

const router = useRouter()
const rows = ref([])
const tip = ref('')
const err = ref('')
const starting = ref('')

const M_LABEL = { low: '弱', mid: '中', high: '强' }

onMounted(async () => {
  try {
    const d = await request('GET', '/api/auth/me/weaknesses')
    rows.value = d.weaknesses || []
  } catch (e) {
    err.value = '加载失败：' + (e.message || '未知错误')
  }
})

function fmtDue(iso) {
  if (!iso) return '未排程'
  const d = new Date(iso)
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const due = new Date(d); due.setHours(0, 0, 0, 0)
  const diff = Math.round((due - today) / 86400000)
  if (diff < 0) return `已到期 ${-diff} 天`
  if (diff === 0) return '今天到期'
  return `${diff} 天后`
}

async function startPractice(docId) {
  starting.value = docId
  try {
    const d = await request('POST', '/api/study/review-session/start',
                            { data: { doc_id: docId, limit: 20 } })
    if (!d.session_id) throw new Error('未取得会话')
    tip.value = ''
    router.push({ path: '/practice', query: { session_id: d.session_id } })
  } catch (e) {
    err.value = '发起重练失败：' + (e.message || '未知错误')
  } finally {
    starting.value = ''
  }
}
</script>

<template>
  <div class="mistakes">
    <div class="route">
      <RouterLink to="/" class="lnk">← 书架</RouterLink>
      <b>错题本</b>
      <RouterLink to="/report" class="lnk">学习报告 →</RouterLink>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <p v-if="!rows.length && !err" class="empty">还没有错题记录——去和 AI 同桌学一章吧。</p>
    <table v-else class="tbl">
      <thead><tr><th>知识点</th><th>教材</th><th>掌握</th><th>复习</th><th class="r">操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.doc_id + r.skill_id">
          <td>{{ r.name }}</td>
          <td class="dim">{{ r.doc_title }}</td>
          <td><span class="badge" :class="r.mastery">{{ M_LABEL[r.mastery] || r.mastery }}</span></td>
          <td>{{ fmtDue(r.due_at) }}</td>
          <td class="r">
            <button :disabled="starting === r.doc_id" @click="startPractice(r.doc_id)">
              {{ starting === r.doc_id ? '发起中…' : '重练本章' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="tip" class="tip">{{ tip }}</p>
  </div>
</template>

<style scoped>
.mistakes { max-width: 860px; margin: 0 auto; padding: 16px; }
.route { display: flex; gap: 12px; align-items: center; margin-bottom: 14px; }
.lnk { color: #163628; text-decoration: none; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl th, .tbl td { padding: 8px 10px; border-bottom: 1px solid #eee4d2; text-align: left; font-size: 14px; }
.r { text-align: right; }
.dim { color: #8a8477; }
.badge { padding: 2px 8px; border-radius: 10px; font-size: 12px; }
.badge.low { background: #fde8e8; color: #a33; }
.badge.mid { background: #fdf3d8; color: #8a6d1a; }
.badge.high { background: #e2f2e5; color: #2c6e3f; }
.err { color: #a33; }
.empty { color: #8a8477; }
.tip { color: #2c6e3f; }
button { padding: 4px 10px; }
</style>
