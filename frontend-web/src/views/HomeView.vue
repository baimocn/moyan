<script setup>
// 书架首页（网页版 v2，2026-09-03）：免登录 · 书架为主体 · 上传收为左上角子功能 · 顶部共享书库搜索
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocuments, getDocument, renameDocument } from '../api/documents.js'
import { uploadFile, getTask } from '../api/upload.js'

const router = useRouter()

const docs = ref([])
const docIdx = ref(-1)
const chapIdx = ref(-1)
const manifest = ref([])
const tip = ref('')
const last = ref(null)

// 搜索（共享书库，多词 AND）
const searchQ = ref('')
let searchTimer = null

// 上传命名弹层 + 重命名弹层共用
const dlg = ref({ show: false, mode: '', title: '', ph: '', val: '' })
let pending = null
const uploading = ref(false)
const fileInput = ref(null)

const ready = computed(() => docIdx.value >= 0 && chapIdx.value >= 0)
const searching = computed(() => searchQ.value.trim().length > 0)

onMounted(() => {
  refresh()
  try {
    const s = JSON.parse(localStorage.getItem('moyan:last') || 'null')
    last.value = s && s.doc_id && Number.isInteger(s.chapter_index) ? s : null
  } catch (e) { last.value = null }
})

// 删除已收敛到管理台（/admin，REN-01 决策）：用户层书架不提供删除入口

function displayName(d) {
  return d.display_title || d.title || cleanName(d.filename)
}
function cleanName(n) {
  return ((n || '').replace(/\.(pdf|md|docx|doc|txt|wps)$/i, '').trim() || '未命名教材')
}
function fmtWan(n) {
  n = Number(n || 0)
  return n >= 10000 ? (n / 10000).toFixed(1) + ' 万字' : n + ' 字'
}
function fmtSrc(d) {
  if (d.source === 'ocr') return '扫描件 OCR'
  if (d.format === 'md') return 'Markdown 直读'
  const m = { pdf: 'PDF', docx: 'Word', pptx: 'PPT', xlsx: '表格' }
  return m[d.format] || String(d.format || '资料').toUpperCase()
}

// ---- 搜索（300ms 防抖）----
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => refresh(), 300)
}
function clearSearch() {
  searchQ.value = ''
  clearTimeout(searchTimer)
  refresh()
}

async function refresh() {
  try {
    const d = await getDocuments(searchQ.value)
    const done = (d.documents || []).filter(x => x.status === 'done')
    const selectedId = docIdx.value >= 0 && docs.value[docIdx.value] ? docs.value[docIdx.value].doc_id : ''
    docs.value = done
    if (!selectedId) { docIdx.value = -1; manifest.value = [] }
    else {
      const idx = done.findIndex(x => x.doc_id === selectedId)
      docIdx.value = idx
      if (idx < 0) manifest.value = []
    }
  } catch (e) { /* 静默：书架拉取失败不打断 */ }
}

async function onDocPick(i) {
  if (i === docIdx.value) { manifest.value = []; docIdx.value = -1; chapIdx.value = -1; return }
  docIdx.value = i
  chapIdx.value = -1
  manifest.value = []
  const doc = docs.value[i]
  if (!doc) return
  try {
    const d = await getDocument(doc.doc_id)
    if (docIdx.value !== i) return
    manifest.value = d.document.manifest || []
  } catch (e) { tip.value = '章节读取失败' }
}

async function resumeLast() {
  const l = last.value
  if (!l) return
  if (!docs.value.length) { tip.value = '书架还没准备好，请稍候'; return }
  const i = docs.value.findIndex(d => d.doc_id === l.doc_id)
  if (i < 0) {
    tip.value = '上次教材已下架'
    last.value = null
    localStorage.removeItem('moyan:last')
    return
  }
  docIdx.value = i
  chapIdx.value = l.chapter_index
  const doc = docs.value[i]
  try {
    const d = await getDocument(doc.doc_id)
    manifest.value = d.document.manifest || []
    if (manifest.value[l.chapter_index]) go()
    else tip.value = '上次章节已变更，请手动选'
  } catch (e) { tip.value = '章节读取失败' }
}

// ---- 上传（左上角子功能）----
function choose() { fileInput.value && fileInput.value.click() }
function onFileChange(e) {
  const f = e.target && e.target.files && e.target.files[0]
  e.target.value = '' // 允许重复选同一文件
  if (f) openDlg('upload', f)
}

