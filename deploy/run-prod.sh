# 墨衍 · 生产启动脚本（Linux / macOS）
#
# 顺序：
#   1) 加载 .env  2) 启动后端（无 reload） 3) 启 Caddy 反代
#
# 用法：
#   chmod +x deploy/run-prod.sh
#   cp .env.production.example .env  &&  vim .env   # 填真值
#   ./deploy/run-prod.sh

set -e

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "❌ .env 不存在。先：cp .env.production.example .env && vim .env"
    exit 1
fi

# 1) 加载 .env 到当前 shell（set -a 让 export 自动）
set -a
. ./.env
set +a

# 2) 检查关键配置
: "${MOYAN_JWT_SECRET:?MOYAN_JWT_SECRET 未配置（生产必填 ≥16 字符随机串）}"
: "${MOYAN_WX_APPID:?MOYAN_WX_APPID 未配置}"
: "${MOYAN_WX_APPSECRET:?MOYAN_WX_APPSECRET 未配置}"

# 3) 启 FastAPI（无 reload；worker 数量可按 CPU 调）
echo "→ 启动墨衍后端（uvicorn）"
exec uvicorn backend.main:app \
    --host "${MOYAN_HOST:-127.0.0.1}" \
    --port "${MOYAN_PORT:-5001}" \
    --workers "${MOYAN_WORKERS:-2}" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --log-level info
