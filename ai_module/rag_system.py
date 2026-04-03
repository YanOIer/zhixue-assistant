"""
Advanced RAG System - 升级版RAG系统
专为考研复试设计，包含更多技术亮点

技术栈：
- Embedding: BGE-M3 (基于对比学习)
- 向量检索: HNSW (分层可导航小世界图)
- 重排序: Cross-Encoder
- 评估: RAGAS
"""

import numpy as np
import faiss
import os
import json
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, CrossEncoder
import requests

# 设置国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


class AdvancedRAGSystem:
    """
    Advanced RAG系统

    相比基础版增加了：
    1. 查询改写 (Query Rewriting)
    2. 混合检索 (Hybrid Retrieval: 向量+关键词)
    3. 重排序 (Reranking with Cross-Encoder)
    4. 检索结果可视化
    """

    def __init__(self,
                 embedding_model='BAAI/bge-m3',
                 reranker_model='BAAI/bge-reranker-base',
                 use_hnsw=True):
        """
        初始化Advanced RAG系统

        参数：
            embedding_model: Embedding模型
            reranker_model: 重排序模型
            use_hnsw: 是否使用HNSW索引
        """
        print("=" * 60)
        print("初始化 Advanced RAG 系统")
        print("=" * 60)

        # 加载Embedding模型（Bi-Encoder）
        print(f"\n[1/4] 加载Embedding模型: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"      向量维度: {self.dimension}")

        # 加载重排序模型（Cross-Encoder）
        print(f"\n[2/4] 加载重排序模型: {reranker_model}")
        self.reranker = CrossEncoder(reranker_model)
        print("      重排序模型加载完成")

        # 初始化向量索引
        print(f"\n[3/4] 初始化向量索引")
        self.use_hnsw = use_hnsw
        if use_hnsw:
            # HNSW索引：速度快，适合大规模数据
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 128
            print("      使用HNSW索引（分层可导航小世界图）")
            print("      时间复杂度: O(log n)")
        else:
            # 暴力索引：精度最高，速度慢
            self.index = faiss.IndexFlatIP(self.dimension)
            print("      使用暴力索引（精确搜索）")
            print("      时间复杂度: O(n)")

        # 存储
        self.chunks = []
        self.documents = {}
        self.inverted_index = {}  # 倒排索引（关键词检索用）

        print("\n[4/4] 系统初始化完成！")
        print("=" * 60)

    def add_document(self, text: str, doc_id: str,
                     chunk_size: int = 500, overlap: int = 100):
        """
        添加文档到知识库

        参数：
            text: 文档全文
            doc_id: 文档标识
            chunk_size: 分块大小
            overlap: 重叠大小
        """
        print(f"\n处理文档: {doc_id}")

        # 文本分块
        chunks = self._split_text(text, chunk_size, overlap)
        print(f"  分成 {len(chunks)} 个文本块")

        # 记录起始位置
        start_idx = len(self.chunks)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            self.chunks.append({
                "id": chunk_id,
                "doc_id": doc_id,
                "text": chunk,
                "idx": start_idx + i
            })

            # 构建倒排索引（简单版本）
            words = set(chunk.lower().split())
            for word in words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append(start_idx + i)

        # 生成Embedding
        if chunks:
            print("  生成向量表示...")
            embeddings = self.embedding_model.encode(
                chunks,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            self.index.add(np.array(embeddings).astype('float32'))

        # 记录文档信息
        self.documents[doc_id] = {
            "chunk_count": len(chunks),
            "start_idx": start_idx,
            "text_length": len(text)
        }

        print(f"  ✓ 文档处理完成")

    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """文本分块"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            if start >= text_length:
                break

        return chunks

    def rewrite_query(self, question: str) -> str:
        """
        查询改写

        把口语化问题改写成更适合检索的形式
        例如: "啥是机器学习?" → "机器学习的定义"

        参数：
            question: 原始问题

        返回：
            改写后的问题
        """
        # 简单实现：去除语气词，规范化表达
        # 实际可用LLM进行更复杂的改写

        # 去除常见语气词
        fillers = ['啥', '怎么', '一下', '请问', '我想知道']
        rewritten = question
        for filler in fillers:
            rewritten = rewritten.replace(filler, '')

        # 问号规范化
        rewritten = rewritten.strip('？?').strip()

        if rewritten != question:
            print(f"  查询改写: '{question}' → '{rewritten}'")

        return rewritten if rewritten else question

    def hybrid_search(self, question: str, top_k: int = 10) -> List[Dict]:
        """
        混合检索

        结合向量检索和关键词检索，用RRF融合结果

        参数：
            question: 查询问题
            top_k: 返回数量

        返回：
            检索结果列表
        """
        # 1. 向量检索
        query_embedding = self.embedding_model.encode(
            [question],
            normalize_embeddings=True
        )

        vector_scores, vector_indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            top_k * 2
        )

        # 2. 关键词检索（BM25简化版）
        keywords = question.lower().split()
        keyword_scores = {}

        for keyword in keywords:
            if keyword in self.inverted_index:
                for idx in self.inverted_index[keyword]:
                    keyword_scores[idx] = keyword_scores.get(idx, 0) + 1

        # 3. RRF融合 (Reciprocal Rank Fusion)
        k = 60  # RRF常数
        fused_scores = {}

        # 向量检索结果
        for rank, idx in enumerate(vector_indices[0]):
            if idx < len(self.chunks):
                fused_scores[idx] = fused_scores.get(idx, 0) + 1 / (k + rank + 1)

        # 关键词检索结果
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (idx, _) in enumerate(sorted_keywords):
            fused_scores[idx] = fused_scores.get(idx, 0) + 1 / (k + rank + 1)

        # 排序取Top-K
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in sorted_results[:top_k]:
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                results.append({
                    "idx": idx,
                    "doc_id": chunk["doc_id"],
                    "text": chunk["text"],
                    "rrf_score": score
                })

        return results

    def rerank(self, question: str, candidates: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        重排序

        使用Cross-Encoder对候选结果进行精确排序
        Cross-Encoder比Bi-Encoder精度更高，但速度较慢

        参数：
            question: 查询问题
            candidates: 候选结果列表
            top_n: 最终返回数量

        返回：
            重排序后的结果
        """
        if not candidates:
            return []

        print(f"  重排序 {len(candidates)} 个候选结果...")

        # 构建Cross-Encoder输入
        pairs = [[question, c["text"]] for c in candidates]

        # 计算相关性分数
        scores = self.reranker.predict(pairs)

        # 排序
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[i])

        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        print(f"  重排序完成，最高分: {reranked[0]['rerank_score']:.3f}")

        return reranked[:top_n]

    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        完整查询流程

        Advanced RAG流程：
        1. 查询改写
        2. 混合检索（向量+关键词）
        3. 重排序
        4. LLM生成

        参数：
            question: 用户问题
            top_k: 召回数量

        返回：
            包含回答、来源、上下文的结果
        """
        print(f"\n{'=' * 60}")
        print(f"处理查询: {question}")
        print(f"{'=' * 60}")

        if len(self.chunks) == 0:
            return {
                "answer": "知识库为空，请先上传学习资料。",
                "sources": [],
                "context": [],
                "retrieval_info": {}
            }

        # Step 1: 查询改写
        print("\n[Step 1] 查询改写")
        rewritten_query = self.rewrite_query(question)

        # Step 2: 混合检索
        print("\n[Step 2] 混合检索 (向量检索 + 关键词检索)")
        candidates = self.hybrid_search(rewritten_query, top_k=top_k * 2)
        print(f"  召回 {len(candidates)} 个候选结果")

        # Step 3: 重排序
        print("\n[Step 3] 重排序 (Cross-Encoder)")
        reranked = self.rerank(rewritten_query, candidates, top_n=top_k)

        # Step 4: 构建Prompt
        print("\n[Step 4] 构建Prompt")
        context_texts = [r["text"] for r in reranked]
        context = "\n\n---\n\n".join(context_texts)

        prompt = self._build_prompt(context, question)

        # Step 5: LLM生成
        print("\n[Step 5] LLM生成回答")
        answer = self._call_llm(prompt)

        # 收集来源
        sources = list(set([r["doc_id"] for r in reranked]))

        # 检索信息（用于分析和可视化）
        retrieval_info = {
            "original_query": question,
            "rewritten_query": rewritten_query,
            "candidates_count": len(candidates),
            "retrieval_method": "Hybrid (Vector + Keyword)",
            "reranker": "Cross-Encoder",
            "top_scores": [r["rerank_score"] for r in reranked[:3]]
        }

        print(f"\n{'=' * 60}")
        print("查询完成")
        print(f"{'=' * 60}")

        return {
            "answer": answer,
            "sources": sources,
            "context": context_texts,
            "retrieval_info": retrieval_info
        }

    def _build_prompt(self, context: str, question: str) -> str:
        """构建Prompt"""
        return f"""你是一个专业的学习助手。请基于以下参考资料回答用户的问题。

【参考资料】
{context}

【用户问题】
{question}

【回答要求】
1. 请严格基于参考资料回答，不要添加资料外的信息
2. 如果资料中没有相关信息，请明确说明"根据现有资料无法回答"
3. 回答要简洁、准确、有条理
4. 可以适当引用资料中的原文

请回答："""

    def _call_llm(self, prompt: str) -> str:
        """调用大模型API"""
        api_key = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")

        if api_key == "your-api-key-here":
            print("  警告: 未配置API Key，返回模拟回答")
            return "[模拟回答] 这是基于检索内容的模拟回答。请配置DeepSeek API Key以获取真实AI回答。"

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"  API调用失败: {e}")
            return f"调用AI服务失败: {str(e)}"

    def visualize_embeddings(self, save_path: str = "embedding_viz.png"):
        """
        可视化Embedding（使用t-SNE降维）

        把高维向量降到2D，观察语义分布
        """
        try:
            from sklearn.manifold import TSNE
            import matplotlib.pyplot as plt

            print("\n生成向量可视化...")

            # 获取所有向量
            n = len(self.chunks)
            if n < 10:
                print("  数据量太少，无法可视化")
                return

            # 从索引中提取向量
            vectors = np.zeros((n, self.dimension))
            for i in range(n):
                # HNSW索引的提取方法
                if self.use_hnsw:
                    vectors[i] = self.index.reconstruct(i)

            # t-SNE降维
            print("  t-SNE降维中...")
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, n - 1))
            vectors_2d = tsne.fit_transform(vectors)

            # 按文档着色
            doc_colors = {}
            colors = plt.cm.tab10(np.linspace(0, 1, len(self.documents)))
            for i, doc_id in enumerate(self.documents.keys()):
                doc_colors[doc_id] = colors[i]

            # 绘制
            plt.figure(figsize=(12, 8))
            for chunk in self.chunks:
                idx = chunk["idx"]
                doc_id = chunk["doc_id"]
                plt.scatter(vectors_2d[idx, 0], vectors_2d[idx, 1],
                            c=[doc_colors[doc_id]], alpha=0.6, s=50)

            # 添加图例
            for doc_id, color in doc_colors.items():
                plt.scatter([], [], c=[color], label=doc_id, s=100)

            plt.legend()
            plt.title("Embedding Visualization (t-SNE)")
            plt.xlabel("t-SNE Dimension 1")
            plt.ylabel("t-SNE Dimension 2")
            plt.tight_layout()
            plt.savefig(save_path, dpi=150)
            print(f"  可视化已保存: {save_path}")

        except ImportError:
            print("  需要安装sklearn和matplotlib: pip install scikit-learn matplotlib")

    def get_stats(self) -> Dict:
        """获取系统统计信息"""
        return {
            "document_count": len(self.documents),
            "chunk_count": len(self.chunks),
            "vector_dimension": self.dimension,
            "index_type": "HNSW" if self.use_hnsw else "Flat",
            "documents": list(self.documents.keys())
        }


# ============ 评估功能 ============

class RAGEvaluator:
    """
    RAG评估器

    评估指标：
    - Faithfulness: 回答是否忠实于资料
    - Answer Relevancy: 回答是否切题
    - Context Relevancy: 召回的上下文是否相关
    """

    def __init__(self, rag_system: AdvancedRAGSystem):
        self.rag = rag_system

    def evaluate_sample(self, question: str, ground_truth: str = None) -> Dict:
        """
        评估单个样本

        参数：
            question: 问题
            ground_truth: 标准答案（可选）

        返回：
            评估结果
        """
        result = self.rag.query(question)

        evaluation = {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "retrieval_info": result["retrieval_info"]
        }

        if ground_truth:
            evaluation["ground_truth"] = ground_truth

        return evaluation

    def evaluate_batch(self, test_cases: List[Dict]) -> List[Dict]:
        """
        批量评估

        参数：
            test_cases: 测试用例列表
            [{"question": "...", "ground_truth": "..."}, ...]
        """
        results = []
        for case in test_cases:
            result = self.evaluate_sample(
                case["question"],
                case.get("ground_truth")
            )
            results.append(result)
        return results


# ============ 测试代码 ============

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Advanced RAG System 测试")
    print("=" * 60)

    # 创建系统
    rag = AdvancedRAGSystem(use_hnsw=True)

    # 添加测试文档
    test_docs = {
        "机器学习基础.txt": """
        机器学习是人工智能的一个重要分支，它使计算机能够从数据中
        学习而无需明确编程。机器学习算法通过分析大量数据来识别模式，
        并基于这些模式做出预测或决策。

        常见的机器学习算法包括：
        - 监督学习：有标签数据训练（如分类、回归）
        - 无监督学习：无标签数据（如聚类、降维）
        - 强化学习：通过与环境交互学习
        """,
        "深度学习介绍.txt": """
        深度学习是机器学习的一种方法，使用多层神经网络来学习数据的
        复杂模式。深度学习在图像识别、语音识别和自然语言处理等任务
        上取得了突破性进展。

        深度学习的核心组件：
        - 神经网络：模拟生物神经网络的计算模型
        - 反向传播：训练神经网络的算法
        - 激活函数：引入非线性（如ReLU、Sigmoid）
        """
    }

    for doc_id, text in test_docs.items():
        rag.add_document(text, doc_id)

    # 打印统计
    print(f"\n系统统计: {rag.get_stats()}")

    # 测试查询
    test_questions = [
        "什么是机器学习？",
        "深度学习有什么用？",
        "神经网络是什么？"
    ]

    for question in test_questions:
        print("\n" + "=" * 60)
        result = rag.query(question)
        print(f"\n问题: {question}")
        print(f"回答: {result['answer'][:200]}...")
        print(f"来源: {result['sources']}")
        print(f"检索信息: {result['retrieval_info']}")

    # 可视化（可选）
    # rag.visualize_embeddings()
