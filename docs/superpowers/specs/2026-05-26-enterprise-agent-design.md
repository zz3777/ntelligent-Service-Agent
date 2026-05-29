---
name: enterprise-agent-design
description: 企业内部智能服务 Agent（综合型）设计方案 — RAG 知识库、OCR 图文提取、MCP 工具调用、全栈管理后台
metadata:
  type: design-spec
---

# 企业内部智能服务 Agent — 设计文档

## 1. 项目概述

面向企业内部打造的全能 AI 助理，支持知识库问答、图片/扫描件信息提取、自然语言触发自动化任务（查库、填单、发邮件），并提供管理后台。

### 核心能力

- **RAG 知识库**：支持上传多格式文档（PDF/Word/Excel），切片向量化后实现精准问答
- **OCR 图文提取**：集成 PaddleOCR 本地模型，对扫描件、照片中的文字提取并自动结构化输出
- **工具调用（MCP）**：可扩展的函数调用框架，LLM 根据意图自动选择执行（查数据库、填表单、发通知），RPA 基于 Playwright 实现无头浏览器自动化
- **全栈管理后台**：基于 FastAPI + Vue 3 开发，支持知识库管理、任务审计、失败重试与人工审批待办
- **生产级部署**：Docker Compose 编排后端、前端、数据库、Redis、向量库、模拟 CRM 共 6 个服务
- **可观测性**：每个请求生成唯一任务 ID，日志写入 PostgreSQL，支持按时间、状态、操作人检索

## 2. 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端框架 | FastAPI | Python async web 框架 |
| AI 编排 | LangChain | Agent 构建、RAG 流程编排 |
| 向量数据库 | ChromaDB | 文档向量存储和相似度检索 |
| OCR | PaddleOCR | 本地 OCR 模型，无需云服务 |
| RPA | Playwright | 无头浏览器自动化 |
| 数据库 | PostgreSQL 16 | 业务数据、审计日志 |
| 缓存/消息 | Redis 7 | 缓存、WebSocket 消息分发 |
| MCP | MCP Python SDK | 标准 MCP 协议实现工具调用 |
| 前端 | Vue 3 + Element Plus | 管理后台 UI |
| 状态管理 | Pinia | Vue 状态管理 |
| 容器化 | Docker Compose | 一键部署 |

## 3. 系统架构

```
┌──────────────┐     ┌──────────────────────────────────────────────────┐
│   Vue3 前端   │────▶│              FastAPI 后端 (统一服务)              │
│  (Element+)   │     │                                                  │
│  - Chat 界面  │     │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  │
│  - 知识库管理  │     │  │ Chat API │  │ Agent 编排引擎│  │ 管理 API  │  │
│  - 任务审计    │     │  │ (REST+)  │  │ (LangChain)  │  │ (CRUD)   │  │
│  - 待办审批    │     │  │ WS流式   │  │ - 会话管理   │  │ - 知识库  │  │
│  - 系统设置    │     │  │          │  │ - LLM 调用   │  │ - 审计日志│  │
│              │     │  │          │  │ - RAG 检索   │  │ - 待办审批│  │
└──────────────┘     │  │          │  │ - MCP Client  │  │ - 用户管理│  │
                     │  └──────────┘  └──────┬───────┘  └──────────┘  │
                     └──────────────────────┼──────────────────────────┘
                                            │ MCP 协议 (子进程 stdio)
              ┌──────────────────────────────┼──────────────────────────┐
              │                              │                          │
       ┌──────▼──────┐              ┌───────▼───────┐        ┌─────────▼────────┐
       │  MCP-DB     │              │  MCP-Mail      │        │   MCP-RPA        │
       │  Server     │              │  Server        │        │   Server         │
       │  (子进程)    │              │  (子进程)       │        │   (子进程)        │
       │  查询数据库  │              │  发送/读取邮件  │        │  Playwright 自动化│
       └──────┬──────┘              └───────┬───────┘        └─────────┬────────┘
              │                             │                          │
       ┌──────▼──────┐                     │                   ┌──────▼──────┐
       │  PostgreSQL │                     │                   │  模拟 CRM   │
       │  (业务数据)  │              ┌──────▼───────┐          │  (Flask)    │
       └─────────────┘              │  SMTP (模拟)  │          └─────────────┘
                                    └──────────────┘
```

### MCP 通信方式

FastAPI 通过子进程 stdio 启动各 MCP Server，使用 MCP Python SDK 的标准协议通信。每个 MCP Server 是独立进程，由 FastAPI 的 lifespan 管理生命周期。

