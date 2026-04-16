"""
智学助手 - 简单启动脚本（不加载RAG模型）
适合前端开发和测试
"""

import sys
import os

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_module'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("Zhixue Assistant - Simple Mode (No RAG)")
print("=" * 60)

# 导入后端
from main import app, set_rag_system
from database import init_db

# 不加载RAG系统
set_rag_system(None)

# 初始化数据库
print("\n[Database] Initializing...")
init_db()

print("\n" + "=" * 60)
print("Server starting...")
print("=" * 60)
print("API URL: http://localhost:8000")
print("API Docs: http://localhost:8000/docs")
print("\nPress Ctrl+C to stop")
print("=" * 60 + "\n")

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