function openDlg(mode, obj) {
  const def = mode === 'rename'
    ? (obj.title || obj.filename || '')
    : ((obj.name || '').replace(/\.[^.]+$/, '') || '未命名教材')
  pending = obj
  dlg.value = {
    show: true, mode,
    title: mode === 'rename' ? '重命名教材' : '给教材起个名',
    ph: mode === 'rename' ? '输入新名称' : '留空用文件名',
    val: def,
  }
}
function dlgCancel() { dlg.value.show = false; pending = null }
function dlgOk() {
  const d = dlg.value
  if (!d.show) return
  const val = (d.val || '').trim()
  dlg.value.show = false
  const obj = pending
  pending = null
  if (d.mode === 'rename') {
    if (!val) return
    renameDocument(obj.doc_id, val).then(() => {
      tip.value = '已重命名 ✓'
      refresh()
    }).catch(e => { tip.value = '重命名失败：' + e.message })
  } else {
    const title = val || (obj.name || '').replace(/\.[^.]+$/, '') || '未命名教材'
    doUpload(obj, title)
  }
}

async function doUpload(file, title) {
  tip.value = '上传解析中…'
  uploading.value = true
  try {
    const r = await uploadFile(file, title)
    if (!r || !r.ok) { tip.value = '上传失败：' + ((r && r.detail) || '未知错误'); return }
    if (r.reused) {
      // 共享书库命中：不重复解析，直接打开已有书
      tip.value = '书库已有此书，已为你打开 ✓'
      await refresh()
      const i = docs.value.findIndex(d => d.doc_id === r.doc_id)
      if (i >= 0) await onDocPick(i)
      return
    }
    if (r.status === 'processing') {
      tip.value = '转换中，请稍候…'
      pollTask(r.task_id, r.doc_id)
    } else {
      tip.value = '已上架 ✓'
      await refresh()
      const i = docs.value.findIndex(d => d.doc_id === r.doc_id)
      if (i >= 0) await onDocPick(i)
    }
  } catch (e) {
    tip.value = '上传失败：' + (e.message || e)
  } finally {
    uploading.value = false
  }
}

function pollTask(taskId) {
  const tick = () => {
    getTask(taskId).then(r => {
      const t = r.task || {}
      if (t.status === 'done' || t.status === 'success') {
        tip.value = '转换完成，已上架 ✓'
        refresh()
      } else if (t.status === 'failed') {
        tip.value = '转换失败：' + (t.message || '未知错误')
      } else {
        tip.value = `转换中 ${t.progress != null ? Math.round(t.progress) + '%' : '…'}`
        setTimeout(tick, 2000)
      }
    }).catch(() => { tip.value = '任务查询失败' })
  }
  tick()
}

function go() {
  const doc = docs.value[docIdx.value]
  const chap = manifest.value[chapIdx.value]
  if (!doc || !chap) return
  router.push({ path: '/tutor', query: { doc_id: doc.doc_id, chapter_index: chap.index } })
}
</script>

