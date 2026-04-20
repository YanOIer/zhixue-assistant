# 智学助手 (Zhixue Assistant)

**北京科技大学 2025 年春季人工智能课程大作业**

> 一个基于微信小程序 + FastAPI + RAG 的智能学习资料助手

## 项目概述

智学助手用于管理学习资料并围绕资料进行问答。当前版本支持文档上传、自动分类、RAG 检索问答，以及对话历史保存。

## 核心功能

1. **文档上传与管理** - 支持 PDF、TXT、DOCX、Markdown 格式
2. **自动文档分类** - 使用朴素贝叶斯分类器，将资料分类到"数学 / 英语 / 政治 / 计算机 / 其他"
3. **智能问答** - 基于 RAG 检索增强生成回答，支持配置 KIMI API
4. **答案来源展示** - 聊天接口返回参考资料来源，便于结果追溯
5. **对话历史** - 支持查看历史记录与一键清空

## 技术架构

```
┌─────────────────────┐
│   微信小程序前端     │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   FastAPI 后端      │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐  ┌───▼────┐
│ RAG   │  │ 文档   │
│ 检索  │  │ 分类   │
└───┬───┘  └───┬────┘
    │           │
└───┴─────┬────┘
          │
┌─────────▼───────────┐
│   SQLite 数据库     │
└─────────────────────┘
```

| 层级 | 技术方案 |
|------|---------|
| 前端 | 微信小程序 (WXML/WXSS/JS) |
| 后端 | Python + FastAPI |
| AI 检索 | BGE-small-zh + FAISS HNSW |
| 大模型 | KIMI (Moonshot) |
| 文档分类 | Multinomial Naive Bayes |
| 数据库 | SQLite |

## 目录结构

```
zhixue-assistant/
├── ai_module/           # RAG 检索、文档分类、文档处理
│   ├── rag_system.py     # RAG 核心系统
│   ├── document_classifier.py  # 文档分类器
│   └── document_processor.py   # 文档处理
├── backend/              # FastAPI 后端
│   ├── main.py           # API 路由
│   └── database.py       # 数据库操作
├── frontend/             # 微信小程序前端
├── test_files/           # 测试资料
├── uploads/              # 上传文件存储
├── config.py             # 配置文件
├── start_rag.py          # RAG 完整模式启动
├── start_simple.py       # 简单模式启动
└── requirements.txt     # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 KIMI API（可选）

编辑 `config.py`，填入你的 API Key：

```python
KIMI_API_KEY = "sk-your-api-key"
```

### 3. 启动后端

```bash
# RAG 完整模式（推荐）
python start_rag.py

# 或简单模式（不加载 RAG，仅调试）
python start_simple.py
```

### 4. 运行小程序

1. 打开微信开发者工具
2. 导入 `frontend/` 目录
3. 配置 AppID 或使用测试号

## 演示流程

1. 启动 `python start_rag.py`
2. 打开首页，展示「AI系统信息」
3. 上传资料，展示自动分类
4. 进入资料库，展示文件管理
5. 进入对话页，提问并展示来源
6. 展示历史记录

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态 |
| POST | `/api/upload` | 上传资料 |
| GET | `/api/files` | 获取资料列表 |
| DELETE | `/api/files/{id}` | 删除资料 |
| POST | `/api/chat` | 提问 |
| GET | `/api/chat/history` | 获取历史 |
| DELETE | `/api/chat/history` | 清空历史 |
| GET | `/api/ai/info` | AI 系统状态 |

## 项目状态

- 版本：1.1.0
- 状态：已完成，可正常运行
