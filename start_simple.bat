@echo off
chcp 65001 >nul
echo ==========================================
echo  智学助手 - 启动后端服务（简单模式）
echo ==========================================
echo.
echo  API地址:  http://localhost:8000
echo  API文档:  http://localhost:8000/docs
echo.
echo  按 Ctrl+C 停止服务
echo ==========================================

set PYTHONIOENCODING=utf-8

:: 优先使用虚拟环境
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe start_simple.py
) else (
    python start_simple.py
)

pause