<template>
  <div class="page">
    <!-- 顶栏：左=品牌+上传子功能 · 中=共享书库搜索 -->
    <div class="topbar">
      <div class="brand">
        <div class="logo">墨</div>
        <div class="bname">墨衍</div>
      </div>
      <button class="up-btn" :disabled="uploading" @click="choose">
        <span class="up-ico">＋</span>
        <span>{{ uploading ? '上传中…' : '上传教材' }}</span>
      </button>
      <div class="search">
        <span class="s-ico">⌕</span>
        <input v-model="searchQ" class="s-input" placeholder="搜索共享书库，大家传过的书都能用"
               @input="onSearchInput" @keyup.enter="refresh" />
        <span v-if="searching" class="s-clear" @click="clearSearch">×</span>
      </div>
    </div>

    <div v-if="last && last.label" class="resume" @click="resumeLast">
      <div class="ri">
        <div class="rit">继续上次</div>
        <div class="risub">上次学到这里 · {{ last.label }}</div>
      </div>
      <div class="rgo">继续 →</div>
    </div>

    <div class="sec">
      <span class="sec-t">{{ searching ? '搜索结果' : '共享书架' }}</span>
      <span class="sec-c" v-if="docs.length">{{ docs.length }} 本就绪</span>
      <span class="sec-c" v-else-if="searching">没有匹配的书籍</span>
    </div>

    <div class="list">
      <div v-for="(d, i) in docs" :key="d.doc_id" class="doc" :class="{ sel: i === docIdx }" @click="onDocPick(i)">
        <div class="doc-top">
          <span class="doc-title">{{ displayName(d) }}</span>
          <span class="pill" v-if="i === docIdx">已选</span>
          <button class="ren" @click.stop="openDlg('rename', d)">重命名</button>
        </div>
        <div class="doc-meta">
          <span>{{ d.chapter_count }} 章</span>
          <span class="sep">·</span>
          <span>{{ fmtWan(d.md_chars) }}</span>
          <span class="sep">·</span>
          <span>{{ fmtSrc(d) }}</span>
        </div>
        <div class="chaps" v-if="i === docIdx">
          <div v-for="c in manifest" :key="c.index" class="chap" :class="{ on: c.index === chapIdx }" @click.stop="chapIdx = c.index">
            <span class="chap-no">{{ c.index + 1 }}</span>
            <span class="chap-t">{{ c.title }}</span>
            <span class="chap-meta">{{ fmtWan(c.char_count) }}</span>
            <span class="tick" v-if="c.index === chapIdx">✓</span>
          </div>
          <div class="chap hint" v-if="!manifest.length">正在读取章节…</div>
        </div>
      </div>

      <!-- 空态：无搜索=书架空引导；有搜索=无结果 -->
      <div v-if="!docs.length" class="empty">
        <template v-if="searching">
          <div class="e-t">没有找到「{{ searchQ.trim() }}」相关的书</div>
          <div class="e-s">换个关键词试试，或者成为第一个上传它的人</div>
          <button class="e-btn" @click="choose">＋ 上传这本书</button>
        </template>
        <template v-else>
          <div class="e-t">书架还是空的</div>
          <div class="e-s">搜索共享书库看看大家传过的书，或上传你的第一本教材</div>
          <button class="e-btn" @click="choose">＋ 上传教材</button>
        </template>
      </div>

      <div class="doc-note">无需登录 · 上传即共享 · 同桌已就位：先思路，后对答案</div>
    </div>

    <div class="foot">
      <div v-if="tip" class="tip">{{ tip }}</div>
      <button class="start" :class="{ off: !ready }" :disabled="!ready" @click="ready && go()">开始学习</button>
    </div>

    <input ref="fileInput" type="file" style="display:none"
           accept=".pdf,.docx,.pptx,.xlsx,.md,.txt,.html,.epub,.jpg,.jpeg,.png,.bmp,.tiff"
           @change="onFileChange" />

    <div v-if="dlg.show" class="dlg-mask" @click.self="dlgCancel">
      <div class="dlg">
        <div class="dlg-t">{{ dlg.title }}</div>
        <input class="dlg-i" v-model="dlg.val" :placeholder="dlg.ph" autofocus
               @keyup.enter="dlgOk" />
        <div class="dlg-btns">
          <button class="dlg-btn" @click="dlgCancel">取消</button>
          <button class="dlg-btn ok" @click="dlgOk">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; padding: 14px 20px 16px; max-width: 640px; margin: 0 auto; width: 100%; }

