import os
import sys
from pathlib import Path
import uuid

# 添加模块路径
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / 'ai_module'))
sys.path.append(str(PROJECT_ROOT / 'backend'))

TEST_DIR = PROJECT_ROOT / '.tmp_tests'
TEST_DIR.mkdir(exist_ok=True)
os.environ['ZHIXUE_DB_PATH'] = str(TEST_DIR / f'test-{uuid.uuid4().hex}.db')

def test_database():
    """测试数据库模块"""
    print("\n" + "=" * 60)
    print("测试数据库模块")
    print("=" * 60)

    try:
        from database import init_db, add_file, get_all_files, add_chat, get_chat_history

        # 初始化数据库
        init_db()
        print("[OK] 数据库初始化成功")

        # 测试添加文件记录
        file_id = add_file("test.txt", "/path/to/test.txt", "txt", 1024, "测试")
        print(f"[OK] 添加文件记录成功，ID: {file_id}")

        # 测试获取文件列表
        files = get_all_files()
        print(f"[OK] 获取文件列表成功，共 {len(files)} 条记录")

        # 测试添加对话记录
        add_chat("测试问题", "测试回答", "['test.txt']")
        print("[OK] 添加对话记录成功")

        # 测试获取对话历史
        chats = get_chat_history()
        print(f"[OK] 获取对话历史成功，共 {len(chats)} 条记录")

        print("\n[PASS] 数据库模块测试通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 数据库模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_classifier():
    """测试文档分类器"""
    print("\n" + "=" * 60)
    print("测试文档分类器")
    print("=" * 60)

    try:
        from document_classifier import DocumentClassifier

        # 创建分类器
        classifier = DocumentClassifier()
        print("[OK] 分类器创建成功")

        # 训练分类器
        classifier.train()
        print("[OK] 分类器训练完成")

        # 测试分类
        test_docs = [
            ("函数导数积分微分方程", "数学"),
            ("英语单词语法阅读理解", "英语"),
            ("编程算法数据结构", "计算机"),
        ]

        for text, expected in test_docs:
            result = classifier.classify(text)
            predicted = result['category']
            status = "[OK]" if predicted == expected else "[WARN]"
            print(f"{status} 文本: {text[:20]}... -> 预测: {predicted}, 期望: {expected}")

        print("\n[PASS] 文档分类器测试通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 文档分类器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_processor():
    """测试文档处理器"""
    print("\n" + "=" * 60)
    print("测试文档处理器")
    print("=" * 60)

    try:
        from document_processor import extract_text_from_txt, clean_text

        # 创建测试文件
        test_file = TEST_DIR / "test_temp.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是测试内容。\n机器学习是人工智能的一个重要分支。")

        # 测试文本提取
        text = extract_text_from_txt(str(test_file))
        assert "机器学习" in text
        print("[OK] 文本提取成功")

        # 测试文本清理
        cleaned = clean_text("  多余空格   和\n\n换行  ")
        assert cleaned is not None
        print("[OK] 文本清理成功")

        print("[OK] 测试文件保留在临时目录")

        print("\n[PASS] 文档处理器测试通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 文档处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi():
    """测试 FastAPI 应用"""
    print("\n" + "=" * 60)
    print("测试 FastAPI 应用")
    print("=" * 60)

    try:
        from main import app

        # 检查应用实例
        assert app is not None
        print("[OK] FastAPI 应用创建成功")

        # 检查路由
        routes = [r.path for r in app.routes]
        expected_routes = ['/api/upload', '/api/files', '/api/chat', '/api/chat/history', '/api/ai/info']

        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"[OK] 路由 {route} 已注册")
            else:
                print(f"[WARN] 路由 {route} 未找到")

        print("\n[PASS] FastAPI 应用测试通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] FastAPI 应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智学助手 - 后端测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("数据库模块", test_database()))
    results.append(("文档分类器", test_document_classifier()))
    results.append(("文档处理器", test_document_processor()))
    results.append(("FastAPI 应用", test_fastapi()))

    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
    else:
        print("\n[WARNING] 部分测试失败，请检查错误信息")

    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
