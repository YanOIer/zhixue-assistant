"""智学助手后端 API。"""

from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import sys

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_MODULE_PATH = PROJECT_ROOT / 'ai_module'
if str(AI_MODULE_PATH) not in sys.path:
    sys.path.append(str(AI_MODULE_PATH))

from database import (  # noqa: E402
    add_chat,
    add_file,
    clear_chat_history,
    delete_file,
    get_all_file_contents,
    get_all_files,
    get_chat_history,
    get_file_by_id,
    init_db,
    save_file_content,
)
from document_classifier import DocumentClassifier  # noqa: E402
from document_processor import process_document  # noqa: E402

APP_VERSION = "1.1.0"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
SUPPORTED_TEXT_TYPES = {'pdf', 'txt', 'docx', 'md'}
SUPPORTED_IMAGE_TYPES = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
SUPPORTED_FILE_TYPES = SUPPORTED_TEXT_TYPES | SUPPORTED_IMAGE_TYPES

app = FastAPI(title="智学助手API", version=APP_VERSION)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_system = None
document_classifier = None


def set_rag_system(rag):
    """设置 RAG 系统实例。"""
    global rag_system
    rag_system = rag


def init_classifier():
    """初始化文档分类器。"""
    global document_classifier
    if document_classifier is None:
        print("初始化文档分类器...")
        document_classifier = DocumentClassifier()
        document_classifier.train()
        print("文档分类器初始化完成")


def format_size(size):
    """格式化文件大小。"""
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    return f"{size / (1024 * 1024):.1f}MB"


def extract_preview(text, limit=180):
    """生成简短预览文本。"""
    cleaned = ' '.join((text or '').split())
    return cleaned[:limit]


def build_safe_filename(filename):
    """将文件名转换为安全格式，保留原始名称。
    
    只去除路径危险字符，保留中文和扩展名。
    """
    safe_name = Path(filename or '').name.strip()
    if not safe_name:
        safe_name = 'upload.txt'

    # 对特殊字符做安全处理：保留中文，去除路径危险字符
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', safe_name)
    return safe_name


def infer_text_answer(question):
    """基于缓存文档内容做本地关键词检索，保证演示可用。"""
    records = get_all_file_contents()
    if not records:
        return {
            "answer": "当前知识库为空。请先上传 PDF、TXT、DOCX 或图片资料，再进行提问。",
            "sources": [],
            "context": [],
            "mode": "empty",
        }

    chinese_terms = re.findall(r'[\u4e00-\u9fff]{2,}', question)
    english_terms = re.findall(r'[a-zA-Z0-9]+', question.lower())
    query_terms = []
    for phrase in chinese_terms:
        query_terms.append(phrase)
        cleaned_phrase = phrase.replace('什么是', '').replace('请解释', '').replace('一下', '')
        if cleaned_phrase and cleaned_phrase != phrase:
            query_terms.append(cleaned_phrase)
        for size in range(2, min(5, len(cleaned_phrase) + 1)):
            for start in range(0, len(cleaned_phrase) - size + 1):
                query_terms.append(cleaned_phrase[start:start + size])
    query_terms.extend(english_terms)
    query_terms = [term for term in dict.fromkeys(query_terms) if term]
    candidates = []

    for file_id, filename, category, created_at, content, preview in records:
        text = (content or preview or '').strip()
        if not text:
            continue

        sample = ' '.join(text.split())
        score = 0
        for term in query_terms:
            score += sample.lower().count(term)

        if not query_terms:
            score = 1

        if score > 0:
            excerpt_start = 0
            if query_terms:
                positions = [sample.lower().find(term) for term in query_terms if sample.lower().find(term) >= 0]
                if positions:
                    excerpt_start = max(positions[0] - 40, 0)
            excerpt = sample[excerpt_start:excerpt_start + 180]
            candidates.append({
                "id": file_id,
                "filename": filename,
                "category": category,
                "score": score,
                "excerpt": excerpt or preview or sample[:180],
            })

    if not candidates:
        latest = records[0]
        return {
            "answer": (
                f"已检索到知识库中的资料，但没有找到与“{question}”高度匹配的内容。"
                f"你可以换个更具体的问法，或先上传更相关的资料。"
            ),
            "sources": [latest[1]],
            "context": [latest[5] or extract_preview(latest[4] or '')],
            "mode": "fallback_no_match",
        }

    top_candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)[:3]
    category_counter = Counter(item["category"] or '其他' for item in top_candidates)
    dominant_category = category_counter.most_common(1)[0][0]
    answer_lines = [
        f"根据本地知识库检索，问题更接近“{dominant_category}”资料。",
        "匹配到的关键信息如下：",
    ]
    for index, item in enumerate(top_candidates, start=1):
        answer_lines.append(f"{index}. {item['excerpt']}")

    return {
        "answer": '\n'.join(answer_lines),
        "sources": [item["filename"] for item in top_candidates],
        "context": [item["excerpt"] for item in top_candidates],
        "mode": "local_retrieval",
    }


