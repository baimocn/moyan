"""墨衍 · 鉴权子包。

入口：
- get_current_user（deps）: FastAPI Depends() 解析 Bearer → 当前用户
- /api/auth/*（router）: wx-login / me / dev-login
"""
