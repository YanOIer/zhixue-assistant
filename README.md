# 智学助手 (Zhixue Assistant)

**北京科技大学 2025年春季人工智能课程大作业**

> ⚠️ **团队私有项目** - 黄重焱、袁立、胡昊

---

## 👋 三位同学看这里

| 我是... | 点击快速开始 |
|---------|-------------|
| **黄重焱（组长）** | [组长职责](./docs/组长职责.md) |
| **袁立（前端）** | [前端开发指南](./docs/前端开发指南.md) |
| **胡昊（后端）** | [后端开发指南](./docs/后端开发指南.md) |

---

## 🚀 5分钟快速开始

### 第一步：安装软件（根据你的分工）

#### 袁立（前端）需要安装：
| 软件 | 下载链接 | 说明 |
|------|---------|------|
| 微信开发者工具 | [下载](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html) | **必装**，小程序开发IDE |
| VS Code | [下载](https://code.visualstudio.com/) | 代码编辑器，推荐 |
| Git | [下载](https://git-scm.com/download/win) | 版本控制工具 |

#### 胡昊（后端）需要安装：
| 软件 | 下载链接 | 说明 |
|------|---------|------|
| Python 3.9+ | [下载](https://www.python.org/downloads/) | **必装**，运行环境 |
| VS Code | [下载](https://code.visualstudio.com/) | 代码编辑器，推荐 |
| Git | [下载](https://git-scm.com/download/win) | 版本控制工具 |
| Postman | [下载](https://www.postman.com/downloads/) | API测试工具 |

---

### 第二步：下载项目代码

```bash
# 所有人都要执行
git clone git@github.com:YanOIer/zhixue-assistant.git
cd zhixue-assistant
```

---

### 第三步：配置开发环境

#### 袁立（前端）配置：
```bash
# 用微信开发者工具打开 frontend/ 目录即可开始
# 详细步骤查看：docs/前端开发指南.md
```

#### 胡昊（后端）配置：
```bash
# 1. 创建Python虚拟环境
python -m venv .venv

# 2. 激活虚拟环境（Windows）
.venv\Scripts\activate

# 3. 安装依赖
pip install -r backend/requirements.txt
pip install -r ai_module/requirements.txt

# 详细步骤查看：docs/后端开发指南.md
```

---

## 📋 项目信息

### 团队分工

| 角色 | 姓名 | GitHub | 主要职责 |
|------|------|--------|----------|
| 组长 | 黄重焱 | @YanOIer | 项目管理、RAG系统、整体协调 |
| 前端 | 袁立 | | 微信小程序开发、UI设计 |
| 后端 | 胡昊 | | FastAPI后端、数据库、API开发 |

### 项目时间线
- **开始日期**：2024年4月6日
- **目标完成**：2024年4月20日
- **截止日期**：2024年4月24日

---

## 🎯 项目简介

智学助手是一款基于 **RAG（检索增强生成）** 技术的智能学习助手微信小程序。

**核心功能：**
1. 📚 **文档上传** - 支持PDF、Word、TXT格式学习资料
2. 🤖 **AI问答** - 基于上传文档的智能问答
3. 🔍 **知识检索** - 显示答案来源，可追溯可验证
4. 📱 **微信小程序** - 随时随地使用

**技术栈：**
| 层级 | 技术 |
|------|------|
| 前端 | 微信小程序 (WXML/WXSS/JS) |
| 后端 | Python + FastAPI |
| AI | RAG (BGE Embedding + FAISS + DeepSeek API) |
| 数据库 | SQLite |

---

## 📁 项目结构

```
zhixue-assistant/
├── 📚 docs/                      # 开发文档
│   ├── 组长职责.md               # 黄重焱看这里
│   ├── 前端开发指南.md           # 袁立看这里
│   └── 后端开发指南.md           # 胡昊看这里
│
├── 📱 frontend/                  # 袁立的工作目录
│   ├── pages/                    # 小程序页面
│   └── ...
│
├── ⚙️ backend/                   # 胡昊的工作目录
│   ├── main.py                   # FastAPI入口
│   └── ...
│
├── 🤖 ai_module/                 # AI核心（已完成✅）
│   ├── rag_system.py             # RAG检索系统
│   └── ...
│
└── 📖 README.md                  # 本文件（大家都要看）
```

---

## 📅 开发计划

### Week 1 (4/6 - 4/13) - 核心功能开发

| 日期 | 任务 | 负责人 |
|------|------|--------|
| 4/6-7 | 环境搭建 | 袁立、胡昊 |
| 4/8-9 | API接口定义 | 黄重焱协调 |
| 4/10-11 | 前端页面开发 | 袁立 |
| 4/12-13 | 后端API开发 | 胡昊 |
| 4/13 | MVP联调 | 三人一起 |

### Week 2 (4/14 - 4/20) - 优化完善

| 日期 | 任务 | 负责人 |
|------|------|--------|
| 4/14-15 | 前端UI美化 | 袁立 |
| 4/16-17 | 后端性能优化 | 胡昊 |
| 4/18-19 | 联调测试 | 三人一起 |
| 4/20 | 文档整理 | 黄重焱 |

### Final (4/21 - 4/24) - 提交准备

- [ ] 最终测试 - 黄重焱
- [ ] 演示准备 - 三人一起

---

## 💬 团队沟通

- **微信群**：智学助手开发群（扫码加入）
- **进度同步**：多用微信交流，实在搞不定的问题别死脑筋，一起解决问题
- **紧急联系**：微信直接@相关同学

---

## 🛠️ 常用命令

### Git操作（三人都要会）
```bash
# 拉取最新代码
git pull origin main

# 创建自己的功能分支
git checkout -b feature/你的功能名

# 提交代码
git add .
git commit -m "feat: 描述你的改动"
git push origin feature/你的功能名

# 查看状态
git status
```

### 后端命令（胡昊用）
```bash
# 启动后端服务
cd backend
python main.py

# 测试RAG
cd ai_module
python rag_system.py
```

---

## ✅ 验收标准

- [ ] 用户能上传学习资料（PDF/Word/TXT）
- [ ] 用户能提问并获得AI回答
- [ ] 回答能显示参考来源
- [ ] 历史记录可查看
- [ ] 直接演示小程序功能（**无需PPT**）

---

## 🔒 私密说明

本项目为**团队私有项目**，GitHub仓库已设置为Private，仅限黄重焱、袁立、胡昊三人访问。

---

**项目状态**：🟡 开发中 | **最后更新**：2024年4月6日

**加油！我们一起完成这个项目！** �