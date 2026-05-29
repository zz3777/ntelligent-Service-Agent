# 企业智能服务 Agent — 学习指南

## 项目结构总览

```
├── backend/          # FastAPI 后端（核心）
│   └── .env          # 配置文件（LLM_API_KEY 在此填写）
├── frontend/         # Vue 3 + Element Plus 前端
├── mock-crm/         # 模拟 CRM 系统（测试用）
├── docs/             # 文档
└── docker-compose.yml
```

---

# 后端模块详解（backend/）

## 1. 入口与生命周期 — `backend/app/main.py`

```python
# FastAPI 应用启动时做的事情（lifespan）：
# 1. init_db()          — 自动建表（PostgreSQL）
# 2. MCP 启动           — 注册并启动 4 个 MCP Server 子进程
# 3. 创建 Agent         — new EnterpriseAgent(mcp_manager)
#
# HTTP 路由注册：
#   /api/chat/*
#   /api/knowledge/*
#   /api/task/*
#   /api/approval/*
#   /api/files/*
#   /api/settings/*
#   /api/health
```

**关键概念**：`lifespan` 是 FastAPI 的启动/关闭回调，代替旧版的 `@app.on_event`。

## 2. 配置 — `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # 用 pydantic-settings 从 .env 文件读取配置
    # .env 文件位于 backend/.env
    #
    # 核心字段：
    #   LLM_API_KEY        — 大模型 API Key（在 .env 中填写）
    #   LLM_BASE_URL       — API 地址（如 https://api.openai.com/v1）
    #   LLM_MODEL          — 模型名（如 gpt-4o）
    #
    # MCP Server 启动命令：
    #   MCP_DB_SERVER_CMD    — python -m app.mcp_servers.db_server
    #   MCP_MAIL_SERVER_CMD  — python -m app.mcp_servers.mail_server
    #   MCP_RPA_SERVER_CMD   — python -m app.mcp_servers.rpa_server
    #   MCP_FILE_SERVER_CMD  — python -m app.mcp_servers.file_server
    #
    # 数据库：
    #   DATABASE_URL  — PostgreSQL 连接串
    #   CHROMA_PERSIST_DIR — ChromaDB 向量库本地路径
```

**关键概念**：`BaseSettings` 会自动合并 `.env` 文件和环境变量。

## 3. 数据库 — `backend/app/core/db.py`

```python
# 使用 SQLAlchemy 异步引擎（asyncpg 驱动）
#   engine              — 异步数据库引擎
#   async_session_factory — 会话工厂（每次请求通过 get_db() 获取）
#   Base                — 模型基类（所有表模型继承它）
#   init_db()           — 创建所有表（Base.metadata.create_all）
```

**关键概念**：`get_db()` 是 FastAPI 的 `Depends` 依赖，用于在路由函数中获取数据库会话。

## 4. Agent 引擎 — `backend/app/agent/engine.py`

```python
# EnterpriseAgent 是核心类，负责：
#
# process_message(message) 的执行流程：
# ┌─────────────────────────────────────────────┐
# │ 1. 检查 LLM_API_KEY 是否配置                 │
# │ 2. 获取所有 MCP 工具列表                      │
# │ 3. 检查消息中是否含搜索关键词（如"搜索"）       │
# │    → 是：调用 ChromaDB 检索知识库，注入上下文   │
# │    → 否：跳过，纯 LLM 聊天                    │
# │ 4. 构造 system prompt + 用户消息              │
# │ 5. 调用 LLM（OpenAI 兼容 API）                │
# │ 6. 如果 LLM 返回 tool_calls：                 │
# │    a. 解析工具名和参数                         │
# │    b. 调用对应 MCP Server 的 tool             │
# │    c. 将结果回传给 LLM 生成最终回复            │
# │ 7. 返回最终文本给用户                          │
# └─────────────────────────────────────────────┘
#
# 关键方法：
#   get_tools_description()  — 获取所有工具的人类可读描述
#   _build_openai_tools()    — 将 MCP 工具转为 OpenAI tool 格式
```

**关键概念**：Agent 本身不执行工具，只负责"调度"——LLM 决定用什么工具，Agent 转发给 MCP Server 执行，再把结果喂回 LLM 做最终回答。

## 5. MCP 客户端 — `backend/app/agent/mcp_client.py`

```python
# 两个类：
#
# MCPServerConnection
#   - 管理一个 MCP Server 子进程的生命周期
#   - connect()    ：启动子进程，建立 stdio 通信
#   - list_tools() ：获取该 Server 提供的工具列表
#   - call_tool()  ：调用具体工具
#   - close()      ：关闭子进程
#
# MCPClientManager
#   - 管理所有 Server 的集合
#   - register_server(name, command)  — 注册服务器
#   - start_all()                     — 启动所有服务器
#   - get_all_tools()                 — 汇总所有工具
#   - call_tool(server, tool, args)   — 路由到具体服务器执行
```

**关键概念**：MCP (Model Context Protocol) 是一种让 LLM 调用外部工具的协议。每个 MCP Server 是一个独立 Python 进程，通过 stdin/stdout 与主进程通信。

## 6. MCP Servers — `backend/app/mcp_servers/`

```
db_server.py    — 数据库操作（查表、执行 SQL）
mail_server.py  — 发送邮件
rpa_server.py   — 浏览器 RPA（Playwright）
file_server.py  — 文件读写
```

每个文件都遵循同一个模板：
```python
# 1. 用 FastMCP 创建一个 server 实例
# 2. 用 @mcp.tool() 装饰器定义工具函数
# 3. 每个工具函数处理一个具体操作
# 4. 通过 mcp.run() 启动（被主进程以子进程方式调用）
```

**关键概念**：这些 Server 是独立进程，Agent 通过 `MCPClientManager` 向它们发请求。这样即使某个 Server 崩溃也不会影响主进程。

## 7. RAG 检索 — `backend/app/agent/rag.py`

```python
# 基于 ChromaDB 的向量检索
#
# search_knowledge(query, top_k=5)
#   - 获取 ChromaDB client
#   - 在 "enterprise_knowledge" 集合中搜索
#   - 返回 { content, score } 列表
#
# add_to_knowledgebase(text, document_id, chunk_index)
#   - 将文本切片写入 ChromaDB
#
# 注意：模型文件（all-MiniLM-L6-v2）第一次使用时下载
```

**关键概念**：向量检索将文本转为向量（嵌入），用语义相似度而非关键词匹配来搜索。存储在 `data/chroma/` 目录。

## 8. 提示词 — `backend/app/agent/prompts.py`

```python
# SYSTEM_PROMPT 是发给 LLM 的系统指令，告诉它：
#   - 你是谁（企业智能服务 Agent）
#   - 你能做什么（知识库、OCR、工具调用、RPA）
#   - 行为规范（先说明再执行、敏感操作要确认）
#   - 可用的工具列表（动态注入）
```

## 9. 数据模型 — `backend/app/models/`

```
conversation.py   — conversations 表：聊天记录
knowledge_base.py — documents 表 + document_chunks 表：知识库
task_log.py       — task_logs 表：任务日志
approval.py       — approvals 表：审批流程
user.py           — users 表：用户
```

每个模型都是 SQLAlchemy 的 `Base` 子类，对应一张 PostgreSQL 表。

## 10. API 路由 — `backend/app/api/`

```
chat.py       — POST /api/chat（聊天）
                 GET  /api/chat/conversations（历史列表）
                 WS   /api/chat/ws（WebSocket 聊天）

