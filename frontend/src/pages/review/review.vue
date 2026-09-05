<template>
  <view class="rv">
    <view class="prog"><text>{{ prog.done }} 已完成 · {{ prog.remaining }} 待重练</text></view>
    <view v-if="err" class="err"><text>{{ err }}</text></view>

    <view v-if="finished" class="card fin">
      <text>🎉 本轮重练完成，FSRS 已按自评重排复习。</text>
    </view>

    <view v-else-if="item" class="card">
      <text class="kp">{{ item.name }}</text>
      <text class="chap">章节：{{ item.chapter_title || '-' }}</text>
      <view v-if="revealed" class="snippet">
        <text>{{ item.snippet || '（本章教材无该点片段，凭理解自评即可）' }}</text>
      </view>
      <button v-else class="reveal" @tap="revealed = true">翻看教材片段</button>
      <view v-if="revealed" class="ratings">
        <button class="r again" :disabled="busy" @tap="ans('again')">没记住</button>
        <button class="r hard" :disabled="busy" @tap="ans('hard')">勉强</button>
        <button class="r good" :disabled="busy" @tap="ans('good')">会了</button>
        <button class="r easy" :disabled="busy" @tap="ans('easy')">轻松</button>
      </view>
    </view>

    <view v-else-if="!err" class="card fin"><text>没有待重练项——全部完成 ✅</text></view>
    <view class="hint"><text>again 留队重讲，其余出队并按 FSRS 重排到期。</text></view>
  </view>
</template>

<script>
import { reviewCurrent, reviewAnswer } from '../../utils/api.js'

export default {
  data: () => ({
    sid: '', prog: { done: 0, remaining: 0 }, item: null,
    finished: false, revealed: false, err: '', busy: false,
  }),
  onLoad(q) {
    this.sid = q.session_id || ''
  },
  onShow() {
    if (this.sid) this.load()
  },
  methods: {
    apply(d) {
      this.prog = d.progress || { done: 0, remaining: 0 }
      this.item = d.next
      this.finished = !!d.finished
      this.revealed = false
    },
    load() {
      reviewCurrent(this.sid)
        .then(d => this.apply(d.current || {}))
        .catch(e => { this.err = e.message || '加载失败' })
    },
    ans(rating) {
      if (!this.item || this.busy) return
      this.busy = true
      reviewAnswer(this.sid, this.item.skill_id, rating)
        .then(d => this.apply({ progress: d.progress, next: d.next, finished: d.finished }))
        .catch(e => { this.err = e.message || '提交失败' })
        .then(() => { this.busy = false })
    },
  },
}
</script>

<style>
.rv { padding: 20rpx; }
.prog { margin-bottom: 16rpx; color: #163628; font-size: 28rpx; }
.card { background: #fffdf8; border: 1rpx solid #eee4d2; border-radius: 14rpx; padding: 24rpx; margin-bottom: 16rpx; }
.kp { font-size: 34rpx; font-weight: 600; display: block; margin-bottom: 8rpx; }
.chap { color: #8a8477; font-size: 24rpx; display: block; margin-bottom: 12rpx; }
.snippet { background: #faf6ec; border-radius: 12rpx; padding: 16rpx; font-size: 26rpx; line-height: 1.7; margin-bottom: 16rpx; }
.reveal { margin-bottom: 16rpx; }
.ratings { display: flex; gap: 12rpx; }
.r { flex: 1; font-size: 26rpx; }
.again { background: #fde8e8; }
.hard { background: #fdf3d8; }
.good { background: #e2f2e5; }
.easy { background: #dceef5; }
.fin { color: #2c6e3f; }
.err { color: #a33; }
.hint { color: #8a8477; font-size: 24rpx; }
</style>
