<template>
  <view class="page">
    <view class="route">
      <view class="rt-l">
        <text class="rt-chap">{{ chapterTitle || '加载中…' }}</text>
        <view class="rt-steps" v-if="planKps.length">
          <view v-for="(k, i) in planKps" :key="i" class="step" :class="{ done: i < kpDone, cur: i === kpCur }">
            <view class="step-dot"></view>
          </view>
        </view>
      </view>
      <view class="rt-r" v-if="streaming">
        <view class="think" v-if="thinkSec > 0 && !gotText">
          <view class="tdot"></view><view class="tdot"></view><view class="tdot"></view>
          <text class="thk">思考中 {{ thinkSec }}s</text>
        </view>
        <view class="stream" v-else>
          <text class="sdot"></text><text class="s-txt">同桌回复中</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="msgs" :scroll-top="scrollTop" scroll-with-animation>
      <view v-for="(m, i) in msgs" :key="m.uid" class="row" :class="m.kind">
        <template v-if="m.kind === 'sys'">
          <view class="sys" :class="{ err: m.err, note: m.note }">{{ m.text }}</view>
        </template>
        <template v-else-if="m.kind === 'judge'">
          <view class="jcard" :class="m.jcls">
            <view class="jtop">
              <text class="jtag">{{ m.jtag }}</text>
              <text class="jt">{{ m.jt }}</text>
              <text class="jscore">{{ m.score }} 分</text>
            </view>
            <view class="jrow" v-if="m.jnext"><text class="jl">下一步</text><text class="jv">{{ m.jnext }}</text></view>
            <view class="jrow" v-if="m.jreview"><text class="jl">裁判四维</text><text class="jv">{{ m.jreview }}</text></view>
          </view>
        </template>
        <template v-else-if="m.kind === 'me'">
          <view class="bub me"><text class="mtxt" user-select>{{ m.text }}</text></view>
        </template>
        <template v-else>
          <view class="avatar">衍</view>
          <view class="col">
            <view class="bub mate" v-if="m.thinking || m.text || m.html">
              <view v-if="m.thinking" class="typing"><view class="tdot"></view><view class="tdot"></view><view class="tdot"></view></view>
              <!-- #ifdef H5 -->
              <view v-else-if="m.html" class="rich" v-html="m.html"></view>
              <!-- #endif -->
              <!-- #ifdef MP-WEIXIN -->
              <mp-html v-else-if="m.html" :content="m.html" :tag-style="tagStyle" class="rich" />
              <!-- #endif -->
              <text v-else class="mtxt">{{ m.text }}</text>
            </view>
            <view v-if="m.question" class="qcard">
              <view class="qhead">{{ m.qIndex ? '第 ' + m.qIndex + ' 题' : '小测' }}<text class="qtype">{{ m.qtype }}</text></view>
              <view class="stem">{{ m.question.stem }}</view>
              <view v-for="o in m.question.options || []" :key="o.key" class="opt" @tap="pick(o.key)">
                <text class="okey">{{ o.key }}</text>
                <text class="otxt">{{ o.text }}</text>
              </view>
              <view v-if="!(m.question.options || []).length" class="free">简答 / 填空：直接在下方输入答案</view>
            </view>
          </view>
        </template>
      </view>
      <view class="tail"></view>
    </scroll-view>

    <view class="dock">
      <view class="inp-wrap">
        <input class="inp" v-model="draft" :disabled="streaming" confirm-type="send"
               :placeholder="streaming ? '同桌正在回复…' : '说点什么…（先思路，后对答案）'" @confirm="send" />
      </view>
      <view class="send" :class="{ off: !canSend }" @tap="send">
        <text v-if="!streaming">发送</text>
        <text v-else class="sending">•••</text>
      </view>
    </view>
  </view>
</template>

<script>
import { startTutor, streamTurn, getStats } from '../../utils/api.js'
import { mdToHtml } from '../../utils/md.js'

let uidSeed = 1
const TYPE_NAME = { single_choice: '单选题', multiple_choice: '多选题', fill_blank: '填空题', short_answer: '简答题' }