def serialize_history_sources(raw_sources):
    try:
        return json.loads(raw_sources) if raw_sources else []
    except json.JSONDecodeError:
        return raw_sources or []


@app.on_event("startup")
async def startup():
    init_db()
    init_classifier()
    print("Server started successfully")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传资料并写入知识库。"""
    original_name = file.filename or "未命名文件"
    extension = Path(original_name).suffix.lower().lstrip('.')

    if extension not in SUPPORTED_FILE_TYPES and extension != 'doc':
        return {
            "success": False,
            "message": "仅支持 PDF、TXT、DOCX、Markdown 和常见图片格式。",
        }

    if extension == 'doc':
        return {
            "success": False,
            "message": "暂不支持老式 DOC 文件，请另存为 DOCX 后上传。",
        }

    saved_name = build_safe_filename(original_name)
    saved_path = UPLOAD_DIR / saved_name

    try:
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = saved_path.stat().st_size
        text = process_document(str(saved_path)) if extension in SUPPORTED_FILE_TYPES else ""
        preview = extract_preview(text)

        classification_result = None
        category = '其他'
        if document_classifier and text:
            try:
                classification_result = document_classifier.classify(text)
                category = classification_result['category']
            except Exception as exc:
                print(f"文档分类失败: {exc}")

        file_id = add_file(original_name, str(saved_path), extension, file_size, category)
        save_file_content(file_id, text, preview)

        if rag_system and text:
            try:
                rag_system.add_document(text, original_name)
                print(f"文档 '{original_name}' 已添加到 RAG 系统")
            except Exception as exc:
                print(f"处理文档内容失败: {exc}")

        return {
            "success": True,
            "message": "上传成功",
            "data": {
                "id": file_id,
                "filename": original_name,
                "savedName": saved_name,
                "size": format_size(file_size),
                "category": category,
                "classification": classification_result,
                "preview": preview,
                "ragIndexed": bool(rag_system and text),
            }
        }
    except Exception as exc:
        if saved_path.exists():
            saved_path.unlink(missing_ok=True)
        return {"success": False, "message": f"上传失败: {exc}"}


@app.get("/api/files")
async def get_files():
    """获取文件列表。"""
    try:
        file_list = []
        for file_row in get_all_files():
            saved_name = Path(file_row[2]).name
            file_list.append({
                "id": file_row[0],
                "name": file_row[1],
                "savedName": saved_name,
                "path": file_row[2],
                "type": file_row[3],
                "size": format_size(file_row[4]),
                "category": file_row[5] or '其他',
                "time": (file_row[6] or '')[:19].replace('T', ' '),
                "url": f"/uploads/{saved_name}",
            })
        return {"success": True, "data": file_list}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@app.post("/api/chat")
async def chat(question: str = Form(...)):
    """问答接口。优先使用 RAG，失败时降级为本地检索回答。"""
    question = question.strip()
    if not question:
        return {"success": False, "message": "问题不能为空"}

    try:
        result = None
        if rag_system:
            try:
                result = rag_system.query(question)
                result["mode"] = "rag"
            except Exception as exc:
                print(f"RAG 查询失败，已降级到本地检索: {exc}")

        if result is None:
            result = infer_text_answer(question)

        answer = result["answer"]
        sources = result.get("sources", [])
        add_chat(question, answer, json.dumps(sources, ensure_ascii=False))
        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "mode": result.get("mode", "unknown"),
        }
    except Exception as exc:
        return {"success": False, "message": f"问答失败: {exc}"}


@app.get("/api/chat/history")
async def chat_history():
    """获取对话历史。"""
    try:
        history = []
        for row in get_chat_history():
            history.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "sources": serialize_history_sources(row[3]),
                "time": row[4],
                "answerPreview": row[2][:100] + ('...' if len(row[2]) > 100 else ''),
            })
        return {"success": True, "data": history}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@app.delete("/api/chat/history")
async def clear_history():
    """清空历史记录。"""
    try:
        clear_chat_history()
        return {"success": True, "message": "历史记录已清空"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@app.delete("/api/files/{file_id}")
async def delete_file_endpoint(file_id: int):
    """删除文件与数据库记录。"""
    try:
        file_row = get_file_by_id(file_id)
        if not file_row:
            return {"success": False, "message": "文件不存在"}

        file_path = Path(file_row[2])
        if file_path.exists():
            try:
                file_path.unlink(missing_ok=True)
            except PermissionError:
                print(f"无法删除物理文件，已跳过: {file_path}")

        delete_file(file_id)
        return {"success": True, "message": "删除成功"}
    except Exception as exc:
        return {"success": False, "message": f"删除失败: {exc}"}


@app.get("/")
async def root():
    """根路径。"""
    return {
        "message": "智学助手API服务运行中",
        "version": APP_VERSION,
        "rag_ready": rag_system is not None,
        "upload_dir": str(UPLOAD_DIR),
    }


@app.get("/api/test")
async def test():
    """测试接口。"""
    return {"success": True, "message": "API连接正常"}


@app.get("/api/ai/info")
async def ai_info():
    """获取 AI 系统状态。"""
    import os
    kimi_key = os.getenv("MOONSHOT_API_KEY", "")
    
    info = {
        "rag_system": {
            "status": "ready" if rag_system else "fallback_mode",
            "method": "语义向量检索",
            "type": "深度学习",
            "embedding": "BAAI/bge-small-zh (本地)",
            "retrieval": "FAISS HNSW 向量索引",
            "api_configured": bool(kimi_key),
            "stats": rag_system.get_stats() if rag_system else None
        },
        "document_classifier": {
            "status": "ready" if document_classifier else "not_initialized",
            "method": "朴素贝叶斯分类器",
            "type": "传统机器学习",
            "algorithm": "多项式朴素贝叶斯",
            "features": "词袋模型 + TF-IDF",
            "categories": ["数学", "英语", "政治", "计算机", "其他"],
            "is_trained": document_classifier.is_trained if document_classifier else False
        },
        "ai_model": {
            "provider": "KIMI (Moonshot)",
            "model": "moonshot-v1-8k",
            "configured": bool(kimi_key),
            "description": "KIMI 是月之暗面开发的国产大模型，中文理解能力强，响应速度快。" if kimi_key else "未配置 API Key，将返回检索内容"
        }
    }
    return {"success": True, "data": info}


@app.post("/api/classify")
async def classify_document(text: str = Form(...)):
    """文档分类接口。"""
    try:
        if not document_classifier:
            return {"success": False, "message": "分类器未初始化"}
        return {"success": True, "data": document_classifier.classify(text)}
    except Exception as exc:
        return {"success": False, "message": f"分类失败: {exc}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
