"""
RAG系统与后端集成模块

该文件用于将RAG系统集成到FastAPI后端中
由组长完成，组员B只需在main.py中导入使用
"""

import os
import sys

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加当前目录到Python路径
sys.path.append(current_dir)

from rag_system import RAGSystem
from document_processor import process_document

# 全局RAG实例
_rag_instance = None

def get_rag_system():
    """
    获取RAG系统实例（单例模式）
    
    返回：
        RAGSystem实例
    """
    global _rag_instance
    
    if _rag_instance is None:
        print("初始化RAG系统...")
        _rag_instance = RAGSystem()
        
        # 尝试加载已有索引
        index_path = os.path.join(current_dir, "vector_index")
        if os.path.exists(f"{index_path}.faiss"):
            _rag_instance.load_index(index_path)
    
    return _rag_instance

def process_uploaded_file(file_path, filename):
    """
    处理上传的文件，提取文本并添加到RAG系统
    
    参数：
        file_path: 文件路径
        filename: 文件名
    
    返回：
        是否处理成功
    """
    try:
        rag = get_rag_system()
        
        # 提取文本
        text = process_document(file_path)
        
        if not text:
            print(f"无法从文件提取文本: {filename}")
            return False
        
        # 添加到RAG系统
        rag.add_document(text, filename)
        
        # 保存索引
        index_path = os.path.join(current_dir, "vector_index")
        rag.save_index(index_path)
        
        return True
        
    except Exception as e:
        print(f"处理文件失败: {e}")
        return False

def query_knowledge_base(question):
    """
    查询知识库
    
    参数：
        question: 用户问题
    
    返回：
        查询结果字典
    """
    rag = get_rag_system()
    return rag.query(question)

# 导出供后端使用
__all__ = ['get_rag_system', 'process_uploaded_file', 'query_knowledge_base']

# 测试
if __name__ == "__main__":
    # 测试获取RAG系统
    rag = get_rag_system()
    print(f"RAG系统状态: {rag.get_stats()}")
