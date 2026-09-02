<template>
  <view class="page">
    <view class="hero">
      <view class="logo">墨</view>
      <view class="brand">
        <text class="bname">墨衍</text>
        <text class="bsub">AI 同桌 · 一章一章带你学透</text>
      </view>
    </view>

    <view v-if="last && last.label" class="resume" @tap="resumeLast">
      <view class="ri">
        <text class="rit">继续上次</text>
        <text class="risub">上次学到这里 · {{ last.label }}</text>
      </view>
      <view class="rgo">继续 →</view>
    </view>

    <view class="sec">
      <text class="sec-t">教材书架</text>
      <text class="sec-c" v-if="docs.length">{{ docs.length }} 本就绪</text>
    </view>

    <scroll-view scroll-y class="list" :style="{ height: listH }">
      <view v-for="(d, i) in docs" :key="d.doc_id" class="doc" :class="{ sel: i === docIdx }" @tap="onDocPick(i)">
        <view class="doc-top">
          <text class="doc-title">{{ d.title || d.filename }}</text>
          <text class="pill" v-if="i === docIdx">已选</text>
          <text class="ren" @tap.stop="renameDoc(d)">重命名</text>
        </view>
        <view class="doc-meta">
          <text>{{ d.chapter_count }} 章</text>
          <text class="sep">·</text>
          <text>{{ fmtWan(d.md_chars) }}</text>
          <text class="sep">·</text>
          <text>{{ fmtSrc(d) }}</text>
        </view>
        <view class="chaps" v-if="i === docIdx">
          <view v-for="c in manifest" :key="c.index" class="chap" :class="{ on: c.index === chapIdx }" @tap.stop="chapIdx = c.index">
            <text class="chap-no">{{ c.index + 1 }}</text>
            <text class="chap-t">{{ c.title }}</text>
            <text class="chap-meta">{{ fmtWan(c.char_count) }}</text>
            <text class="tick" v-if="c.index === chapIdx">✓</text>
          </view>
          <view class="chap hint" v-if="!manifest.length">正在读取章节…</view>
        </view>
      </view>

      <view class="doc up" @tap="choose">
        <view class="up-ico">＋</view>
        <view class="up-txt">
          <text class="up-t">上传新教材</text>
          <text class="up-s">PDF / Word / PPT / 扫描件，原件即清理</text>
        </view>
      </view>
      <view class="doc-note">同桌已就位。规矩：先思路，后对答案。</view>
    </scroll-view>

    <view class="foot">
      <view v-if="tip" class="tip">{{ tip }}</view>
      <view class="start" :class="{ off: !ready }" @tap="ready && go()">开始学习</view>
    </view>

    <!-- #ifdef H5 -->
    <!-- H5 命名弹层：uni.showModal 的 editable 在 H5 端不生效（实测无输入框），
         故网页端用自制弹层；小程序端仍走 showModal editable -->
    <view v-if="dlg.show" class="dlg-mask" @tap.self="dlgCancel">
      <view class="dlg">
        <text class="dlg-t">{{ dlg.title }}</text>
        <input class="dlg-i" v-model="dlg.val" :placeholder="dlg.ph" :focus="dlg.show" confirm-type="done" @confirm="dlgOk" />
        <view class="dlg-btns">
          <view class="dlg-btn" @tap="dlgCancel">取消</view>
          <view class="dlg-btn ok" @tap="dlgOk">确定</view>
        </view>
      </view>
    </view>
    <!-- #endif -->
  </view>
</template>

<script>
import { getDocuments, getDocument, uploadFile, getTask, renameDocument } from '../../utils/api.js'

