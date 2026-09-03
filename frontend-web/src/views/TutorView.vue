<script setup>
// 同桌辅导页 —— 与小程序 pages/tutor/tutor 等价
// SSE 事件流：reasoning-delta(仅思考态) / text-delta / meta / judge / question / question-batch / report / error
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { startTutor, streamTurn } from '../api/tutor.js'
import { getStats } from '../api/documents.js'
import { mdToHtml } from '../utils/md.js'

const route = useRoute()

let uidSeed = 1
const TYPE_NAME = { single_choice: '单选题', multiple_choice: '多选题', fill_blank: '填空题', short_answer: '简答题' }

const docId = String(route.query.doc_id || '')
const chapterIndex = Number(route.query.chapter_index || 0)

const sid = ref('')
const chapterTitle = ref('')
const msgs = ref([])
const draft = ref('')
const streaming = ref(false)
const planKps = ref([])
const kpCur = ref(-1)
const kpDone = ref(0)
const thinkSec = ref(0)
const gotText = ref(false)
const msgsEl = ref(null)

let thinkTimer = null
let mdTimer = null

const canSend = computed(() => !streaming.value && !!sid.value && draft.value.trim())

onMounted(() => {
  startTutor(docId, chapterIndex).then(d => {
    if (!d.ok) { pushSys(d.detail || '开局失败', true); return }
    sid.value = d.session_id
    chapterTitle.value = d.chapter || '教学'
    planKps.value = (d.plan || []).map(k => k.name)
    document.title = (d.chapter || '教学').slice(0, 12) + ' · 墨衍'
    // 记住最近进度（与小程序同键 moyan:last），供首页"继续上次"
    try {
      localStorage.setItem('moyan:last', JSON.stringify({
        doc_id: docId,
        chapter_index: chapterIndex,
        label: (d.chapter || '本章'),
        ts: Date.now(),
      }))
    } catch (e) { /* 存储失败非致命 */ }
    const plan = planKps.value
    pushSys(plan.length ? `本次共 ${plan.length} 站：${plan.map((k, i) => `${i + 1}.${k}`).join('  ')}` : '开始学习')
    pushMate(d.greeting || '（开场白缺失）')
    refreshStats()
  }).catch(e => pushSys('开局请求失败：' + e, true))
  thinkTimer = setInterval(() => {
    if (streaming.value && !gotText.value) thinkSec.value++
  }, 1000)
})

onBeforeUnmount(() => {
  if (thinkTimer) clearInterval(thinkTimer)
  if (mdTimer) clearTimeout(mdTimer)
})

