<template>
  <view class="wrap">
    <scroll-view scroll-y class="chat" :scroll-top="scrollTop" scroll-with-animation>
      <view v-for="(m, i) in msgs" :key="i" class="msg" :class="m.cls">
        <view class="who" v-if="m.who">{{ m.who }}</view>
        <text>{{ m.text }}</text>
        <view v-if="m.chips && m.chips.length" class="chips">
          <text v-for="(c, j) in m.chips" :key="j" class="chip" :class="c.cls">{{ c.text }}</text>
        </view>
        <view v-if="m.question" class="qcard">
          <view class="stem">{{ m.question.stem }}</view>
          <view v-for="o in m.question.options || []" :key="o.key">
            <button class="opt" size="mini" @click="pick(o.key)">{{ o.key }}. {{ o.text }}</button>
          </view>
          <view v-if="!(m.question.options || []).length" class="free">（简答/填空：直接输入）</view>
        </view>
      </view>
      <view style="height: 20rpx;"></view>
    </scroll-view>
    <view class="inputbar">
      <input class="inp" v-model="draft" :disabled="streaming" confirm-type="send"
             placeholder="说点什么…（先思路，后对答案）" @confirm="send" />
      <button class="send" size="mini" :disabled="streaming || !draft.trim()" @click="send">发送</button>
    </view>
  </view>
</template>

<script>
import { startTutor, streamTurn, getStats } from '../../utils/api.js'

export default {
  data() {
    return {
      docId: '', chapterIndex: 0, sid: '',
      msgs: [], draft: '', streaming: false,
      scrollTop: 0, planKps: [], curKp: '', docIdStats: ''
    }
  },
  onLoad(query) {
    this.docId = query.doc_id || ''
    this.chapterIndex = Number(query.chapter_index || 0)
    this.docIdStats = this.docId
    startTutor(this.docId, this.chapterIndex).then(d => {
      if (!d.ok) { this.push('系统', d.detail || '开局失败'); return }
      this.sid = d.session_id
      this.planKps = (d.plan || []).map(k => k.name)
      this.push('同桌', d.greeting || '（开场白缺失）')
      this.push('系统', this.planKps.map((k, i) => `站${i + 1} ${k}`).join(' · '))
      this.refreshStats()
    }).catch(e => this.push('系统', '开局请求失败：' + e))
  },
  methods: {
    push(who, text, cls) {
      this.msgs.push({ who, text: text || '', cls: cls || (who === '你' ? 'me' : 'mate'), chips: [], question: null })
      this.scroll()
      return this.msgs[this.msgs.length - 1]
    },
    scroll() { this.$nextTick(() => { this.scrollTop = this.scrollTop === 99999 ? 100000 : 99999 }) },
    refreshStats() {
      getStats(this.docIdStats).then(d => {
        const s = d.stats || {}
        this.push('系统', `档案：薄弱 弱${s.weak_points?.low || 0}/中${s.weak_points?.mid || 0}/强${s.weak_points?.high || 0} · 待复习 ${s.review_due || 0} · tokens ${s.tokens?.total || 0}`)
      }).catch(() => {})
    },
    handle(ev) {
      const t = ev.type
      if (t === 'text-delta') {
        const last = this.msgs[this.msgs.length - 1]
        if (last && last.cls === 'mate' && last.who === '同桌' && !last.question && !last.locked) {
          last.text += ev.delta
        } else {
          this.push('同桌', ev.delta)
        }
      } else if (t === 'judge') {
        const j = ev.judgement || {}
        const map = { correct: '答对', partial_correct: '部分对', incorrect: '答错', off_topic: '答非所问', unanswered: '未作答' }
        const c = map[j.correctness] || j.correctness || '—'
        const last = this.msgs[this.msgs.length - 1]
        const chips = [{ cls: c === '答对' ? 'good' : (c === '部分对' ? 'mid' : 'bad'), text: `${c} · ${Math.round((j.score || 0) * 100)}分` },
                       { cls: 'grey', text: '下一步：' + ({ reteach: '再讲', alternative_explanation: '换讲法', practice_question: '巩固题', skip: '推进' }[j.decision] || j.decision) }]
        if (j.review && j.review.scores) {
          chips.push({ cls: 'grey', text: '裁判四维 ' + Object.values(j.review.scores).map(v => Math.round(v * 10) / 10).join('/') })
        }
        if (last && last.who === '同桌') last.chips = chips
      } else if (t === 'meta') {
        if (ev.state) { this.curKp = ev.kp || this.curKp }
        if (ev.question || ev.kp) { /* 状态角标由路线图呈现 */ }
      } else if (t === 'question') {
        const last = this.msgs[this.msgs.length - 1]
        if (last && last.who === '同桌') { last.question = ev.question; last.locked = true }
        else this.push('同桌', ev.question.stem).question = ev.question
      } else if (t === 'question-batch') {
        this.push('同桌', '章末考开始，共 ' + (ev.questions || []).length + ' 题：\n' +
          (ev.questions || []).map(q => `${q.index + 1}. ${q.stem}`).join('\n'))
      } else if (t === 'report') {
        const r = ev.report || {}
        this.push('同桌', `掌握度报告：${r.summary}`)
      } else if (t === 'error') {
        this.push('系统', '[错误] ' + ev.error)
      }
      this.scroll()
    },
    pick(key) { this.draft = key; this.send() },
    send() {
      const text = this.draft.trim()
      if (!text || this.streaming || !this.sid) return
      this.streaming = true
      this.draft = ''
      this.push('你', text)
      const cur = this.push('同桌', '')
      cur.locked = false
      streamTurn({ session_id: this.sid, user_text: text }, ev => this.handle(ev))
        .then(() => { this.streaming = false; this.refreshStats() })
        .catch(e => { this.streaming = false; this.push('系统', '请求失败：' + e) })
    }
  }
}
</script>
<style>
.wrap { display: flex; flex-direction: column; height: 100vh; }
.chat { flex: 1; padding: 20rpx; }
.msg { max-width: 88%; margin-bottom: 18rpx; padding: 16rpx 20rpx; border-radius: 12rpx; line-height: 1.7; }
.msg.me { background: #e8f0e4; margin-left: auto; }
.msg.mate { background: #fff; border: 1px solid #e2d9c8; }
.who { font-size: 22rpx; color: #7a5c3e; margin-bottom: 6rpx; }
.chips { margin-top: 8rpx; }
.chip { display: inline-block; font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 16rpx; margin-right: 8rpx; background: #eee; color: #666; }
.chip.good { background: #e2f0e4; color: #3a7d44; } .chip.bad { background: #f6e0e0; color: #a33c3c; }
.chip.mid { background: #f5ecd4; color: #b08a2e; } .chip.grey { background: #eee; color: #777; }
.qcard { background: #fbf8f0; border: 1px dashed #7a5c3e; border-radius: 10rpx; padding: 14rpx; margin-top: 10rpx; }
.stem { font-weight: bold; margin-bottom: 8rpx; }
.opt { margin: 8rpx 0; }
.free { font-size: 22rpx; color: #999; }
.inputbar { display: flex; gap: 12rpx; padding: 16rpx; background: #f3ecdd; }
.inp { flex: 1; background: #fff; border: 1px solid #e2d9c8; border-radius: 10rpx; padding: 12rpx; }
.send { background: #7a5c3e; color: #fff; }
</style>
