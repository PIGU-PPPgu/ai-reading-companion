# IntelliTutor Knowledge Graph 排查记录

日期：2026-04-23
项目：`/Users/pigou/.openclaw/workspace/ai-reading-companion/deeptutor`

## 目标
排查 Knowledge Graph 是否导致 Mac 死机/后端被杀。

## 已做检查

### 1. 修复了一个真实 bug
文件：`deeptutor/deeptutor/capabilities/knowledge_graph.py`
- 原来 `_parse_triples()` 手写 JSON 解析，鲁棒性差。
- 已改为复用共享 `parse_json_response()`。
- 现在可处理：
  - 纯 JSON
  - Markdown ```json 代码块
  - 前后带解释文字的 JSON

附带修复：
文件：`deeptutor/deeptutor/utils/json_parser.py`
- 将 `logging.Logger | None` 改为 `Optional[logging.Logger]`
- 原因：系统 `python3` 是 3.9.6，`|` 联合类型会直接报错。

### 2. 核心结论：图谱生成函数本身能跑通
直接在项目 venv 中执行：
- `generate_from_content(content, 'demo-math')`
- 成功返回：`10 nodes / 17 edges`

结论：
- **底层图谱构建逻辑不是直接导致死机的根因**
- 至少在小样本内容下，生成逻辑本身正常

### 3. API 服务层表现异常
现象：
- 后端启动后可访问 `/openapi.json`
- 但继续做接口调用时，服务进程被直接杀掉
- 进程状态：`Process exited with signal SIGKILL`

这说明：
- 不是普通 Python 异常
- 更像是：
  - 内存压力过高
  - 被系统 OOM / 资源管理直接杀进程
  - 或某个重量级路径导致服务瞬时资源爆炸

### 4. 前端图谱页面代码初步检查
文件：`web/app/(workspace)/graph/page.tsx`
发现：
- 页面会并发加载：
  - `fetchGraph(kb)`
  - `fetchStats(kb)`
  - `getWeakNodes(kb)`
- 页面支持：
  - `expandGraph(kb, 5, 1500)`
- `深度拆解`按钮目标节点数高达 **1500**

风险判断：
- 如果图谱较大，前端渲染 + 后端返回大 JSON + D3 交互，资源压力会明显升高
- 真正高危的不是普通 generate，而是 **expandGraph + 前端可视化**

### 5. graph_generator 初步检查
文件：`deeptutor/deeptutor/services/knowledge_graph/graph_generator.py`
发现：
- 普通生成会：
  - 调 LLM
  - `_extract_json()`
  - `KnowledgeNode.from_dict()` / `KnowledgeEdge.from_dict()`
  - `save_graph()` 到本地 JSON
- 没看到明显无限递归或显式爆内存逻辑
- 输入内容被截断到 `content[:8000]`

结论：
- 普通 `generate_from_content()` 路径目前看**不算重灾区**
- 更像是服务/API/前端联动时出问题

## 当前判断

### 新增回归嫌疑点（2026-04-23 深夜二次排查）

进一步检查前端/扩展实现后，发现以下高风险点：

#### 1. `InteractiveGraph.tsx` 的 minimap 实现非常可疑
文件：`deeptutor/web/components/knowledge-graph/InteractiveGraph.tsx`

现状：
- 在 `simulation.on("tick")` 里每一帧都调用 `updateMinimap()`
- `updateMinimap()` 内部会：
  - `mmSvg.selectAll("*").remove()`
  - 然后**整张 minimap 的边和节点全部重绘**

这意味着：
- 力导向图每 tick 一次
- 每次 tick 都会对 minimap 做一次**全量 DOM 销毁 + 全量重建**
- 如果节点上千、边更多，这个开销会非常夸张

这很像典型的前端回归 bug：
- 小图没事
- 中大型图开始疯狂吃 CPU / 内存
- 浏览器、Node、系统一起承压

**这是目前最像真凶的点。**

#### 2. `InteractiveGraph.tsx` 还在组件内重复拉 stats
现状：
- 父页面 `graph/page.tsx` 已经会加载 `fetchStats(kb)`
- `InteractiveGraph.tsx` 内部又在 `useEffect` 里再次 `fetchStats(kbName)`

这不一定会直接炸机，但属于重复请求和重复状态更新，放大了图页开销。

#### 3. 高亮节点时会自动触发缩放动画
现状：
- `highlightedNodeId` 存在时会自动 `svg.transition().duration(500).call(zoom.transform, ...)`
- 图大时，缩放动画、力导向模拟、minimap 重绘会叠加

这条单独看不致命，但会放大前端卡顿。

#### 4. expand 依然是高风险放大器，但不一定是首要元凶
文件：`deeptutor/deeptutor/services/knowledge_graph/expansion_agent.py`

现状：
- 默认 `target_nodes=1500`
- 每批 5 个叶子节点，逐批扩展并保存
- 如果 LLM 返回质量差、结构密、图连接度升高，前端压力会被迅速放大

但结合“之前 1000 节点也没事”的用户反馈，**更像是近期前端增强（尤其 minimap / 动画 / 交互）触发了回归**，而不是单纯因为节点数大。

### 最可能的风险排序
1. **InteractiveGraph 的 minimap 每 tick 全量重绘（最高嫌疑）**
2. **前端图渲染 + 动画 + 缩放联动导致资源飙升**
3. **图谱扩展（expand）放大图规模，进一步触发前端回归问题**
4. **API 服务进程资源限制或异常退出**
5. **普通生成接口本身**

## 已确认事实
- 不是单纯“图谱生成函数一运行就炸”
- 是**某个 Knowledge Graph 相关路径会把进程顶到被系统杀掉**
- `SIGKILL` 是关键证据

## 建议下一步

### A. 优先缩小风险面
1. **先修 `InteractiveGraph` 的 minimap 更新策略**
   - 禁止在每个 simulation tick 里全量 `remove()` + 重绘
   - 至少改成：
     - 只在若干 tick / 节流后更新
     - 或 simulation end 时更新
     - 或复用既有元素，只更新坐标
2. 去掉 `InteractiveGraph` 内部重复 `fetchStats()`
3. 高节点量时关闭或降级：
   - minimap
   - 自动缩放动画
   - 某些 hover/tooltip/边标签效果
4. `expandGraph()` 默认目标节点从 `1500` 降到更保守值（即使它不是真凶，也该限流）
5. 图谱页增加节点数保护：
   - 超过一定数量先不自动渲染完整图
   - 先展示树/摘要/分层加载
6. generate 接口增加日志：
   - 输入长度
   - LLM 返回长度
   - 节点数/边数
   - save_graph 耗时

### B. 做系统级证据收集
下次复现时同步观察：
- Activity Monitor 的内存压力
- Console.app 里是否出现 OOM / killed / jetsam / memory pressure
- `vm_stat` / `memory_pressure` 输出

### C. 做代码级记录点
建议在这些位置加日志：
- `kg_graph.py::generate_graph`
- `graph_generator.py::generate_from_content`
- `graph_store.py::save_graph`
- `expand_graph()` 路径
- 前端 `handleGenerate()` / `handleExpand()`

## 本次结论（一句话）
**目前证据更支持“Knowledge Graph 某条重路径把系统资源打满，导致进程被 SIGKILL”，而不是“普通图谱构建代码逻辑错误直接让电脑死机”。**
