# 智学助手 (Zhixue Assistant)

**北京科技大学 2025年春季人工智能课程大作业**

> 基于 RAG（检索增强生成）技术的智能学习助手微信小程序

---

## 项目概述

智学助手是一款基于 RAG（检索增强生成）技术的智能学习助手微信小程序，帮助学生更高效地管理和学习资料。

### 核心功能

1. **文档上传** - 支持 PDF、TXT、Word 格式学习资料上传
2. **智能分类** - 自动识别文档类型（数学/英语/政治/计算机/其他）
3. **AI 问答** - 基于上传文档的智能问答，优先走 RAG，失败自动降级到本地检索
4. **知识溯源** - 显示答案来源，可追溯可验证
5. **对话历史** - 保存问答记录，支持查看和继续对话

### 技术架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  微信小程序  │────▶│  FastAPI    │────▶│   RAG系统   │
│  (前端)     │◀────│  (后端)     │◀────│  (AI核心)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   SQLite    │
                    │  (数据库)   │
                    └─────────────┘
```

| 层级 | 技术 |
|------|------|
| 前端 | 微信小程序 (WXML/WXSS/JS) |
| 后端 | Python + FastAPI |
| AI | RAG (BGE Embedding + FAISS + DeepSeek API) |
| 分类器 | 朴素贝叶斯分类器 |
| 数据库 | SQLite |

---

## 快速开始

### 环境准备

确保已安装 Python 3.9+ 和 Git。

### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Mac/Linux)
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 DeepSeek API (可选)

如需使用真实 AI 回答，设置环境变量：

```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here

# Mac/Linux
export DEEPSEEK_API_KEY=your_api_key_here
```

### 4. 启动后端服务

**方式一：简单启动（不加载 RAG 模型）**

```bash
python -c "
import sys
sys.path.append('ai_module')
sys.path.append('backend')
from main import app, set_rag_system
from database import init_db
set_rag_system(None)
init_db()
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

**方式二：完整启动（加载 RAG 模型）**

```bash
python start_server.py
```

> 注意：首次启动会下载模型（约 500MB），请耐心等待。
> 如果模型或 API Key 不可用，系统仍会以“本地知识库检索演示模式”启动，适合课程作业答辩演示。

### 5. 启动微信小程序前端

1. 打开微信开发者工具
2. 点击 "导入项目"
3. 选择 `frontend/` 目录
4. 填入你的小程序 AppID（或选择测试号）
5. 点击确定

默认地址是 `http://127.0.0.1:8000`。如果你要用真机调试，可在小程序“我的”页面直接修改后端地址，不需要改代码。

---

## 项目结构

```
zhixue-assistant/
├── frontend/                  # 微信小程序前端
│   ├── pages/                 # 页面目录
│   │   ├── index/             # 首页
│   │   ├── library/           # 资料库
│   │   ├── chat/              # 对话页面
│   │   ├── profile/           # 个人中心
│   │   └── history/           # 对话历史
│   ├── app.js                 # 小程序入口
│   ├── app.json               # 全局配置
│   └── app.wxss               # 全局样式
│
├── backend/                   # FastAPI后端
│   ├── main.py                # API入口
│   ├── database.py            # 数据库操作
│   └── requirements.txt       # 后端依赖
│
├── ai_module/                 # AI核心模块
│   ├── rag_system.py          # RAG检索系统
│   ├── document_processor.py  # 文档处理
│   ├── document_classifier.py # 文档分类器
│   ├── download_models.py     # 模型下载
│   └── models/                # 本地模型缓存
│
├── start_server.py            # 完整启动脚本
├── test_backend.py            # 后端测试脚本
├── requirements.txt           # 完整依赖列表
└── README.md                  # 本文件
```

---

## API 接口文档

### 基础信息