/* 顶栏：品牌+上传 靠左，搜索占满剩余宽度 */
.topbar { display: flex; align-items: center; gap: 10px; padding: 2px 0 12px; }
.brand { display: flex; align-items: center; flex-shrink: 0; }
.logo { width: 34px; height: 34px; border-radius: 10px; background: var(--ink); color: #f2e6c9; font-size: 18px; font-weight: 500; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(22, 54, 40, 0.18); }
.bname { font-size: 17px; font-weight: 500; letter-spacing: 3px; color: var(--ink); margin-left: 8px; }

.up-btn { display: flex; align-items: center; flex-shrink: 0; border: 1px dashed #cbbf9e; background: #faf6ea; color: #5a503a; font-size: 13px; padding: 7px 12px; border-radius: 999px; cursor: pointer; transition: background .15s; }
.up-btn:hover { background: #f3ecd8; }
.up-btn:disabled { opacity: .55; cursor: default; }
.up-ico { font-size: 14px; margin-right: 4px; color: var(--ink-soft); }

.search { flex: 1; min-width: 0; display: flex; align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 999px; padding: 7px 13px; }
.search:focus-within { border-color: var(--ink-soft); box-shadow: 0 0 0 3px rgba(44, 110, 79, 0.10); }
.s-ico { font-size: 15px; color: #a8987a; }
.s-input { flex: 1; min-width: 0; border: 0; outline: none; background: transparent; font-size: 13px; color: var(--tx); margin-left: 7px; }
.s-input::placeholder { color: #b3a685; }
.s-clear { font-size: 16px; color: #a8987a; cursor: pointer; padding: 0 2px 0 8px; }

.resume { display: flex; align-items: center; background: linear-gradient(135deg, #163628 0%, #2c6e4f 100%); color: #f2e6c9; border-radius: 12px; padding: 12px 15px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(22, 54, 40, 0.18); cursor: pointer; }
.ri { flex: 1; display: flex; flex-direction: column; }
.rit { font-size: 14px; font-weight: 500; letter-spacing: 1px; }
.risub { font-size: 12px; color: #d8c9a0; margin-top: 3px; }
.rgo { font-size: 13px; color: #f2e6c9; padding: 5px 13px; border: 1px solid #f2e6c9; border-radius: 999px; }

.sec { display: flex; align-items: baseline; justify-content: space-between; padding: 2px 3px 10px; }
.sec-t { font-size: 16px; font-weight: 500; color: var(--tx); }
.sec-c { font-size: 12px; color: #9a8f74; }

.list { flex: 1; min-height: 0; overflow-y: auto; }
.doc { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 15px 16px; margin-bottom: 12px; transition: border-color .15s; cursor: pointer; }
.doc.sel { border-color: var(--ink-soft); box-shadow: 0 3px 10px rgba(44, 110, 79, 0.12); }
.doc-top { display: flex; align-items: center; }
.doc-title { flex: 1; font-size: 15px; font-weight: 500; color: #1f1f1f; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pill { font-size: 11px; color: #fff; background: var(--ink-soft); border-radius: 999px; padding: 3px 10px; margin-left: 9px; }
.ren { font-size: 12px; color: #a08a5a; padding: 3px 9px; border: 1px solid #ddd0b4; border-radius: 999px; margin-left: 9px; background: transparent; cursor: pointer; }
.ren:hover { background: #f6efdd; }
.doc-meta { display: flex; align-items: center; font-size: 12px; color: #94896f; margin-top: 8px; }
.sep { margin: 0 6px; color: #c9bfa5; }

.chaps { margin-top: 12px; border-top: 1px dashed #eee5d2; padding-top: 9px; }
.chap { display: flex; align-items: center; padding: 11px 9px; border-radius: 9px; margin-bottom: 4px; }
.chap.on { background: #e8f1e6; }
.chap-no { width: 24px; height: 24px; border-radius: 50%; background: #efe8d8; color: #7a6a45; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.chap.on .chap-no { background: var(--ink-soft); color: #fff; }
.chap-t { flex: 1; margin-left: 10px; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chap-meta { font-size: 11px; color: var(--tx-3); margin-left: 7px; flex-shrink: 0; }
.tick { color: var(--ink-soft); font-size: 14px; margin-left: 7px; font-weight: 500; }
.chap.hint { color: #9a8f74; font-size: 13px; justify-content: center; }

.empty { text-align: center; padding: 44px 20px 20px; }
.e-t { font-size: 16px; color: #4a4433; font-weight: 500; }
.e-s { font-size: 13px; color: #a09474; margin-top: 8px; }
.e-btn { margin-top: 18px; border: 0; background: var(--ink); color: #f2e6c9; font-size: 14px; padding: 10px 22px; border-radius: 999px; cursor: pointer; box-shadow: 0 4px 12px rgba(22, 54, 40, 0.20); }
.doc-note { text-align: center; color: #b0a487; font-size: 12px; padding: 6px 0 14px; letter-spacing: 1px; }

.foot { padding-top: 12px; }
.tip { text-align: center; font-size: 12px; color: #a08a5a; margin-bottom: 8px; }
.start { width: 100%; border: 0; background: var(--ink); color: #f2e6c9; font-size: 17px; font-weight: 500; letter-spacing: 4px; text-align: center; padding: 14px 0; border-radius: 999px; box-shadow: 0 6px 16px rgba(22, 54, 40, 0.22); cursor: pointer; }
.start.off { background: transparent; color: #a8a08a; box-shadow: none; border: 1px dashed #cfc8b6; cursor: default; }

.dlg-mask { position: fixed; inset: 0; background: rgba(20, 26, 18, 0.45); display: flex; align-items: center; justify-content: center; z-index: 999; }
.dlg { width: 340px; max-width: calc(100vw - 48px); background: var(--card); border-radius: 14px; padding: 22px 20px 16px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25); }
.dlg-t { font-size: 17px; font-weight: 500; color: var(--ink); }
.dlg-i { margin-top: 15px; background: var(--paper); border: 1px solid #ddd0b4; border-radius: 8px; padding: 10px 12px; font-size: 15px; color: var(--tx); outline: none; width: 100%; }
.dlg-i:focus { border-color: var(--ink-soft); }
.dlg-btns { display: flex; justify-content: flex-end; margin-top: 18px; }
.dlg-btn { font-size: 14px; color: var(--tx-2); padding: 7px 17px; border-radius: 999px; background: transparent; border: 0; cursor: pointer; }
.dlg-btn.ok { background: var(--ink); color: #f2e6c9; margin-left: 9px; font-weight: 500; }
</style>