## 4. 后端模块设计

### 4.1 目录结构

```
backend/
├── app/
│   ├── main.py                     # FastAPI 入口，lifespan 管理（启动 MCP 子进程）
│   ├── core/
│   │   ├── config.py               # 配置项（已有，需扩展 LLM 配置）
│   │   ├── db.py                   # 数据库引擎/会话管理
│   │   └── redis.py                # Redis 客户端
│   ├── models/                     # SQLAlchemy ORM 模型
│   │   ├── user.py                 # 用户模型
│   │   ├── knowledge_base.py       # 知识库文档
│   │   ├── conversation.py         # 对话/会话
│   │   ├── task_log.py             # 任务审计日志
│   │   └── approval.py             # 人工审批待办
│   ├── schemas/                    # Pydantic 请求/响应模型
│   │   ├── chat.py
│   │   ├── knowledge.py
│   │   ├── task.py
│   │   ├── approval.py
│   │   └── file.py                  # 文件上传/提取文字响应
│   ├── api/                        # 路由层
│   │   ├── chat.py                 # Chat REST API + WebSocket
│   │   ├── knowledge.py            # 知识库管理 CRUD
│   │   ├── task.py                 # 任务审计查询
│   │   └── approval.py             # 审批待办处理
│   ├── agent/                      # Agent 编排引擎
│   │   ├── engine.py               # LangChain Agent 主逻辑
│   │   ├── rag.py                  # RAG 检索封装（ChromaDB）
│   │   ├── mcp_client.py           # MCP Client 管理器（子进程生命周期）
│   │   └── prompts.py              # 系统提示词模板
│   ├── services/                   # 业务逻辑层
│   │   ├── knowledge_service.py    # 文档处理/切片/向量化
│   │   ├── task_service.py         # 任务审计日志服务
│   │   └── approval_service.py     # 审批流程服务
│   └── mcp_servers/                # MCP Server 实现
│       ├── __init__.py
│       ├── base.py                 # MCP Server 基类/通用逻辑
│       ├── db_server.py            # 数据库查询工具
│       ├── mail_server.py          # 邮件工具
│       └── rpa_server.py           # RPA 浏览器自动化（Playwright）
├── tests/
├── Dockerfile
├── requirements.txt
└── .env
```

### 4.2 核心数据模型

#### User（用户）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| username | str | 用户名 |
| password_hash | str | 密码哈希 |
| role | enum | admin / user |
| created_at | datetime | 创建时间 |

#### Document（知识库文档）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| filename | str | 原文件名 |
| file_type | str | pdf / docx / xlsx / image |
| file_size | int | 文件大小（字节） |
| status | enum | uploading / processing / ready / failed |
| storage_type | enum | knowledge（入库）/ temp（临时提取不入库）|
| chunk_count | int | 切片数量 |
| error_message | str | 处理失败时的错误信息 |
| created_at | datetime | 上传时间 |

#### DocumentChunk（文档切片）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| document_id | UUID | 所属文档 |
| content | text | 切片文本内容 |
| chunk_index | int | 切片序号 |
| vector_id | str | ChromaDB 中的向量 ID（仅入库场景） |
| created_at | datetime | 创建时间 |

#### Conversation（对话）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 用户 ID |
| title | str | 对话标题 |
| messages | JSONB | 消息列表 [{role, content, tool_calls}] |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 最后更新时间 |

#### TaskLog（任务审计日志）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | str | 唯一任务 ID（可展示给用户） |
| user_id | UUID | 操作人 |
| conversation_id | UUID | 所属对话 |
| action | str | 操作描述 |
| tool_name | str | 调用的工具名 |
| tool_server | str | 所属 MCP Server |
| input_params | JSONB | 输入参数 |
| output_summary | str | 输出摘要 |
| status | enum | success / failed / pending_approval |
| duration_ms | int | 执行耗时 |
| created_at | datetime | 创建时间 |

#### Approval（审批待办）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | str | 关联任务 ID |
| tool_name | str | 需要审批的工具 |
| params | JSONB | 待执行的参数 |
| reason | str | 触发审批的原因 |
| status | enum | pending / approved / rejected |
| created_by | UUID | 操作人 |
| reviewed_by | UUID | 审批人 |
| created_at | datetime | 创建时间 |
| reviewed_at | datetime | 审批时间 |

### 4.3 Agent 编排引擎

