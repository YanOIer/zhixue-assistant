# 智学助手 (Zhixue Assistant)

**北京科技大学 2025 年春季人工智能课程大作业**

---

## 📖 项目简介

智学助手是一款面向学生的**智能学习资料管理助手**，基于微信小程序 + FastAPI 构建，集成了机器学习技术实现文档自动分类和智能问答功能。

### 核心特性

| 特性 | 说明 |
|------|------|
| 📱 **微信小程序** | 跨平台移动端界面，无需安装即可使用 |
| 🤖 **AI 赋能** | 内置机器学习模型，无需人工干预 |
| 🔒 **本地运行** | 核心 AI 模型完全本地运行，不依赖外部 API |
| 📊 **可追溯** | 问答结果附带参考来源，便于验证 |

---

## 🎯 核心功能

| 功能 | 描述 | 技术实现 |
|------|------|---------|
| **文档上传** | 支持 PDF/TXT/DOCX/Markdown 格式 | FastAPI 文件上传 |
| **自动分类** | 上传时自动识别学科类别 | 朴素贝叶斯分类器 |
| **智能问答** | 基于知识库回答问题 | 本地语义检索 |
| **历史记录** | 保存问答会话 | SQLite 数据库 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        微信小程序前端                          │
│                     (frontend/ 目录)                         │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP REST API
┌─────────────────────────────▼───────────────────────────────┐
│                        FastAPI 后端                           │
│                      (backend/main.py)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ 文件管理API │  │ 聊天问答API│  │ AI系统状态 API    │   │
│  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘   │
└────────┼────────────────┼──────────────────┼───────────────┘
         │                │                  │
    ┌────▼────┐     ┌─────▼─────┐    ┌─────▼─────┐
    │文档处理  │     │  语义检索  │    │文档分类器  │
    │         │     │(rag_system)│    │(classifier)│
    └────┬────┘     └─────┬─────┘    └─────┬─────┘
         │                │                  │
         └────────────────┼──────────────────┘
                          │
              ┌───────────▼───────────┐
              │     SQLite 数据库      │
              │    (zhixue.db)         │
              └───────────────────────┘
```

---

## 📁 项目结构

```
zhixue-assistant/
│
├── frontend/                    # 🟢 微信小程序前端
│   ├── pages/                   # 页面目录
│   │   ├── index/               # 首页（上传资料入口）
│   │   ├── files/               # 资料库页面
│   │   ├── chat/                # 对话页面
│   │   ├── history/             # 历史记录页面
│   │   ├── mine/                # 我的页面
│   │   └── aiinfo/              # AI系统信息页面
│   ├── app.js                   # 全局逻辑
│   ├── app.json                 # 页面配置
│   ├── app.wxss                 # 全局样式
│   └── images/                  # 图片资源
│
├── backend/                     # 🔵 FastAPI 后端
│   ├── main.py                  # API 路由定义
│   └── database.py              # 数据库操作
│
├── ai_module/                   # 🟡 AI 核心模块
│   ├── rag_system.py            # 语义检索系统
│   ├── document_classifier.py   # 文档分类器
│   ├── document_processor.py     # 文档处理工具
│   └── models/                  # 本地 AI 模型缓存
│       └── models--BAAI--bge-small-zh/  # 向量化模型
│
├── uploads/                     # 📂 用户上传文件存储
├── test_files/                  # 📝 测试用文档资料
│
├── config.py                    # ⚙️ 项目配置文件
├── start_rag.py                 # 🚀 RAG模式启动脚本
├── start_simple.py              # 🚀 简单模式启动脚本
├── requirements.txt             # 📦 Python依赖
└── zhixue.db                    # 💾 SQLite 数据库文件
```

---

## 🔬 AI 模块详解

### 1. 文档分类器 (`document_classifier.py`)

**解决问题**：自动识别上传文档属于哪个学科

| 项目 | 说明 |
|------|------|
| **算法** | Multinomial Naive Bayes（多项式朴素贝叶斯） |
| **特征** | 词袋模型 + TF-IDF |
| **分类** | 数学 / 英语 / 政治 / 计算机 / 其他 |

**工作流程**：
```
上传文档 → 文本预处理 → 词袋向量化 → TF-IDF权重 → 贝叶斯分类 → 输出类别+置信度
```

### 2. 语义检索系统 (`rag_system.py`)

**解决问题**：根据用户问题，从知识库中找到相关内容

| 项目 | 说明 |
|------|------|
| **向量化** | BGE-small-zh（24M参数，中文语义 Embedding） |
| **索引** | FAISS HNSW（近似最近邻检索） |
| **分块** | 滑动窗口（500字/块，100字重叠） |

**工作流程**：
```
上传文档 → 文本分块 → 向量化 → 存储向量索引
    ↓