function newMsg(kind, who) {
  return { uid: 'm' + uidSeed++, kind, who, text: '', html: '',
           question: null, locked: false, thinking: false, err: false, note: false,
           jtag: '', jt: '', jcls: '', score: '', jnext: '', jreview: '', qIndex: 0, qtype: '' }
}
function pushSys(text, err, note) {
  const m = newMsg('sys'); m.text = text || ''; m.err = !!err
  m.note = !!note || m.text.length > 36
  msgs.value.push(m); scroll(); return m
}
// 档案消息就地更新：已存在"档案："开头的 sys 则替换，否则新增
function setArchiveSys(text) {
  const idx = msgs.value.findIndex(m => m.kind === 'sys' && m.text && m.text.startsWith('档案：'))
  if (idx >= 0) {
    msgs.value[idx].text = text
    msgs.value[idx].note = text.length > 36
    scroll()
  } else {
    pushSys(text, false, text.length > 36)
  }
}
function pushMate(text) {
  const m = newMsg('mate', '同桌')
  m.text = text || ''
  if (m.text) m.html = mdToHtml(m.text)
  msgs.value.push(m); scroll(); return m
}
function pushMe(text) {
  const m = newMsg('me', '你'); m.text = text || ''
  msgs.value.push(m); scroll(); return m
}
function lastMate() {
  for (let i = msgs.value.length - 1; i >= 0; i--) {
    if (msgs.value[i].kind === 'mate') return msgs.value[i]
  }
  return null
}
function scheduleMd(m, force) {
  if (force) {
    m.html = mdToHtml(m.text); m.thinking = false; scroll()
    return
  }
  if (mdTimer) return
  mdTimer = setTimeout(() => {
    mdTimer = null
    const tgt = m && m.kind === 'mate' ? m : lastMate()
    if (tgt && tgt.text && !tgt.locked) { tgt.html = mdToHtml(tgt.text); scroll() }
  }, 150)
}
function scroll() {
  nextTick(() => {
    const el = msgsEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}
function refreshStats() {
  if (!docId) return
  getStats(docId).then(d => {
    const s = d.stats || {}
    const weak = s.weak_points || {}
    setArchiveSys(`档案：薄弱 ${weak.low || 0} / ${weak.mid || 0} / ${weak.high || 0}（弱/中/强） · 待复习 ${s.review_due || 0} · tokens ${s.tokens && s.tokens.total || 0}`)
  }).catch(() => {})
}

function handle(ev) {
  const t = ev.type
  if (t === 'reasoning-delta') {
    return
  } else if (t === 'text-delta') {
    gotText.value = true
    const last = lastMate()
    if (last && last.text === '' && !last.locked) last.thinking = false
    if (last && !last.locked) {
      last.text += ev.delta || ''
      scheduleMd(last, false)
    } else {
      const m = pushMate(ev.delta || ''); scheduleMd(m, false)
    }
  } else if (t === 'judge') {
    renderJudge(ev.judgement || {})
  } else if (t === 'meta') {
    if (ev.kp && planKps.value.length) {
      const i = planKps.value.indexOf(ev.kp)
      if (i >= 0) kpCur.value = i
    }
    if (ev.state) kpDone.value = Math.max(kpDone.value, (kpCur.value >= 0 ? kpCur.value : 0))
  } else if (t === 'question') {
    const q = ev.question || {}
    let host = lastMate()
    if (!host || host.locked || host.question) host = pushMate('')
    host.locked = true
    host.question = q
    host.qtype = TYPE_NAME[q.type] || ''
    scroll()
  } else if (t === 'question-batch') {
    const qs = ev.questions || []
    pushSys('章末考 · 共 ' + qs.length + ' 题，逐题作答', false, true)
    for (const q of qs) pushSys(`${q.index + 1}. ${q.stem}`, false, true)
  } else if (t === 'report') {
    pushSys('（掌握度报告）' + ((ev.report || {}).summary || ''))
  } else if (t === 'error') {
    pushSys('[错误] ' + (ev.error || '未知'), true)
  }
  scroll()
}

function renderJudge(j) {
  const map = { correct: '答对了', partial_correct: '部分对', incorrect: '答错了', off_topic: '答非所问', unanswered: '未作答' }
  const c = map[j.correctness] || j.correctness || '—'
  const score = Math.round((j.score || 0) * 100)
  const m = newMsg('judge')
  m.jtag = '判定'
  m.jt = c
  m.jcls = j.correctness === 'correct' ? 'good' : (j.correctness === 'partial_correct' ? 'mid' : 'bad')
  m.score = score
  const nextMap = { reteach: '再讲一遍', alternative_explanation: '换个讲法', practice_question: '巩固一道', skip: '推进下一站' }
  m.jnext = nextMap[j.decision] || j.decision || ''
  if (j.review && j.review.scores) {
    m.jreview = Object.values(j.review.scores).map(v => Math.round(v * 10) / 10).join(' / ')
  }
  msgs.value.push(m)
  scroll()
}

function pick(key) {
  if (streaming.value || !sid.value) return
  draft.value = key
  send()
}

function send() {
  const text = (draft.value || '').trim()
  if (!text || streaming.value || !sid.value) return
  streaming.value = true
  gotText.value = false
  thinkSec.value = 0
  draft.value = ''
  pushMe(text)
  const m = pushMate('')
  m.thinking = true
  streamTurn({ session_id: sid.value, user_text: text }, ev => handle(ev))
    .then(() => {
      streaming.value = false
      thinkSec.value = 0
      const last = lastMate()
      if (last) {
        last.thinking = false
        if (!last.text && !last.question && last.kind === 'mate') {
          msgs.value = msgs.value.filter(x => x !== last)
        } else {
          scheduleMd(last, true)
        }
      }
      refreshStats()
    })
    .catch(e => {
      streaming.value = false; thinkSec.value = 0
      const last = lastMate()
      if (last && last.kind === 'mate' && !last.text) last.thinking = false
      pushSys('请求失败：' + (e && e.message ? e.message : e), true)
    })
}
</script>

<template>
  <div class="page">
    <div class="route">
      <div class="rt-l">
        <div class="rt-chap">{{ chapterTitle || '加载中…' }}</div>
        <div class="rt-steps" v-if="planKps.length">
          <div v-for="(k, i) in planKps" :key="i" class="step" :class="{ done: i < kpDone, cur: i === kpCur }">
            <div class="step-dot"></div>
          </div>
        </div>
      </div>
      <div class="rt-r" v-if="streaming">
        <div class="think" v-if="thinkSec > 0 && !gotText">
          <span class="tdot"></span><span class="tdot"></span><span class="tdot"></span>
          <span class="thk">思考中 {{ thinkSec }}s</span>
        </div>
        <div class="stream" v-else>
          <span class="sdot"></span><span class="s-txt">同桌回复中</span>
        </div>
      </div>
    </div>

    <div class="msgs" ref="msgsEl">
      <div v-for="m in msgs" :key="m.uid" class="row" :class="m.kind">
        <template v-if="m.kind === 'sys'">
          <div class="sys" :class="{ err: m.err, note: m.note }">{{ m.text }}</div>
        </template>
        <template v-else-if="m.kind === 'judge'">
          <div class="jcard" :class="m.jcls">
            <div class="jtop">
              <span class="jtag">{{ m.jtag }}</span>
              <span class="jt">{{ m.jt }}</span>
              <span class="jscore">{{ m.score }} 分</span>
            </div>
            <div class="jrow" v-if="m.jnext"><span class="jl">下一步</span><span class="jv">{{ m.jnext }}</span></div>
            <div class="jrow" v-if="m.jreview"><span class="jl">裁判四维</span><span class="jv">{{ m.jreview }}</span></div>
          </div>
        </template>
        <template v-else-if="m.kind === 'me'">
          <div class="bub me"><span class="mtxt">{{ m.text }}</span></div>
        </template>
        <template v-else>
          <div class="avatar">衍</div>
          <div class="col">
            <div class="bub mate" v-if="m.thinking || m.text || m.html">
              <div v-if="m.thinking" class="typing"><span class="tdot"></span><span class="tdot"></span><span class="tdot"></span></div>
              <div v-else-if="m.html" class="rich" v-html="m.html"></div>
              <span v-else class="mtxt">{{ m.text }}</span>
            </div>
            <div v-if="m.question" class="qcard">
              <div class="qhead">{{ m.qIndex ? '第 ' + m.qIndex + ' 题' : '小测' }}<span class="qtype">{{ m.qtype }}</span></div>
              <div class="stem">{{ m.question.stem }}</div>
              <div v-for="o in m.question.options || []" :key="o.key" class="opt" @click="pick(o.key)">
                <span class="okey">{{ o.key }}</span>
                <span class="otxt">{{ o.text }}</span>
              </div>
              <div v-if="!(m.question.options || []).length" class="free">简答 / 填空：直接在下方输入答案</div>
            </div>
          </div>
        </template>
      </div>
      <div class="tail"></div>
    </div>

    <div class="dock">
      <div class="inp-wrap">
        <input class="inp" v-model="draft" :disabled="streaming"
               :placeholder="streaming ? '同桌正在回复…' : '说点什么…（先思路，后对答案）'"
               @keyup.enter="send" />
      </div>
      <button class="send" :class="{ off: !canSend }" :disabled="!canSend" @click="send">
        <span v-if="!streaming">发送</span>
        <span v-else class="sending">•••</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--paper); }

