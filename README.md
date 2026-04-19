# IntelliTutor - AI智能学习伴侣

> 🚀 基于 [DeepTutor](https://github.com/PIGU-PPPgu/DeepTutor)（港大 DSA Lab, Apache-2.0）深度改造的 K12 全学科智能学习平台

## 截图

<table>
<tr>
<td><img src="screenshots/homepage.png" alt="Homepage" width="400"/></td>
<td><img src="screenshots/chat-session.png" alt="Chat" width="400"/></td>
</tr>
<tr>
<td><img src="screenshots/knowledge.png" alt="Knowledge Base" width="400"/></td>
<td><img src="screenshots/interactive-graph.png" alt="Knowledge Graph" width="400"/></td>
</tr>
</table>

## 我们在 DeepTutor 上做了什么

DeepTutor 是一个优秀的 RAG 对话框架，但我们做了 **远超 fork 的改造**：

### 🆕 全新实现的 Capability（10个）

| Capability | 功能 | 亮点 |
|-----------|------|------|
| 🎓 **Content Analyzer** | 内容自动识别+拆解 | 6种类型，99%准确率，中考考点标注 |
| 📈 **Learning Guide** | 个性化学习计划 | 拓扑排序+布鲁姆+艾宾浩斯 |
| 💡 **Socratic Dialog** | 苏格拉底式引导对话 | 3种模式，绝不说答案 |
| 🕸️ **Knowledge Graph** | 交互式知识图谱 | D3.js，掌握度追踪，1500+节点 |
| 📊 **Assessment** | 自适应测评 | 4题型+难度自适应+掌握度更新 |
| 📋 **Parent Report** | 家长周报 | 学习进度+辅导建议 |
| 🔊 **Audio Companion** | NotebookLM式播客 | 双人对话+TTS |
| 📚 **Flashcard** | 间隔重复闪卡 | 4种卡片+艾宾浩斯 |
| 🗺️ **Mindmap** | 思维导图 | Mermaid 渲染 |
| 📖 **Content Manager** | 内容导入管理 | PDF/EPUB/URL |

### 🔧 核心改造

- **品牌重塑**: DeepTutor → IntelliTutor
- **LLM 适配**: 接入 GPT-5.4 / GLM-5 / DeepSeek，替换原版 OpenAI-only
- **Embedding**: Qwen3-Embedding-8B（4096维）via 硅基流动
- **Stream API 修复**: 6个 Capability 的 `stream.thinking()` → `stream.content()`，解决前端不渲染问题
- **Knowledge Graph 引擎**: 全新实现，支持 JSON 导入、递归扩展（1500+节点）、掌握度颜色系统
- **前端 9 个页面**: Chat、Knowledge Graph、Knowledge Base、Settings 等
- **API 50+ 端点**: 完整的 REST API + SSE 流式
- **380+ 测试用例**: 从 87 failed 修复到 3 failed

### 📊 能力全景（17 Capabilities + 9 Tools）

| 模块 | 功能 | 来源 |
|------|------|------|
| 🎯 Chat | RAG + Web Search 对话 | 基座 |
| 🧩 Deep Solve | 多步推理解题 | 基座 |
| 📝 Deep Question | 深度提问 | 基座 |
| 🔬 Deep Research | 多智能体研究 | 基座 |
| 🎬 Math Animator | 数学动画分镜 | 基座 |
| 📊 Visualize | SVG/Chart.js/Mermaid 可视化 | 基座 |
| 🧠 Memory Chat | 三层记忆系统 | 基座 |
| 🎓 Content Analyzer | 内容识别+拆解 | **新实现** |
| 📈 Learning Guide | 个性化学习计划 | **新实现** |
| 💡 Socratic Dialog | 苏格拉底对话 | **新实现** |
| 🕸️ Knowledge Graph | 交互式知识图谱 | **新实现** |
| 📊 Assessment | 自适应测评 | **新实现** |
| 📋 Parent Report | 家长周报 | **新实现** |
| 🔊 Audio Companion | 播客式音频 | **新实现** |
| 📚 Flashcard | 间隔重复闪卡 | **新实现** |
| 🗺️ Mindmap | 思维导图 | **新实现** |
| 📖 Content Manager | 内容导入 | **新实现** |

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Next.js 16 + React 19 + TailwindCSS + D3.js |
| 后端 | Python 3.12 + FastAPI + WebSocket |
| LLM | GPT-5.4 (api.intellicode.top) / GLM-5 (硅基流动) |
| Embedding | Qwen3-Embedding-8B (4096维) via 硅基流动 |
| RAG | LlamaIndex + 自定义知识库管线 |
| TTS | 硅基流动 siliconflow-tts-001 |

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/PIGU-PPPgu/ai-reading-companion.git
cd ai-reading-companion/deeptutor

# 2. 安装
pip install -e ".[dev]"

# 3. 配置
cp .env.example .env
# 编辑 .env 填入 LLM API key

# 4. 启动后端
python -m deeptutor serve --port 8001

# 5. 启动前端
cd web && pnpm install
PORT=3782 npx next dev -p 3782
```

访问 http://localhost:3782

## 项目结构

```
ai-reading-companion/
├── deeptutor/              # DeepTutor fork（核心引擎）
│   ├── deeptutor/
│   │   ├── capabilities/   # 17 Capability 插件（10个全新实现）
│   │   ├── agents/         # ChatAgent, ResearchAgent, ExpansionAgent
│   │   ├── services/       # LLM, RAG, Memory, KnowledgeGraph
│   │   ├── api/            # FastAPI 路由（50+ 端点）
│   │   └── core/           # StreamBus, Context, Protocol
│   ├── web/                # Next.js 前端（9 页面）
│   └── tests/              # 380+ 测试
├── content/                # 教材 PDF
├── screenshots/            # 截图
└── README.md
```

## 进度

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 0 | 基座搭建 | ✅ 完成 |
| Phase 1 | 核心引擎（content-analyzer + learning-guide + socratic-dialog） | ✅ 完成（提前一周） |
| Phase 2 | 音频+测评+闪卡+家长报告 | ✅ 完成（提前两周） |
| Phase 3 | 前端+扩展（微信小程序+内容导入） | ⏳ 待开始 |
| Phase 4 | 打磨+测试 | 📋 待开始 |
| Phase 5 | 上线准备 | 📋 待开始 |

## License

Apache-2.0（基于 [DeepTutor](https://github.com/HKUDS/DeepTutor)）