- 基础 URL: `http://localhost:8000`
- 文档地址: `http://localhost:8000/docs`

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态检查 |
| GET | `/api/test` | API 测试 |
| POST | `/api/upload` | 上传文件 |
| GET | `/api/files` | 获取文件列表 |
| DELETE | `/api/files/{id}` | 删除文件 |
| POST | `/api/chat` | 发送问题 |
| GET | `/api/chat/history` | 获取对话历史 |
| DELETE | `/api/chat/history` | 清空对话历史 |
| GET | `/api/ai/info` | 获取 AI 系统信息 |
| POST | `/api/classify` | 文档分类 |

### 示例请求

**上传文件**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.pdf"
```

**发送问题**
```bash
curl -X POST http://localhost:8000/api/chat \
  -d "question=什么是机器学习" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

---

## 开发说明

### 演示模式说明

- 有 RAG 模型时：上传资料后会进入向量检索 + 大模型回答流程
- 没有 RAG 模型或没有 DeepSeek Key 时：系统自动切换到本地知识库检索模式
- 本地检索模式仍支持：
  - 上传资料
  - 文档分类
  - 资料库展示
  - 基于文档内容回答问题
  - 返回参考来源
  - 保存对话历史

### RAG 系统工作原理

1. **文档处理**: 上传的文档被切分成小块文本
2. **向量化**: 使用 BGE 模型将文本转换为向量
3. **索引存储**: 向量存储在 FAISS 索引中
4. **检索**: 用户提问时，将问题向量化并检索相似文本
5. **重排序**: 使用重排序模型精排检索结果
6. **生成回答**: 将检索到的上下文发送给 DeepSeek LLM 生成回答

### 文档分类器

使用朴素贝叶斯算法，自动将文档分类到以下类别：
- 数学
- 英语
- 政治
- 计算机
- 其他

### 数据库结构

**files 表** - 存储上传的文件信息
- id: 主键
- filename: 文件名
- filepath: 文件路径
- file_type: 文件类型
- file_size: 文件大小
- category: 文档分类
- created_at: 创建时间

**chats 表** - 存储对话历史
- id: 主键
- question: 用户问题
- answer: AI 回答
- sources: 参考来源
- created_at: 创建时间

---

## 测试

运行后端测试：

```bash
.venv\Scripts\python.exe test_backend.py
```

---

## 常见问题

### 1. 模型下载慢

设置国内镜像：
```bash
set HF_ENDPOINT=https://hf-mirror.com
```

### 2. 微信小程序无法连接后端

确保：
- 手机和电脑在同一 WiFi 下
- 关闭 Windows 防火墙
- 使用电脑的局域网 IP 而非 localhost

### 3. RAG 模型占用内存过大

在 `rag_system.py` 中修改参数：
```python
rag = RAGSystem(
    use_hnsw=False,      # 禁用 HNSW
    use_reranker=False,  # 禁用重排序
    device='cpu'         # 使用 CPU
)
```

---

## 团队分工

| 角色 | 姓名 | GitHub | 主要职责 |
|------|------|--------|----------|
| 组长 | 黄重焱 | @YanOIer | 项目管理、RAG系统、整体协调 |
| 前端 | 袁立 | - | 微信小程序开发、UI设计 |
| 后端 | 胡昊 | - | FastAPI后端、数据库、API开发 |

---

## 功能特点

| 功能 | 说明 |
|------|------|
| 📄 文档上传 | 支持 PDF、TXT、Word 格式 |
| 🏷️ 智能分类 | 自动识别文档类型（数学/英语/政治/计算机/其他）|
| 🤖 AI 问答 | 基于上传文档的智能问答 |
| 🔍 知识溯源 | 显示答案来源，可追溯可验证 |
| 💬 对话历史 | 保存问答记录，支持查看和继续对话 |

---

## 许可证

本项目为北京科技大学 2025 年春季人工智能课程大作业。

---

**项目状态**: ✅ 已完成 | **最后更新**: 2026年4月16日

**加油！我们一起完成这个项目！** 🚀
