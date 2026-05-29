# 企业智能服务 Agent

面向企业内部的全能 AI 助理，支持 RAG 知识库问答、OCR 图文提取、MCP 协议工具调用和全栈管理后台。

## 架构概览

```
┌─────────────┐     ┌─────────────────────────────────────┐     ┌──────────────┐
│   Frontend  │     │            FastAPI Backend           │     │  PostgreSQL  │
│  Vue 3 +    │◄───►│  ┌───────────────────────────────┐  │◄───►│   + Redis    │
│  Element    │ WS  │  │   EnterpriseAgent (引擎编排)    │  │     └──────────────┘
│  Plus       │     │  │   ┌─────────┐ ┌────────────┐  │  │     ┌──────────────┐
└─────────────┘     │  │   │ RAG     │ │ MCP Client │  │  │◄───►│   ChromaDB   │
                    │  │   │(LangChain│ │ Manager    │  │  │     │  (向量数据库) │
                    │  │   │ Chroma) │ │            │  │  │     └──────────────┘
                    │  │   └─────────┘ └───────┬─────┘  │
                    │  └───────────────────────┼─────────┘
                    │                          │ stdio
                    │              ┌───────────┼───────────┐
                    │              │           │           │
                    │         ┌────┴────┐ ┌───┴───┐ ┌─────┴─────┐
                    │         │DB Server│ │Mail   │ │File Server │
                    │         │(SELECT) │ │Server │ │(OCR/提取)  │
                    │         └─────────┘ └───┬───┘ └───────────┘
                    │                    ┌────┴────┐
                    │                    │RPA      │
                    │                    │Server   │
                    │                    │(Playwright)
                    │                    └────┬────┘
                    │                         │
                    │                    ┌────┴────┐
                    │                    │Mock CRM │
                    │                    │(Flask)  │
                    │                    └─────────┘
```

## 技术栈

| 层 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python) |
| 数据库 | PostgreSQL 16 (SQLAlchemy async) |
| 缓存 | Redis 7 |
| 向量数据库 | ChromaDB |
| OCR | PaddleOCR (本地, 无需云服务) |
| RPA | Playwright (浏览器自动化) |
| MCP 协议 | MCP Python SDK 1.5+ (stdio 通信) |
| LLM 集成 | OpenAI / DeepSeek / Claude 兼容 |
| 前端 | Vue 3 + Element Plus + Pinia + Vue Router |
| 容器化 | Docker Compose |

## 功能特性

### 智能对话
- 基于 LLM 的自然语言问答
- RAG 知识库增强检索
- WebSocket 实时流式响应
- 拖拽文件上传并自动提取文字

### 知识库管理
- 支持 PDF / Word / Excel / 图片格式
- 自动切片和向量化
- 语义检索测试
- 文档状态跟踪 (上传中 → 处理中 → 就绪/失败)

### MCP 工具调用
| 工具服务器 | 提供能力 |
|------------|----------|
| DB Server | 数据库查询 (SELECT-only 只读) |
| Mail Server | 发送邮件 (需人工审批) |
| RPA Server | 浏览器自动化 (导航/点击/填表/截图等 7 个原子操作) |
| File Server | 文字提取 / OCR 识别 |

### RPA 浏览器自动化
Agent 通过 RPA Server 操作外部系统（如 Mock CRM），流程为：
1. `extract_page_info()` 获取页面交互元素信息
2. LLM 分析页面结构并规划操作步骤
3. 依次执行 `navigate` → `fill_input` → `click` 等原子操作
4. 通过 `screenshot` 确认操作结果

### 审批流程
敏感操作（发邮件等）自动创建审批待办，需管理员批准后执行。

### 任务审计
每一次 Agent 操作记录详细的执行日志，包括耗时、参数、结果等。

### Mock CRM
内置模拟 CRM 系统 (Flask)，用于演示 RPA 自动化操作遗留系统场景。
- 默认账号: `admin` / `demo123`
- 客户和订单 CRUD

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 设置 LLM API Key（必须）
export LLM_API_KEY=your_api_key_here
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4o

# 启动所有服务
docker compose up -d

