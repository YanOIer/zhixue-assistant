@echo off
chcp 65001 >nul
echo ==========================================
echo 智学助手 - 启动完整服务（含RAG）
echo ==========================================
echo.
echo 注意：首次启动会下载模型（约500MB）
echo.

:: 激活虚拟环境
call .venv\Scripts\activate

:: 设置环境变量
set PYTHONIOENCODING=utf-8

:: 启动完整服务
python start_server.py

pause
