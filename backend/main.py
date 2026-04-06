"""
智学助手 - 后端API服务
使用FastAPI框架
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import sys

# 添加AI模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_module'))

app = FastAPI(title="智学助手API", version="1.0.0")

# 允许跨域（小程序需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传文件夹存在
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 导入数据库模块
from database import init_db, add_file, get_all_files, add_chat, get_chat_history, update_file_category

# 导入AI模块
from document_processor import process_document
from document_classifier import DocumentClassifier

# 全局RAG系统实例（由组长初始化）
rag_system = None

# 全局文档分类器实例
document_classifier = None

def set_rag_system(rag):
    """设置RAG系统实例"""
    global rag_system
    rag_system = rag

def init_classifier():
    """初始化文档分类器"""
    global document_classifier
    if document_classifier is None:
        print("初始化文档分类器...")
        document_classifier = DocumentClassifier()
        document_classifier.train()
        print("文档分类器初始化完成")

@app.on_event("startup")
async def startup():
    """服务启动时初始化"""
    init_db()
    init_classifier()
    print("服务启动完成")

# ============ 文件相关接口 ============

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件接口
    
    参数：
        file: 上传的文件
    
    返回：
        success: 是否成功
        message: 提示信息
        data: 文件信息（包含自动分类结果）
    """
    try:
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件类型
        file_type = file.filename.split('.')[-1].lower()
        
        # 保存到数据库
        file_id = add_file(file.filename, file_path, file_type, file_size)
        
        # 分类结果
        classification_result = None
        
        # 如果有分类器，自动分类文档
        if document_classifier and file_type in ['pdf', 'txt']:
            try:
                # 提取文本
                text = process_document(file_path)
                if text:
                    # 自动分类
                    classification_result = document_classifier.classify(text)
                    print(f"文档 '{file.filename}' 分类结果: {classification_result['category']}")
            except Exception as e:
                print(f"文档分类失败: {e}")
        
        # 如果有RAG系统，处理文档内容
        if rag_system and file_type in ['pdf', 'txt']:
            try:
                # 提取文本并添加到RAG
                if file_type == 'txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    rag_system.add_document(text, file.filename)
                # PDF处理需要额外库，暂时跳过
            except Exception as e:
                print(f"处理文档内容失败: {e}")
        
        return {
            "success": True,
            "message": "上传成功",
            "data": {
                "id": file_id,
                "filename": file.filename,
                "size": format_size(file_size),
                "category": classification_result['category'] if classification_result else None,
                "classification": classification_result
            }
        }
    except Exception as e:
        return {"success": False, "message": f"上传失败: {str(e)}"}

@app.get("/api/files")
async def get_files():
    """
    获取文件列表
    
    返回：
        success: 是否成功
        data: 文件列表
    """
    try:
        files = get_all_files()
        file_list = []
        for f in files:
            file_list.append({
                "id": f[0],
                "name": f[1],
                "path": f[2],
                "type": f[3],
                "size": format_size(f[4]),
                "time": f[5][:10]  # 只返回日期部分
            })
        return {"success": True, "data": file_list}
    except Exception as e:
        return {"success": False, "message": str(e)}

def format_size(size):
    """格式化文件大小"""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f}KB"
    else:
        return f"{size/(1024*1024):.1f}MB"

# ============ 问答相关接口 ============

@app.post("/api/chat")
async def chat(question: str = Form(...)):
    """
    问答接口
    
    参数：
        question: 用户问题
    
    返回：
        success: 是否成功
        answer: AI回答
        sources: 参考来源
    """
    try:
        if rag_system:
            # 使用RAG系统生成回答
            result = rag_system.query(question)
            answer = result["answer"]
            sources = result["sources"]
        else:
            # RAG系统未初始化，返回模拟回答
            answer = f"这是关于'{question}'的模拟回答。RAG系统正在初始化中..."
            sources = []
        
        # 保存对话记录
        add_chat(question, answer, str(sources))
        
        return {
            "success": True,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        return {"success": False, "message": f"问答失败: {str(e)}"}

@app.get("/api/chat/history")
async def chat_history():
    """
    获取对话历史
    
    返回：
        success: 是否成功
        data: 对话历史列表
    """
    try:
        chats = get_chat_history()
        history = []
        for c in chats:
            history.append({
                "id": c[0],
                "question": c[1],
                "answer": c[2],
                "sources": c[3],
                "time": c[4]
            })
        return {"success": True, "data": history}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============ 测试接口 ============

@app.get("/")
async def root():
    """根路径，测试服务是否运行"""
    return {
        "message": "智学助手API服务运行中",
        "version": "1.0.0",
        "rag_ready": rag_system is not None
    }

@app.get("/api/test")
async def test():
    """测试接口"""
    return {"success": True, "message": "API连接正常"}

# ============ AI系统信息接口 ============

@app.get("/api/ai/info")
async def ai_info():
    """
    获取AI系统信息
    
    返回：
        两种AI方法的状态和配置信息
    """
    info = {
        "rag_system": {
            "status": "ready" if rag_system else "not_initialized",
            "method": "Retrieval-Augmented Generation (RAG)",
            "type": "深度学习",
            "components": {
                "embedding": "BAAI/bge-small-zh",
                "retrieval": "FAISS HNSW",
                "reranker": "BAAI/bge-reranker-v2-m3",
                "llm": "DeepSeek Chat"
            },
            "stats": rag_system.get_stats() if rag_system else None
        },
        "document_classifier": {
            "status": "ready" if document_classifier else "not_initialized",
            "method": "Naive Bayes Classifier",
            "type": "传统机器学习",
            "algorithm": "多项式朴素贝叶斯",
            "features": "词袋模型",
            "categories": ["数学", "英语", "政治", "计算机", "其他"],
            "is_trained": document_classifier.is_trained if document_classifier else False
        }
    }
    
    return {"success": True, "data": info}

@app.post("/api/classify")
async def classify_document(text: str = Form(...)):
    """
    文档分类接口
    
    参数：
        text: 待分类的文档文本
    
    返回：
        分类结果
    """
    try:
        if document_classifier:
            result = document_classifier.classify(text)
            return {
                "success": True,
                "data": result
            }
        else:
            return {
                "success": False,
                "message": "分类器未初始化"
            }
    except Exception as e:
        return {"success": False, "message": f"分类失败: {str(e)}"}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