# 访问
# 前端: http://localhost
# API:  http://localhost:8000/api/health
# Mock CRM: http://localhost:5000
```

### 方式二：本地开发

**前置要求：**
- Python 3.12+
- Node.js 22+
- PostgreSQL 16
- Redis 7
- Conda (推荐)

**后端启动：**

```bash
cd backend

# 创建 conda 环境
conda create -n enterprise-agent python=3.12
conda activate enterprise-agent

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium --with-deps

# 配置环境变量
export DATABASE_URL=postgresql+asyncpg://agent:agent123@localhost:5432/enterprise_agent
export REDIS_URL=redis://localhost:6379/0
export LLM_API_KEY=your_api_key
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4o

# 启动服务
uvicorn app.main:app --reload --port 8000
```

**前端启动：**

```bash
cd frontend
npm install
npm run dev
```

**Mock CRM 启动：**

```bash
cd mock-crm
pip install flask
python app.py
```

## 项目结构

```
├── backend/
│   └── app/
│       ├── agent/              # Agent 编排引擎
│       │   ├── engine.py       # EnterpriseAgent 主逻辑
│       │   ├── mcp_client.py   # MCP Client 管理器
│       │   ├── prompts.py      # 系统提示词模板
│       │   └── rag.py          # ChromaDB RAG 检索
│       ├── api/                # FastAPI 路由
│       │   ├── chat.py         # Chat REST + WebSocket
│       │   ├── knowledge.py    # 知识库 CRUD
│       │   ├── task.py         # 任务审计
│       │   ├── approval.py     # 审批
│       │   └── files.py        # 文件上传
│       ├── core/               # 基础设施
│       │   ├── config.py       # 配置
│       │   ├── db.py           # 数据库引擎
│       │   └── redis.py        # Redis 连接
│       ├── mcp_servers/        # MCP Server 实现
│       │   ├── base.py         # 基类
│       │   ├── db_server.py    # 数据库查询
│       │   ├── mail_server.py  # 邮件
│       │   ├── rpa_server.py   # 浏览器 RPA
│       │   └── file_server.py  # 文件处理/OCR
│       ├── models/             # ORM 模型
│       ├── schemas/            # Pydantic 模型
│       └── services/           # 业务服务
├── frontend/
│   └── src/
│       ├── layouts/            # 主布局
│       ├── views/              # 页面
│       │   ├── chat/           # 智能对话
│       │   ├── knowledge/      # 知识库
│       │   ├── tasks/          # 任务审计
│       │   ├── approvals/      # 审批
│       │   └── settings/       # 系统设置
│       ├── components/         # 通用组件
│       ├── stores/             # Pinia 状态管理
│       └── api/                # API 封装
├── mock-crm/                   # 模拟 CRM
├── docs/                       # 设计文档
├── docker-compose.yml          # 容器编排
└── README.md
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql+asyncpg://agent:agent123@localhost:5432/enterprise_agent` | 数据库连接串 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接串 |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB 持久化路径 |
| `LLM_API_KEY` | `""` | LLM API Key |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | LLM API 地址 |
| `LLM_MODEL` | `gpt-4o` | LLM 模型名称 |
| `SMTP_SERVER` | `localhost` | SMTP 服务器 |
| `SMTP_PORT` | `1025` | SMTP 端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `CORS_ORIGINS` | `["http://localhost", "http://localhost:80"]` | CORS 允许源 |

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送对话消息 |
| GET | `/api/chat/conversations` | 获取对话列表 |
| WS | `/api/chat/ws` | 对话 WebSocket |
| POST | `/api/knowledge/upload` | 上传文档到知识库 |
| GET | `/api/knowledge/list` | 文档列表 |
| POST | `/api/files/upload-temp` | 上传文件并提取文字 (不存储) |
| GET | `/api/tasks` | 任务审计列表 |
| GET | `/api/approvals` | 审批待办列表 |
| POST | `/api/approvals/{id}/approve` | 批准审批 |
| POST | `/api/approvals/{id}/reject` | 驳回审批 |
| GET | `/api/health` | 健康检查 |

## 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 日常问答/知识检索 | GPT-4o / Claude Sonnet | 理解能力强，回答准确 |
| RPA 页面分析 | DeepSeek-V3 | 成本低，结构分析够用 |
| OCR 文字提取 | PaddleOCR (本地) | 无需 API 调用，速度快 |
