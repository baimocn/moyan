# 墨衍 · 生产部署指南

> 适用于 Caddy 2 反代 + ACME 自动证书 + 本机 FastAPI 后端。
> 部署前置已完成：鉴权（微信 openid + JWT）+ 限流（slowapi user_id 主 / IP 兑底）。

## 0. 准备

| 组件 | 要求 | 备注 |
|---|---|---|
| 操作系统 | Linux / macOS / Windows | Windows 路径示例给出 |
| Python | 3.13（主）+ .docling-venv（3.13） | `.docling-venv` 见 `tools/docling_worker.py` |
| 域名 | moyan.example.com A/AAAA 解析到本机 | Caddy 自动 ACME |
| 端口 | 80, 443, 5001 | 80/443 给 Caddy，5001 给 FastAPI（监听 127.0.0.1） |
| 数据库 | PostgreSQL 14+（推荐）/ SQLite 3（demo） | `MOYAN_DB_URL=postgresql+psycopg2://...` |

## 1. 拉取代码 + 装依赖

```bash
git clone <repo> moyan && cd moyan
pip install -r requirements.txt

# Docling 子环境（按需）
uv venv --python 3.13 .docling-venv
.docling-venv/Scripts/python -m pip install docling onnxruntime rapidocr_onnxruntime
```

## 2. 配 .env

```bash
cp .env.production.example .env
vim .env
```

必填项：
- `MOYAN_WX_APPID` / `MOYAN_WX_APPSECRET`  ← 微信小程序后台
- `MOYAN_JWT_SECRET`  ← `python -c "import secrets;print(secrets.token_urlsafe(48))"`
- `MOYAN_AUTH_DISABLED=0`  ← 生产必 0
- `MOYAN_DB_URL`  ← 指向 PostgreSQL
- `MOYAN_AI_MAIN_*`  ← 教学对话 AI key

## 3. 启后端

```bash
# Linux / macOS
chmod +x deploy/run-prod.sh
./deploy/run-prod.sh

# Windows
powershell -ExecutionPolicy Bypass -File deploy/run-prod.ps1
```

后端监听 127.0.0.1:5001（仅本机，由 Caddy 代理出公网）。

## 4. 装 + 启 Caddy

Caddyfile 用了 `rate_limit` 指令（防穿透兜底），属于第三方模块 `github.com/mholt/caddy-ratelimit`，**标准 caddy 二进制不包含**，需用 xcaddy 自带。

```bash
# 方式 A：标准 caddy（不含 rate_limit）
#   - 后端 slowapi 仍是主防线
#   - Caddy 兜底失效，功能可降级运行
# Ubuntu:
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy

# 方式 B（推荐）：xcaddy 自带 rate_limit 模块
go install github.com/caddyserver/xcaddy/cmd/xcaddy@latest
~/go/bin/xcaddy build --with github.com/mholt/caddy-ratelimit
sudo mv caddy /usr/local/bin/

# 配置域名（先导环境变量）
export MOYAN_DOMAIN=moyan.example.com
export [email protected]

# 跑
caddy run --config deploy/Caddyfile
```

**校验 Caddyfile 语法**（改完配置后必须跑）：
```bash
caddy validate --config deploy/Caddyfile --adapter caddyfile
# 输出 "valid configuration" 即通过
```

## 5. 验证

```bash
# 健康
curl https://moyan.example.com/api/health
# 鉴权（拿 token）
curl -X POST https://moyan.example.com/api/auth/wx-login \
     -H 'Content-Type: application/json' \
     -d '{"code":"<jscode>"}'
# 鉴权后调教学
curl -X POST https://moyan.example.com/api/tutor/start \
     -H 'Authorization: Bearer <token>' \
     -H 'Content-Type: application/json' \
     -d '{"doc_id":"...","chapter_index":0}'
```

## 6. 限流档位（slowapi + Caddy 兜底）

| 端点 | 档位 | 维度 |
|---|---|---|
| `/api/tutor/*` | 30 / 分钟 | user_id（无鉴权走 IP） |
| `/api/upload` | 5 / 小时 | user_id（无鉴权走 IP） |
| `/api/auth/*` | 30 / 分钟 | Caddy 兜底 30r/m |
| `/api/upload` | 5r/m | Caddy 兜底 |

429 响应：`{"ok": false, "detail": "...", "retry_after": 60}` + `Retry-After` header。

## 7. 回滚

```bash
# 后端回滚
git checkout HEAD~1 -- backend/
pkill -f "uvicorn backend.main" && ./deploy/run-prod.sh

# Caddy 回滚
caddy stop
# 修 Caddyfile 后 caddy run --config deploy/Caddyfile
```

## 8. 监控建议

- 后端：`/api/health` 含 DB 引擎、AI 引擎 ready 状态、mock 标记 → 接 Uptime Kuma / Prometheus
- Caddy：自带 access log（stdout）→ `caddy run | tee /var/log/moyan/caddy.log`
- 数据库：PostgreSQL 走常规 `pg_dump` 每日备份

## 9. 已知前置

- 微信小程序后台 → 服务器域名白名单：moyan.example.com
- 微信 Web 授权（如用 H5 网页版）：mp.weixin.qq.com 后台 → 网页授权域名 同上
- 端口开放：443（公网），5001 仅 127.0.0.1 监听
