<script setup>
// 墨衍 · 学习报告（M5 Phase 11 RPT-02）：接 /api/study/report，轻量 SVG 趋势
import { ref, computed, onMounted } from 'vue'
import { request } from '../api/client.js'

const rep = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    const d = await request('GET', '/api/study/report')
    rep.value = d.report || {}
  } catch (e) {
    err.value = '加载失败：' + (e.message || '未知错误')
  }
})

const trend = computed(() => rep.value?.trend || [])
const maxCount = computed(() => Math.max(1, ...trend.value.map(t => t.count)))
const M_LABEL = { low: '弱', mid: '中', high: '强' }
const weakRows = computed(() => {
  const w = rep.value?.weaknesses || {}
  return Object.entries(w).map(([m, c]) => ({ m, c }))
})
const weakTotal = computed(() => weakRows.value.reduce((a, r) => a + r.c, 0))
</script>

<template>
  <div class="report">
    <div class="route">
      <RouterLink to="/" class="lnk">← 书架</RouterLink>
      <b>学习报告</b>
      <RouterLink to="/mistakes" class="lnk">错题本 →</RouterLink>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <template v-if="rep">
      <p v-if="rep.scope_note" class="note">{{ rep.scope_note }}</p>

      <div class="cards">
        <div class="card"><b>{{ rep.teaching?.turns ?? 0 }}</b><span>教学轮次</span></div>
        <div class="card"><b>{{ rep.teaching?.sessions ?? 0 }}</b><span>学习会话</span></div>
        <div class="card"><b>{{ rep.streak_days ?? 0 }}</b><span>连续天数</span></div>
        <div class="card"><b>{{ weakTotal }}</b><span>错题总数</span></div>
      </div>

      <section class="card">
        <h2>判定趋势（近 {{ rep.days }} 天）</h2>
        <p v-if="!trend.length" class="dim">暂无判定记录。</p>
        <svg v-else :viewBox="`0 0 ${trend.length * 34 + 20} 160`" class="chart">
          <g v-for="(t, i) in trend" :key="t.date">
            <rect :x="i * 34 + 14" :y="140 - (t.count / maxCount) * 110"
                  width="22" :height="(t.count / maxCount) * 110" rx="3"
                  :fill="t.avg_score >= 0.6 ? '#2c6e3f' : (t.avg_score >= 0.4 ? '#c9a227' : '#a33')" />
            <text :x="i * 34 + 25" y="154" text-anchor="middle" class="xl">{{ t.date.slice(5) }}</text>
            <text :x="i * 34 + 25" :y="136 - (t.count / maxCount) * 110" text-anchor="middle" class="xv">
              {{ t.avg_score.toFixed(2) }}</text>
          </g>
        </svg>
        <p class="dim">柱高 = 判定次数；颜色 = 当日均分（≥0.6 绿 / ≥0.4 黄 / 低红）</p>
      </section>

      <section class="card">
        <h2>薄弱点分布</h2>
        <p v-if="!weakRows.length" class="dim">暂无薄弱点记录。</p>
        <div v-else class="wrow" v-for="r in weakRows" :key="r.m">
          <span class="badge" :class="r.m">{{ M_LABEL[r.m] || r.m }}</span>
          <b>{{ r.c }}</b>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.report { max-width: 860px; margin: 0 auto; padding: 16px; }
.route { display: flex; gap: 12px; align-items: center; margin-bottom: 14px; }
.lnk { color: #163628; text-decoration: none; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 12px; }
.card { background: #fffdf8; border: 1px solid #eee4d2; border-radius: 10px; padding: 14px; }
.card b { font-size: 24px; display: block; }
.card span { color: #8a8477; font-size: 13px; }
section.card { margin-bottom: 12px; }
h2 { font-size: 15px; margin-bottom: 10px; }
.chart { width: 100%; }
.xl { font-size: 10px; fill: #8a8477; }
.xv { font-size: 11px; fill: #163628; }
.dim { color: #8a8477; font-size: 13px; }
.wrow { display: flex; gap: 10px; align-items: center; margin: 6px 0; }
.badge { padding: 2px 10px; border-radius: 10px; font-size: 13px; }
.badge.low { background: #fde8e8; color: #a33; }
.badge.mid { background: #fdf3d8; color: #8a6d1a; }
.badge.high { background: #e2f2e5; color: #2c6e3f; }
.err { color: #a33; }
.note { background: #fdf3d8; padding: 8px 12px; border-radius: 8px; font-size: 13px; }
</style>
