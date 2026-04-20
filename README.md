# 智学助手 (Zhixue Assistant)

**北京科技大学 2025 年春季人工智能课程大作业**

> 一个基于微信小程序 + FastAPI + RAG 的智能学习资料助手

## 项目概述

智学助手用于管理学习资料并围绕资料进行问答。当前版本支持文档上传、自动分类、RAG 检索问答、失败时自动降级到本地检索演示模式，以及对话历史保存。

## 当前已实现功能

1. 文档上传与管理
   支持 `PDF`、`TXT`、`DOCX`、`Markdown`，以及 `JPG/JPEG/PNG/BMP/GIF` 图片上传。
2. 文档内容提取
   文本类文件会自动抽取正文；图片会尝试走 OCR 提取文字。
3. 自动文档分类
   使用朴素贝叶斯分类器，将资料分类到“数学 / 英语 / 政治 / 计算机 / 其他”。
4. 智能问答
   优先使用 RAG 检索增强问答；当 RAG 或大模型不可用时，会自动切换到本地知识库检索回答。
5. 答案来源展示
   聊天接口会返回参考资料来源，便于答辩演示和结果追溯。
6. 对话历史
   支持查看历史记录与一键清空历史。
7. 前端后端地址可配置
   小程序“我的”页面可以直接修改后端地址，便于本机调试和真机调试切换。

## 技术架构

```text
微信小程序前端
    ↓
FastAPI 后端
    ↓
文档处理 / 分类 / RAG 检索
    ↓
SQLite 数据库存储
```

| 层级 | 技术 |
|------|------|
| 前端 | 微信小程序 (`WXML` / `WXSS` / `JS`) |
| 后端 | Python + FastAPI |
| AI 检索 | Sentence Transformers + FAISS + DeepSeek API |
| 文档分类 | Multinomial Naive Bayes |
| 数据库 | SQLite |

## 目录结构

```text
zhixue-assistant/
├── ai_module/                # RAG、分类、文档处理
├── backend/                  # FastAPI 后端与数据库操作
├── frontend/                 # 微信小程序前端
├── test_files/               # 测试资料
├── uploads/                  # 上传文件保存目录
├── init_rag_data.py          # 初始化 RAG 并加载测试资料
├── start_rag.py              # RAG 完整模式启动脚本（加载模型，推荐）
├── start_simple.py           # 简单模式启动脚本（不加载 RAG，仅调试用）
├── test_backend.py           # 后端测试脚本
├── requirements.txt          # 项目依赖
└── README.md
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

如果只是先跑后端测试或启动接口，至少需要安装 `FastAPI` 及相关依赖；否则像 `test_backend.py` 里的 FastAPI 路由测试会因为缺少依赖而失败。

### 3. 配置环境变量

如需启用真实大模型回答，可配置：

```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here

# macOS / Linux
export DEEPSEEK_API_KEY=your_api_key_here
```

可选数据库路径：

```bash
set ZHIXUE_DB_PATH=D:\path\to\zhixue.db
```

说明：

- 默认数据库为项目根目录下的 `zhixue.db`
- 如果默认路径不可写，后端会自动回退到 `.runtime/zhixue_runtime.db`

### 4. 启动后端

**推荐使用 RAG 完整模式（答辩/演示用）：**
```bash
python start_rag.py
```
首次启动会加载本地 Embedding 模型（BAAI/bge-small-zh，约 130MB），
加载完成后自动从数据库恢复知识库向量索引。
未配置 `DEEPSEEK_API_KEY` 时，RAG 问答自动降级为本地语义检索。

**简单模式（仅前端调试用，不加载 RAG）：**
```bash
python start_simple.py
```

启动后默认访问：

- API: `http://127.0.0.1:8000`
- Swagger 文档: `http://127.0.0.1:8000/docs`

### 5. 导入微信小程序前端

1. 打开微信开发者工具
2. 导入 `frontend/` 目录
3. 配置自己的 AppID 或测试号
4. 启动后端后运行小程序

默认后端地址是 `http://127.0.0.1:8000`。如果需要真机调试，可以在小程序“我的”页面直接修改后端地址，无需改代码。

## 页面说明

当前小程序主要包含 5 个页面：

- `首页`
  用于检查后端状态、上传文件、查看最近上传资料，并快速跳转到资料库、对话页和历史页。
- `资料库`
  展示所有已上传文件，支持搜索、查看详情、预览文件和删除文件。
- `对话页`
  输入问题后调用 `/api/chat`，并在回答底部展示当前回答模式是 `RAG 检索增强` 还是 `本地知识库检索`。
- `历史页`
  查看历史问答摘要，支持继续提问和刷新列表。
- `我的`
  查看 AI 系统状态、清空聊天历史、清理缓存，并修改后端地址。

## 推荐演示流程

如果你要做课程答辩或现场展示，推荐按下面顺序演示：

1. 启动 `python start_rag.py`（RAG 完整模式）
2. 打开首页，先展示「AI系统信息」页面，说明系统架构（Embedding → FAISS → LLM）
3. 上传一份 `PDF/TXT/DOCX/Markdown` 资料，展示自动分类结果和上传成功提示
4. 进入资料库，展示文件列表、分类标签、文件预览与删除功能
5. 进入对话页，围绕刚上传的资料提一个具体问题
6. 展示回答结果、来源列表，以及回答模式标记
7. 进入历史记录页，展示问答已被保存
8. 在“我的”页面展示 AI 系统信息与后端地址配置能力

如果现场网络不稳定或没有配置 API Key，建议直接使用简单模式演示；系统会自动走本地检索逻辑，功能展示仍然完整。

