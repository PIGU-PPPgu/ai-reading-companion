# 📖 AI 阅读家教 — 基于 DeepTutor 的智能阅读辅导系统

> 基于 [DeepTutor](https://github.com/HKUDS/DeepTutor)（港大，Apache-2.0）深度定制的 **K-12 阅读理解与数学辅导平台**。

## 🎯 项目定位

面向初中生（七年级）的 AI 个性化阅读家教，支持**数学概念学习**和**名著阅读理解**，具备知识图谱、记忆系统、苏格拉底式对话等核心能力。

## 🏗️ 技术栈

| 组件 | 技术选型 |
|------|---------|
| 后端 | DeepTutor (Python 3.12, FastAPI) |
| 前端 | Next.js 16 + TypeScript |
| LLM | GPT-5.4 (via api.intellicode.top) |
| Embedding | Qwen3-Embedding-8B (4096维, via 硅基流动) |
| RAG | LlamaIndex + 向量存储 |
| 知识库 | 七年级数学、骆驼祥子 |

## 📊 功能对比：原版 DeepTutor vs 我们的增强版

### Capabilities（能力层）

| 功能 | 原版 DeepTutor | 我们的增强版 | 说明 |
|------|:-:|:-:|------|
| Chat（智能对话） | ✅ | ✅ | 原版核心功能 |
| Deep Solve（多步解题） | ✅ | ✅ | 原版核心功能 |
| Deep Research（深度研究） | ✅ | ✅ | 原版核心功能 |
| Guide（引导式学习） | ✅ | ✅ | 原版核心功能 |
| Co-Writer（智能写作） | ✅ | ✅ | 原版核心功能 |
| Visualize（可视化） | ✅ | ✅ | 原版核心功能 |
| Math Animator（数学动画） | ✅ | ✅ | 原版核心功能 |
| Notebook（笔记本） | ✅ | ✅ | 原版核心功能 |
| Question（出题） | ✅ | ✅ | 原版核心功能 |
| Vision Solver（图片解题） | ✅ | ✅ | 原版核心功能 |
| **Content Analyzer（内容分析）** | ❌ | ✅ 🆕 | 4阶段：检测→分析→结构化→验证 |
| **Socratic Dialog（苏格拉底对话）** | ❌ | ✅ 🆕 | 引导式提问，不直接给答案 |
| **Learning Guide（学习引导）** | ❌ | ✅ 🆕 | 个性化学习路径规划 |
| **Audio Companion（语音伴读）** | ❌ | ✅ 🆕 | TTS 朗读 + 听力理解 |
| **Assessment（学习评估）** | ❌ | ✅ 🆕 | 多维度能力评估 |
| **Flashcard（闪卡记忆）** | ❌ | ✅ 🆕 | 间隔重复 + 主动回忆 |
| **Parent Report（家长报告）** | ❌ | ✅ 🆕 | 学习进度 + 知识掌握分析 |
| **Content Manager（内容管理）** | ❌ | ✅ 🆕 | 教材/题目/知识点的上传管理 |
| **Mindmap（思维导图）** | ❌ | ✅ 🆕 | 自动生成概念关系图 |
| **Knowledge Graph（知识图谱）** | ❌ | ✅ 🆕 | 三元组提取 + 7种关系 + BFS查询 + Mermaid可视化 |
| **Memory Enhanced Chat（记忆增强对话）** | ❌ | ✅ 🆕 | 三层记忆系统：短期/中期/长期 |

### Tools（工具层）

| 工具 | 原版 | 我们的增强版 | 说明 |
|------|:-:|:-:|------|
| RAG（知识库检索） | ✅ | ✅ | |
| Web Search | ✅ | ✅ | |
| Code Execution | ✅ | ✅ | |
| Brainstorm | ✅ | ✅ | |
| Reason | ✅ | ✅ | |
| Paper Search | ✅ | ✅ | |
| **Knowledge Graph Tool** | ❌ | ✅ 🆕 | 知识图谱操作工具 |
| **Content Analyzer Tool** | ❌ | ✅ 🆕 | 内容分析工具 |
| **TeX Chunker / Downloader** | ❌ | ✅ 🆕 | 数学公式处理 |

### 统计

| 指标 | 原版 | 我们 |
|------|------|------|
| Capabilities | 10 | **18** (+8) |
| Tools | 6 | **9** (+3) |
| 知识库 | — | 七年级数学、骆驼祥子 |
| 单元测试 | — | 380+ passed |

## 🚀 快速启动

### 1. 后端

```bash
cd deeptutor
pip install -e . --break-system-packages  # 或用 venv
deeptutor serve --port 8001
```

### 2. 前端

```bash
cd deeptutor/web
pnpm install
PORT=3782 npx next dev -p 3782
```

### 3. 配置

编辑 `deeptutor/.env`：

```env
LLM_BINDING=openai
LLM_MODEL=gpt-5.4
LLM_API_KEY=your-api-key
LLM_HOST=https://your-llm-endpoint/v1

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B
EMBEDDING_API_KEY=your-embedding-key
EMBEDDING_HOST=https://api.siliconflow.cn/v1
```

## 📸 截图

> 对话界面：支持知识库检索 + 工具调用 + 流式回复

## 🔧 已知问题 & TODO

- [x] 知识库下拉框 disabled → 已修（默认启用 rag）
- [x] 测试文件名冲突 → 已修（318→380+ passed）
- [x] LLM function calling 不稳定 → 已切换 GPT-5.4
- [ ] Knowledge Graph 前端入口
- [ ] Memory Enhanced Chat 前端入口
- [ ] 端到端测试所有新 capability

## 📄 License

基于 [DeepTutor](https://github.com/HKUDS/DeepTutor) (Apache-2.0) 二次开发。
