"""
RAG 检索系统
============
基于 BGE-small-zh Embedding + FAISS HNSW 向量索引的本地语义检索系统。
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
from sentence_transformers import SentenceTransformer, CrossEncoder
import requests
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
    """
    查找本地已下载的模型
    
    参数:
        model_name: 模型名称，如 "BAAI/bge-small-zh"
    
    返回:
        如果本地有，返回本地路径；否则返回原模型名（会自动下载）
    
    说明:
        HuggingFace模型下载后会放在: models/models--作者--模型名/snapshots/版本号/
        我们需要找到这个路径，这样就不会重复下载了
    """
    # 如果传入的已经是路径，直接返回
    if os.path.exists(model_name):
        return model_name
    
    # 构建本地缓存路径格式
    # 例如: BAAI/bge-small-zh → models--BAAI--bge-small-zh
    local_model_name = model_name.replace('/', '--')
    local_path = os.path.join(DEFAULT_CACHE_DIR, f"models--{local_model_name}")
    
    if not os.path.exists(local_path):
        print(f"  模型未下载，将从网络下载: {model_name}")
        return model_name
    
    # 找到 snapshots 下的版本文件夹
    snapshots_dir = os.path.join(local_path, "snapshots")
    if not os.path.exists(snapshots_dir):
        return model_name
    
    # 获取最新版本文件夹
    versions = os.listdir(snapshots_dir)
    if not versions:
        return model_name
    
    # 返回完整本地路径
    model_path = os.path.join(snapshots_dir, versions[0])
    
    # 关键：检查模型权重文件是否存在（避免缓存损坏）
    # 检查常见的模型权重文件
    model_files = [
        "model.safetensors",
        "pytorch_model.bin", 
        "model.safetensors.index.json",
        "pytorch_model.bin.index.json"
    ]
    
    has_model_file = any(
        os.path.exists(os.path.join(model_path, f)) 
        for f in model_files
    )
    
    if not has_model_file:
        print(f"  警告: 本地模型缓存不完整，缺少权重文件")
        print(f"  将重新下载模型: {model_name}")
        return model_name
    
    print(f"  找到本地模型: {model_path}")
    return model_path


# ==================== 主类：RAG系统 ====================

class RAGSystem:
    """
    RAG检索系统
    
    功能：
    - 加载Embedding模型（把文字转成向量）
    - 添加文档并建立索引
    - 搜索相关文档
    - 调用大模型生成回答
    
    使用方法：
        # 1. 创建系统（会自动加载模型）
        rag = RAGSystem()
        
        # 2. 添加文档
        rag.add_document("文档内容", "文档ID")
        
        # 3. 提问
        result = rag.query("你的问题")
        print(result["answer"])
    """
    
    def __init__(
        self,
        embedding_model: str = 'BAAI/bge-small-zh',  # 默认使用小模型，省内存
        reranker_model: str = 'BAAI/bge-reranker-v2-m3',
        use_hnsw: bool = True,      # 是否用HNSW加速搜索
        use_reranker: bool = True,  # 是否用重排序（更准但更慢）
        device: str | None = None   # 'cpu' 或 'cuda'，默认自动选
    ):
        """
        初始化RAG系统
        
        参数说明：
            embedding_model: Embedding模型名或本地路径
                - 'BAAI/bge-small-zh': 小型中文模型（推荐，省内存）
                - 'BAAI/bge-large-zh': 大型中文模型（更准但更慢）
            
            reranker_model: 重排序模型名
                - 'BAAI/bge-reranker-v2-m3': 轻量级重排序
            
            use_hnsw: 是否用HNSW索引
                - True: 搜索快，适合大数据量
                - False: 简单暴力搜索，适合小数据量
            
            use_reranker: 是否启用重排序
                - True: 结果更准，但占用更多内存
                - False: 省内存，适合低配置电脑
            
            device: 计算设备
                - 'cpu': 用CPU（默认，省显存）
                - 'cuda': 用GPU（如果有的话）
                - None: 自动选择
        """
        print("=" * 60)
        print("初始化 RAG 系统")
        print("=" * 60)
        
        # 选择计算设备
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = str(device)  # 确保是字符串类型
        self.device = device
        print(f"使用设备: {device}")
        
        # ---------- 第1步：加载Embedding模型 ----------
        print(f"\n[1/3] 加载Embedding模型: {embedding_model}")
        print("      说明：首次使用会下载模型（约100-500MB），请耐心等待")
        print("            下载后保存在本地，下次使用会直接加载")
        
        # 关键：先检查本地是否有模型，有就直接用本地路径
        local_embedding_path = find_local_model(embedding_model)
        
        self.embedding_model = SentenceTransformer(
            local_embedding_path,  # 使用本地路径或模型名
            device=device,
            cache_folder=DEFAULT_CACHE_DIR
        )
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"      向量维度: {self.dimension}")
        print(f"      Model loaded")
        
        # ---------- 第2步：加载重排序模型 ----------
        self.use_reranker = use_reranker
        self.reranker = None
        
        if use_reranker:
            print(f"\n[2/3] 加载重排序模型: {reranker_model}")
            print("      说明：重排序会让结果更准确，但会占用更多内存")
            
            local_reranker_path = find_local_model(reranker_model)
            
            self.reranker = CrossEncoder(
                local_reranker_path,
                device=device,
                max_length=512,  # 限制输入长度，省内存
                cache_folder=DEFAULT_CACHE_DIR
            )
            print(f"      Model loaded")
        else:
            print(f"\n[2/3] 跳过重排序（已禁用）")
        
        # ---------- 第3步：初始化向量索引 ----------
        print(f"\n[3/3] 初始化向量索引")
        
        self.use_hnsw = use_hnsw
        
        if use_hnsw:
            # HNSW索引：搜索速度快，适合大数据量
            # 参数说明：
            #   32: 每个节点的邻居数
            #   efConstruction=200: 构建时的搜索范围（越大越准越慢）
            #   efSearch=128: 搜索时的范围
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 128
            print("      使用HNSW索引（快速搜索）")
        else:
            # 简单索引：暴力搜索，适合小数据量
            self.index = faiss.IndexFlatIP(self.dimension)
            print("      使用简单索引（暴力搜索）")
        
        # 初始化存储
        self.chunks = []           # 存储所有文本块
        self.documents = {}        # 存储文档信息
        self.inverted_index = {}   # 倒排索引（用于关键词搜索）
        self.batch_size = 32       # 批处理大小（控制内存）
        
        print("\n" + "=" * 60)
        print("RAG系统初始化完成！")
        print("=" * 60)
    
    # ==================== 文档处理 ====================
    
    def add_document(self, text: str, doc_id: str, chunk_size: int = 500, overlap: int = 100):
        """
        添加文档到知识库
        
        参数:
            text: 文档全文内容
            doc_id: 文档唯一标识（如文件名）
            chunk_size: 每个文本块的大小（字符数）
            overlap: 相邻块之间的重叠大小（让语义更连贯）
        
        示例:
            rag.add_document("这是长文档...", "article1.txt")
        """
        print(f"\n处理文档: {doc_id}")
        
        # 第1步：文本分块
        chunks = self._split_text(text, chunk_size, overlap)
        print(f"  分成 {len(chunks)} 个文本块")
        
        start_idx = len(self.chunks)  # 记录起始位置
        
        # 第2步：存储文本块，构建倒排索引
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            self.chunks.append({
                "id": chunk_id,
                "doc_id": doc_id,
                "text": chunk,
                "idx": start_idx + i
            })
            
            # 构建简单的倒排索引（关键词→文档位置）
            words = set(chunk.lower().split())
            for word in words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append(start_idx + i)
        
        # 第3步：生成向量并添加到索引
        if chunks:
            print("  生成向量表示...")
            embeddings = self._encode_texts(chunks)
            self.index.add(embeddings)
            print(f"  向量数量: {self.index.ntotal}")
        
        # 记录文档信息
        self.documents[doc_id] = {
            "chunk_count": len(chunks),
            "start_idx": start_idx,
            "text_length": len(text)
        }
        
        print(f"  Document processed")
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        把长文本切分成小块
        
        为什么要切分？
        - Embedding模型有长度限制（如512个token）
        - 小块更精准，大段文字容易稀释语义
        
        参数:
            text: 原文
            chunk_size: 每块大小
            overlap: 重叠大小（让相邻块有联系）
        
        返回:
            文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)

        # 每步前进 chunk_size - overlap，保留 overlap 大小的重叠保证语义连贯
        step = max(chunk_size - overlap, 1)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end])
            start += step  # 正确：逐步前进

        return chunks
    
    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        把文本列表转成向量
        
        使用批处理来节省内存，避免一次性处理太多文本
        """
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # encode参数说明：
            # - normalize_embeddings=True: 归一化向量（让余弦相似度计算更简单）
            # - show_progress_bar=False: 不显示内部进度条
            embeddings = self.embedding_model.encode(
                batch,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            all_embeddings.append(embeddings)
            
            # 定期清理内存
            if i % (self.batch_size * 10) == 0:
                gc.collect()
        
        # 合并所有向量
        return np.vstack(all_embeddings).astype('float32')
    
    # ==================== 搜索功能 ====================
    
    def search(self, question: str, top_k: int = 5) -> List[Dict]:
        """
        搜索相关文档
        
        参数:
            question: 查询问题
            top_k: 返回最相关的几个结果
        
        返回:
            结果列表，每个结果包含：
            - idx: 索引位置
            - doc_id: 文档ID
            - text: 文本内容
            - score: 相似度分数
        """
        if len(self.chunks) == 0:
            print("警告：知识库为空，请先添加文档")
            return []
        
        # 第1步：把问题转成向量
        query_embedding = self.embedding_model.encode(
            [question],
            normalize_embeddings=True
        )
        
        # 第2步：向量搜索
        # search返回两个数组：distances（距离）和 indices（索引）
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            top_k
        )
        
        # 第3步：组装结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            results.append({
                "idx": int(idx),
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "score": float(distances[0][i])  # 相似度分数
            })
        
        return results
    
    def rerank(self, question: str, candidates: List[Dict], top_n: int = 3) -> List[Dict]:
        """
        重排序：用更精确的模型对搜索结果重新排序
        
        为什么要重排序？
        - Embedding搜索是"粗排"，速度快但精度有限
        - CrossEncoder是"精排"，把问题和文档一起理解，更准确
        
        参数:
            question: 问题
            candidates: 候选结果（来自search）
            top_n: 最终返回几个
        """
        if not self.use_reranker or not candidates:
            return candidates[:top_n]
        
        print(f"  重排序 {len(candidates)} 个结果...")
        
        # 构建输入对：[问题, 候选文档]
        pairs = [[question, c["text"]] for c in candidates]
        
        # CrossEncoder预测相关性分数
        scores = self.reranker.predict(pairs)
        
        # 把分数加到结果中
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[i])
        
        # 按重排序分数排序
        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        
        print(f"  重排序完成，最高分: {reranked[0]['rerank_score']:.3f}")
        
        return reranked[:top_n]
    
    # ==================== 查询功能 ====================
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        完整查询流程
        
        流程：
        1. 搜索相关文档
        2. 重排序（如果启用）
        3. 构建Prompt
        4. 调用大模型生成回答（无API Key时返回检索内容）
        
        参数:
            question: 用户问题
            top_k: 召回多少个相关文档
        
        返回:
            包含answer（回答）、sources（来源）、context（上下文）的字典
        """
        print(f"\n{'=' * 60}")
        print(f"查询: {question}")
        print(f"{'=' * 60}")
        
        # 检查知识库
        if len(self.chunks) == 0:
            return {
                "answer": "知识库为空，请先上传学习资料。",
                "sources": [],
                "context": []
            }
        
        # 第1步：搜索
        print("\n[Step 1] 搜索相关文档...")
        candidates = self.search(question, top_k=top_k * 2)  # 多召回一些给重排序用
        
        if not candidates:
            return {
                "answer": "未找到相关文档，请尝试其他问题或添加更多资料。",
                "sources": [],
                "context": []
            }
        
        print(f"  找到 {len(candidates)} 个候选结果")
        
        # 第2步：重排序
        print("\n[Step 2] 重排序...")
        top_results = self.rerank(question, candidates, top_n=top_k)
        
        # 第3步：构建上下文
        print("\n[Step 3] 构建上下文...")
        context_texts = [r["text"] for r in top_results]
        context = "\n\n---\n\n".join(context_texts)
        
        # 第4步：调用大模型（无API Key时直接返回检索内容）
        print("\n[Step 4] 生成回答...")
        answer = self._call_llm(context, question)
        
        # 收集来源文档ID
        sources = list(set([r["doc_id"] for r in top_results]))
        
        print(f"\n{'=' * 60}")
        print("查询完成")
        print(f"{'=' * 60}")
        
        return {
            "answer": answer,
            "sources": sources,
            "context": context_texts
        }
    
    def _build_prompt(self, context: str, question: str) -> str:
        """
        构建给大模型的Prompt
        
        好的Prompt能让AI回答更准确
        """
        return f"""你是一个专业的学习助手。请基于以下参考资料回答用户的问题。

