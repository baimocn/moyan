<template>
  <view class="wrap">
    <view class="head">墨衍 · 选课</view>
    <view class="card">
      <picker mode="selector" :range="docNames" @change="onDoc">
        <view class="row">教材：{{ docNames[docIdx] || '点选教材' }}</view>
      </picker>
      <picker mode="selector" :range="chapNames" @change="onChap">
        <view class="row">章节：{{ chapNames[chapIdx] || '点选章节' }}</view>
      </picker>
      <button class="go" :disabled="!ready" @click="go">开始学习</button>
      <view class="tip">同桌已就位。规矩：先思路，后对答案。</view>
    </view>
  </view>
</template>

<script>
import { getDocuments, getDocument } from '../../utils/api.js'

export default {
  data() {
    return { docs: [], docIdx: -1, chapIdx: -1, manifest: [] }
  },
  computed: {
    docNames() { return this.docs.map(d => `${d.filename}（${d.chapter_count}章）`) },
    chapNames() { return this.manifest.map(c => `${c.title}（${c.char_count}字）`) },
    ready() { return this.docIdx >= 0 && this.chapIdx >= 0 }
  },
  onShow() {
    getDocuments().then(d => {
      this.docs = (d.documents || []).filter(x => x.status === 'done')
    }).catch(() => {})
  },
  methods: {
    onDoc(e) {
      this.docIdx = Number(e.detail.value)
      const doc = this.docs[this.docIdx]
      getDocument(doc.doc_id).then(d => {
        this.manifest = d.document.manifest || []
        this.chapIdx = -1
      })
    },
    onChap(e) { this.chapIdx = Number(e.detail.value) },
    go() {
      const doc = this.docs[this.docIdx]
      const chap = this.manifest[this.chapIdx]
      uni.navigateTo({ url: `/pages/tutor/tutor?doc_id=${doc.doc_id}&chapter_index=${chap.index}` })
    }
  }
}
</script>
<style>
.wrap { padding: 20rpx; }
.head { font-size: 34rpx; letter-spacing: 4rpx; margin: 20rpx 0; }
.card { background: #fff; border: 1px solid #e2d9c8; border-radius: 12rpx; padding: 24rpx; }
.row { padding: 18rpx 8rpx; border-bottom: 1px dashed #e2d9c8; }
.go { margin-top: 24rpx; background: #7a5c3e; color: #fff; }
.tip { font-size: 24rpx; color: #8a7a5e; margin-top: 16rpx; }
</style>
