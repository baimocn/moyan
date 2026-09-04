<template>
  <view class="page">
    <view class="hero">
      <view class="logo">墨</view>
      <view class="brand">
        <text class="bname">墨衍</text>
        <text class="bsub">AI 同桌 · 一章一章带你学透</text>
      </view>
      <view class="up-btn" @tap="choose">
        <text class="up-btn-t">{{ uploading ? '上传中…' : '＋ 上传' }}</text>
      </view>
    </view>

    <!-- 共享书库搜索（v2 同步）：hero 下方通栏，300ms 防抖 -->
    <view class="search">
      <input
        class="s-input"
        v-model="searchQ"
        placeholder="搜索共享书库"
        placeholder-style="color:#a09474;font-size:28rpx"
        confirm-type="search"
        @confirm="searchNow"
      />
      <text class="s-clear" v-if="searchQ" @tap="clearSearch">×</text>
    </view>

    <view v-if="last && last.label" class="resume" @tap="resumeLast">
      <view class="ri">
        <text class="rit">继续上次</text>
        <text class="risub">上次学到这里 · {{ last.label }}</text>
      </view>
      <view class="rgo">继续 →</view>
    </view>

    <view class="sec">
      <text class="sec-t">{{ searching ? '搜索中…' : (searchQ ? '搜索结果' : '共享书架') }}</text>
      <text class="sec-c" v-if="docs.length">{{ docs.length }} 本就绪 · 大家传过的都能用</text>
    </view>

    <scroll-view scroll-y class="list">
      <view v-for="(d, i) in docs" :key="d.doc_id" class="doc" :class="{ sel: i === docIdx }" @tap="onDocPick(i)">
        <view class="doc-top">
          <text class="doc-title">{{ d.display_title || d.title || cleanName(d.filename) }}</text>
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

      <view class="empty" v-if="!docs.length">
        <view class="e-t">{{ searchQ ? '没找到相关的书' : '书架还是空的' }}</view>
        <view class="e-s">{{ searchQ ? '换个词试试，或从聊天记录把书传上来' : '搜索大家传过的书，或点右上角「＋ 上传」传你的第一本教材' }}</view>
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
      docs: [], docIdx: -1, chapIdx: -1, manifest: [], tip: '', polling: false, last: null,
      searchQ: '', searching: false, uploading: false,
      dlg: { show: false, mode: '', title: '', ph: '', val: '' }, pending: null
    }
  },
  watch: {
    // 搜索 300ms 防抖（网页 v2 同款节奏）
    searchQ() {
      clearTimeout(this._st)
      this._st = setTimeout(() => this.searchNow(), 300)
    }
  },
  computed: {
    docNames() { return this.docs.map(d => `${d.display_title || d.title || this.cleanName(d.filename)}（${d.chapter_count}章）`) },
    chapNames() { return this.manifest.map(c => `${c.title}（${c.char_count}字）`) },
    ready() { return this.docIdx >= 0 && this.chapIdx >= 0 }
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
    refresh(selectId) {
      // 搜索词非空时即搜索请求（书架与搜索共用同一列表管线）
      const q = (this.searchQ || '').trim()
      this._lastQ = q
      return getDocuments(q).then(d => {
        if (this._lastQ !== q) return // 竞态保护：仅采纳最后一次请求
        const done = (d.documents || []).filter(x => x.status === 'done')
        const curId = selectId || (this.docIdx >= 0 && this.docs[this.docIdx] ? this.docs[this.docIdx].doc_id : '')
        this.docs = done
        const idx = curId ? done.findIndex(x => x.doc_id === curId) : -1
        this.docIdx = idx
        if (idx < 0) { this.manifest = []; this.chapIdx = -1 }
      })
    },
    searchNow() {
      const q = (this.searchQ || '').trim()
      this.searching = true
      // 不用 .finally：部分低版本基础库不 polyfill
      const done = () => { if (this._lastQ === q) this.searching = false }
      this.refresh().then(done, done)
    },
    clearSearch() {
      this.searchQ = ''
      clearTimeout(this._st)
      this.searching = false
      this.refresh()
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
    // 本地兜底：后端未返回 display_title 时去文档扩展名
    cleanName(n) {
      return ((n || '').replace(/\.(pdf|md|docx|doc|txt|wps)$/i, '').trim() || '未命名教材')
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
      this.tip = ''
      this.uploading = true
      uni.showLoading({ title: '解析中', mask: true })
      uploadFile(file, title).then(r => {
        uni.hideLoading()
        this.uploading = false
        if (!r || !r.ok) {
          // 429 限流：后端返回 {ok:false, detail, retry_after}
          if (r && r.retry_after) this.tip = `上传太频繁，约 ${Math.max(1, Math.ceil(r.retry_after / 60))} 分钟后再试`
          else this.tip = '上传失败：' + ((r && r.detail) || '未知错误')
          return
        }
        if (r.reused) {
          // 共享书库去重命中：同书秒回，自动选中并展开章节
          this.tip = '书库已有此书，直接使用 ✓'
          this.refresh(r.doc_id).then(() => {
            const doc = this.docs[this.docIdx]
            if (!doc) return
            return getDocument(doc.doc_id).then(d => { this.manifest = d.document.manifest || [] })
          }).catch(() => {})
          return
        }
        if (r.status === 'processing') {
          this.tip = '转换中，请稍候…'
          this.pollTask(r.task_id, r.doc_id)
        } else {
          this.tip = '已上架 ✓'
          this.refresh()
        }
      }).catch(e => { uni.hideLoading(); this.uploading = false; this.tip = '上传失败：' + e })
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
        content: d.display_title || d.title || this.cleanName(d.filename),
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
.page { height: 100vh; display: flex; flex-direction: column; padding: 32rpx 28rpx 24rpx; box-sizing: border-box; max-width: 760px; margin: 0 auto; width: 100%; }
/* #ifdef H5 */
/* uni h5 页面头占 44px，min-height:100vh 会把 .foot 顶出视口（2026-09-03 实测 foot 在 y≈1790） */
.page { height: calc(100vh - 44px); }
/* #endif */
.foot { padding-top: 20rpx; max-width: 760px; margin: 0 auto; width: 100%; box-sizing: border-box; }

.resume { display: flex; align-items: center; background: linear-gradient(135deg, #163628 0%, #2c6e4f 100%); color: #f2e6c9; border-radius: 20rpx; padding: 22rpx 26rpx; margin-bottom: 20rpx; box-shadow: 0 6rpx 16rpx rgba(22, 54, 40, 0.18); }
.ri { flex: 1; display: flex; flex-direction: column; }
.rit { font-size: 27rpx; font-weight: 500; letter-spacing: 2rpx; }
.risub { font-size: 22rpx; color: #d8c9a0; margin-top: 6rpx; }
.rgo { font-size: 26rpx; color: #f2e6c9; padding: 8rpx 22rpx; border: 2rpx solid #f2e6c9; border-radius: 999rpx; }

.hero { display: flex; align-items: center; padding: 12rpx 4rpx 20rpx; }
.logo { width: 84rpx; height: 84rpx; border-radius: 26rpx; background: #163628; color: #f2e6c9; font-size: 44rpx; font-weight: 500; display: flex; align-items: center; justify-content: center; letter-spacing: 0; box-shadow: 0 6rpx 16rpx rgba(22, 54, 40, 0.18); }
.brand { flex: 1; margin-left: 22rpx; display: flex; flex-direction: column; min-width: 0; }
.bname { font-size: 44rpx; font-weight: 500; letter-spacing: 10rpx; color: #163628; line-height: 1.15; }
.bsub { font-size: 22rpx; color: #8a7f66; margin-top: 6rpx; letter-spacing: 2rpx; }

/* 右上角上传小按钮（D1：书多时底部卡够不着，收进顶栏） */
.up-btn { flex-shrink: 0; background: #163628; color: #f2e6c9; border-radius: 999rpx; padding: 14rpx 26rpx; box-shadow: 0 6rpx 14rpx rgba(22, 54, 40, 0.2); }
.up-btn-t { font-size: 26rpx; font-weight: 500; letter-spacing: 1rpx; }

/* 共享书库搜索（D2：hero 下方通栏，网页 v2 同款观感）
   真机注意：input 不设显式 height 时默认行高偏小会裁字，必须 height+line-height 撑足 */
.search { position: relative; margin-bottom: 18rpx; }
.s-input { width: 100%; height: 88rpx; box-sizing: border-box; background: #fffdf8; border: 2rpx solid #eae2cf; border-radius: 999rpx; padding: 0 72rpx 0 32rpx; font-size: 29rpx; line-height: 84rpx; color: #2b2b2b; }
.s-clear { position: absolute; right: 24rpx; top: 50%; transform: translateY(-50%); width: 44rpx; height: 44rpx; border-radius: 50%; background: #efe8d8; color: #8a7f66; font-size: 30rpx; display: flex; align-items: center; justify-content: center; }

.sec { display: flex; align-items: baseline; justify-content: space-between; padding: 8rpx 6rpx 18rpx; }
.sec-t { font-size: 30rpx; font-weight: 500; color: #2b2b2b; }
.sec-c { font-size: 22rpx; color: #9a8f74; }

.list { flex: 1; min-height: 0; }
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

/* 空态（书架空 / 搜索无结果） */
.empty { background: #fffdf8; border: 2rpx dashed #ddd0b4; border-radius: 24rpx; padding: 60rpx 40rpx; text-align: center; margin-bottom: 20rpx; }
.e-t { font-size: 30rpx; font-weight: 500; color: #3a3a3a; }
.e-s { font-size: 23rpx; color: #a09474; margin-top: 14rpx; line-height: 1.6; }

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