`agent/engine.py` 是核心编排逻辑：

1. 接收用户消息
2. 生成唯一 task_id
3. 从 ChromaDB 检索相关文档片段（RAG）
4. 将检索结果 + 对话历史 + MCP 工具列表传给 LLM
5. LLM 选择：直接回答 / 调用 MCP 工具
6. 如需调用工具：
   - 通过 MCP Client 调用对应 Server
   - 记录 TaskLog
   - 对敏感操作（如发邮件）创建 Approval 记录，暂停执行
   - 将工具结果返回给 LLM 继续推理
7. 最终生成回答，流式返回给前端

### 4.4 MCP 工具清单

#### MCP-DB Server — 数据库查询

| 工具 | 说明 | 安全机制 |
|------|------|---------|
| `query_database(sql)` | 执行只读 SQL 查询 | 只允许 SELECT，独立只读连接 |
| `list_tables()` | 列出所有表和字段 | 仅返回结构信息 |

#### MCP-Mail Server — 邮件

| 工具 | 说明 | 安全机制 |
|------|------|---------|
| `send_email(to, subject, body)` | 发送邮件 | 需要人工审批 |
| `read_inbox(limit)` | 读取收件箱 | 仅读取 |

#### MCP-RPA Server — 浏览器自动化

| 工具 | 说明 |
|------|------|
| `navigate(url)` | 打开网页 |
| `click(selector, text)` | 点击元素 |
| `fill_input(selector, value)` | 填写输入框 |
| `select_option(selector, value)` | 选择下拉框 |
| `extract_text(selector)` | 提取页面文本 |
| `extract_page_info()` | 提取页面结构信息（表单、按钮、链接） |
| `screenshot()` | 截图 base64 输出 |

所有 RPA 操作默认记录完整步骤和截图。

#### MCP-File Server — 文件处理/文字提取

| 工具 | 说明 |
|------|------|
| `extract_text_from_file(file_id)` | 从已上传的图片/PDF/Word/Excel 中提取文字，不入库 |
| `ocr_image(file_id)` | 对图片进行 OCR 识别，返回结构化文字 |

文件处理走统一管道：图片 → PaddleOCR，PDF/Word/Excel → 对应解析库。提取结果直接返回给 LLM 或用户，不写入 ChromaDB。

### 4.5 文件处理 API

文件处理有两种场景：

| API | 方法 | 说明 |
|-----|------|------|
| `POST /api/knowledge/upload` | 上传 | 入库场景：切片 → 向量化 → 存 ChromaDB，供 RAG 检索 |
| `POST /api/files/upload-temp` | 上传 | 临时场景：解析文字后直接返回，不入库，文件自动清理 |
| `GET /api/knowledge/list` | 列表 | 知识库文档列表（分页） |
| `GET /api/knowledge/{id}` | 详情 | 文档详情 + 切片列表 |
| `DELETE /api/knowledge/{id}` | 删除 | 删除文档及对应向量 |
| `POST /api/knowledge/{id}/reprocess` | 重新处理 | 重新切片+向量化 |
| `POST /api/knowledge/test-search` | 测试检索 | 输入文字测试召回效果 |

### 4.6 文件处理流程

```
用户上传文件
    │
    ├── 场景 A：入库（POST /api/knowledge/upload）
    │      │
    │      ▼
    │   创建 Document 记录 (status=uploading, storage_type=knowledge)
    │      │
    │      ▼
    │   后台任务:
    │     1. 提取文本：PaddleOCR(图片) / PyMuPDF(PDF) / python-docx(Word) / openpyxl(Excel)
    │     2. 文本切片（按段落/固定大小）
    │     3. 调用 Embedding 模型生成向量
    │     4. 存入 ChromaDB
    │     5. 更新 Document (status=ready)
    │     6. 写入 DocumentChunk 记录
    │
    └── 场景 B：临时提取（POST /api/files/upload-temp）
           │
           ▼
         提取文本 → 直接返回文字内容
           │
           ▼
         临时文件自动清理（24h 后 / 提取后立即清理）
```

在 Chat 页面中，用户可直接拖拽图片到输入框 → 调用 `extract_text_from_file` 工具 → 结果显示在对话流中，全程不写入知识库。

### 4.7 MCP 调度策略

- **原子操作 + 快捷操作混合**：暴露原子工具（navigate/click/fill_input）给 LLM 灵活组合，同时提供快捷工具（crm_query_customer）减少 token 消耗
- **页面结构缓存**：已知页面结构缓存，第二次访问不重复提取
- **审批门控**：危险操作（发邮件、提交数据）默认需要人工审批

