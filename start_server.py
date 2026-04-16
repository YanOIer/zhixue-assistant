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
print("Zhixue Assistant - Starting Server")
print("=" * 60)

# 导入RAG系统
try:
    from rag_system import RAGSystem
    print("\n[1/3] RAG system module imported successfully")
except ImportError as e:
    print(f"\n[1/3] RAG system import failed: {e}")
    sys.exit(1)

# Import backend modules
try:
    from main import app, set_rag_system
    from database import init_db
    print("[2/3] Backend modules imported successfully")
except ImportError as e:
    print(f"[2/3] Backend modules import failed: {e}")
    sys.exit(1)

# Initialize RAG system
print("\n[3/3] Initializing RAG system...")
print("-" * 60)
try:
    rag = RAGSystem(
        use_hnsw=True,
        use_reranker=True,
        device='cpu'
    )
    # Set RAG system to backend
    set_rag_system(rag)
    print("-" * 60)
    print("RAG system initialized successfully")
except Exception as e:
    print(f"RAG system initialization failed: {e}")
    print("Continuing to start service, but AI features will not be available")
    rag = None

# Initialize database
print("\n[Database] Initializing...")
init_db()

# Print system info
print("\n" + "=" * 60)
print("System Information")
print("=" * 60)
if rag:
    stats = rag.get_stats()
    print(f"Document count: {stats['document_count']}")
    print(f"Chunk count: {stats['chunk_count']}")
    print(f"Vector dimension: {stats['vector_dimension']}")
    print(f"Index type: {stats['index_type']}")
print("=" * 60)

print("\nStarting server...")
print("API URL: http://localhost:8000")
print("Docs URL: http://localhost:8000/docs")
print("\nPress Ctrl+C to stop service")
print("=" * 60 + "\n")

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
