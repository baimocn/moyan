<script setup>
// 墨衍 · 重练流（M5 Phase 11 PRAC-02）：current → 自评 → answer（FSRS 重排）
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '../api/client.js'

const route = useRoute()
const router = useRouter()
const sid = route.query.session_id || ''

const prog = ref({ done: 0, remaining: 0 })
const nextItem = ref(null)
const finished = ref(false)
const revealed = ref(false)
const err = ref('')
const busy = ref(false)

const RATING = [
  { key: 'again', label: '没记住', cls: 'again' },
  { key: 'hard', label: '勉强', cls: 'hard' },
  { key: 'good', label: '会了', cls: 'good' },
  { key: 'easy', label: '轻松', cls: 'easy' },
]

function apply(d) {
  prog.value = d.progress || { done: 0, remaining: 0 }
  nextItem.value = d.next
  finished.value = !!d.finished
  revealed.value = false
}

async function loadCurrent() {
  const d = await request('GET', `/api/study/review-session/${sid}/current`)
  apply(d.current || {})
}

async function answer(rating) {
  if (!nextItem.value || busy.value) return
  busy.value = true
  try {
    const d = await request('POST', `/api/study/review-session/${sid}/answer`,
                            { data: { skill_id: nextItem.value.skill_id, rating } })
    apply({ progress: d.progress, next: d.next, finished: d.finished })
  } catch (e) {
    err.value = e.message || '提交失败'
  } finally {
    busy.value = false
  }
}

const remainingText = computed(() =>
  `${prog.value.done || 0} 已完成 · ${prog.value.remaining || 0} 待重练`)

onMounted(async () => {
  if (!sid) { err.value = '缺少会话参数（请从错题本发起）'; return }
  try { await loadCurrent() } catch (e) { err.value = e.message || '加载失败' }
})
</script>

<template>
  <div class="practice">
    <div class="route">
      <RouterLink to="/mistakes" class="lnk">← 错题本</RouterLink>
      <b>重练</b>
      <span class="dim">{{ remainingText }}</span>
    </div>
    <p v-if="err" class="err">{{ err }}</p>

    <div v-if="finished" class="card fin">🎉 本轮重练完成，FSRS 已按你的自评重排复习。</div>

    <div v-else-if="nextItem" class="card">
      <p class="kp">{{ nextItem.name }}</p>
      <p class="chap">章节：{{ nextItem.chapter_title || '-' }} · 上次判定原因：{{ nextItem.reason || '-' }}</p>
      <div v-if="revealed" class="snippet">{{ nextItem.snippet || '（本章教材无该点片段，凭理解自评即可）' }}</div>
      <button v-else class="reveal" @click="revealed = true">翻看教材片段</button>

      <div v-if="revealed" class="ratings">
        <button v-for="r in RATING" :key="r.key" :class="r.cls"
                :disabled="busy" @click="answer(r.key)">{{ r.label }}</button>
      </div>
    </div>

    <div v-else-if="!err" class="card fin">没有待重练项——全部完成 ✅</div>

    <p class="dim">自评即复习：again 留队重讲，其余出队并按 FSRS 重排下次到期时间。</p>
  </div>
</template>

<style scoped>
.practice { max-width: 720px; margin: 0 auto; padding: 16px; }
.route { display: flex; gap: 12px; align-items: center; margin-bottom: 14px; }
.lnk { color: #163628; text-decoration: none; }
.dim { color: #8a8477; font-size: 13px; margin-left: auto; }
.card { background: #fffdf8; border: 1px solid #eee4d2; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
.kp { font-size: 18px; font-weight: 600; }
.chap { color: #8a8477; font-size: 13px; }
.snippet { white-space: pre-wrap; background: #faf6ec; border-radius: 8px; padding: 12px; line-height: 1.7; margin: 10px 0; }
.reveal { margin: 10px 0; }
.ratings { display: flex; gap: 10px; margin-top: 12px; }
.ratings button { flex: 1; padding: 8px 0; }
.ratings .again { background: #fde8e8; }
.ratings .hard { background: #fdf3d8; }
.ratings .good { background: #e2f2e5; }
.ratings .easy { background: #dceef5; }
.fin { color: #2c6e3f; }
.err { color: #a33; }
button { padding: 6px 12px; border: 1px solid #d8cdb4; border-radius: 8px; background: #fff; cursor: pointer; }
</style>
