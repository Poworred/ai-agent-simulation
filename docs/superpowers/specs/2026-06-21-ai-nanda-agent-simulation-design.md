# AI 南大｜多智能体校园社会模拟系统设计规格

**日期：** 2026-06-21  
**状态：** 设计已由用户逐节确认，等待审查与实现计划  
**目标形态：** React/Next.js 前端 + Python FastAPI 后端 + SQLite + 真实 LLM 调用层

---

## 1. 背景与目标

AI 南大是一个面向中国高校场景的轻量级多智能体校园社会模拟原型。它参考 HKUST Aivilization、Stanford Generative Agents、AI Town 与 Concordia 等项目，把南昌大学校园抽象为一个 AI Agent 可以感知、行动、对话、记忆和反思的虚拟环境。

MVP 的核心命题是：

> 如果把校园生活建模为地点、时间、课程、社团、关系和事件，AI Agent 能否产生足够可读、可看、可传播的校园生活叙事？

第一版不是复刻 10 万 Agent 规模的 Aivilization，也不是做一个泛化聊天机器人。它要完成一个可演示的真实 LLM Agent MVP：用户打开网页后，可以观察 5-8 个 AI 新生在简化南大校园中连续经历一周生活，并能对少数 Agent 进行轻量干预。

### 1.1 成功标准

MVP 至少需要满足：

- 前端能展示简化校园地图、Agent 位置、事件流和 Agent 详情。
- 后端能创建并推进一场 7 天模拟。
- 至少 5 个主 Agent 具备 profile、state、schedule、memory 和 relationship。
- 至少 6 个地点可被访问并触发不同事件。
- 至少支持一次真实 LLM 生成的多 Agent 对话。
- 每个主 Agent 每天能生成一条反思或 fallback 反思。
- 用户干预进入 Agent 记忆，并影响后续决策，而不是直接改写状态。
- LLM 输出经过结构化校验，失败时可降级，不中断模拟。
- 单次演示能在 5 分钟内说明项目价值。

### 1.2 明确不做

第一版不做：

- 用户登录和账号系统。
- 多用户协同观看。
- WebSocket 实时推送。
- 长期后台自动模拟。
- LangGraph / AutoGen / CrewAI 等复杂 Agent 框架。
- 真实教务系统。
- 真实 GIS 校园地图。
- 100+ Agent 或 10 万 Agent 级规模。
- 真实经济系统、真钱交易或复杂社会治理。
- 真实社会科学预测。

---

## 2. 参考项目带来的设计原则

### 2.1 Stanford Generative Agents

Stanford Generative Agents 的开源实现采用 Python 后端模拟系统 + Django 环境服务器。其核心机制是：

```text
Observe -> Store Memory -> Retrieve Memories -> Reflect -> Plan -> Act -> Update World
```

可直接借鉴的部分：

- Memory Stream：用自然语言记录 Agent 经历。
- Retrieval：按最近性、重要性和相关性检索记忆。
- Reflection：把多条原始记忆总结成更高层的长期记忆。
- Planning：根据 profile、记忆和当前目标生成日程。
- Replay / saved simulation：保留模拟过程，便于调试和展示。

对 AI 南大的转化：

```text
校园观察 -> 事件写入 -> 记忆检索 -> 每日反思 -> 日程计划 -> 行动选择 -> Game Master 更新世界
```

### 2.2 HKUST Aivilization / AIvilization v0

Aivilization 更偏大规模 AI 社会沙盒，强调统一 Agent 架构、分层规划、自适应 profile、双过程记忆、人类引导和资源约束。第一版不学习它的规模，而学习它的思想：

- Agent 不应只靠一段 prompt，而应有稳定架构。
- 人类干预不直接改写世界结果，而是进入记忆、目标或计划。
- 长期目标需要拆成周目标、日目标和即时行动。
- 短期执行痕迹和长期语义总结要分开。

对 AI 南大的转化：

```text
AgentProfile + AgentState + Goals + Memory + Human Steering + Game Master
```

### 2.3 本项目采用的融合方向

AI 南大第一版采用：

> Stanford-style Smallville Agent Loop + Aivilization-style Human Steering + Campus Game Master

