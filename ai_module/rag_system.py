"""
本地语义检索系统
================
基于 BGE-small-zh Embedding + FAISS HNSW 向量索引的本地语义检索。
无需外部 API Key，完全本地运行。
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import faiss
import os
import json
import gc
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import torch

# ==================== 配置区域 ====================

# 设置国内镜像（下载更快）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 模型缓存目录（当前目录下的 models 文件夹）
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
os.environ['TRANSFORMERS_CACHE'] = DEFAULT_CACHE_DIR
os.environ['HF_HOME'] = DEFAULT_CACHE_DIR
os.environ['SENTENCE_TRANSFORMERS_HOME'] = DEFAULT_CACHE_DIR

print(f"模型缓存目录: {DEFAULT_CACHE_DIR}")


# ==================== 本地模型检测 ====================

def find_local_model(model_name: str) -> str:
    """查找本地已下载的模型。"""
    if os.path.exists(model_name):
        return model_name
    
    local_model_name = model_name.replace('/', '--')
    local_path = os.path.join(DEFAULT_CACHE_DIR, f"models--{local_model_name}")
    
    if not os.path.exists(local_path):
        print(f"  模型未下载，将从网络下载: {model_name}")
        return model_name
    
    snapshots_dir = os.path.join(local_path, "snapshots")
    if not os.path.exists(snapshots_dir):
        return model_name
    
    versions = os.listdir(snapshots_dir)
    if not versions:
        return model_name
    
    model_path = os.path.join(snapshots_dir, versions[0])
    
    model_files = ["model.safetensors", "pytorch_model.bin", "model.safetensors.index.json", "pytorch_model.bin.index.json"]
    has_model_file = any(os.path.exists(os.path.join(model_path, f)) for f in model_files)
    
    if not has_model_file:
        print(f"  警告: 本地模型缓存不完整，缺少权重文件")
        print(f"  将重新下载模型: {model_name}")
        return model_name
    
    print(f"  找到本地模型: {model_path}")
    return model_path


# ==================== 主类：RAG系统 ====================

class RAGSystem:
    """
    本地语义检索系统
    
    功能：
    - 加载 Embedding 模型（把文字转成向量）
    - 添加文档并建立索引
    - 搜索相关文档片段
    
    使用方法：
        rag = RAGSystem()
        rag.add_document("文档内容", "文档ID")
        result = rag.query("你的问题")
    """
    
    def __init__(
        self,
        embedding_model: str = 'BAAI/bge-small-zh',
        use_hnsw: bool = True,
        device: str | None = None
    ):
        """初始化 RAG 系统。"""
        print("=" * 60)
        print("初始化 RAG 系统")
        print("=" * 60)
        
        # 选择计算设备
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = str(device)
        self.device = device
        print(f"使用设备: {device}")
        
        # 加载 Embedding 模型
        print(f"\n[1/2] 加载 Embedding 模型: {embedding_model}")
        
        local_embedding_path = find_local_model(embedding_model)
        
        self.embedding_model = SentenceTransformer(
            local_embedding_path,
            device=device,
            cache_folder=DEFAULT_CACHE_DIR
        )
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"      向量维度: {self.dimension}")
        print(f"      Model loaded")
        
        # 初始化向量索引
        print(f"\n[2/2] 初始化向量索引")
        
        self.use_hnsw = use_hnsw
        
        if use_hnsw:
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 128
            print("      使用 HNSW 索引（快速搜索）")
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            print("      使用简单索引（暴力搜索）")
        
        # 初始化存储
        self.chunks = []
        self.documents = {}
        self.batch_size = 32
        
        print("\n" + "=" * 60)
        print("检索系统初始化完成！")
        print("=" * 60)
    
    # ==================== 文档处理 ====================
    
    def add_document(self, text: str, doc_id: str, chunk_size: int = 500, overlap: int = 100):
        """添加文档到知识库。"""
        print(f"\n处理文档: {doc_id}")
        
        chunks = self._split_text(text, chunk_size, overlap)
        print(f"  分成 {len(chunks)} 个文本块")
        
        start_idx = len(self.chunks)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            self.chunks.append({
                "id": chunk_id,
                "doc_id": doc_id,
                "text": chunk,
                "idx": start_idx + i
            })
        
        if chunks:
            print("  生成向量表示...")
            embeddings = self._encode_texts(chunks)
            self.index.add(embeddings)
            print(f"  向量数量: {self.index.ntotal}")
        
        self.documents[doc_id] = {
            "chunk_count": len(chunks),
            "start_idx": start_idx,
            "text_length": len(text)
        }
        
        print(f"  Document processed")
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """把长文本切分成小块。"""
        chunks = []
        start = 0
        text_length = len(text)
        step = max(chunk_size - overlap, 1)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end])
            start += step

        return chunks
    
    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        """把文本列表转成向量。"""
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = self.embedding_model.encode(
                batch,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            all_embeddings.append(embeddings)
            
            if i % (self.batch_size * 10) == 0:
                gc.collect()
        
        return np.vstack(all_embeddings).astype('float32')
    
    # ==================== 搜索功能 ====================
    
    def search(self, question: str, top_k: int = 5) -> List[Dict]:
        """搜索相关文档。"""
        if len(self.chunks) == 0:
            print("警告：知识库为空，请先添加文档")
            return []
        
        query_embedding = self.embedding_model.encode(
            [question],
            normalize_embeddings=True
        )
        
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            top_k
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            results.append({
                "idx": int(idx),
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "score": float(distances[0][i])
            })
        
        return results
    
    # ==================== 查询功能 ====================
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """完整查询流程。"""
        print(f"\n{'=' * 60}")
        print(f"查询: {question}")
        print(f"{'=' * 60}")
        
        if len(self.chunks) == 0:
            return {
                "answer": "知识库为空，请先上传学习资料。",
                "sources": [],
                "context": []
            }
        
        print("\n[Step 1] 搜索相关文档...")
        results = self.search(question, top_k=top_k)
        
        if not results:
            return {
                "answer": "未找到相关文档，请尝试其他问题或添加更多资料。",
                "sources": [],
                "context": []
            }
        
        print(f"  找到 {len(results)} 个相关结果")
        
        # 构建上下文
        print("\n[Step 2] 返回检索结果...")
        context_texts = [r["text"] for r in results]
        context = "\n\n---\n\n".join(context_texts)
        answer = self._format_answer(context, question)
        
        sources = list(set([r["doc_id"] for r in results]))
        
        print(f"\n{'=' * 60}")
        print("查询完成")
        print(f"{'=' * 60}")
        
        return {
            "answer": answer,
            "sources": sources,
            "context": context_texts
        }
    
    def _format_answer(self, context: str, question: str) -> str:
        """格式化检索结果为回答。"""
        return f"""根据本地知识库检索，找到以下相关内容：

