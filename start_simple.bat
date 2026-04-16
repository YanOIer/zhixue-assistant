@echo off
chcp 65001 >nul
echo ==========================================
echo 智学助手 - 启动后端服务
echo ==========================================
echo.

:: 激活虚拟环境
call .venv\Scripts\activate

:: 设置环境变量
set PYTHONIOENCODING=utf-8

:: 启动服务
echo 正在启动服务...
echo API地址: http://localhost:8000
echo 文档地址: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ==========================================
python -c "
import sys
import os
sys.path.append('ai_module')
sys.path.append('backend')
from main import app, set_rag_system
from database import init_db
set_rag_system(None)
init_db()
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"

pause
