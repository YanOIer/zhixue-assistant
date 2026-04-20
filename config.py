"""
智学助手 - 项目配置文件
"""

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 上传文件配置
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 数据库配置
DATABASE_PATH = os.path.join(BASE_DIR, "zhixue.db")

# AI模块配置
AI_MODULE_DIR = os.path.join(BASE_DIR, "ai_module")
MODEL_CACHE_DIR = os.path.join(AI_MODULE_DIR, "models")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# RAG系统配置
RAG_CONFIG = {
    "embedding_model": "BAAI/bge-small-zh",
    "reranker_model": "BAAI/bge-reranker-v2-m3",
    "use_hnsw": True,
    "use_reranker": False,  # CPU模式禁用（模型2.2GB过大）；设为True在GPU环境下启用
    "device": "cpu",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "top_k": 5
}

# API配置
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False
}

# KIMI API配置（从环境变量或配置文件读取）
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
# 如果环境变量未设置，可以使用以下方式（不推荐，密钥会暴露在代码中）
# KIMI_API_KEY = "sk-your-api-key-here"
if KIMI_API_KEY:
    os.environ["MOONSHOT_API_KEY"] = KIMI_API_KEY

# 文档分类器配置
CLASSIFIER_CATEGORIES = ["数学", "英语", "政治", "计算机", "其他"]

# 微信小程序配置（需要在微信小程序后台配置）
WECHAT_CONFIG = {
    "appid": "your_appid_here",
    "appsecret": "your_appsecret_here"
}