export default {
  data() {
    return {
      docs: [], docIdx: -1, chapIdx: -1, manifest: [], tip: '', polling: false, listH: '600px', last: null,
      dlg: { show: false, mode: '', title: '', ph: '', val: '' }, pending: null
    }
  },
  computed: {
    docNames() { return this.docs.map(d => `${d.title || d.filename}（${d.chapter_count}章）`) },
    chapNames() { return this.manifest.map(c => `${c.title}（${c.char_count}字）`) },
    ready() { return this.docIdx >= 0 && this.chapIdx >= 0 }
  },
  onLoad() {
    try {
      const h = uni.getSystemInfoSync()
      this.listH = (h.windowHeight - 460) + 'px'
    } catch (e) { /* 保持默认 */ }
  },
  onShow() {
    this.refresh()
    try {
      const s = uni.getStorageSync('moyan:last')
      if (s && s.doc_id && Number.isInteger(s.chapter_index)) this.last = s
      else this.last = null
    } catch (e) { this.last = null }
  },
  methods: {
    resumeLast() {
      if (!this.last) return
      if (!this.docs.length) { this.tip = '书架还没准备好，请稍候'; return }
      const i = this.docs.findIndex(d => d.doc_id === this.last.doc_id)
      if (i < 0) { this.tip = '上次教材已下架'; this.last = null; try { uni.removeStorageSync('moyan:last') } catch (e) {}; return }
      this.docIdx = i
      const doc = this.docs[i]
      this.chapIdx = this.last.chapter_index
      getDocument(doc.doc_id).then(d => {
        if (this.docIdx !== i) return
        this.manifest = d.document.manifest || []
        if (this.manifest[this.chapIdx]) this.go()
        else { this.tip = '上次章节已变更，请手动选' }
      }).catch(() => { this.tip = '章节读取失败' })
    },
    fmtWan(n) {
      n = Number(n || 0)
      return n >= 10000 ? (n / 10000).toFixed(1) + ' 万字' : n + ' 字'
    },
    fmtSrc(d) {
      if (d.source === 'ocr') return '扫描件 OCR'
      if (d.format === 'md') return 'Markdown 直读'
      const m = { pdf: 'PDF', docx: 'Word', pptx: 'PPT', xlsx: '表格' }
      return m[d.format] || String(d.format || '资料').toUpperCase()
    },
    refresh() {
      getDocuments().then(d => {
        const done = (d.documents || []).filter(x => x.status === 'done')
        const selectedId = this.docIdx >= 0 && this.docs[this.docIdx] ? this.docs[this.docIdx].doc_id : ''
        this.docs = done
        if (!selectedId) { this.docIdx = -1; this.manifest = [] }
        else {
          const idx = done.findIndex(x => x.doc_id === selectedId)
          this.docIdx = idx
          if (idx < 0) this.manifest = []
        }
      }).catch(() => {})
    },
    onDocPick(i) {
      if (i === this.docIdx) { this.manifest = []; this.docIdx = -1; this.chapIdx = -1; return }
      this.docIdx = i
      const doc = this.docs[i]
      if (!doc) return
      this.chapIdx = -1
      this.manifest = []
      getDocument(doc.doc_id).then(d => {
        if (this.docIdx !== i) return
        this.manifest = d.document.manifest || []
      }).catch(() => { this.tip = '章节读取失败' })
    },
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
      this.pickH5File()
      // #endif
    },
    // #ifdef H5
    // uni-app 的 <input> 组件编译后是 uni-input，不支持 type=file 也不暴露原生
    // click()（旧实现 this.$refs.fileInput.click() 直接 TypeError，上传点不动）。
    // 这里动态创建原生 input[type=file] 触发系统文件选择器（H5 标准做法）。
    pickH5File() {
      const el = document.createElement('input')
      el.type = 'file'
      el.accept = '.pdf,.docx,.pptx,.xlsx,.md,.txt,.html,.epub,.jpg,.jpeg,.png,.bmp,.tiff'
      el.style.display = 'none'
      el.addEventListener('change', (e) => {
        const f = e.target && e.target.files && e.target.files[0]
        if (el.parentNode) el.parentNode.removeChild(el)
        if (f) this.askName(f)
      })
      document.body.appendChild(el)
      el.click()
    },
    // H5 命名弹层（上传与重命名共用）
    openNameDlg(mode, obj) {
      const def = mode === 'rename' ? (obj.title || obj.filename || '') : ((obj.name || '').replace(/\.[^.]+$/, '') || '未命名教材')
      this.pending = obj
      this.dlg = {
        show: true, mode,
        title: mode === 'rename' ? '重命名教材' : '给教材起个名',
        ph: mode === 'rename' ? '输入新名称' : '留空用文件名',
        val: def
      }
    },
    dlgOk() {
      const dlg = this.dlg
      if (!dlg.show) return
      const val = (dlg.val || '').trim()
      this.dlg.show = false
      const obj = this.pending
      this.pending = null
      if (dlg.mode === 'rename') {
        if (!val) return
        renameDocument(obj.doc_id, val).then(() => {
          this.tip = '已重命名 ✓'
          this.refresh()
        }).catch(e => { this.tip = '重命名失败：' + e })
      } else {
        const title = val || (obj.name || '').replace(/\.[^.]+$/, '') || '未命名教材'
        this.doUpload(obj, title)
      }
    },
    dlgCancel() {
      this.dlg.show = false
      this.pending = null
    },
    // #endif
    askName(f) {
      // #ifdef H5
      this.openNameDlg('upload', f)
      // #endif
      // #ifdef MP-WEIXIN
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
      // #endif
    },
    doUpload(file, title) {
      this.tip = '上传解析中…'
      uni.showLoading({ title: '解析中', mask: true })
      uploadFile(file, title).then(r => {
        uni.hideLoading()
        if (!r || !r.ok) { this.tip = '上传失败：' + ((r && r.detail) || '未知错误'); return }
        if (r.status === 'processing') {
          this.tip = '转换中，请稍候…'
          this.pollTask(r.task_id, r.doc_id)
        } else {
          this.tip = '已上架 ✓'
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
            this.tip = '转换完成，已上架 ✓'
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
    renameDoc(d) {
      // #ifdef H5
      this.openNameDlg('rename', d)
      // #endif
      // #ifdef MP-WEIXIN
      uni.showModal({
        title: '重命名教材',
        editable: true,
        placeholderText: '输入新名称',
        content: d.title || d.filename,
        success: r => {
          const title = r.confirm ? (r.content || '').trim() : ''
          if (!title) return
          renameDocument(d.doc_id, title).then(() => {
            this.tip = '已重命名 ✓'
            this.refresh()
          }).catch(e => { this.tip = '重命名失败：' + e })
        }
      })
      // #endif
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
page { background: #f6f2e8; }
/* H5 桌面端：内容居中限宽，避免 1280+ 宽屏拉成超长条 */
.page { min-height: 100vh; display: flex; flex-direction: column; padding: 32rpx 28rpx 24rpx; box-sizing: border-box; max-width: 760px; margin: 0 auto; width: 100%; }
.foot { padding-top: 20rpx; max-width: 760px; margin: 0 auto; width: 100%; box-sizing: border-box; }

.resume { display: flex; align-items: center; background: linear-gradient(135deg, #163628 0%, #2c6e4f 100%); color: #f2e6c9; border-radius: 20rpx; padding: 22rpx 26rpx; margin-bottom: 20rpx; box-shadow: 0 6rpx 16rpx rgba(22, 54, 40, 0.18); }
.ri { flex: 1; display: flex; flex-direction: column; }
.rit { font-size: 27rpx; font-weight: 500; letter-spacing: 2rpx; }
.risub { font-size: 22rpx; color: #d8c9a0; margin-top: 6rpx; }
.rgo { font-size: 26rpx; color: #f2e6c9; padding: 8rpx 22rpx; border: 2rpx solid #f2e6c9; border-radius: 999rpx; }

.hero { display: flex; align-items: center; padding: 12rpx 4rpx 28rpx; }
.logo { width: 84rpx; height: 84rpx; border-radius: 26rpx; background: #163628; color: #f2e6c9; font-size: 44rpx; font-weight: 500; display: flex; align-items: center; justify-content: center; letter-spacing: 0; box-shadow: 0 6rpx 16rpx rgba(22, 54, 40, 0.18); }
.brand { margin-left: 22rpx; display: flex; flex-direction: column; }
.bname { font-size: 44rpx; font-weight: 500; letter-spacing: 10rpx; color: #163628; line-height: 1.15; }
.bsub { font-size: 22rpx; color: #8a7f66; margin-top: 6rpx; letter-spacing: 2rpx; }

.sec { display: flex; align-items: baseline; justify-content: space-between; padding: 8rpx 6rpx 18rpx; }
.sec-t { font-size: 30rpx; font-weight: 500; color: #2b2b2b; }
.sec-c { font-size: 22rpx; color: #9a8f74; }

.list { flex: 1; }
.doc { background: #fffdf8; border: 2rpx solid #eae2cf; border-radius: 24rpx; padding: 26rpx 28rpx; margin-bottom: 20rpx; transition: border-color 0.15s; }
.doc.sel { border-color: #2c6e4f; box-shadow: 0 4rpx 14rpx rgba(44, 110, 79, 0.12); }
.doc-top { display: flex; align-items: center; }
.doc-title { flex: 1; font-size: 30rpx; font-weight: 500; color: #1f1f1f; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pill { font-size: 20rpx; color: #fff; background: #2c6e4f; border-radius: 999rpx; padding: 6rpx 18rpx; margin-left: 16rpx; }
.ren { font-size: 22rpx; color: #a08a5a; padding: 6rpx 16rpx; border: 2rpx solid #ddd0b4; border-radius: 999rpx; margin-left: 16rpx; cursor: pointer; }
.doc-meta { display: flex; align-items: center; font-size: 22rpx; color: #94896f; margin-top: 14rpx; }
.sep { margin: 0 10rpx; color: #c9bfa5; }

.chaps { margin-top: 22rpx; border-top: 2rpx dashed #eee5d2; padding-top: 16rpx; }
.chap { display: flex; align-items: center; padding: 20rpx 16rpx; border-radius: 16rpx; margin-bottom: 6rpx; }
.chap.on { background: #e8f1e6; }
.chap-no { width: 44rpx; height: 44rpx; border-radius: 50%; background: #efe8d8; color: #7a6a45; font-size: 22rpx; display: flex; align-items: center; justify-content: center; }
.chap.on .chap-no { background: #2c6e4f; color: #fff; }
.chap-t { flex: 1; margin-left: 18rpx; font-size: 27rpx; color: #333; }
.chap-meta { font-size: 20rpx; color: #a69a7e; margin-left: 12rpx; }
.tick { color: #2c6e4f; font-size: 26rpx; margin-left: 12rpx; font-weight: 500; }
.chap.hint { color: #9a8f74; font-size: 24rpx; justify-content: center; }

.doc.up { display: flex; align-items: center; border-style: dashed; border-color: #cbbf9e; background: #faf6ea; cursor: pointer; }
.up-ico { width: 64rpx; height: 64rpx; border-radius: 50%; background: #163628; color: #f2e6c9; font-size: 36rpx; display: flex; align-items: center; justify-content: center; }
.up-txt { margin-left: 22rpx; display: flex; flex-direction: column; }
.up-t { font-size: 28rpx; color: #3a3a3a; }
.up-s { font-size: 21rpx; color: #a09474; margin-top: 6rpx; }
.doc-note { text-align: center; color: #b0a487; font-size: 22rpx; padding: 10rpx 0 30rpx; letter-spacing: 1rpx; }

.tip { text-align: center; font-size: 22rpx; color: #a08a5a; margin-bottom: 14rpx; }
.start { background: #163628; color: #f2e6c9; font-size: 32rpx; font-weight: 500; letter-spacing: 6rpx; text-align: center; padding: 26rpx 0; border-radius: 999rpx; box-shadow: 0 8rpx 20rpx rgba(22, 54, 40, 0.22); cursor: pointer; }
.start.off { background: transparent; color: #a8a08a; box-shadow: none; border: 2rpx dashed #cfc8b6; }

/* H5 命名弹层 */
.dlg-mask { position: fixed; inset: 0; background: rgba(20, 26, 18, 0.45); display: flex; align-items: center; justify-content: center; z-index: 999; }
.dlg { width: 560rpx; background: #fffdf8; border-radius: 24rpx; padding: 40rpx 36rpx 30rpx; box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25); }
.dlg-t { font-size: 32rpx; font-weight: 500; color: #163628; }
.dlg-i { margin-top: 28rpx; background: #f6f2e8; border: 2rpx solid #ddd0b4; border-radius: 14rpx; padding: 18rpx 22rpx; font-size: 28rpx; color: #2b2b2b; }
.dlg-btns { display: flex; justify-content: flex-end; margin-top: 34rpx; }
.dlg-btn { font-size: 28rpx; color: #8a7f66; padding: 12rpx 30rpx; border-radius: 999rpx; }
.dlg-btn.ok { background: #163628; color: #f2e6c9; margin-left: 16rpx; font-weight: 500; }
</style>
