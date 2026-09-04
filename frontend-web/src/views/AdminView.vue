<template>
  <div class="admin">
    <!-- 口令门 -->
    <div v-if="phase === 'gate'" class="gate card">
      <h1>墨衍 · 管理台</h1>
      <p class="sub">此页仅限站长：输入管理口令进入（口令由服务端 <code>MOYAN_ADMIN_WEB_PASSWORD</code> 配置）。</p>
      <input v-model="pwd" type="password" placeholder="管理口令" @keyup.enter="enter" />
      <button class="ok" :disabled="busy || !pwd" @click="enter">{{ busy ? '验证中…' : '进入' }}</button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <!-- 看板 -->
    <template v-else-if="phase === 'panel'">
      <header class="bar">
        <span class="brand">墨衍 · 管理台</span>
        <button class="out" @click="logout">退出</button>
      </header>

      <p v-if="err" class="err wide">{{ err }}</p>
      <p v-if="tip" class="tip wide">{{ tip }}</p>

      <section v-if="stats" class="grid">
        <div class="card stat"><b>{{ n(stats.pv.today) }}</b><span>今日浏览 PV</span></div>
        <div class="card stat"><b>{{ n(stats.pv.total) }}</b><span>累计浏览 PV</span></div>
        <div class="card stat"><b>{{ n(stats.uv.today) }}</b><span>今日访客 UV</span></div>
        <div class="card stat"><b>{{ n(stats.uv.total) }}</b><span>累计访客 UV</span></div>
        <div class="card stat"><b>{{ n(stats.tokens.today) }}</b><span>今日 tokens</span></div>
        <div class="card stat"><b>{{ n(stats.tokens.total) }}</b><span>累计 tokens（{{ n(stats.tokens.calls) }} 次调用）</span></div>
        <div class="card stat"><b>{{ n(stats.teaching.turns) }}</b><span>教学轮次</span></div>
        <div class="card stat"><b>{{ n(stats.teaching.docs_done) }}</b><span>上架教材</span></div>
      </section>
      <p v-if="stats" class="src">来源分布：{{ srcLine }}</p>

      <section v-if="usage" class="card tbl">
        <h2>AI 用量台账（近 {{ usage.days }} 天）</h2>
        <p class="sub">总计：{{ n(usage.total.total_tokens) }} tokens · {{ n(usage.total.calls) }} 次调用</p>
        <table v-if="usage.daily.length">
          <thead><tr><th>日期</th><th>用途</th><th>模型</th><th>输入</th><th>输出</th><th>合计</th><th>次数</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in usage.daily" :key="i">
              <td>{{ r.date }}</td><td>{{ r.endpoint }}</td><td class="mono">{{ r.model }}</td>
              <td>{{ n(r.prompt_tokens) }}</td><td>{{ n(r.completion_tokens) }}</td>
              <td><b>{{ n(r.total_tokens) }}</b></td><td>{{ n(r.calls) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="sub">近 {{ usage.days }} 天暂无 AI 调用。</p>
      </section>

      <section class="card tbl">
        <h2>文档管理（{{ docs.length }}）</h2>
        <p class="sub">删除将联级清除该书全部学习记录，无法恢复。</p>
        <table v-if="docs.length">
          <thead><tr><th>教材</th><th>状态</th><th class="right">操作</th></tr></thead>
          <tbody>
            <tr v-for="d in docs" :key="d.doc_id">
              <td>{{ title(d) }} <span class="mono dim">{{ d.doc_id }}</span></td>
              <td><span class="badge" :class="d.status">{{ d.status }}</span></td>
              <td class="right"><button class="del" @click="removeDoc(d)">删除</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="sub">暂无文档。</p>
      </section>
    </template>

    <p v-else class="sub">正在校验身份…</p>
  </div>
</template>

<script setup>
// 墨衍 · /admin 管理台（Phase 4）：口令门 → 数据看板 + 用量台账 + 文档管理
// 网页端免登录原则不变：口令只在本页使用，换到的 token 存本地供管理接口用
import { ref, computed, onMounted } from 'vue'
import { adminLogin, getAdminStats, getAdminUsage } from '../api/admin.js'
import { getDocuments, deleteDocument } from '../api/documents.js'
import { me } from '../api/auth.js'
import { getToken, setAuth, clearAuth } from '../api/client.js'

const phase = ref('checking') // checking | gate | panel
const pwd = ref('')
const err = ref('')
const tip = ref('')
const busy = ref(false)
const stats = ref(null)
const usage = ref(null)
const docs = ref([])

onMounted(async () => {
  if (!getToken()) { phase.value = 'gate'; return }
  try {
    const r = await me()
    if (r.role === 'admin') { phase.value = 'panel'; await loadAll() }
    else phase.value = 'gate'
  } catch (e) { phase.value = 'gate' }
})

async function enter() {
  if (busy.value || !pwd.value) return
  busy.value = true; err.value = ''
  try {
    const r = await adminLogin(pwd.value)
    setAuth(r.token)
    phase.value = 'panel'
    await loadAll()
  } catch (e) { err.value = e.message || '验证失败' }
  busy.value = false
}

async function loadAll() {
  err.value = ''
  try {
    const [s, u, d] = await Promise.all([getAdminStats(), getAdminUsage(30), getDocuments()])
    stats.value = s; usage.value = u; docs.value = Array.isArray(d) ? d : (d.items || [])
  } catch (e) {
    if (e.status === 401 || e.status === 403) { logout() }
    else err.value = '数据加载失败：' + (e.message || '未知错误')
  }
}

async function removeDoc(d) {
  if (!window.confirm(`确定删除《${title(d)}》？\n该书全部教学会话与学习记录将一并删除，无法恢复。`)) return
  try {
    await deleteDocument(d.doc_id)
    tip.value = `已删除《${title(d)}》✓`
    docs.value = docs.value.filter(x => x.doc_id !== d.doc_id)
    if (stats.value) getAdminStats().then(s => { stats.value = s }).catch(() => {})
  } catch (e) { tip.value = ''; err.value = '删除失败：' + (e.message || '未知错误') }
}

function logout() {
  clearAuth()
  phase.value = 'gate'; pwd.value = ''
  stats.value = null; usage.value = null; docs.value = []
}

const srcLine = computed(() => {
  const s = stats.value && stats.value.sources || {}
  const name = { web: '网页', mp: '小程序' }
  return Object.entries(s).map(([k, v]) => `${name[k] || k} ${v}`).join(' · ') || '暂无'
})

function n(x) { return (x ?? 0).toLocaleString('en-US') }
function title(d) { return d.display_title || d.title || d.filename || d.doc_id }
</script>

<style scoped>
.admin { max-width: 960px; margin: 0 auto; padding: 24px 16px 60px; }
.card { background: #fffdf8; border: 1px solid #e5ddc8; border-radius: 12px; padding: 16px; }
.gate { max-width: 380px; margin: 12vh auto 0; text-align: center; }
.gate h1 { color: #163628; font-size: 20px; margin: 4px 0 8px; }
.gate input { width: 100%; box-sizing: border-box; padding: 10px 12px; margin: 12px 0;
  border: 1px solid #d8cfb8; border-radius: 8px; background: #fff; font-size: 14px; }
.gate .ok { width: 100%; padding: 10px 0; border: 0; border-radius: 8px; cursor: pointer;
  background: #163628; color: #f6f2e8; font-size: 14px; }
.gate .ok:disabled { opacity: .55; cursor: default; }
.sub { color: #8a836f; font-size: 12px; margin: 6px 0; }
.err { color: #b03a2e; font-size: 13px; }
.err.wide, .tip.wide { margin: 0 0 12px; }
.tip { color: #163628; font-size: 13px; }
.bar { display: flex; align-items: center; justify-content: space-between;
  background: #163628; color: #f6f2e8; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; }
.brand { font-size: 16px; font-weight: 600; }
.out { border: 1px solid rgba(246, 242, 232, .4); background: transparent; color: #f6f2e8;
  border-radius: 8px; padding: 5px 14px; cursor: pointer; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.stat { display: flex; flex-direction: column; gap: 4px; }
.stat b { color: #163628; font-size: 22px; }
.stat span { color: #8a836f; font-size: 12px; }
.src { color: #8a836f; font-size: 12px; margin: 10px 2px 16px; }
.tbl { margin-top: 14px; }
.tbl h2 { color: #163628; font-size: 15px; margin: 0 0 4px; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid #efe9d8; }
th { color: #8a836f; font-weight: 500; font-size: 12px; }
.right { text-align: right; }
.mono { font-family: ui-monospace, Consolas, monospace; font-size: 12px; }
.dim { color: #b3ac97; margin-left: 6px; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 99px; background: #efe9d8; color: #6b6450; }
.badge.done { background: #163628; color: #f6f2e8; }
.badge.failed, .badge.rejected { background: #f5e0dd; color: #b03a2e; }
.del { border: 1px solid #d9a79c; color: #b03a2e; background: transparent;
  border-radius: 6px; padding: 3px 10px; cursor: pointer; font-size: 12px; }
.del:hover { background: #b03a2e; color: #fff; }
@media (max-width: 640px) { .grid { grid-template-columns: repeat(2, 1fr); } }
</style>