export default {
  data() {
    return {
      docId: '', chapterIndex: 0, sid: '', chapterTitle: '',
      msgs: [], draft: '', streaming: false,
      scrollTop: 0, planKps: [], kpCur: -1, kpDone: 0,
      thinkSec: 0, gotText: false, docIdStats: '',
      tagStyle: {
        p: 'margin:0 0 6px;line-height:1.8;font-size:15px;color:#2b2b2b',
        strong: 'color:#163628', em: 'color:#5a4a2a',
        code: 'background:#f1ecdd;border-radius:4px;padding:0 4px;font-size:13px;color:#163628',
        pre: 'background:#22302a;color:#eae2cc;border-radius:8px;padding:10px 12px;font-size:13px;line-height:1.6;margin:6px 0;overflow-x:auto',
        ul: 'padding-left:20px;margin:4px 0', ol: 'padding-left:20px;margin:4px 0',
        li: 'margin:3px 0;line-height:1.7',
        h3: 'font-size:17px;font-weight:500;margin:10px 0 4px;color:#163628',
        h4: 'font-size:15px;font-weight:500;margin:8px 0 4px;color:#163628',
        blockquote: 'border-left:3px solid #c8b98a;margin:6px 0;padding:2px 10px;color:#7a6f55',
        a: 'color:#2c6e4f'
      },
      _mdTimer: null, _thinkTimer: null
    }
  },
  computed: {
    canSend() { return !this.streaming && !!this.sid && this.draft.trim() }
  },
  onLoad(query) {
    this.docId = query.doc_id || ''
    this.chapterIndex = Number(query.chapter_index || 0)
    this.docIdStats = this.docId
    startTutor(this.docId, this.chapterIndex).then(d => {
      if (!d.ok) { this.pushSys(d.detail || '开局失败', true); return }
      this.sid = d.session_id
      this.chapterTitle = d.chapter || '教学'
      this.planKps = (d.plan || []).map(k => k.name)
      uni.setNavigationBarTitle({ title: (d.chapter || '教学').slice(0, 12) })
      // 记住最近进度（双端共用 uni.storage），供 index 页显示"继续上次"
      try {
        const docTitle = (this.docs && this.docs[0] && this.docs[0].title) || ''
        uni.setStorageSync('moyan:last', {
          doc_id: this.docId,
          chapter_index: this.chapterIndex,
          label: docTitle ? (docTitle + ' · ' + (d.chapter || '本章')) : (d.chapter || '本章'),
          ts: Date.now()
        })
      } catch (e) { /* 存储失败非致命 */ }
      const plan = this.planKps
      this.pushSys(plan.length ? `本次共 ${plan.length} 站：${plan.map((k, i) => `${i + 1}.${k}`).join('  ')}` : '开始学习')
      this.pushMate(d.greeting || '（开场白缺失）')
      this.refreshStats()
    }).catch(e => this.pushSys('开局请求失败：' + e, true))
    this._thinkTimer = setInterval(() => {
      if (this.streaming && !this.gotText) this.thinkSec++
    }, 1000)
  },
  onUnload() {
    if (this._thinkTimer) clearInterval(this._thinkTimer)
    if (this._mdTimer) clearTimeout(this._mdTimer)
  },
  methods: {
    newMsg(kind, who) {
      return { uid: 'm' + uidSeed++, kind, who, text: '', html: '', cls: '', chips: [],
               question: null, locked: false, thinking: false, err: false, note: false,
               jtag: '', jt: '', jcls: '', score: '', jnext: '', jreview: '', qIndex: 0, qtype: '' }
    },
    pushSys(text, err, note) {
      const m = this.newMsg('sys'); m.text = text || ''; m.err = !!err
      m.note = !!note || m.text.length > 36
      this.msgs.push(m); this.scroll(); return m
    },
    pushMate(text) {
      const m = this.newMsg('mate', '同桌')
      m.text = text || ''
      if (m.text) m.html = mdToHtml(m.text)
      this.msgs.push(m); this.scroll(); return m
    },
    pushMe(text) {
      const m = this.newMsg('me', '你'); m.text = text || ''
      this.msgs.push(m); this.scroll(); return m
    },
    lastMate() {
      for (let i = this.msgs.length - 1; i >= 0; i--) {
        const m = this.msgs[i]
        if (m.kind === 'mate') return m
      }
      return null
    },
    scheduleMd(m, force) {
      if (force) {
        m.html = mdToHtml(m.text); m.thinking = false; this.scroll()
        return
      }
      if (this._mdTimer) return
      this._mdTimer = setTimeout(() => {
        this._mdTimer = null
        const last = this.lastMate()
        const tgt = m && m.kind === 'mate' ? m : last
        if (tgt && tgt.text && !tgt.locked) { tgt.html = mdToHtml(tgt.text); this.scroll() }
      }, 150)
    },
    scroll() {
      this.$nextTick(() => { this.scrollTop = this.scrollTop === 99999 ? 100000 : 99999 })
    },
    refreshStats() {
      if (!this.docIdStats) return
      getStats(this.docIdStats).then(d => {
        const s = d.stats || {}
        const weak = s.weak_points || {}
        this.pushSys(`档案：薄弱 ${weak.low || 0} / ${weak.mid || 0} / ${weak.high || 0}（弱/中/强） · 待复习 ${s.review_due || 0} · tokens ${s.tokens && s.tokens.total || 0}`)
      }).catch(() => {})
    },
    handle(ev) {
      const t = ev.type
      if (t === 'reasoning-delta') {
        return
      } else if (t === 'text-delta') {
        this.gotText = true
        const last = this.lastMate()
        if (last && last.text === '' && !last.locked) { last.thinking = false }
        if (last && !last.locked) {
          last.text += ev.delta || ''
          this.scheduleMd(last, false)
        } else {
          const m = this.pushMate(ev.delta || ''); this.scheduleMd(m, false)
        }
      } else if (t === 'judge') {
        this.renderJudge(ev.judgement || {})
      } else if (t === 'meta') {
        if (ev.kp && this.planKps.length) {
          const i = this.planKps.indexOf(ev.kp)
          if (i >= 0) this.kpCur = i
        }
        if (ev.state) this.kpDone = Math.max(this.kpDone, (this.kpCur >= 0 ? this.kpCur : 0))
      } else if (t === 'question') {
        const q = ev.question || {}
        let host = this.lastMate()
        if (!host || host.locked || host.question) host = this.pushMate('')
        host.locked = true
        host.question = q
        host.qtype = TYPE_NAME[q.type] || ''
        this.scroll()
      } else if (t === 'question-batch') {
        const qs = ev.questions || []
        this.pushSys('章末考 · 共 ' + qs.length + ' 题，逐题作答', false, true)
        for (const q of qs) this.pushSys(`${q.index + 1}. ${q.stem}`, false, true)
      } else if (t === 'report') {
        this.pushSys('（掌握度报告）' + ((ev.report || {}).summary || ''))
      } else if (t === 'error') {
        this.pushSys('[错误] ' + (ev.error || '未知'), true)
      }
      this.scroll()
    },
    renderJudge(j) {
      const map = { correct: '答对了', partial_correct: '部分对', incorrect: '答错了', off_topic: '答非所问', unanswered: '未作答' }
      const c = map[j.correctness] || j.correctness || '—'
      const score = Math.round((j.score || 0) * 100)
      const m = this.newMsg('judge')
      m.jtag = '判定'
      m.jt = c
      m.jcls = j.correctness === 'correct' ? 'good' : (j.correctness === 'partial_correct' ? 'mid' : 'bad')
      m.score = score
      const nextMap = { reteach: '再讲一遍', alternative_explanation: '换个讲法', practice_question: '巩固一道', skip: '推进下一站' }
      m.jnext = nextMap[j.decision] || j.decision || ''
      if (j.review && j.review.scores) {
        m.jreview = Object.values(j.review.scores).map(v => Math.round(v * 10) / 10).join(' / ')
      }
      this.msgs.push(m)
      this.scroll()
    },
    pick(key) {
      if (this.streaming || !this.sid) return
      this.draft = key
      this.send()
    },
    send() {
      const text = (this.draft || '').trim()
      if (!text || this.streaming || !this.sid) return
      this.streaming = true
      this.gotText = false
      this.thinkSec = 0
      this.draft = ''
      this.pushMe(text)
      const m = this.pushMate('')
      m.thinking = true
      streamTurn({ session_id: this.sid, user_text: text }, ev => this.handle(ev))
        .then(() => {
          this.streaming = false
          this.thinkSec = 0
          const last = this.lastMate()
          if (last) {
            last.thinking = false
            if (!last.text && !last.question && last.kind === 'mate') {
              this.msgs = this.msgs.filter(x => x !== last)
            } else {
              this.scheduleMd(last, true)
            }
          }
          this.refreshStats()
        })
        .catch(e => {
          this.streaming = false; this.thinkSec = 0
          const last = this.lastMate()
          if (last && last.kind === 'mate' && !last.text) last.thinking = false
          this.pushSys('请求失败：' + (e && e.message ? e.message : e), true)
        })
    }
  }
}
</script>

