"""墨衍 · 本地启动入口（服务器模式：FastAPI + PostgreSQL + 异步任务）

用法：
    pip install -r requirements.txt
    python run.py
浏览器打开 http://127.0.0.1:5001
"""
import uvicorn

from backend import config

if __name__ == "__main__":
    print(f"墨衍 本地服务已启动：http://{config.HOST}:{config.PORT}")
    # 生产模式跑（reload=False）：uvicorn 的 reloader 会开 multiprocessing 子进程，
    # 在受限环境/2G 服务器上都是多余的负担
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="info",
    )