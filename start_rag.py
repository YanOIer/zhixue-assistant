"""
智学助手 - RAG 完整模式启动脚本
加载 RAG 模型、向量索引、历史文档，提供完整的检索增强生成能力
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── 模块路径 ──────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AI_MODULE    = os.path.join(PROJECT_ROOT, 'ai_module')
BACKEND      = os.path.join(PROJECT_ROOT, 'backend')

for p in (AI_MODULE, BACKEND):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── 加载配置（设置环境变量）─────────────────────────────────────
import config  # noqa: E402
if config.KIMI_API_KEY:
    print(f"  ✅ KIMI API Key 已配置")

# ── 颜色打印 ──────────────────────────────────────────────────
def cprint(text, color='green'):
    C = {'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m', 'end': '\033[0m'}
    print(f"{C.get(color,'')}{text}{C['end']}")

# ── Banner ────────────────────────────────────────────────────
print("=" * 62)
print("  🤖 智学助手 · RAG 完整模式")
print("  Embedding : BAAI/bge-small-zh (本地语义向量化)")
print("  向量检索  : FAISS HNSW 索引")
print("  文档分类  : Naive Bayes 词袋分类器")
print("  检索模式  : 本地语义检索（无需配置 API Key）")
print("=" * 62)

# ── 1. 初始化数据库 ────────────────────────────────────────────
print("\n[1/4] 初始化数据库...")
from database import init_db, get_all_file_contents
init_db()
cprint("  ✅ 数据库就绪", 'green')

# ── 2. 加载 / 初始化 RAG 系统 ──────────────────────────────────
print("\n[2/4] 加载 RAG 系统...")
from rag_system import RAGSystem

INDEX_PATH = os.path.join(AI_MODULE, "vector_index")
# CPU 环境默认禁用重排序（重排序模型 2.2GB，CPU 加载极慢），如需启用请改为 True
rag = RAGSystem(use_hnsw=True, use_reranker=False, device='cpu')

# 尝试加载已有索引
if os.path.exists(f"{INDEX_PATH}.faiss"):
    rag.load(INDEX_PATH)
    cprint(f"  ✅ 向量索引已加载 (文档 {len(rag.documents)} 篇，片段 {len(rag.chunks)} 块)", 'green')
else:
    cprint("  ℹ️  未找到历史索引，将从数据库重建", 'yellow')

# ── 3. 从数据库补充加载文档（索引中没有时）────────────────────
print("\n[3/4] 从数据库重建知识库（补充索引缺失的文档）...")
rows = get_all_file_contents()
loaded_ids = set(rag.documents.keys())
# get_all_file_contents() 返回列: id, filename, category, created_at, content, preview
# row[4] = content（文本内容）
missing = [(row[0], row[1], row[4]) for row in rows
           if row[1] and row[1] not in loaded_ids and row[4]]

if not missing:
    cprint("  ✅ 知识库已是最新，无需补充", 'green')
else:
    for file_id, filename, text in missing:
        if not text or not text.strip():
            continue
        rag.add_document(text, filename)
        print(f"    + 已添加: {filename}")
    rag.save(INDEX_PATH)
    cprint(f"  ✅ 补充完成，当前 {len(rag.documents)} 篇文档，{len(rag.chunks)} 个片段", 'green')

stats = rag.get_stats()
print(f"\n  📊 知识库统计：")
print(f"     文档数量 : {stats['document_count']}")
print(f"     切片数量 : {stats['chunk_count']}")
print(f"     向量维度 : {stats['vector_dimension']}")
print(f"     索引类型 : {stats['index_type']}")
print(f"     运行设备 : {stats['device']}")
print(f"     启用重排 : {'是' if stats['use_reranker'] else '否'}")

# ── 4. 挂载 RAG 到 FastAPI ────────────────────────────────────
print("\n[4/4] 启动 FastAPI 服务...")
from main import app, set_rag_system, APP_VERSION

set_rag_system(rag)

print(f"\n{'=' * 62}")
print(f"  🎉 智学助手 RAG 完整模式已启动！")
print(f"  版本    : {APP_VERSION}")
print(f"  API地址  : http://localhost:8000")
print(f"  API文档  : http://localhost:8000/docs")
print(f"  检索模式  : 本地语义检索（RAG向量检索）")
print(f"{'=' * 62}")
print("  按 Ctrl+C 停止服务")
print(f"{'=' * 62}\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