用户提问 → 问题向量化 → FAISS检索 → 返回相关片段
```

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 微信开发者工具（调试用）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端

**方式一：RAG 完整模式（推荐）**
```bash
python start_rag.py
# 或双击 start_rag.bat
```

**方式二：简单模式（仅前端调试）**
```bash
python start_simple.py
```

### 3. 运行小程序

1. 打开**微信开发者工具**
2. 点击「导入项目」
3. 项目目录选择：`d:\Code\Projects\zhixue-assistant\frontend`
4. 填写 AppID（使用测试号即可）
5. 点击确定

> ⚠️ **重要**：勾选「不校验合法域名」（详情 → 本地设置）

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务健康检查 |
| POST | `/api/upload` | 上传文档 |
| GET | `/api/files` | 获取文件列表 |
| GET | `/api/files/{id}` | 获取单个文件 |
| DELETE | `/api/files/{id}` | 删除文件 |
| POST | `/api/chat` | 发送问题 |
| GET | `/api/chat/history` | 获取历史 |
| DELETE | `/api/chat/history` | 清空历史 |
| GET | `/api/ai/info` | AI 系统状态 |

---

## 📊 数据库结构

```sql
-- 文件表
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    filename TEXT,
    category TEXT,
    content TEXT,
    preview TEXT,
    created_at TIMESTAMP
);

-- 聊天记录表
CREATE TABLE chat_history (
    id TEXT PRIMARY KEY,
    question TEXT,
    answer TEXT,
    sources TEXT,
    created_at TIMESTAMP
);
```

---

## 🔧 配置说明

编辑 `config.py`：

```python
# 数据库路径
DATABASE_PATH = "zhixue.db"

# RAG 配置
RAG_CONFIG = {
    "embedding_model": "BAAI/bge-small-zh",
    "use_hnsw": True,
    "device": "cpu",           # 可改为 "cuda" 使用 GPU
    "chunk_size": 500,
    "chunk_overlap": 100,
    "top_k": 5                 # 返回前 5 个相关片段
}

# 分类类别
CLASSIFIER_CATEGORIES = ["数学", "英语", "政治", "计算机", "其他"]
```

---

## ❓ 常见问题

**Q: 启动报模块找不到？**
```bash
pip install -r requirements.txt
```

**Q: 分类结果都是"其他"？**
> 文档内容太少或没有包含预设关键词，上传有实际内容的文档即可。

**Q: 问答没有返回内容？**
> 需要先上传相关文档，问题关键词要出现在文档中。

**Q: 模型下载很慢？**
> 已配置 HuggingFace 国内镜像，首次运行会自动下载模型。

---

## 👥 团队分工

| 成员 | 负责模块 |
|------|---------|
| @YanOIer | 项目框架、AI模块、后端开发 |
| 组员A | （待分配） |
| 组员B | （待分配） |

---

## 📄 项目状态

- **版本**：1.1.0
- **状态**：功能完善，可正常运行
- **更新**：详见 [CHANGELOG](演示指南.md)

---

> 📚 相关文档：[演示指南.md](演示指南.md) | [用户手册](USER_MANUAL.md)
