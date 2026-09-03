<script setup>
// 登录/注册页（网页版新增；小程序端用 wx.login 无此页）
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login') // login | register
const email = ref('')
const password = ref('')
const nick = ref('')
const busy = ref(false)
const err = ref('')

function switchMode(m) {
  mode.value = m
  err.value = ''
}

async function submit() {
  if (busy.value) return
  err.value = ''
  const em = email.value.trim()
  const pw = password.value
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { err.value = '邮箱格式不正确'; return }
  if (mode.value === 'register' && pw.length < 8) { err.value = '密码至少 8 位'; return }
  if (!pw) { err.value = '请输入密码'; return }
  busy.value = true
  try {
    if (mode.value === 'register') await auth.register(em, pw, nick.value.trim())
    else await auth.login(em, pw)
    router.push('/')
  } catch (e) {
    err.value = e.message || '请求失败'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="wrap">
    <div class="card">
      <div class="hero">
        <div class="logo">墨</div>
        <div class="brand">
          <div class="bname">墨衍</div>
          <div class="bsub">AI 同桌 · 一章一章带你学透</div>
        </div>
      </div>

      <div class="tabs">
        <button class="tab" :class="{ on: mode === 'login' }" @click="switchMode('login')">登录</button>
        <button class="tab" :class="{ on: mode === 'register' }" @click="switchMode('register')">注册</button>
      </div>

      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span class="fl">邮箱</span>
          <input v-model="email" type="email" autocomplete="email" placeholder="you@example.com" />
        </label>
        <label class="field" v-if="mode === 'register'">
          <span class="fl">昵称（可选）</span>
          <input v-model="nick" type="text" maxlength="20" placeholder="同桌怎么称呼你" />
        </label>
        <label class="field">
          <span class="fl">密码</span>
          <input v-model="password" type="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
                 :placeholder="mode === 'register' ? '至少 8 位' : '密码'" />
        </label>

        <div class="err" v-if="err">{{ err }}</div>

        <button class="go" type="submit" :disabled="busy">
          {{ busy ? '请稍候…' : (mode === 'login' ? '登录' : '注册并开始') }}
        </button>
      </form>

      <p class="note">同桌已就位。规矩：先思路，后对答案。</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.card { width: 100%; max-width: 400px; background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 32px 30px 24px; box-shadow: 0 12px 40px rgba(22, 54, 40, 0.10); }

.hero { display: flex; align-items: center; margin-bottom: 26px; }
.logo { width: 52px; height: 52px; border-radius: 16px; background: var(--ink); color: #f2e6c9; font-size: 28px; font-weight: 500; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(22, 54, 40, 0.18); }
.brand { margin-left: 14px; }
.bname { font-size: 26px; font-weight: 500; letter-spacing: 6px; color: var(--ink); line-height: 1.15; }
.bsub { font-size: 12px; color: var(--tx-2); margin-top: 3px; letter-spacing: 1px; }

.tabs { display: flex; background: var(--paper); border-radius: 999px; padding: 4px; margin-bottom: 22px; }
.tab { flex: 1; border: 0; background: transparent; color: var(--tx-2); font-size: 14px; padding: 8px 0; border-radius: 999px; cursor: pointer; transition: all .15s; }
.tab.on { background: var(--ink); color: #f2e6c9; font-weight: 500; }

.form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.fl { font-size: 12px; color: var(--tx-2); }
.field input { background: var(--paper); border: 1px solid #ddd0b4; border-radius: 10px; padding: 11px 13px; font-size: 14px; color: var(--tx); outline: none; transition: border-color .15s; }
.field input:focus { border-color: var(--ink-soft); }

.err { font-size: 13px; color: var(--err); background: #fdf3ef; border: 1px solid #f0d5cc; border-radius: 8px; padding: 8px 12px; }

.go { margin-top: 6px; border: 0; background: var(--ink); color: #f2e6c9; font-size: 16px; font-weight: 500; letter-spacing: 4px; padding: 13px 0; border-radius: 999px; cursor: pointer; box-shadow: 0 6px 16px rgba(22, 54, 40, 0.22); transition: opacity .15s; }
.go:disabled { opacity: 0.6; cursor: default; }

.note { text-align: center; color: #b0a487; font-size: 12px; margin: 18px 0 0; letter-spacing: 1px; }
</style>
