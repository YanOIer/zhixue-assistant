"""
初始化RAG系统并添加测试文档
"""
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_module'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from rag_system import RAGSystem
from document_processor import process_document
from database import init_db, add_file
import glob

def init_rag_with_test_data():
    """初始化RAG系统并加载测试文档"""
    print("=" * 60)
    print("初始化RAG系统并加载测试文档")
    print("=" * 60)

    # 初始化数据库
    print("\n[1/3] 初始化数据库...")
    init_db()

    # 创建RAG系统（轻量级配置）
    print("\n[2/3] 创建RAG系统...")
    print("提示：首次启动会下载模型（约100MB），请耐心等待")
    try:
        rag = RAGSystem(
            embedding_model='BAAI/bge-small-zh',
            use_hnsw=True,
            use_reranker=False,  # 禁用重排序节省内存
            device='cpu'
        )
        print("RAG系统创建成功")
    except Exception as e:
        print(f"RAG系统创建失败: {e}")
        return None

    # 加载测试文档
    print("\n[3/3] 加载测试文档...")
    test_files_dir = 'test_files'

    if not os.path.exists(test_files_dir):
        print(f"测试文件目录不存在: {test_files_dir}")
        return rag

    # 获取所有txt和pdf文件
    files = glob.glob(os.path.join(test_files_dir, '*.txt')) + \
            glob.glob(os.path.join(test_files_dir, '*.pdf'))

    print(f"找到 {len(files)} 个测试文件")

    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"\n处理: {filename}")

        try:
            # 提取文本
            text = process_document(file_path)
            if not text:
                print(f"  跳过: 无法提取文本")
                continue

            # 添加到RAG系统
            rag.add_document(text, filename)

            # 获取文件大小
            file_size = os.path.getsize(file_path)
            file_type = filename.split('.')[-1].lower()

            # 添加到数据库
            add_file(filename, file_path, file_type, file_size, '其他')
            print(f"  成功添加到知识库")

        except Exception as e:
            print(f"  处理失败: {e}")

    # 显示统计
    print("\n" + "=" * 60)
    print("RAG系统统计")
    print("=" * 60)
    stats = rag.get_stats()
    print(f"文档数量: {stats['document_count']}")
    print(f"文本块数量: {stats['chunk_count']}")
    print(f"向量维度: {stats['vector_dimension']}")
    print("=" * 60)

    return rag

if __name__ == "__main__":
    rag = init_rag_with_test_data()

    if rag:
        # 测试查询
        print("\n" + "=" * 60)
        print("测试查询")
        print("=" * 60)

        test_questions = [
            "什么是机器学习？",
            "监督学习有哪些算法？",
            "什么是导数？",
            "积分的公式有哪些？"
        ]

        for question in test_questions:
            print(f"\n问题: {question}")
            result = rag.query(question)
            print(f"回答: {result['answer'][:100]}...")
            print(f"来源: {result['sources']}")

        # 保存索引
        print("\n保存索引到文件...")
        rag.save("knowledge_base")
        print("完成！")
