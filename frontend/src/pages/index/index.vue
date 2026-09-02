<template>
  <view class="wrap">
    <view class="head">墨衍 · 选课</view>
    <view class="card">
      <picker mode="selector" :range="docNames" @change="onDoc">
        <view class="row">教材：{{ docNames[docIdx] || '点选教材' }}</view>
      </picker>
      <view class="subrow" v-if="docIdx >= 0">
        <text class="sub">上传/导入后自动转 MD，原件即清理</text>
        <text class="ren" @click="rename">✎ 重命名</text>
      </view>
      <picker mode="selector" :range="chapNames" @change="onChap">
        <view class="row">章节：{{ chapNames[chapIdx] || '点选章节' }}</view>
      </picker>
      <button class="go" :disabled="!ready" @click="go">开始学习</button>
      <button class="up" @click="choose">＋ 上传教材</button>
      <view class="tip" v-if="tip">{{ tip }}</view>
      <view class="tip">同桌已就位。规矩：先思路，后对答案。</view>
    </view>

    <!-- H5 端文件选择（小程序走 wx.chooseMessageFile，条件编译） -->
    <!-- #ifdef H5 -->
    <input ref="fileInput" type="file" accept=".pdf,.docx,.pptx,.xlsx,.md,.txt,.html,.epub,.jpg,.jpeg,.png,.bmp,.tiff" style="display:none" @change="onFilePicked" />
    <!-- #endif -->
  </view>
</template>

<script>
import { getDocuments, getDocument, uploadFile, getTask, renameDocument } from '../../utils/api.js'

export default {
  data() {
    return { docs: [], docIdx: -1, chapIdx: -1, manifest: [], tip: '', polling: false }
  },
  computed: {
    docNames() { return this.docs.map(d => `${d.title || d.filename}（${d.chapter_count}章）`) },
    chapNames() { return this.manifest.map(c => `${c.title}（${c.char_count}字）`) },
    ready() { return this.docIdx >= 0 && this.chapIdx >= 0 }
  },
  onShow() {
    this.refresh()
  },
  methods: {
    refresh() {
      getDocuments().then(d => {
        this.docs = (d.documents || []).filter(x => x.status === 'done')
        if (this.docIdx > this.docs.length - 1) this.docIdx = -1
      }).catch(() => {})
    },
    onDoc(e) {
      this.docIdx = Number(e.detail.value)
      const doc = this.docs[this.docIdx]
      if (!doc) return
      getDocument(doc.doc_id).then(d => {
        this.manifest = d.document.manifest || []
        this.chapIdx = -1
      })
    },
    onChap(e) { this.chapIdx = Number(e.detail.value) },
    choose() {
      // #ifdef MP-WEIXIN
      wx.chooseMessageFile({
        count: 1,
        type: 'file',
        success: res => {
          const f = res.tempFiles && res.tempFiles[0]
          if (f) this.askName(f)
        },
        fail: () => {}
      })
      // #endif
      // #ifdef H5
      this.$refs.fileInput && this.$refs.fileInput.click()
      // #endif
    },
    onFilePicked(e) {
      const f = e.target.files && e.target.files[0]
      if (f) this.askName(f)
    },
    // 先让用户给书起名，再上传
    askName(f) {
      const defName = (f.name || '').replace(/\.[^.]+$/, '') || '未命名教材'
      uni.showModal({
        title: '给教材起个名',
        editable: true,
        placeholderText: '留空用文件名',
        content: defName,
        success: r => {
          const title = r.confirm ? (r.content || '').trim() : ''
          this.doUpload(f.path || f, title || defName)
        }
      })
    },
    doUpload(file, title) {
      this.tip = '上传中…'
      uni.showLoading({ title: '解析中' })
      uploadFile(file, title).then(r => {
        uni.hideLoading()
        if (!r || !r.ok) { this.tip = '上传失败：' + (r && r.detail) || '未知错误'; return }
        if (r.status === 'processing') {
          this.tip = `转换中（${r.task_id || ''}）…`
          this.pollTask(r.task_id, r.doc_id)
        } else {
          this.tip = '已加入教学计划 ✓（原件已清理）'
          this.refresh()
        }
      }).catch(e => { uni.hideLoading(); this.tip = '上传失败：' + e })
    },
    pollTask(taskId, docId) {
      if (this.polling) return
      this.polling = true
      const tick = () => {
        getTask(taskId).then(r => {
          const t = r.task || {}
          if (t.status === 'done' || t.status === 'success') {
            this.polling = false
            this.tip = '转换完成 ✓（原件已清理）'
            this.refresh()
          } else if (t.status === 'failed') {
            this.polling = false
            this.tip = '转换失败：' + (t.message || '未知错误')
          } else {
            this.tip = `转换中 ${t.progress != null ? Math.round(t.progress) + '%' : '…'}`
            setTimeout(tick, 2000)
          }
        }).catch(() => { this.polling = false; this.tip = '任务查询失败' })
      }
      tick()
    },
    rename() {
      const doc = this.docs[this.docIdx]
      if (!doc) return
      uni.showModal({
        title: '重命名教材',
        editable: true,
        placeholderText: '输入新名称',
        content: doc.title || doc.filename,
        success: r => {
          const title = r.confirm ? (r.content || '').trim() : ''
          if (!title) return
          renameDocument(doc.doc_id, title).then(() => {
            this.tip = '已重命名 ✓'
            this.refresh()
          }).catch(e => { this.tip = '重命名失败：' + e })
        }
      })
    },
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
.subrow { display: flex; justify-content: space-between; align-items: center; padding: 8rpx 8rpx 4rpx; }
.sub { font-size: 22rpx; color: #a09078; }
.ren { font-size: 24rpx; color: #7a5c3e; padding: 4rpx 12rpx; border: 1px solid #cbbfa8; border-radius: 8rpx; }
.go { margin-top: 24rpx; background: #7a5c3e; color: #fff; }
.up { margin-top: 16rpx; background: #f5ecd4; color: #7a5c3e; border: 1px dashed #cbbfa8; }
.tip { font-size: 24rpx; color: #8a7a5e; margin-top: 16rpx; }
</style>