也就是说：

- 工程结构学习 Stanford 的小规模可运行模拟。
- 干预、目标和记忆思想学习 Aivilization。
- 校园世界由 Game Master 统一仲裁，避免 LLM 直接改写数据库。

### 2.4 深度调研后的实现约束

2026-06-21 的多来源调研进一步确认：Stanford Generative Agents 更适合作为 AI 南大 MVP 的直接工程参考，Aivilization 更适合作为长期设计理念参考。

实现时必须保留三条约束：

1. **可回放事件流。** 事件流不是装饰性日志，而是 replay、debug、记忆写入和作品集展示的共同基础。因此 `events.state_delta`、`event_type`、`agent_ids` 和 `llm_generated` 必须在实现中保留。
2. **行动验证器 / Game Master。** LLM 或 Agent Runtime 只能提出 action，所有世界状态变化必须由 Game Master 验证后应用。这对应 Aivilization 中 action simulation / validation 的思想。
3. **种子数据可演化。** 第一版可以用 Python seed data，但结构上要为未来 JSON/CSV 导入 persona、history 和 memory stream 留空间。这对应 Stanford 用 CSV 历史文件初始化 Agent memory stream 的工程入口。

这意味着第一版不是“聊天角色集合”，而是一个小规模、可回放、可调试的校园社会模拟系统。

---

## 3. 总体架构

第一版采用 **React/Next.js 前端 + Python FastAPI 后端 + SQLite + 真实 LLM 调用层**。

```text
Next.js Frontend
  ├─ 校园地图
  ├─ Agent 列表与位置
  ├─ 全局事件流
  ├─ Agent 详情面板
  ├─ 用户干预输入
  └─ 时间控制：开始 / 暂停 / 单步 / 快进

FastAPI Backend
  ├─ API Layer
  ├─ Simulation Engine
  ├─ Game Master
  ├─ Agent Runtime
  │   ├─ Perception Builder
  │   ├─ Memory Retriever
  │   ├─ Goal Manager
  │   ├─ Planner
  │   ├─ Action Selector
  │   ├─ Dialogue Generator
  │   └─ Reflection Generator
  ├─ Event System
  ├─ Memory System
  ├─ Relationship System
  ├─ LLM Service
  └─ SQLite Store
```

### 3.1 前端职责

前端不决定 Agent 下一步行为，只展示后端提供的状态并提交用户操作：

- 展示简化南大校园节点地图。
- 展示 Agent 当前位置、状态和当前行动。
- 展示持续更新的事件流。
- 展示 Agent 人设、目标、状态、记忆和关系。
- 提交用户干预。
- 提供初始化、单步、连续运行、暂停和快进控制。

### 3.2 后端职责

后端维护可运行校园世界：

- 保存模拟时间、地点、路径、Agent、事件、记忆和关系。
- 每个 tick 推进世界状态。
- 用规则处理常规行为：上课、吃饭、回宿舍、移动、地点开放判断。
- 用 LLM 处理高价值节点：多 Agent 对话、每日反思、用户干预解释、复杂事件选择、关键事件文本。
- 用 Game Master 校验行动并写回 SQLite。

### 3.3 架构取舍

选择 FastAPI 后端而不是 Next.js 单体，是因为项目核心展示点是 Agent Runtime、World State、Memory Store 和 LLM Service。Python 更适合表达 Agent 工程逻辑和测试模拟规则。

暂不做独立 worker / WebSocket，是为了降低 MVP 复杂度。第一版由前端定时调用 `/tick` 推进模拟即可。

---

## 4. 核心数据模型

SQLite 是第一版的持久化中心。关系表保证结构清晰，部分字段使用 JSON 以避免过早复杂建模。

```text
World State
  ├─ simulation_runs
  ├─ locations
  ├─ paths
  ├─ agents
  ├─ schedules
  ├─ events
  ├─ memories
  ├─ relationships
  ├─ user_interventions
  └─ llm_calls
```

### 4.1 simulation_runs

记录一场模拟的状态。

字段：

- `id`
- `name`
- `current_day`
- `current_minute`
- `tick_minutes`
- `status`: `idle | running | paused | completed`
- `created_at`
- `updated_at`