{context}

---
📚 提示：以上内容来自知识库检索结果，如需调整检索范围，请上传更多相关资料。"""
    
    # ==================== 保存/加载 ====================
    
    def save(self, path: str):
        """保存索引到文件。"""
        try:
            faiss.write_index(self.index, f"{path}.faiss")
            
            with open(f"{path}.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "chunks": self.chunks,
                    "documents": self.documents,
                    "dimension": self.dimension
                }, f, ensure_ascii=False, indent=2)
            
            print(f"索引已保存: {path}")
            return True
            
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    def load(self, path: str):
        """从文件加载索引。"""
        try:
            self.index = faiss.read_index(f"{path}.faiss")
            
            with open(f"{path}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = data["chunks"]
                self.documents = data["documents"]
            
            print(f"索引已加载: {path}")
            print(f"  文档数: {len(self.documents)}")
            print(f"  文本块数: {len(self.chunks)}")
            return True
            
        except FileNotFoundError:
            print(f"文件不存在: {path}")
            return False
            
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    # ==================== 工具方法 ====================
    
    def get_stats(self) -> Dict:
        """获取系统统计信息。"""
        return {
            "document_count": len(self.documents),
            "chunk_count": len(self.chunks),
            "vector_dimension": self.dimension,
            "index_type": "HNSW" if self.use_hnsw else "Flat",
            "device": self.device,
            "document_list": list(self.documents.keys())
        }
    
    def clear(self):
        """清空知识库。"""
        self.chunks = []
        self.documents = {}
        
        if self.use_hnsw:
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 128
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
        
        print("知识库已清空")
    
    def __del__(self):
        """析构时清理资源。"""
        if hasattr(self, 'embedding_model'):
            del self.embedding_model
        gc.collect()


# 保持向后兼容
AdvancedRAGSystem = RAGSystem


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAG 系统测试")
    print("=" * 60)
    
    print("\n>>> 创建RAG系统")
    rag = RAGSystem(use_hnsw=True, device='cpu')
    
    print("\n>>> 添加测试文档")
    
    doc1 = """
    机器学习是人工智能的一个重要分支。它让计算机能够从数据中自动学习规律，
    而不需要人工编写具体规则。
    
    机器学习主要分为三类：
    1. 监督学习：给机器看带标签的数据
    2. 无监督学习：让机器自己发现数据中的规律
    3. 强化学习：让机器通过试错来学习
    """
    
    doc2 = """
    深度学习是机器学习的一种方法，使用多层神经网络来模拟人脑的工作方式。
    深度学习在图像识别、语音识别、自然语言处理等领域取得了巨大成功。
    """
    
    rag.add_document(doc1, "机器学习基础.txt")
    rag.add_document(doc2, "深度学习介绍.txt")
    
    print(f"\n>>> 系统统计: {rag.get_stats()}")
    
    print("\n>>> 测试查询")
    
    questions = ["什么是机器学习？", "深度学习和机器学习有什么区别？"]
    
    for q in questions:
        print(f"\n{'='*60}")
        result = rag.query(q)
        print(f"\n问题: {q}")
        print(f"回答: {result['answer'][:200]}...")
        print(f"来源: {result['sources']}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
