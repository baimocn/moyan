<template>
  <view class="pp">
    <text class="h">隐私与数据说明</text>
    <view class="sec">
      <text class="sh">收集什么</text>
      <text class="li">· 上传的教材文件与解析内容（章节、切片）</text>
      <text class="li">· 你与 AI 同桌的对话（讲解/提问/判定/复习）</text>
      <text class="li">· 学习档案：薄弱点、掌握度、复习排程</text>
      <text class="li">· 用量台账与浏览统计</text>
    </view>
    <view class="sec">
      <text class="sh">用途</text>
      <text class="li">· 提供并改进教学服务</text>
      <text class="li">· 构建教学对话语料，让同桌越用越懂学习</text>
    </view>
    <view class="sec">
      <text class="sh">保留多久</text>
      <text class="li">· 学习与对话数据 24 个月滚动清理；台账同</text>
      <text class="li">· 可经管理员通道请求提前删除</text>
    </view>
    <view class="sec">
      <text class="sh">身份说明</text>
      <text class="li">· 微信登录以 openid 标识；请勿在对话中提交敏感个人信息</text>
    </view>
    <button class="ack" @tap="ack">我已阅读并同意</button>
  </view>
</template>

<script>
export default {
  methods: {
    ack() {
      try { uni.setStorageSync('moyan:privacy_ack', 1) } catch (e) { /* 存储失败不阻断 */ }
      uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) })
    },
  },
}
</script>

<style>
.pp { padding: 20rpx 30rpx 60rpx; }
.h { font-size: 36rpx; font-weight: 600; display: block; margin-bottom: 20rpx; }
.sec { margin-bottom: 24rpx; }
.sh { font-size: 30rpx; font-weight: 600; display: block; margin-bottom: 8rpx; color: #163628; }
.li { display: block; font-size: 26rpx; color: #555; line-height: 1.8; }
.ack { margin-top: 30rpx; background: #163628; color: #f6f2e8; }
</style>