第一版可以默认只有一个活跃 run，但所有状态数据保留 `run_id`。

### 4.2 locations

地点是行动约束，不只是地图装饰。

首批地点：

- 宿舍区
- 教学楼
- 食堂
- 图书馆
- 体育场
- 社团招新点
- 失物招领处
- 校门 / 商业街

字段：

- `id`
- `name`
- `type`
- `description`
- `x`
- `y`
- `open_minutes` JSON
- `available_actions` JSON
- `event_tags` JSON

### 4.3 paths

地点连接图。

字段：

- `from_location_id`
- `to_location_id`
- `distance_minutes`

第一版不做真实 GIS，只用节点图和移动耗时。

### 4.4 agents

Agent 表同时保存稳定档案和当前状态。

档案字段：

- `id`
- `name`
- `role`
- `major`
- `personality`
- `interests` JSON
- `long_term_goals` JSON
- `social_style`

状态字段：

- `current_location_id`
- `current_goal`
- `current_action`
- `mood`
- `energy`
- `stress`
- `adaptation_score`
- `last_reflection_at`

### 4.5 schedules

记录课程、饭点、社团、学习和休息计划。

字段：

- `id`
- `agent_id`
- `day`
- `start_minute`
- `end_minute`
- `type`: `class | meal | club | study | rest | free`
- `title`
- `location_id`
- `priority`

### 4.6 events

事件既是前端事件流，也是世界事实和调试日志。

字段：

- `id`
- `run_id`
- `day`
- `minute`
- `event_type`
- `location_id`
- `agent_ids` JSON
- `summary`
- `details`
- `visibility`
- `llm_generated`
- `state_delta` JSON

事件承担三件事：

1. 展示给用户。
2. 支持调试和回放。
3. 写入相关 Agent 记忆。

### 4.7 memories

记忆分四类：

- `short_term`: 最近行动、对话、事件。
- `long_term`: 每日反思和重要经历。
- `relationship`: 对其他 Agent 的印象。
- `intervention`: 用户输入建议或任务。

字段：

- `id`
- `agent_id`
- `memory_type`
- `content`
- `importance`
- `tags` JSON
- `source`
- `related_agent_id`
- `related_event_id`
- `created_day`
- `created_minute`
- `last_accessed_at`
- `expires_at`

第一版不使用向量数据库，但 Memory Retriever 要按最近性、重要性和相关性评分。

### 4.8 relationships

关系网络先保持简单。

字段：

- `agent_a_id`
- `agent_b_id`
- `affinity`
- `familiarity`
- `trust`
- `relationship_tags` JSON
- `last_interaction_event_id`

示例规则：

- 对话成功：`familiarity + 1`
- 求助成功：`trust + 1`
- 误会事件：`affinity - 1`

### 4.9 user_interventions

用户干预不直接改变状态，而是进入记忆和下一轮感知。

字段：

- `id`
- `agent_id`
- `content`
- `status`: `pending | considered | accepted | ignored | completed`
- `created_day`
- `created_minute`
- `handled_event_id`

处理流程：

```text
用户输入建议
  -> 写入 user_interventions
  -> 写入 intervention memory
  -> 下一个 tick 进入 Agent perception
  -> LLM 或规则判断是否采纳
  -> Game Master 应用合法行动
  -> 生成事件说明
```

### 4.10 llm_calls

记录 LLM 调用，便于调试和成本控制。

字段：

- `id`
- `run_id`
- `agent_id`
- `function_name`
- `prompt_version`
- `input_summary`
- `output_json`
- `status`
- `latency_ms`
- `error_message`
- `created_at`

不记录 API key 或敏感信息。

---

## 5. Agent 行为循环

每个 tick 后端按顺序推进 Agent。

```text
Simulation Engine 推进时间
  -> 读取 World State
  -> 为每个 Agent 构建 Perception
  -> 检索相关 Memory
  -> Planner / Action Selector 选择候选行动
  -> 必要时调用 LLM
  -> Agent 提出 Action
  -> Game Master 校验 Action
  -> 更新 World State
  -> 生成 Event
  -> 写入 Memory / Relationship
  -> 返回前端展示
```