## 5. 前端设计

### 5.1 技术栈

Vue 3 + Element Plus + Pinia + Vue Router + marked + highlight.js

### 5.2 页面结构

```
frontend/src/
├── router/index.js
├── layouts/MainLayout.vue     # 侧边栏 + 顶栏 + 内容区
├── views/
│   ├── chat/ChatView.vue      # 智能对话（核心）
│   ├── knowledge/
│   │   ├── KnowledgeList.vue   # 文档列表
│   │   └── KnowledgeUpload.vue # 文档上传
│   ├── tasks/TaskAudit.vue    # 任务审计
│   ├── approvals/ApprovalList.vue # 审批待办
│   └── settings/SettingsView.vue  # 系统设置
├── stores/                    # Pinia
│   ├── chat.js
│   ├── knowledge.js
│   └── task.js
├── api/                       # API 封装
│   ├── chat.js
│   ├── knowledge.js
│   └── task.js
└── components/
    ├── MessageBubble.vue      # 聊天气泡（Markdown 渲染）
    └── ToolCallCard.vue       # 工具调用卡片
```

### 5.3 页面功能

| 页面 | 功能 |
|------|------|
| 智能对话 | 流式输出，工具调用卡片内嵌显示，对话历史管理，**拖拽图片/文件到输入框提取文字** |
| 知识库 | 文档列表（状态/大小/时间），拖拽上传，删除，**快速提取文字（不入库）**，**测试检索效果**，**查看切片详情** |
| 任务审计 | 表格展示，按时间/状态/操作人筛选，详情展开 |
| 审批待办 | 待办列表，审批/驳回操作 |
| 系统设置 | LLM 模型选择、API Key、MCP Server 配置 |

### 5.4 Chat 页面交互流程

```
用户输入文字 ──→ WebSocket 发送 ──→ Agent 处理
                                       ↓
用户拖入图片/文件 ──→ 上传到临时目录 ──→ Agent 调用 extract_text_from_file
                                       ↓
Agent 状态更新（"正在思考"、"正在检索"、"正在调用工具"）
                                       ↓
工具调用时插入 ToolCallCard（工具名 + 参数 + 结果）
                                       ↓
文字流式输出（Markdown 渲染）
                                       ↓
完整消息展示
```

## 6. 模拟 CRM 设计

### 6.1 定位

独立的 mock 服务，用于演示 Agent 操控外部业务系统的能力。RPA 脚本通过 Playwright 操作此系统的网页界面。

### 6.2 技术选型

Flask + Jinja2 模板 + JSON 文件存储（最轻量实现）

### 6.3 页面和 API

| 页面 | 路径 | RPA 演示场景 |
|------|------|-------------|
| 登录页 | /login | 演示自动登录 |
| 仪表盘 | / | 数据概览 |
| 客户列表 | /customers | 数据查询 |
| 新建客户 | /customers/new | 表单填写 |
| 订单列表 | /orders | 数据查询 |
| 新建订单 | /orders/new | 表单填写 |

### 6.4 预配置账号

RPA Server 预置 mock-crm 的登录凭据：
- 用户名：admin
- 密码：demo123

## 7. Docker Compose 服务编排

| 服务 | 镜像 | 说明 |
|------|------|------|
| postgres | postgres:16-alpine | 业务数据库 |
| redis | redis:7-alpine | 缓存 + 消息队列 |
| chroma | chromadb/chroma | 向量数据库 |
| backend | 自建 | FastAPI + Agent + MCP Server（子进程） |
| frontend | 自建（多阶段构建） | Vue 3 + Nginx |
| mock-crm | 自建 | Flask 演示系统 |

### MCP Server 管理

MCP Server 不作为独立容器运行，而是由 backend 服务在启动时通过 `asyncio.create_subprocess_exec` 启动为子进程，通过 stdio 通信。

## 8. 可观测性

- 每个请求生成唯一 `task_id`（格式：`T20260526-XXXXXX`）
- 所有 Agent 操作记录到 `task_logs` 表
- 前端管理后台支持按时间、状态、操作人检索
- RPA 操作自动截图留存

## 9. 安全设计

- MCP-DB 使用独立的只读数据库连接
- 敏感操作（发邮件、提交数据）需要人工审批
- 审批记录完整保留，支持驳回并附原因
- RPA 操作全程记录可回查