## RAG 与演示模式

当前系统有两条回答路径：

- `RAG 模式`
  文档会被切块、向量化、写入 FAISS，提问时先检索再交给大模型生成回答。
- `本地检索演示模式`
  当未加载 RAG、没有可用大模型、或者 RAG 查询异常时，系统会改为基于数据库中缓存的文本内容做关键词检索，并返回命中的资料片段。

这意味着即使没有完整模型和 API Key，系统仍然可以完成：

- 上传资料
- 自动分类
- 资料列表展示
- 基于资料内容问答
- 来源展示
- 历史记录保存

## 文件支持说明

支持上传类型：

- 文本类：`pdf`、`txt`、`docx`、`md`
- 图片类：`jpg`、`jpeg`、`png`、`bmp`、`gif`

额外说明：

- 老式 `doc` 文件当前不支持，需先转换为 `docx`
- 图片 OCR 依赖 `pytesseract` 与系统级 `Tesseract-OCR`
- PDF 提取依赖 `PyPDF2`

## 初始化测试资料

如果你想快速构建一个带测试资料的 RAG 知识库，可以运行：

```bash
python init_rag_data.py
```

它会：

- 初始化数据库
- 创建轻量级 RAG 系统
- 读取 `test_files/` 下的 `txt/pdf` 文件
- 将测试资料写入 RAG 与数据库

## 本地开发与联调建议

推荐的本地联调顺序：

1. 先运行 `python start_rag.py`（或 `start_simple.py` 用于快速调试）
2. 用浏览器访问 `http://127.0.0.1:8000/docs`，确认接口正常
3. 再打开微信开发者工具导入 `frontend/`
4. 如果模拟器无法访问后端，在“我的”页面修改 API 地址
5. 真机调试时将地址改成电脑局域网 IP，例如 `http://192.168.1.10:8000`

联调时可以优先检查：

- 根接口 `/` 是否返回 `message` 和 `rag_ready`
- `/api/files` 是否能正常返回文件列表
- `/api/chat` 是否能正常返回 `answer`、`sources` 和 `mode`

## API 概览

基础地址：`http://localhost:8000`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态与模式信息 |
| GET | `/api/test` | 基础联通性测试 |
| POST | `/api/upload` | 上传资料 |
| GET | `/api/files` | 获取资料列表 |
| DELETE | `/api/files/{file_id}` | 删除资料 |
| POST | `/api/chat` | 提问 |
| GET | `/api/chat/history` | 获取历史记录 |
| DELETE | `/api/chat/history` | 清空历史记录 |
| GET | `/api/ai/info` | 获取 AI 系统状态 |
| POST | `/api/classify` | 对文本执行分类 |

接口特点：

- `/api/upload` 会返回分类结果、文本预览、是否已写入 RAG
- `/api/chat` 会返回回答内容、来源列表和当前模式
- 根接口 `/` 会返回 `rag_ready`，用于前端显示当前是 RAG 模式还是演示模式

## 测试

运行后端测试：

```bash
python test_backend.py
```

当前测试覆盖：

- 数据库初始化与读写
- 文档分类器训练与分类
- 文档处理基础能力
- FastAPI 路由注册

说明：

- 测试脚本会在 `.tmp_tests/` 下生成临时数据库
- 如果环境中未安装 `fastapi`，FastAPI 相关测试会失败，但数据库、分类器和文档处理测试仍可单独运行

## 常见问题

### 1. RAG 模式启动很慢

首次下载模型较慢，可尝试设置国内镜像：

```bash
set HF_ENDPOINT=https://hf-mirror.com
```

### 2. 小程序连接不上后端

请检查：

- 后端服务是否已启动
- 小程序中的后端地址是否填写正确
- 真机调试时是否使用了电脑局域网 IP
- 手机和电脑是否处于同一网络
- 微信开发者工具中是否关闭了不必要的域名校验限制

### 3. 上传图片后没有识别出文字

请确认本机已安装：

- `pytesseract`
- `Pillow`
- 系统级 `Tesseract-OCR`

### 4. 没有配置 DeepSeek Key 能不能演示

可以。系统会自动切到本地检索演示模式，仍可完成上传、分类、问答和历史展示。

### 5. 为什么上传成功但没有进入 RAG

常见原因：

- 当前是简单模式启动（`start_simple.py`）
- 知识库为空（需先上传文档）
- 未上传文档导致 RAG 无法检索相关内容

这时接口返回里通常会显示资料已加入本地知识库，但不会标记为已写入 RAG。

### 6. 为什么 `doc` 文件不能上传

当前后端只支持 `docx`，老式 `doc` 文件会直接提示不支持。答辩或演示前建议统一将 Word 文件另存为 `docx`。

## 后续可扩展方向

- 增加文件分科筛选和排序能力
- 为聊天记录增加“继续当前上下文”能力
- 对 OCR 和 PDF 扫描件做更稳定的文本识别
- 支持持久化保存和恢复 FAISS 索引
- 为资料库补充预览摘要与高亮搜索结果

## 团队分工

| 角色 | 姓名 | GitHub | 主要职责 |
|------|------|--------|----------|
| 组长 | 黄重焱 | @YanOIer | 项目管理、RAG 系统、整体协调 |
| 前端 | 袁立 | - | 微信小程序开发、UI 设计 |
| 后端 | 胡昊 | - | FastAPI 后端、数据库、API 开发 |

## 项目状态

- 当前版本：`1.1.0`
- 当前状态：已完成基础功能联调，可在 RAG 模式或演示模式下运行

本项目为北京科技大学 2025 年春季人工智能课程大作业。
