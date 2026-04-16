"""
智学助手 - 完整启动脚本
启动后端服务和RAG系统
"""

import sys
import os

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_module'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("智学助手 - 启动服务器")
print("=" * 60)

# 导入RAG系统
try:
    from rag_system import RAGSystem
    print("\n[1/3] RAG系统模块导入成功 ✓")
except ImportError as e:
    print(f"\n[1/3] RAG系统导入失败: {e}")
    sys.exit(1)

# 导入后端应用
try:
    from main import app, set_rag_system
    from database import init_db
    print("[2/3] 后端模块导入成功 ✓")
except ImportError as e:
    print(f"[2/3] 后端模块导入失败: {e}")
    sys.exit(1)

# 初始化RAG系统
print("\n[3/3] 初始化RAG系统...")
print("-" * 60)
try:
    rag = RAGSystem(
        use_hnsw=True,
        use_reranker=True,
        device='cpu'
    )
    # 将RAG系统设置到后端
    set_rag_system(rag)
    print("-" * 60)
    print("RAG系统初始化完成 ✓")
except Exception as e:
    print(f"RAG系统初始化失败: {e}")
    print("将继续启动服务，但AI功能不可用")
    rag = None

# 初始化数据库
print("\n[数据库] 初始化...")
init_db()

# 打印系统信息
print("\n" + "=" * 60)
print("系统信息")
print("=" * 60)
if rag:
    stats = rag.get_stats()
    print(f"文档数量: {stats['document_count']}")
    print(f"文本块数: {stats['chunk_count']}")
    print(f"向量维度: {stats['vector_dimension']}")
    print(f"索引类型: {stats['index_type']}")
print("=" * 60)

print("\n🚀 启动服务器...")
print("API地址: http://localhost:8000")
print("文档地址: http://localhost:8000/docs")
print("\n按 Ctrl+C 停止服务")
print("=" * 60 + "\n")

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
