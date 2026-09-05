<template>
  <view class="mk">
    <view v-if="err" class="err"><text>{{ err }}</text></view>
    <view v-if="!rows.length && !err" class="empty"><text>还没有错题记录——去和 AI 同桌学一章吧。</text></view>
    <view v-for="r in rows" :key="r.doc_id + r.skill_id" class="item">
      <view class="l1">
        <text class="name">{{ r.name }}</text>
        <text class="badge" :class="r.mastery">{{ r.mastery === 'low' ? '弱' : (r.mastery === 'mid' ? '中' : '强') }}</text>
      </view>
      <view class="l2">
        <text class="dim">{{ r.doc_title }}</text>
        <text class="dim">{{ dueText(r.due_at) }}</text>
      </view>
      <button class="go" size="mini" :disabled="starting === r.doc_id" @tap="start(r.doc_id)">
        {{ starting === r.doc_id ? '发起中…' : '重练本章' }}
      </button>
    </view>
  </view>
</template>

<script>
import { getMyWeaknesses, startReview } from '../../utils/api.js'

export default {
  data: () => ({ rows: [], err: '', starting: '' }),
  onShow() {
    getMyWeaknesses()
      .then(d => { this.rows = d.weaknesses || [] })
      .catch(e => { this.err = e.message || '加载失败' })
  },
  methods: {
    dueText(iso) {
      if (!iso) return '未排程'
      const d = new Date(iso); const t = new Date(); t.setHours(0, 0, 0, 0)
      d.setHours(0, 0, 0, 0)
      const diff = Math.round((d - t) / 86400000)
      if (diff < 0) return `已到期 ${-diff} 天`
      if (diff === 0) return '今天到期'
      return `${diff} 天后`
    },
    start(docId) {
      this.starting = docId
      startReview(docId)
        .then(d => uni.navigateTo({ url: `/pages/review/review?session_id=${d.session_id}` }))
        .catch(e => { this.err = e.message || '发起失败' })
        .then(() => { this.starting = '' })
    },
  },
}
</script>

<style>
.mk { padding: 20rpx; }
.item { background: #fffdf8; border: 1rpx solid #eee4d2; border-radius: 14rpx; padding: 20rpx; margin-bottom: 16rpx; }
.l1 { display: flex; justify-content: space-between; align-items: center; }
.name { font-size: 30rpx; font-weight: 600; }
.badge { font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 16rpx; background: #fde8e8; color: #a33; }
.badge.mid { background: #fdf3d8; color: #8a6d1a; }
.badge.high { background: #e2f2e5; color: #2c6e3f; }
.l2 { display: flex; justify-content: space-between; margin: 8rpx 0 12rpx; }
.dim { color: #8a8477; font-size: 24rpx; }
.go { background: #163628; color: #f6f2e8; }
.empty, .err { padding: 30rpx; text-align: center; color: #8a8477; }
.err { color: #a33; }
</style>