第一版采用顺序执行：

```text
Agent 1 action -> 更新世界
Agent 2 看到更新后的世界 -> action
...
```

未来可扩展为两阶段批处理：先收集所有 action，再由 Game Master 批量仲裁。

### 5.1 Perception Builder

为 Agent 构建当前感知，不调用 LLM。

示例：

```json
{
  "agent": "王一诺",
  "time": "Day 1 08:10",
  "location": "宿舍区",
  "current_goal": "赶去高数课",
  "nearby_agents": ["林见川"],
  "schedule": {
    "next": "08:30 高等数学课 @ 教学楼"
  },
  "available_actions": ["move", "talk", "idle"],
  "recent_events": ["王一诺昨晚担心自己找不到教学楼"],
  "user_interventions": []
}
```

### 5.2 Memory Retriever

借鉴 Generative Agents 的检索思想，采用：

```text
memory_score = recency_score + importance_score + relevance_score
```

第一版规则：

- 最近记忆更高分。
- 迟到、对话、社团、失物、关系变化、用户干预更高分。
- 和当前地点、当前 Agent、当前任务、附近人物相关的记忆更高分。

### 5.3 Goal Manager

目标分三层：

```text
Long-term Goal
  -> Weekly / Daily Goal
    -> Immediate Goal
```

示例：

```text
长期目标：适应大学生活，认识朋友，加入技术社团。
今日目标：上好第一节高数课，中午去食堂，下午看看社团招新。
即时目标：8:10 从宿舍去教学楼，避免迟到。
```

### 5.4 Planner

基础计划由规则生成，个性化调整由 LLM 在每天开始或重大事件后生成。

规则计划示例：

```text
07:30 起床
08:10 前往教学楼
08:30 上课
12:00 去食堂
16:00 社团招新点
22:30 回宿舍
```

个性化调整考虑：

- 性格和兴趣。
- 昨日反思。
- 未完成目标。
- 用户干预。
- 精力、压力和适应度。

### 5.5 Action Schema

第一版只允许结构化行动：

```text
move
attend_class
eat
talk
join_activity
ask_help
handle_lost_item
study
rest
reflect
idle
```

示例：

```json
{
  "type": "move",
  "agent_id": "agent_wang_yinuo",
  "target_location_id": "teaching_building",
  "reason": "08:30 有高等数学课，需要提前出发"
}
```

### 5.6 Game Master

Game Master 负责世界仲裁。

它检查：

- 目标地点是否存在。
- 路径是否连通。
- 时间是否合理。
- Agent 当前动作是否可中断。
- 是否需要移动耗时。
- talk 是否发生在同一地点。
- LLM 输出的 action 是否在允许集合内。

Game Master 是唯一可以应用 state delta 的模块。Agent 和 LLM 只能提出 action，不能直接改数据库。

---

## 6. LLM 调用设计

第一版真实接入 LLM，但严格控制调用点。

### 6.1 调用点

LLM 只用于：

1. Agent 初始人设生成或补全。
2. 每日计划微调。
3. 多 Agent 对话。
4. 用户干预解释。
5. 复杂事件决策。
6. 每日反思。
7. 关键事件文案润色。

不用 LLM 的地方：

- 普通移动。
- 常规上课。
- 常规吃饭。
- 地点开放判断。
- 路径计算。
- 简单 schedule 推进。

### 6.2 输出校验

所有 LLM 输出必须是 JSON，并通过 Pydantic 校验。

流程：

```text
LLM call
  -> JSON parse
  -> Pydantic validation
  -> Game Master legality check
  -> Apply or fallback
```

校验失败时：

1. 重试一次。
2. 仍失败则使用模板 fallback。
3. 写入 llm_calls 和 system event。
4. 不阻塞模拟。

### 6.3 成本控制

默认规模：

- 5 个主 Agent。
- 3 个背景 Agent。
- 主 Agent 参与 LLM。
- 背景 Agent 以规则为主。

估算完整 7 天：