<style>
page { background: #f6f2e8; }
.page { height: 100vh; display: flex; flex-direction: column; box-sizing: border-box; background: #f6f2e8; }

.route { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 28rpx 14rpx; border-bottom: 2rpx solid #ece4d2; background: #faf6ec; }
.rt-chap { font-size: 27rpx; font-weight: 500; color: #163628; display: block; max-width: 430rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rt-steps { display: flex; align-items: center; margin-top: 10rpx; }
.step { width: 34rpx; height: 6rpx; border-radius: 3rpx; background: #ddd3ba; margin-right: 6rpx; }
.step.done { background: #2c6e4f; }
.step.cur { background: #b98a3e; width: 52rpx; }

.think, .stream { display: flex; align-items: center; }
.tdot { width: 10rpx; height: 10rpx; border-radius: 50%; background: #2c6e4f; margin-right: 6rpx; animation: blink 1.2s infinite; }
.tdot:nth-child(2) { animation-delay: 0.2s; }
.tdot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 60%, 100% { opacity: 0.25; } 30% { opacity: 1; } }
.thk { font-size: 21rpx; color: #8a7f66; margin-left: 4rpx; }
.s-txt { font-size: 21rpx; color: #8a7f66; }

.msgs { flex: 1; padding: 24rpx 26rpx 0; box-sizing: border-box; }
.row { display: flex; margin-bottom: 26rpx; }
.row.me { justify-content: flex-end; }
.row.sys { justify-content: center; }
.row.judge { justify-content: flex-start; }
/* 宽屏（桌面浏览器 / iPad）下消息行限宽居中，气泡不再被 1280+ 宽屏拉成超长条 */
@media (min-width: 600px) {
  .row { max-width: 720px; margin-left: auto; margin-right: auto; }
  .col { max-width: 560px; }
  .bub.mate { max-width: 100%; }
  .bub.me { max-width: 420px; }
  .jcard, .qcard { max-width: 100%; }
  .sys { max-width: 560px; }
}

.sys { max-width: 88%; font-size: 22rpx; color: #9a8f74; background: rgba(255, 253, 248, 0.8); border: 2rpx solid #efe7d4; border-radius: 999rpx; padding: 10rpx 26rpx; line-height: 1.6; text-align: center; }
.sys.note { border-radius: 16rpx; text-align: left; max-width: 94%; white-space: pre-wrap; padding: 16rpx 22rpx; color: #6f6750; }
.sys.err { color: #b3442e; border-color: #f0d5cc; background: #fdf3ef; }

.avatar { width: 76rpx; height: 76rpx; border-radius: 50%; background: #163628; color: #f2e6c9; font-size: 32rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 18rpx; box-shadow: 0 4rpx 10rpx rgba(22, 54, 40, 0.16); }
.col { flex: 1; min-width: 0; }

.bub { border-radius: 22rpx; padding: 20rpx 24rpx; font-size: 15px; line-height: 1.7; }
.bub.mate { background: #fffdf8; border: 2rpx solid #ece3cd; border-top-left-radius: 6rpx; max-width: 100%; }
.bub.me { background: #163628; color: #f5efdd; border-bottom-right-radius: 6rpx; max-width: 86%; margin-left: auto; }
.mtxt { font-size: 15px; line-height: 1.7; word-break: break-all; }
.rich { font-size: 15px; }
.rich p { margin: 0 0 6px; line-height: 1.8; }
.rich strong { color: #163628; }
.rich code { background: #f1ecdd; border-radius: 4px; padding: 0 4px; font-size: 13px; color: #163628; }
.rich pre { background: #22302a; color: #eae2cc; border-radius: 8px; padding: 10px 12px; font-size: 13px; line-height: 1.6; margin: 6px 0; overflow-x: auto; }
.rich pre code { background: transparent; padding: 0; color: inherit; }
.rich ul, .rich ol { padding-left: 20px; margin: 4px 0; }
.rich li { margin: 3px 0; line-height: 1.7; }
.rich h3 { font-size: 17px; font-weight: 500; margin: 10px 0 4px; color: #163628; }
.rich h4 { font-size: 15px; font-weight: 500; margin: 8px 0 4px; color: #163628; }
.rich blockquote { border-left: 3rpx solid #c8b98a; margin: 6rpx 0; padding: 2rpx 10rpx; color: #7a6f55; }

.typing { display: flex; align-items: center; padding: 6rpx 2rpx; }

.qcard { margin-top: 14rpx; background: #fdf8ec; border: 2rpx solid #dccfae; border-radius: 18rpx; padding: 20rpx 22rpx; }
.qhead { display: flex; align-items: center; font-size: 21rpx; color: #8a7a4f; margin-bottom: 10rpx; }
.qtype { margin-left: 14rpx; background: #efe7d0; border-radius: 999rpx; padding: 2rpx 14rpx; font-size: 20rpx; color: #7a6a45; }
.stem { font-size: 28rpx; font-weight: 500; color: #333; line-height: 1.6; margin-bottom: 16rpx; }
.opt { display: flex; align-items: center; background: #fffdf8; border: 2rpx solid #e5dbc2; border-radius: 14rpx; padding: 14rpx 18rpx; margin-bottom: 12rpx; }
.opt:active { background: #eef3e6; border-color: #2c6e4f; }
.okey { width: 44rpx; height: 44rpx; border-radius: 50%; background: #efe8d8; color: #7a6a45; font-size: 23rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.otxt { flex: 1; margin-left: 16rpx; font-size: 26rpx; color: #3a3a3a; line-height: 1.5; }
.free { font-size: 22rpx; color: #a08a5a; padding: 6rpx 2rpx; }

.jcard { min-width: 420rpx; max-width: 92%; background: #fffdf8; border-radius: 18rpx; padding: 18rpx 22rpx; border-left: 10rpx solid #888; box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.04); }
.jcard.good { border-left-color: #2c6e4f; }
.jcard.mid { border-left-color: #b98a3e; }
.jcard.bad { border-left-color: #b3442e; }
.jtop { display: flex; align-items: center; }
.jtag { font-size: 20rpx; color: #fff; background: #555; border-radius: 999rpx; padding: 2rpx 14rpx; margin-right: 14rpx; }
.jcard.good .jtag { background: #2c6e4f; } .jcard.mid .jtag { background: #b98a3e; } .jcard.bad .jtag { background: #b3442e; }
.jt { font-size: 26rpx; font-weight: 500; color: #333; }
.jscore { margin-left: auto; font-size: 24rpx; color: #8a7f66; }
.jrow { display: flex; align-items: center; margin-top: 12rpx; font-size: 22rpx; }
.jl { color: #a09577; margin-right: 12rpx; flex-shrink: 0; }
.jv { color: #555; }

.dock { display: flex; align-items: center; padding: 16rpx 22rpx; padding-bottom: calc(16rpx + env(safe-area-inset-bottom)); border-top: 2rpx solid #ece4d2; background: #faf6ec; }
.inp-wrap { flex: 1; background: #fffdf8; border: 2rpx solid #e2d9c2; border-radius: 999rpx; padding: 0 30rpx; height: 80rpx; display: flex; align-items: center; }
.inp { flex: 1; font-size: 28rpx; color: #333; }
.send { margin-left: 18rpx; height: 80rpx; padding: 0 40rpx; border-radius: 999rpx; background: #163628; color: #f2e6c9; font-size: 28rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 12rpx rgba(22, 54, 40, 0.2); }
.send.off { background: #cfc8b6; box-shadow: none; }
.sending { letter-spacing: 4rpx; }
.tail { height: 30rpx; }
</style>
