<template>
  <view class="pf">
    <view v-if="err" class="err"><text>{{ err }}</text></view>
    <template v-if="rep">
      <view class="cards">
        <view class="card"><text class="num">{{ rep.teaching.turns }}</text><text class="lab">教学轮次</text></view>
        <view class="card"><text class="num">{{ rep.teaching.sessions }}</text><text class="lab">学习会话</text></view>
        <view class="card"><text class="num">{{ rep.streak_days }}</text><text class="lab">连续天数</text></view>
      </view>
      <view class="sec">
        <text class="sh">判定趋势（近 {{ rep.days }} 天）</text>
        <view v-if="!rep.trend.length"><text class="dim">暂无判定记录。</text></view>
        <view v-for="t in rep.trend" :key="t.date" class="trow">
          <text class="tdate">{{ t.date.slice(5) }}</text>
          <text class="tval">{{ t.count }} 次 · 均分 {{ t.avg_score }}</text>
        </view>
      </view>
      <view class="sec">
        <text class="sh">薄弱点分布</text>
        <view class="trow"><text class="badge low">弱</text><text class="tval">{{ (rep.weaknesses.low || 0) }}</text></view>
        <view class="trow"><text class="badge mid">中</text><text class="tval">{{ (rep.weaknesses.mid || 0) }}</text></view>
        <view class="trow"><text class="badge high">强</text><text class="tval">{{ (rep.weaknesses.high || 0) }}</text></view>
      </view>
    </template>
  </view>
</template>

<script>
import { getMeStats } from '../../utils/api.js'

export default {
  data: () => ({ rep: null, err: '' }),
  onShow() {
    getMeStats()
      .then(d => { this.rep = d.report || {} })
      .catch(e => { this.err = e.message || '加载失败' })
  },
}
</script>

<style>
.pf { padding: 20rpx; }
.cards { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
.card { flex: 1; background: #fffdf8; border: 1rpx solid #eee4d2; border-radius: 14rpx; padding: 24rpx 16rpx; text-align: center; }
.num { font-size: 40rpx; font-weight: 600; display: block; color: #163628; }
.lab { color: #8a8477; font-size: 24rpx; }
.sec { background: #fffdf8; border: 1rpx solid #eee4d2; border-radius: 14rpx; padding: 20rpx; margin-bottom: 16rpx; }
.sh { font-size: 30rpx; font-weight: 600; display: block; margin-bottom: 12rpx; }
.trow { display: flex; justify-content: space-between; padding: 8rpx 0; }
.tdate, .tval { font-size: 26rpx; color: #555; }
.badge { font-size: 22rpx; padding: 4rpx 14rpx; border-radius: 16rpx; }
.badge.low { background: #fde8e8; color: #a33; }
.badge.mid { background: #fdf3d8; color: #8a6d1a; }
.badge.high { background: #e2f2e5; color: #2c6e3f; }
.dim { color: #8a8477; }
.err { color: #a33; padding: 20rpx; }
</style>