```text
每日计划：5 agents × 7 days = 35 calls
每日反思：5 agents × 7 days = 35 calls
关键对话：约 10-20 calls
复杂事件：约 10 calls
用户干预：约 3-5 calls
合计：约 90-105 calls
```

支持 `llm_mode`：

- `normal`: 正常调用。
- `cheap`: 减少调用，只保留对话、干预、反思。
- `offline`: 不调用 LLM，使用模板。

### 6.4 降级策略

```text
真实 LLM
  -> 重试一次
  -> 模板生成
  -> 规则 action
  -> system event 记录失败
```

例如反思失败时：

```text
王一诺回顾了今天的课程、吃饭和社交经历，决定明天继续适应校园生活。
```

### 6.5 LLM 提供商与安全边界

第一版需要封装 LLM Provider 接口，避免业务代码直接依赖某一家 SDK。默认实现可以优先使用 Claude API，也允许后续替换为 OpenAI 或本地模型。

内部接口保持稳定：

```text
generate_agent_profile
plan_day
generate_dialogue
decide_intervention
decide_complex_event
reflect_day
polish_event
```

LLM 输入不得包含真实学生隐私、真实教务数据或真实具体个人信息。所有种子角色必须是虚构角色，地点和校园事件只能使用公共、泛化、非隐私信息。

LLM 输出必须经过内容边界检查。若输出包含攻击、歧视、骚扰、违法、隐私泄露、真实个人指认或不适合校园展示的内容，系统应丢弃该输出并使用安全模板 fallback。

用户干预也要经过基础过滤：明显攻击、骚扰、违法、歧视或要求 Agent 做不当行为的输入，不写入 Agent 决策上下文，只生成一条被拒绝的 system event。

---

## 7. 前端页面设计

第一版只需要两个页面：

```text
/
  主模拟页

/about
  项目说明页，后置
```

### 7.1 主模拟页布局

采用三栏布局：

```text
┌──────────────────────────────────────────────┐
│ 顶部栏：AI 南大 | Day 1 08:20 | 控制按钮       │
├───────────────┬──────────────────┬───────────┤
│ Agent 列表     │ 校园地图           │ 事件流      │
│ 王一诺         │ 宿舍区 ─ 教学楼     │ 08:05...  │
│ 陈念           │ 食堂 ─ 图书馆       │ 08:12...  │
│ 周岚           │ 社团招新点          │ 08:22...  │
├───────────────┴──────────────────┴───────────┤
│ 底部/抽屉：选中 Agent 详情 + 用户干预输入       │
└──────────────────────────────────────────────┘
```

组件：

```text
SimulationPage
  ├─ SimulationHeader
  ├─ AgentSidebar
  ├─ CampusMap
  ├─ EventFeed
  └─ AgentDetailPanel
```

### 7.2 SimulationHeader

展示：

- 项目名。
- 当前模拟时间。
- 模拟状态。
- 初始化 / 重置。
- 单步 tick。
- 连续运行。
- 暂停。
- 快进 1 小时。
- 快进到当天结束。

连续运行由前端 `setInterval` 调用后端 `/tick`，不做 WebSocket。

### 7.3 CampusMap

使用 SVG 或绝对定位 div 展示：

- 地点节点。
- 地点之间路径。
- Agent 圆点或头像。
- 当前选中 Agent 高亮。
- hover 地点显示名称和在场 Agent。

### 7.4 EventFeed

展示：

- 时间。
- 事件类型 tag。
- 事件摘要。
- 相关 Agent。
- 点击展开详情。

事件类型：

```text
class
meal
social
club
lost_item
reflection
intervention
system
```

### 7.5 AgentDetailPanel

展示：

- 基础档案。
- 当前状态。
- 当前目标。
- 当前行动。
- 心情 / 精力 / 压力 / 适应度。
- 最近事件。
- 重要记忆。
- 关系摘要。
- 用户干预输入框。

---

## 8. 后端 API 设计

### 8.1 Run API

创建模拟：

```http
POST /api/runs
```

获取当前世界状态：

```http
GET /api/runs/{run_id}/state
```

推进一个或多个 tick：

```http
POST /api/runs/{run_id}/tick
```

请求：

```json
{
  "tick_count": 1,
  "llm_mode": "normal"
}
```

