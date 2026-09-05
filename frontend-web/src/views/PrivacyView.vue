<script setup>
// 墨衍 · 隐私与数据保留策略页（CMP-01，内容与 GET /api/privacy 同源）
const items = [
  {
    h: '我们收集什么',
    ps: [
      '上传的教材文件及其解析内容（章节、切片）',
      '你与 AI 同桌的完整对话（讲解、提问、判定、复习记录）',
      '学习档案：薄弱点、掌握度、复习排程',
      '用量台账（AI token 消耗）与页面浏览统计（浏览器设备标识）',
    ],
  },
  {
    h: '用来做什么',
    ps: [
      '提供并改进教学服务（讲解、判定、错题与复习）',
      '构建教学对话语料，让 AI 同桌越用越懂学习',
    ],
  },
  {
    h: '保留多久',
    ps: [
      '学习与对话数据：24 个月滚动清理',
      '用量与浏览台账：24 个月滚动清理',
      '到期的数据自动滚动删除；也可以随时请求提前删除',
    ],
  },
  {
    h: '你的权利',
    ps: [
      '免登录身份基于浏览器本地设备标识，无保密性——请不要在对话中提交敏感个人信息',
      '可联系管理员查询、导出或删除与你的设备标识关联的全部数据',
    ],
  },
]
</script>

<template>
  <div class="privacy">
    <h1>隐私与数据保留策略</h1>
    <p class="meta">版本 2026-09-05 · 墨衍 AI 同桌</p>
    <section v-for="it in items" :key="it.h">
      <h2>{{ it.h }}</h2>
      <ul><li v-for="p in it.ps" :key="p">{{ p }}</li></ul>
    </section>
    <p class="back"><RouterLink to="/">← 返回书架</RouterLink></p>
  </div>
</template>

<style scoped>
.privacy { max-width: 720px; margin: 0 auto; padding: 24px 16px; }
h1 { font-size: 22px; }
h2 { font-size: 16px; margin-top: 20px; }
.meta { color: #888; font-size: 13px; }
li { margin: 6px 0; line-height: 1.6; }
.back { margin-top: 28px; }
</style>
