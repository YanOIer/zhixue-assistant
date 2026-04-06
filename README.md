# 智学助手 (Zhixue Assistant)

**北京科技大学 2025年春季人工智能课程大作业**

> ⚠️ **团队私有项目** - 仅限课程组成员访问

---

## 快速开始（团队成员）

### 1. 克隆项目
```bash
git clone git@github.com:YanOIer/zhixue-assistant.git
cd zhixue-assistant
```

### 2. 查看你的分工
根据你的角色查看对应的开发指南：
- **组长** → [docs/组长职责.md](./docs/组长职责.md)
- **前端开发** → [docs/前端开发指南.md](./docs/前端开发指南.md)  
- **后端开发** → [docs/后端开发指南.md](./docs/后端开发指南.md)

### 3. 项目时间线
- **开始日期**：2024年4月6日
- **目标完成**：2024年4月20日
- **截止日期**：2024年4月24日

---

## 项目简介

智学助手是一款基于 **RAG（检索增强生成）** 技术的智能学习助手微信小程序。

### 核心功能
1. 📚 **文档上传** - 支持PDF、Word、TXT格式学习资料
2. 🤖 **AI问答** - 基于上传文档的智能问答
3. 🔍 **知识检索** - 显示答案来源，可追溯可验证
4. 📱 **微信小程序** - 随时随地使用

### 技术栈
| 层级 | 技术 |
|------|------|
| 前端 | 微信小程序 (WXML/WXSS/JS) |
| 后端 | Python + FastAPI |
| AI | RAG (BGE Embedding + FAISS + DeepSeek API) |
| 数据库 | SQLite |

---

## 团队分工

| 角色 | 姓名 | 主要职责 | 状态 |
|------|------|----------|------|
| 组长 | | 项目管理、RAG系统、协调 | 🟡 |
| 前端 | | 微信小程序开发 | ⚪ |
| 后端 | | FastAPI后端、数据库 | ⚪ |

**图例**：🟢 已完成 | 🟡 进行中 | ⚪ 未开始

---

## 项目结构

```
zhixue-assistant/
├── docs/                    # 📚 团队分工文档
│   ├── 组长职责.md
│   ├── 前端开发指南.md
│   └── 后端开发指南.md
│
├── frontend/                # 📱 微信小程序前端
│   ├── pages/               # 页面代码
│   └── ...
│
├── backend/                 # 🖥️ FastAPI后端
│   ├── main.py
│   └── ...
│
├── ai_module/               # 🤖 AI/RAG模块（已完成✅）
│   ├── rag_system.py        # RAG检索系统
│   └── ...
│
└── README.md                # 本文件
```

---

## 开发进度

### Week 1 (4/6 - 4/13) - 核心功能开发
- [ ] 环境搭建完成（所有人）
- [ ] API接口定义完成（前后端）
- [ ] MVP可用（能上传、能问答）

### Week 2 (4/14 - 4/20) - 优化完善
- [ ] 前端UI美化
- [ ] 后端性能优化
- [ ] 联调测试完成

### Final (4/21 - 4/24) - 提交准备
- [ ] 最终测试
- [ ] 演示准备

---

## Git 工作流

### 提交代码
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 创建功能分支
git checkout -b feature/你的功能名称

# 3. 提交更改
git add .
git commit -m "feat: 描述你的改动"

# 4. 推送到远程
git push origin feature/你的功能名称

# 5. 在GitHub创建 Pull Request
```

### 提交规范
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `refactor`: 代码重构

---

## 团队沟通

- **每日同步**：微信群，每晚10点同步进度
- **周会**：腾讯会议，每周日晚8点
- **紧急联系**：直接微信@相关人员

---

## 快速命令

```bash
# 启动后端
cd backend
python main.py

# 运行RAG测试
cd ai_module
python rag_system.py

# 查看Git状态
git status
git log --oneline -10
```

---

## 课程作业说明

### 使用的AI方法
1. **RAG（检索增强生成）** - 深度学习
   - Embedding模型：BAAI/bge-small-zh
   - 向量检索：FAISS HNSW
   - 生成模型：DeepSeek API

2. **朴素贝叶斯分类器** - 传统机器学习
   - 自动识别文档类别
   - 拉普拉斯平滑

### 验收方式
- 直接演示小程序功能
- 无需PPT

---

## 私密性说明

本项目为**团队私有项目**，GitHub仓库已设置为Private，仅限授权成员访问。

---

**最后更新**：2024年4月6日

**项目状态**：🟡 开发中