快进：

```http
POST /api/runs/{run_id}/fast-forward
```

重置：

```http
POST /api/runs/{run_id}/reset
```

### 8.2 Agent API

获取 Agent 详情：

```http
GET /api/agents/{agent_id}
```

提交用户干预：

```http
POST /api/agents/{agent_id}/interventions
```

请求：

```json
{
  "content": "你可以去社团招新点看看。"
}
```

### 8.3 Event API

获取事件流：

```http
GET /api/runs/{run_id}/events?limit=50&agent_id=optional
```

### 8.4 Debug API

用于解释和调试行为：

```http
GET /api/debug/agents/{agent_id}/perception
GET /api/debug/agents/{agent_id}/memories
GET /api/debug/runs/{run_id}/llm-calls
```

Debug API 可以后端先实现，不一定第一版做漂亮 UI。

---

## 9. Tick 执行流程

`POST /tick` 是核心接口。默认 `tick_minutes = 30`，一周模拟从 `Day 1 07:30` 开始，到 `Day 7 23:30` 后标记为 `completed`。前端连续运行时建议每 1.5-2 秒请求一个 tick；演示时可以用 `cheap` 或 `offline` 模式快进。

第一版不模拟分钟级真实移动细节。路径距离用于判断移动是否能在当前 tick 内完成：若 `distance_minutes <= tick_minutes`，该 tick 内完成移动；若大于一个 tick，则 Agent 进入 `moving` 状态并在后续 tick 抵达。

夜间反思触发口径：当时间进入 `22:30` 或当天最后一个 tick 时，对主 Agent 触发 daily reflection；若使用 `cheap/offline` 模式，则允许用模板或批量摘要替代真实 LLM 反思。

```text
1. 加载 run 和 world state
2. current_minute += tick_minutes
3. 检查当天是否结束
4. 生成全局随机事件候选
5. 按 Agent 顺序构建 perception
6. 检索相关 memories
7. 判断 schedule pressure
8. 选择 action
9. 必要时调用 LLM
10. Game Master 校验 action
11. 应用 state delta
12. 生成 event
13. 写入 memories / relationships
14. 如果到夜间，触发 daily reflection
15. 返回 new_events 和 updated_agents
```

单个 Agent 决策失败时，不应导致整场模拟失败。fallback 为规则行动或 idle。

---

## 10. 测试策略

### 10.1 后端单元测试

覆盖：

- `test_create_run_initializes_world_state`
- `test_tick_advances_simulation_time`
- `test_run_completes_after_seven_days`
- `test_game_master_rejects_invalid_location`
- `test_game_master_rejects_unconnected_move`
- `test_game_master_applies_valid_move`
- `test_game_master_requires_same_location_for_talk`
- `test_memory_retriever_prioritizes_recent_memory`
- `test_memory_retriever_prioritizes_important_memory`
- `test_memory_retriever_includes_pending_intervention`
- `test_agent_moves_to_class_when_schedule_is_near`
- `test_agent_eats_at_meal_time`
- `test_agent_considers_user_intervention`

### 10.2 LLM Service 测试

Contract tests：

- 合法 JSON 通过。
- 缺字段失败。
- 非法 action type 失败。
- fallback 可触发。

真实 LLM 冒烟测试标记为：

```text
@pytest.mark.llm
```

默认不跑，手动运行。

### 10.3 前端测试

优先 Playwright：

- 用户能打开主页面。
- 地图显示地点和 Agent。
- 点击 Agent 显示详情。
- 输入干预调用 API。
- 点击运行周期性 tick。
- 点击暂停停止 tick。

### 10.4 模拟质量测试

人工或半自动验收：

- 完整跑 7 天不崩溃。
- 至少 20 条有意义事件。
- 至少 3 类事件。
- 至少一次多 Agent 对话。
- 每个主 Agent 至少 1 条每日反思。
- 用户干预至少影响一次行动。
- 事件流可读且具备校园语境。

---

## 11. 开发里程碑

### Milestone 0：项目骨架

目标：前后端能启动。

内容：

- `backend/` FastAPI app。
- SQLite 配置。
- pytest setup。
- `frontend/` Next.js app。
- API client。
- basic layout。

