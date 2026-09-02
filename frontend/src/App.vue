<script>
import { silentLogin } from './utils/auth.js'

export default {
  onLaunch() {
    // 静默登录：MP-WEIXIN 调 wx.login → 后端 wx-login；H5 调 dev-login。
    // 失败仅 log 提示，不阻塞首屏。401 触发时 api.js 会 force 重登。
    silentLogin()
  },
}
</script>
<style>
page { background: #f6f2e8; color: #2b2b2b; }
</style>