knowledge.py  — POST /api/knowledge/upload（上传文档）
                 GET  /api/knowledge/list（文档列表）
                 DELETE /api/knowledge/{id}（删除）
                 POST /api/knowledge/{id}/reprocess（重新处理）

settings.py   — GET  /api/settings/llm（查看当前 LLM 配置状态，只读）
                 LLM 配置通过 backend/.env 文件管理

files.py      — 文件管理相关
task.py       — 任务相关
approval.py   — 审批相关
```

## 11. 全局状态 — `backend/app/agent/state.py`

```python
# 存放全局单例，解决模块间循环导入问题
#
# mcp_manager = MCPClientManager()   — 全局唯一的 MCP 管理器
# agent: EnterpriseAgent | None      — 全局唯一的 Agent 实例
#                                     （lifespan 中创建，chat.py 引用）
```

---

# 前端模块详解（frontend/）

## 技术栈
- Vue 3（Composition API + `<script setup>`）
- Element Plus（UI 组件库）
- Vite（构建工具）

## 核心文件

```
src/
├── main.js                    — 入口，挂载 Vue 实例
├── App.vue                    — 根组件，布局框架
├── router/index.js            — 路由配置
├── views/
│   ├── chat/ChatView.vue      — 聊天页面
│   ├── knowledge/             — 知识库管理
│   ├── settings/SettingsView.vue  — LLM 设置
│   ├── task/                  — 任务管理
│   └── approval/              — 审批管理
└── components/                — 通用组件
```

---

# 数据流

## 聊天流程
```
用户在浏览器输入消息
       ↓
  Vue 前端 → fetch POST /api/chat
       ↓
  FastAPI → agent.process_message(message)
       ↓
  LLM（OpenAI 兼容 API）→ 返回文本 or 工具调用
       ↓
  如有工具调用 → MCP Server 子进程执行 → 结果回 LLM
       ↓
  最终回复返回给前端显示
```

## 知识库流程
```
用户上传文档（PDF/DOCX/图片）
       ↓
  POST /api/knowledge/upload
       ↓
  提取文字 → 分片（每 500 字）
       ↓
  存入 PostgreSQL（document_chunks 表）
       ↓
  [目前缺步骤] 写入 ChromaDB 做向量索引
       ↓
  用户搜索 "查找 XX 制度"
       ↓
  agent 检测到关键词 → chroma 检索 → 注入 LLM 上下文
```

---

# 部署

## 启动方式

```bash
# 1. 启动数据库
docker compose up -d postgres redis

# 2. 启动后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 启动前端
cd frontend
npm run dev
```

---

# 关键词索引

| 概念 | 说明 | 所在文件 |
|------|------|----------|
| Lifespan | FastAPI 应用生命周期回调 | `main.py` |
| MCP | 模型上下文协议，工具调用标准 | `mcp_client.py` |
| RAG | 检索增强生成，知识库问答 | `rag.py` |
| Agent | 编排引擎，协调 LLM + 工具 | `engine.py` |
| ChromaDB | 向量数据库 | `rag.py` |
| SQLAlchemy | ORM 框架 | `db.py` + `models/*` |
| tool_calls | LLM 返回的工具调用指令 | `engine.py` |
