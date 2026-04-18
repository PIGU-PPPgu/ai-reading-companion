# DeepTutor 插件开发接口文档

> 版本: v1.0 | 基于 DeepTutor 源码逆向分析 | 2026-04-17

## 架构概览

```
用户消息 → ChatOrchestrator → Capability → Tools
                                  ↓
                              StreamBus (事件流)
                                  ↓
                              Knowledge Base (RAG)
```

三层架构：
- **Level 1: Tools** — 单一功能原子工具（RAG搜索、代码执行等）
- **Level 2: Capabilities** — 多步骤 Agent Pipeline（Deep Solve、Deep Question 等）
- **Level 3: Orchestrator** — 路由层，根据 context 分发到对应 Capability

## 核心 API

### HTTP Endpoints

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/plugins/list` | GET | 列出所有已注册的 tools + capabilities + plugins |
| `/api/v1/plugins/tools/{name}/execute` | POST | 执行单个 tool |
| `/api/v1/plugins/tools/{name}/execute-stream` | POST | 执行 tool 并 SSE 流式返回日志+结果 |
| `/api/v1/plugins/capabilities/{name}/execute-stream` | POST | 执行 capability（SSE 流式） |
| `/api/v1/chat/sessions` | GET | 列出聊天会话 |
| `/api/v1/knowledge/list` | GET | 列出知识库及状态 |
| `/api/v1/knowledge/{name}` | GET | 知识库详情 |
| `/api/v1/knowledge/{name}/upload` | POST | 上传文件到知识库 |
| `/api/v1/knowledge/create` | POST | 创建知识库 |
| `/api/v1/settings` | GET/POST | LLM/Embedding 配置 |

### 完整 API 列表

<details>
<summary>点击展开全部 API 端点</summary>

```
/api/v1/chat/sessions                     GET  - 列出会话
/api/v1/chat/sessions/{id}                GET  - 获取会话详情
/api/v1/knowledge/list                    GET  - 列出知识库
/api/v1/knowledge/{name}                  GET  - 知识库详情
/api/v1/knowledge/create                  POST - 创建知识库
/api/v1/knowledge/{name}/upload           POST - 上传文件
/api/v1/knowledge/{name}/config           GET  - 知识库配置
/api/v1/knowledge/configs                 GET  - 全局KB配置
/api/v1/knowledge/configs/sync            POST - 同步KB配置
/api/v1/knowledge/rag-providers           GET  - 可用RAG引擎
/api/v1/knowledge/default                 GET/POST - 默认知识库
/api/v1/plugins/list                      GET  - 插件列表
/api/v1/plugins/tools/{name}/execute      POST - 执行tool
/api/v1/plugins/tools/{name}/execute-stream POST - 流式执行tool
/api/v1/plugins/capabilities/{name}/execute-stream POST - 流式执行capability
/api/v1/solve/sessions                    GET  - 解题会话
/api/v1/settings                          GET/POST - 全局设置
/api/v1/settings/catalog                  GET  - 设置目录
/api/v1/system/status                     GET  - 系统状态
/api/v1/system/test/llm                   POST - 测试LLM连接
/api/v1/system/test/embeddings            POST - 测试Embedding连接
/api/v1/system/test/search                POST - 测试搜索
```

</details>

## 开发插件（Tool）

### 接口定义

```python
from deeptutor.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult

class MyTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        """声明工具名称、描述和参数"""
        return ToolDefinition(
            name="my_tool",
            description="What this tool does.",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",       # string|integer|boolean|number|array|object
                    description="描述",
                    required=True,
                ),
            ],
        )

    async def execute(self, **kwargs) -> ToolResult:
        """执行工具逻辑"""
        query = kwargs.get("query", "")
        # ... 业务逻辑 ...
        return ToolResult(
            content="结果文本",
            sources=[{"type": "my_tool", "query": query}],
            metadata={"key": "value"},
            success=True,
        )

    def get_prompt_hints(self, language: str = "en") -> ToolPromptHints:
        """可选：给 LLM 的提示信息"""
        return ToolPromptHints(
            short_description="简短描述",
            when_to_use="何时使用",
            input_format="输入格式",
        )
```

### 注册 Tool

在 `deeptutor/tools/builtin/__init__.py` 中：

```python
BUILTIN_TOOL_TYPES = (
    ...,  # 已有的 tools
    MyTool,  # 新增
)
```

### 已有内置 Tools

| Tool | 名称 | 说明 |
|------|------|------|
| RAGTool | `rag` | 知识库 RAG 搜索 |
| WebSearchTool | `web_search` | 网页搜索 |
| CodeExecutionTool | `code_execution` | Python 代码执行 |
| BrainstormTool | `brainstorm` | 头脑风暴 |
| ReasonTool | `reason` | 深度推理 |
| PaperSearchToolWrapper | `paper_search` | arXiv 论文搜索 |
| GeoGebraAnalysisTool | `geogebra_analysis` | 数学图片分析 → GeoGebra |

### Tool 别名系统

```python
TOOL_ALIASES = {
    "rag_hybrid": ("rag", {}),
    "rag_naive": ("rag", {}),
    "code_execute": ("code_execution", {}),
}
```

## 开发插件（Capability）

### 接口定义

```python
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus

class MyCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="my_capability",
        description="What this capability does.",
        stages=["planning", "execution", "summary"],  # 阶段
        tools_used=["rag", "web_search"],              # 使用的tools
        cli_aliases=["mc"],                            # CLI别名
        config_defaults={"temperature": 0.7},
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        """执行完整的多步骤 pipeline"""
        # Stage 1: 规划
        async with stream.stage("planning", source=self.manifest.name):
            plan = await self._plan(context)

        # Stage 2: 执行
        async with stream.stage("execution", source=self.manifest.name):
            result = await self._execute(plan, context)

        # Stage 3: 总结
        async with stream.stage("summary", source=self.manifest.name):
            await stream.emit_text(result.summary)
```

### 注册 Capability

在 `deeptutor/runtime/bootstrap/builtin_capabilities.py` 中：

```python
BUILTIN_CAPABILITY_CLASSES = {
    ...,  # 已有的
    "my_capability": "deeptutor.capabilities.my_cap:MyCapability",
}
```

### 已有内置 Capabilities

| Capability | 名称 | 说明 |
|-----------|------|------|
| ChatCapability | `chat` | 普通对话 |
| DeepSolveCapability | `deep_solve` | 深度解题 |
| DeepQuestionCapability | `deep_question` | 深度提问 |
| DeepResearchCapability | `deep_research` | 深度研究 |
| MathAnimatorCapability | `math_animator` | 数学动画 |
| VisualizeCapability | `visualize` | 可视化 |

## 核心数据结构

### UnifiedContext

```python
@dataclass
class UnifiedContext:
    session_id: str = ""
    user_message: str = ""
    conversation_history: list[dict] = field(default_factory=list)
    enabled_tools: list[str] | None = None
    active_capability: str | None = None
    knowledge_bases: list[str] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)
    config_overrides: dict = field(default_factory=dict)
    language: str = "en"
    notebook_context: str = ""
    history_context: str = ""
    memory_context: str = ""
    metadata: dict = field(default_factory=dict)
```

### StreamEvent 类型

```
SESSION  - 会话元数据
THINKING - 内部思考过程
TEXT     - 文本输出
TOOL_CALL - 工具调用
RESULT   - 最终结果
ERROR    - 错误
DONE     - 完成
```

## 配置系统

### LLM 配置

```json
{
    "services": {
        "llm": {
            "active_profile_id": "llm-profile-default",
            "profiles": [{
                "binding": "openai",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_key": "sk-xxx",
                "models": [{
                    "model": "Pro/zai-org/GLM-5"
                }]
            }]
        },
        "embedding": {
            "profiles": [{
                "binding": "openai",
                "base_url": "https://api.siliconflow.cn/v1",
                "models": [{
                    "model": "Qwen/Qwen3-Embedding-8B",
                    "dimension": "4096"
                }]
            }]
        }
    }
}
```

### 知识库配置

位置: `data/knowledge_bases/kb_config.json`

```json
{
    "defaults": {
        "default_kb": "骆驼祥子",
        "rag_provider": "llamaindex",
        "search_mode": "hybrid"
    },
    "knowledge_bases": {
        "七年级数学": {
            "path": "七年级数学",
            "status": "ready",
            "rag_provider": "llamaindex"
        }
    }
}
```

## Phase 1 开发指引：content-analyzer 插件

### 方案 A: 作为 Tool 开发（推荐先用）

```python
class ContentAnalyzerTool(BaseTool):
    """内容类型自动识别 + 结构化拆解"""
    name = "content_analyzer"

    async def execute(self, **kwargs) -> ToolResult:
        content = kwargs.get("content", "")
        content_type = await self._detect_type(content)  # 文学/数学/英语/科学/社科
        structured = await self._analyze(content, content_type)
        return ToolResult(content=json.dumps(structured), metadata={"type": content_type})
```

### 方案 B: 作为 Capability 开发（更灵活）

```python
class ContentAnalyzerCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="content_analyzer",
        stages=["detect", "analyze", "structure", "validate"],
        tools_used=["rag"],
    )
```

### 开发步骤

1. 在 `deeptutor/capabilities/` 下创建 `content_analyzer.py`
2. 实现 `ContentAnalyzerCapability`
3. 在 `builtin_capabilities.py` 注册
4. 通过 `/api/v1/plugins/capabilities/content_analyzer/execute-stream` 测试
5. 前端集成

### 内容类型识别规则

| 类型 | 检测关键词 | 拆解方式 |
|------|-----------|---------|
| 文学名著 | 章/回/人物/描写 | 章节/人物/主题/写作手法 |
| 数学教材 | 定理/公式/例题/证明 | 知识点/公式/例题/前置链 |
| 英语教材 | vocabulary/grammar/text | 词汇/语法/课文 |
| 科学教材 | 实验/现象/定律 | 概念/实验/公式/应用 |
| 社科教材 | 时间/事件/人物 | 时间线/事件/人物/因果 |

---

*文档基于 DeepTutor v1.0 源码分析，Pigou 的 AI 阅读家教项目专用*