验收：

- 后端 `/health` 可访问。
- 前端首页可打开。
- 前端能请求后端 `/health`。

### Milestone 1：静态校园观察器

目标：先做“看起来像 AI 南大”。

内容：

- 种子地点。
- 种子 Agent。
- 假事件流。
- 地图节点展示。
- Agent 列表和详情。

验收：

- 用户能看到校园地图、Agent、事件流和详情面板。

### Milestone 2：规则模拟

目标：不用 LLM，也能跑基础校园生活。

内容：

- simulation_runs。
- tick 推进。
- schedule。
- move / attend_class / eat / idle。
- 基础事件生成。
- SQLite 持久化。

验收：

- 点击 tick 后 Agent 会按时间移动。
- 上课去教学楼。
- 饭点去食堂。
- 事件流持续更新。

### Milestone 3：Game Master + Memory

目标：让行为可解释、状态合法。

内容：

- Game Master 校验 action。
- events 写入。
- short_term memory 写入。
- Memory Retriever。
- relationship 简单更新。
- Agent 详情展示记忆。

验收：

- 非法 action 被拒绝或修正。
- Agent 最近事件进入记忆。
- Agent 详情能看到最近记忆和关系摘要。

### Milestone 4：真实 LLM 接入

目标：引入真实 Agent 智能感。

内容：

- LLM Service。
- Pydantic 输出 schema。
- generate_dialogue。
- reflect_day。
- decide_intervention。
- fallback。
- llm_calls 日志。

验收：

- 至少一次真实多 Agent 对话。
- 每天结束能生成反思。
- 用户干预能被 Agent 接受 / 忽略 / 延后。
- LLM 失败不导致模拟崩溃。

### Milestone 5：校园事件与内容策划

目标：让项目不像通用小镇换皮。

内容：

- 8 个角色设定。
- 6-8 个南大地点。
- 课程表模板。
- 社团招新事件。
- 迷路事件。
- 失物招领事件。
- 下雨、讲座、活动冲突等随机事件。
- 事件文案模板。

验收：

- 一周模拟至少出现 20 条有效事件。
- 至少 3 类事件。
- 用户能感受到校园语境。

### Milestone 6：演示优化与用户测试

目标：完成作品集闭环。

内容：

- README。
- 一键启动说明。
- demo seed。
- 手动测试 checklist。
- 5-10 人用户反馈表。
- 录屏 / 截图。
- 简历表述更新。

验收：

- 5 分钟内讲清项目。
- 至少 3 人能复述一个 Agent 故事。
- 至少 3 人能说出它和普通 AI 聊天的区别。
- 收集 10 条有效反馈。

---

## 12. 风险与应对

### 12.1 LLM 调用成本失控

应对：

- 只有关键节点调用。
- 加 `llm_mode=cheap/offline`。
- 普通事件模板化。
- 主 Agent 调 LLM，背景 Agent 规则化。

### 12.2 Agent 行为像随机游走

应对：

- schedule pressure 优先级高。
- long-term goal / daily goal 明确。
- 每个 action 必须有 reason。
- Game Master 生成可解释事件。

### 12.3 事件流无聊

应对：

- 事件文本具体。
- 增加校园场景模板。
- 引入迷路、社团、失物、误会、求助等高可读事件。
- LLM 只润色关键事件。

### 12.4 架构过大做不完

应对：

- 每个 milestone 都能独立演示。
- 先规则模拟，再 LLM。
- 不做 WebSocket。
- 不做登录。
- 不做复杂地图。
- 不做向量数据库。

### 12.5 调试困难

应对：

- 加 debug API。
- 保存 llm_calls。
- 保存 event state_delta。
- Agent 详情显示行动 reason。
- fallback 写入 system event。

---

## 13. 后续步骤

1. 审查本设计规格，确认是否存在遗漏、过度设计或不一致。
2. 用户复核并确认设计文档。
3. 基于本 spec 创建详细 implementation plan。
4. 按里程碑执行：骨架 -> 静态观察器 -> 规则模拟 -> Game Master + Memory -> LLM -> 校园内容 -> 演示测试。
