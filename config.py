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
    "use_reranker": True,
    "device": "cpu",  # 可选: "cuda" 如果有GPU
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

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 文档分类器配置
CLASSIFIER_CATEGORIES = ["数学", "英语", "政治", "计算机", "其他"]

# 微信小程序配置（需要在微信小程序后台配置）
WECHAT_CONFIG = {
    "appid": "your_appid_here",
    "appsecret": "your_appsecret_here"
}