【参考资料】
{context}

【用户问题】
{question}

【回答要求】
1. 请严格基于参考资料回答，不要添加资料外的信息
2. 如果资料中没有相关信息，请明确说明"根据现有资料无法回答"
3. 回答要简洁、准确、有条理

请回答："""
    
    def _call_llm(self, context: str, question: str) -> str:
        """
        调用 KIMI 大模型 API 或返回检索内容
        
        需要设置环境变量 MOONSHOT_API_KEY
        """
        # 构建 prompt
        prompt = self._build_prompt(context, question)
        
        # 获取 KIMI API Key
        api_key = os.getenv("MOONSHOT_API_KEY", "sk-vtxfDn2uLrgSY0hHHr9ncdvlEkKKCr9ENkEoGGmtz7xLOUkb")
        
        if not api_key:
            print("  提示: 未配置 KIMI API Key，直接返回检索内容")
            return f"""根据本地知识库检索，找到以下相关内容：

{context}

---
💡 提示：配置 KIMI API Key (MOONSHOT_API_KEY) 可获得更智能的AI回答"""
        
        print(f"  使用 KIMI API 生成回答...")
        
        try:
            response = requests.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshot-v1-8k",  # 可选: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"  KIMI API调用失败: {e}")
            return f"调用KIMI服务失败: {str(e)}"
    
    # ==================== 保存/加载 ====================
    
    def save(self, path: str):
        """
        保存索引到文件
        
        参数:
            path: 保存路径（不含扩展名）
                例如 save("data/knowledge_base")
                会生成: knowledge_base.faiss 和 knowledge_base.json
        
        说明:
            保存后可以下次直接加载，不需要重新处理文档
        """
        try:
            # 保存FAISS索引（向量数据）
            faiss.write_index(self.index, f"{path}.faiss")
            
            # 保存文档信息（JSON格式）
            with open(f"{path}.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "chunks": self.chunks,
                    "documents": self.documents,
                    "inverted_index": self.inverted_index,
                    "dimension": self.dimension
                }, f, ensure_ascii=False, indent=2)
            
            print(f"索引已保存: {path}")
            return True
            
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    def load(self, path: str):
        """
        从文件加载索引
        
        参数:
            path: 加载路径（不含扩展名）
        
        示例:
            rag.load("data/knowledge_base")  # 加载之前保存的索引
        """
        try:
            # 加载FAISS索引
            self.index = faiss.read_index(f"{path}.faiss")
            
            # 加载文档信息
            with open(f"{path}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = data["chunks"]
                self.documents = data["documents"]
                self.inverted_index = data["inverted_index"]
            
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
        """获取系统统计信息"""
        return {
            "document_count": len(self.documents),      # 文档数量
            "chunk_count": len(self.chunks),            # 文本块数量
            "vector_dimension": self.dimension,         # 向量维度
            "index_type": "HNSW" if self.use_hnsw else "Flat",
            "device": self.device,
            "use_reranker": self.use_reranker,
            "document_list": list(self.documents.keys())
        }
    
    def clear(self):
        """清空知识库"""
        self.chunks = []
        self.documents = {}
        self.inverted_index = {}
        
        # 重新初始化索引
        if self.use_hnsw:
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 128
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
        
        print("知识库已清空")
    
    def __del__(self):
        """析构时清理资源"""
        # 删除模型释放内存
        if hasattr(self, 'embedding_model'):
            del self.embedding_model
        if hasattr(self, 'reranker'):
            del self.reranker
        gc.collect()


# 保持向后兼容
AdvancedRAGSystem = RAGSystem


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAG 系统测试")
    print("=" * 60)
    
    # 创建RAG系统
    print("\n>>> 创建RAG系统（首次会下载模型，请等待）")
    rag = RAGSystem(
        use_hnsw=True,      # 使用快速索引
        use_reranker=True,  # 启用重排序
        device='cpu'        # 使用CPU
    )
    
    # 添加测试文档
    print("\n>>> 添加测试文档")
    
    doc1 = """
    机器学习是人工智能的一个重要分支。它让计算机能够从数据中自动学习规律，
    而不需要人工编写具体规则。比如，通过看很多猫的图片，机器就能学会识别猫。
    
    机器学习主要分为三类：
    1. 监督学习：给机器看带标签的数据（如"这是猫，这是狗"）
    2. 无监督学习：让机器自己发现数据中的规律
    3. 强化学习：让机器通过试错来学习（如玩游戏）
    """
    
    doc2 = """
    深度学习是机器学习的一种方法，使用多层神经网络来模拟人脑的工作方式。
    深度学习的"深度"指的是神经网络的层数很多。
    
    深度学习在图像识别、语音识别、自然语言处理等领域取得了巨大成功。
    例如，ChatGPT就是基于深度学习的Transformer架构。
    """
    
    rag.add_document(doc1, "机器学习基础.txt")
    rag.add_document(doc2, "深度学习介绍.txt")
    
    # 打印统计
    print(f"\n>>> 系统统计: {rag.get_stats()}")
    
    # 测试查询
    print("\n>>> 测试查询")
    
    questions = [
        "什么是机器学习？",
        "深度学习和机器学习有什么区别？",
        "监督学习是什么？"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        result = rag.query(q)
        print(f"\n问题: {q}")
        print(f"回答: {result['answer'][:200]}...")
        print(f"来源: {result['sources']}")
    
    # 保存索引示例
    # print("\n>>> 保存索引")
    # rag.save("test_index")
    
    # 加载索引示例
    # print("\n>>> 加载索引")
    # rag.load("test_index")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)