.route { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px 9px; border-bottom: 1px solid #ece4d2; background: #faf6ec; }
.rt-l { display: flex; flex-direction: column; }
.rt-chap { font-size: 15px; font-weight: 500; color: var(--ink); max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rt-steps { display: flex; align-items: center; margin-top: 6px; }
.step { width: 18px; height: 3px; border-radius: 2px; background: #ddd3ba; margin-right: 4px; }
.step.done { background: var(--ink-soft); }
.step.cur { background: var(--gold); width: 28px; }

.think, .stream { display: flex; align-items: center; }
.tdot { width: 5px; height: 5px; border-radius: 50%; background: var(--ink-soft); margin-right: 4px; animation: blink 1.2s infinite; }
.tdot:nth-child(2) { animation-delay: 0.2s; }
.tdot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 60%, 100% { opacity: 0.25; } 30% { opacity: 1; } }
.thk { font-size: 11px; color: var(--tx-2); margin-left: 3px; }
.sdot { width: 5px; height: 5px; border-radius: 50%; background: var(--gold); margin-right: 4px; animation: blink 1.2s infinite; }
.s-txt { font-size: 11px; color: var(--tx-2); }

.msgs { flex: 1; min-height: 0; overflow-y: auto; padding: 14px 18px 0; }
.row { display: flex; margin-bottom: 14px; }
.row.me { justify-content: flex-end; }
.row.sys { justify-content: center; }
/* 宽屏下消息行限宽居中 */
@media (min-width: 600px) {
  .row { max-width: 720px; margin-left: auto; margin-right: auto; }
  .col { max-width: 560px; }
}

.sys { max-width: 88%; font-size: 12px; color: #9a8f74; background: rgba(255, 253, 248, 0.8); border: 1px solid #efe7d4; border-radius: 999px; padding: 6px 15px; line-height: 1.6; text-align: center; }
.sys.note { border-radius: 9px; text-align: left; max-width: 94%; white-space: pre-wrap; padding: 9px 12px; color: #6f6750; }
.sys.err { color: var(--err); border-color: #f0d5cc; background: #fdf3ef; }

.avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--ink); color: #f2e6c9; font-size: 17px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 10px; box-shadow: 0 2px 6px rgba(22, 54, 40, 0.16); }
.col { flex: 1; min-width: 0; }

.bub { border-radius: 12px; padding: 11px 13px; font-size: 15px; line-height: 1.7; }
.bub.mate { background: var(--card); border: 1px solid #ece3cd; border-top-left-radius: 4px; max-width: 100%; }
.bub.me { background: var(--ink); color: #f5efdd; border-bottom-right-radius: 4px; max-width: 86%; margin-left: auto; }
.mtxt { font-size: 15px; line-height: 1.7; word-break: break-all; }

.typing { display: flex; align-items: center; padding: 4px 1px; }

.qcard { margin-top: 8px; background: #fdf8ec; border: 1px solid #dccfae; border-radius: 10px; padding: 11px 12px; }
.qhead { display: flex; align-items: center; font-size: 11px; color: #8a7a4f; margin-bottom: 6px; }
.qtype { margin-left: 8px; background: #efe7d0; border-radius: 999px; padding: 1px 8px; font-size: 11px; color: #7a6a45; }
.stem { font-size: 15px; font-weight: 500; color: #333; line-height: 1.6; margin-bottom: 9px; }
.opt { display: flex; align-items: center; background: var(--card); border: 1px solid #e5dbc2; border-radius: 8px; padding: 8px 10px; margin-bottom: 7px; cursor: pointer; transition: all .12s; }
.opt:hover { background: #eef3e6; border-color: var(--ink-soft); }
.okey { width: 24px; height: 24px; border-radius: 50%; background: #efe8d8; color: #7a6a45; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.otxt { flex: 1; margin-left: 9px; font-size: 14px; color: #3a3a3a; line-height: 1.5; }
.free { font-size: 12px; color: #a08a5a; padding: 4px 1px; }

.jcard { min-width: 220px; max-width: 92%; background: var(--card); border-radius: 10px; padding: 10px 12px; border-left: 5px solid #888; box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); }
.jcard.good { border-left-color: var(--ink-soft); }
.jcard.mid { border-left-color: var(--gold); }
.jcard.bad { border-left-color: var(--err); }
.jtop { display: flex; align-items: center; }
.jtag { font-size: 11px; color: #fff; background: #555; border-radius: 999px; padding: 1px 8px; margin-right: 8px; }
.jcard.good .jtag { background: var(--ink-soft); }
.jcard.mid .jtag { background: var(--gold); }
.jcard.bad .jtag { background: var(--err); }
.jt { font-size: 14px; font-weight: 500; color: #333; }
.jscore { margin-left: auto; font-size: 13px; color: var(--tx-2); }
.jrow { display: flex; align-items: center; margin-top: 7px; font-size: 12px; }
.jl { color: #a09577; margin-right: 7px; flex-shrink: 0; }
.jv { color: #555; }

.dock { display: flex; align-items: center; padding: 9px 13px; padding-bottom: calc(9px + env(safe-area-inset-bottom)); border-top: 1px solid #ece4d2; background: #faf6ec; }
.inp-wrap { flex: 1; background: var(--card); border: 1px solid #e2d9c2; border-radius: 999px; padding: 0 17px; height: 42px; display: flex; align-items: center; }
.inp { flex: 1; font-size: 15px; color: #333; border: 0; outline: none; background: transparent; }
.send { margin-left: 10px; height: 42px; padding: 0 22px; border-radius: 999px; background: var(--ink); color: #f2e6c9; font-size: 15px; border: 0; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(22, 54, 40, 0.2); cursor: pointer; }
.send.off { background: #cfc8b6; box-shadow: none; cursor: default; }
.sending { letter-spacing: 3px; }
.tail { height: 16px; }
</style>
