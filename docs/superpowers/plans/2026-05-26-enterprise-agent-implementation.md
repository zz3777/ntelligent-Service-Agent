# 企业内部智能服务 Agent — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 FastAPI + Vue 3 + LangChain 构建面向企业内部的全能 AI 助理，支持 RAG 知识库问答、OCR 图文提取、MCP 工具调用和全栈管理后台。

**Architecture:** 统一 FastAPI 后端通过子进程 stdio 管理多个 MCP Server（DB/Mail/RPA/File），子进程间通过 MCP Python SDK 通信。前端 Vue 3 通过 WebSocket 实现流式对话。模拟 CRM 作为独立 Flask 服务供 RPA 演示。

**Tech Stack:** FastAPI, SQLAlchemy (async), LangChain, ChromaDB, MCP Python SDK, PaddleOCR, Playwright, Vue 3, Element Plus, PostgreSQL, Redis, Docker Compose

---

## 文件结构

### 后端（新建文件）

| 文件 | 职责 |
|------|------|
| `backend/app/core/db.py` | 异步数据库引擎、会话工厂 |
| `backend/app/core/redis.py` | Redis 连接池 |
| `backend/app/models/user.py` | User ORM 模型 |
| `backend/app/models/knowledge_base.py` | Document + DocumentChunk ORM 模型 |
| `backend/app/models/conversation.py` | Conversation ORM 模型 |
| `backend/app/models/task_log.py` | TaskLog ORM 模型 |
| `backend/app/models/approval.py` | Approval ORM 模型 |
| `backend/app/models/__init__.py` | 模型注册/导入 |
| `backend/app/schemas/chat.py` | Chat 请求/响应 Pydantic 模型 |
| `backend/app/schemas/knowledge.py` | 知识库相关 Pydantic 模型 |
| `backend/app/schemas/task.py` | 任务审计 Pydantic 模型 |
| `backend/app/schemas/approval.py` | 审批 Pydantic 模型 |
| `backend/app/schemas/file.py` | 文件上传/提取响应 Pydantic 模型 |
| `backend/app/api/chat.py` | Chat REST + WebSocket 路由 |
| `backend/app/api/knowledge.py` | 知识库管理 CRUD 路由 |
| `backend/app/api/task.py` | 任务审计路由 |
| `backend/app/api/approval.py` | 审批待办路由 |
| `backend/app/agent/engine.py` | LangChain Agent 编排主逻辑 |
| `backend/app/agent/rag.py` | ChromaDB RAG 检索封装 |
| `backend/app/agent/mcp_client.py` | MCP Client 管理器（子进程生命周期） |
| `backend/app/agent/prompts.py` | 系统提示词模板 |
| `backend/app/services/knowledge_service.py` | 文档处理/切片/向量化 |
| `backend/app/services/task_service.py` | 任务审计日志服务 |
| `backend/app/services/approval_service.py` | 审批流程服务 |
| `backend/app/mcp_servers/base.py` | MCP Server 基类/通用工具 |
| `backend/app/mcp_servers/db_server.py` | 数据库查询 MCP Server |
| `backend/app/mcp_servers/mail_server.py` | 邮件 MCP Server |
| `backend/app/mcp_servers/rpa_server.py` | RPA 浏览器自动化 MCP Server |
| `backend/app/mcp_servers/file_server.py` | 文件处理/OCR MCP Server |

### 后端（修改文件）

| 文件 | 变更 |
|------|------|
| `backend/app/main.py` | 添加 lifespan MCP 子进程管理，注册路由 |
| `backend/app/core/config.py` | 扩展 LLM 配置、MCP Server 路径等配置项 |
| `backend/requirements.txt` | 添加 MCP SDK、SQLAlchemy、chromadb 等依赖 |
| `backend/Dockerfile` | 无大变更（如果依赖已包含） |

### 前端（新建文件）

| 文件 | 职责 |
|------|------|
| `frontend/src/router/index.js` | 路由定义 |
| `frontend/src/layouts/MainLayout.vue` | 主布局（侧边栏+顶栏+内容区） |
| `frontend/src/views/chat/ChatView.vue` | 智能对话页面 |
| `frontend/src/views/knowledge/KnowledgeList.vue` | 知识库文档列表 |
| `frontend/src/views/knowledge/KnowledgeUpload.vue` | 文档上传 |
| `frontend/src/views/tasks/TaskAudit.vue` | 任务审计页面 |
| `frontend/src/views/approvals/ApprovalList.vue` | 审批待办页面 |
| `frontend/src/views/settings/SettingsView.vue` | 系统设置页面 |
| `frontend/src/stores/chat.js` | Chat 状态管理 |
| `frontend/src/stores/knowledge.js` | 知识库状态管理 |
| `frontend/src/stores/task.js` | 任务/审计状态管理 |
| `frontend/src/api/chat.js` | Chat API 封装 |
| `frontend/src/api/knowledge.js` | 知识库 API 封装 |
| `frontend/src/api/task.js` | 任务 API 封装 |
| `frontend/src/components/MessageBubble.vue` | 聊天气泡组件 |
| `frontend/src/components/ToolCallCard.vue` | 工具调用卡片组件 |

### 模拟 CRM

| 文件 | 职责 |
|------|------|
| `mock-crm/app.py` | Flask 应用，页面+API |
| `mock-crm/templates/login.html` | 登录页 |
| `mock-crm/templates/dashboard.html` | 仪表盘 |
| `mock-crm/templates/customers.html` | 客户列表 |
| `mock-crm/templates/customer_form.html` | 新建/编辑客户 |
| `mock-crm/templates/orders.html` | 订单列表 |
| `mock-crm/templates/order_form.html` | 新建/编辑订单 |
| `mock-crm/data.json` | 模拟数据 |
| `mock-crm/requirements.txt` | Flask 依赖 |
| `mock-crm/Dockerfile` | Docker 镜像 |

---

## 实现任务

### Task 1: 项目基础设施 — 依赖和配置

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/config.py`
- Create: `backend/app/core/db.py`
- Create: `backend/app/core/redis.py`

- [ ] **Step 1: 更新 requirements.txt**

写入完整依赖：

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
langchain==0.3.17
langchain-community==0.3.16
langchain-openai==0.3.7
chromadb==0.5.23
paddleocr==2.9.1
playwright==1.50.0
asyncpg==0.30.0
redis==5.2.1
pydantic==2.10.4
pydantic-settings==2.7.1
sqlalchemy[asyncio]==2.0.36
alembic==1.14.1
httpx==0.28.1
loguru==0.7.3
python-dotenv==1.0.1
mcp==1.5.0
pypdf2==3.0.1
python-docx==1.1.2
openpyxl==3.1.5
websockets==14.1
```

- [ ] **Step 2: 扩展配置类**

写入 `backend/app/core/config.py`：

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "企业智能服务 Agent"
    VERSION: str = "0.1.0"
    CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:80"]

    DATABASE_URL: str = "postgresql+asyncpg://agent:agent123@localhost:5432/enterprise_agent"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o"

    MCP_DB_SERVER_CMD: str = "python -m app.mcp_servers.db_server"
    MCP_MAIL_SERVER_CMD: str = "python -m app.mcp_servers.mail_server"
    MCP_RPA_SERVER_CMD: str = "python -m app.mcp_servers.rpa_server"
    MCP_FILE_SERVER_CMD: str = "python -m app.mcp_servers.file_server"

    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 3: 创建 db.py**

写入 `backend/app/core/db.py`：

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

- [ ] **Step 4: 创建 redis.py**

写入 `backend/app/core/redis.py`：

```python
from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None = None


async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
```

- [ ] **Step 5: 验证导入**

Run: `cd backend && python -c "from app.core.config import settings; from app.core.db import Base; from app.core.redis import get_redis; print('OK')"` — 忽略数据库连接错误，只要 ImportError 不出现就算通过

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/app/core/config.py backend/app/core/db.py backend/app/core/redis.py
git commit -m "feat: add project infrastructure - config, db, redis"
```

---

### Task 2: ORM 数据模型

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/knowledge_base.py`
- Create: `backend/app/models/conversation.py`
- Create: `backend/app/models/task_log.py`
- Create: `backend/app/models/approval.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 User 模型**

写入 `backend/app/models/user.py`：

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(Enum("admin", "user", name="user_role"), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: 创建知识库模型（Document + DocumentChunk）**

写入 `backend/app/models/knowledge_base.py`：

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)  # pdf/docx/xlsx/image
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(16), default="uploading", nullable=False
    )  # uploading/processing/ready/failed
    storage_type: Mapped[str] = mapped_column(
        String(16), default="knowledge", nullable=False
    )  # knowledge/temp
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["Document"] = relationship(back_populates="chunks")
```

- [ ] **Step 3: 创建 Conversation 模型**

写入 `backend/app/models/conversation.py`：

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), default="新对话")
    messages: Mapped[str] = mapped_column(Text, default="[]")  # JSON 字符串
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 4: 创建 TaskLog 模型**

写入 `backend/app/models/task_log.py`：

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class TaskLog(Base):
    __tablename__ = "task_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    tool_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tool_server: Mapped[str | None] = mapped_column(String(32), nullable=True)
    input_params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="success")  # success/failed/pending_approval
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 5: 创建 Approval 模型**

写入 `backend/app/models/approval.py`：

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[str] = mapped_column(String(32), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False)
    params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/approved/rejected
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    reviewed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

- [ ] **Step 6: 更新 models/__init__.py**

写入 `backend/app/models/__init__.py`：

```python
from app.models.user import User
from app.models.knowledge_base import Document, DocumentChunk
from app.models.conversation import Conversation
from app.models.task_log import TaskLog
from app.models.approval import Approval

__all__ = ["User", "Document", "DocumentChunk", "Conversation", "TaskLog", "Approval"]
```

- [ ] **Step 7: 验证模型导入**

Run: `cd backend && python -c "from app.models import User, Document, DocumentChunk, Conversation, TaskLog, Approval; print('Models OK')"`
Expected: `Models OK`

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add ORM models for user, knowledge, conversation, task_log, approval"
```

---

### Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/chat.py`
- Create: `backend/app/schemas/knowledge.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/schemas/approval.py`
- Create: `backend/app/schemas/file.py`

- [ ] **Step 1: 创建 chat schemas**

写入 `backend/app/schemas/chat.py`：

```python
from pydantic import BaseModel
from uuid import UUID


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str
    file_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    task_id: str
    reply: str


class ConversationListItem(BaseModel):
    id: UUID
    title: str
    updated_at: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 knowledge schemas**

写入 `backend/app/schemas/knowledge.py`：

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    storage_type: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentChunkOut(BaseModel):
    id: UUID
    content: str
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailOut(DocumentOut):
    chunks: list[DocumentChunkOut]


class TestSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class TestSearchResult(BaseModel):
    content: str
    score: float
    document_name: str
```

- [ ] **Step 3: 创建 task schemas**

写入 `backend/app/schemas/task.py`：

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TaskLogOut(BaseModel):
    id: UUID
    task_id: str
    action: str
    tool_name: str | None
    tool_server: str | None
    status: str
    duration_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskLogDetailOut(TaskLogOut):
    input_params: str | None
    output_summary: str | None
    user_id: UUID | None


class TaskLogListResponse(BaseModel):
    items: list[TaskLogOut]
    total: int
```

- [ ] **Step 4: 创建 approval schemas**

写入 `backend/app/schemas/approval.py`：

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ApprovalOut(BaseModel):
    id: UUID
    task_id: str
    tool_name: str
    params: str | None
    reason: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalActionRequest(BaseModel):
    comment: str | None = None


class ApprovalListResponse(BaseModel):
    items: list[ApprovalOut]
    total: int
```

- [ ] **Step 5: 创建 file schemas**

写入 `backend/app/schemas/file.py`：

```python
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    text: str | None = None
    storage_type: str  # "knowledge" or "temp"
```

- [ ] **Step 6: 验证 schemas 导入**

Run: `cd backend && python -c "from app.schemas.chat import ChatRequest; from app.schemas.knowledge import DocumentOut; from app.schemas.task import TaskLogOut; from app.schemas.approval import ApprovalOut; from app.schemas.file import FileUploadResponse; print('Schemas OK')"`
Expected: `Schemas OK`

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas for all API endpoints"
```

---

### Task 4: FastAPI 路由 — Chat API + WebSocket

**Files:**
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 chat 路由**

写入 `backend/app/api/chat.py`：

```python
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationListItem
from app.models.conversation import Conversation

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    conv_id = request.conversation_id or uuid.uuid4()
    task_id = f"T{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    if not request.conversation_id:
        conv = Conversation(id=conv_id, title=request.message[:64], messages="[]")
        db.add(conv)
        await db.commit()

    return ChatResponse(conversation_id=conv_id, task_id=task_id, reply="开发中")


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc()).limit(50)
    )
    convs = result.scalars().all()
    return [ConversationListItem.model_validate(c) for c in convs]


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            await websocket.send_json({"type": "status", "content": "处理中..."})
            await websocket.send_json({"type": "message", "content": f"收到: {msg.get('message', '')}"})
    except WebSocketDisconnect:
        pass
```

- [ ] **Step 2: 更新 main.py 注册路由**

写入 `backend/app/main.py`（覆盖现有文件）：

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.api import chat

# Agent 和 MCP Client 将在后续任务中集成
mcp_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # MCP Client 初始化将在 Task 8 中添加
    yield
    if mcp_manager:
        await mcp_manager.shutdown_all()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}
```

- [ ] **Step 3: 验证 FastAPI 启动**

Run: `cd backend && timeout 3 python -c "from app.main import app; print('FastAPI app loaded')" 2>&1 || true`
Expected: `FastAPI app loaded`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/chat.py backend/app/main.py
git commit -m "feat: add chat API with REST and WebSocket endpoints"
```

---

### Task 5: FastAPI 路由 — 知识库管理、任务审计、审批

**Files:**
- Create: `backend/app/api/knowledge.py`
- Create: `backend/app/api/task.py`
- Create: `backend/app/api/approval.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建知识库路由**

写入 `backend/app/api/knowledge.py`：

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.db import get_db
from app.schemas.knowledge import DocumentOut, DocumentDetailOut, DocumentChunkOut, TestSearchRequest, TestSearchResult
from app.models.knowledge_base import Document, DocumentChunk
from app.services.knowledge_service import process_document, extract_text_from_file

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
    type_map = {"pdf": "pdf", "docx": "docx", "doc": "docx", "xlsx": "xlsx", "xls": "xlsx",
                "png": "image", "jpg": "image", "jpeg": "image", "bmp": "image"}
    file_type = type_map.get(ext, "unknown")

    doc = Document(
        filename=file.filename,
        file_type=file_type,
        file_size=0,
        status="processing",
        storage_type="knowledge",
    )
    db.add(doc)
    await db.commit()

    content = await file.read()
    doc.file_size = len(content)

    try:
        text = await extract_text_from_file(content, file_type)
        chunk_count = await process_document(doc.id, text, db)
        doc.status = "ready"
        doc.chunk_count = chunk_count
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)

    await db.commit()
    await db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/list", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).where(Document.storage_type == "knowledge").order_by(Document.created_at.desc())
    )
    return [DocumentOut.model_validate(d) for d in result.scalars().all()]


@router.get("/{doc_id}", response_model=DocumentDetailOut)
async def get_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentDetailOut.model_validate(doc)


@router.delete("/{doc_id}")
async def delete_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id))
    await db.delete(doc)
    await db.commit()
    return {"message": "已删除"}


@router.post("/{doc_id}/reprocess", response_model=DocumentOut)
async def reprocess_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    doc.status = "processing"
    await db.commit()
    try:
        text = "重新处理占位"  # 实际应重新读取文件
        chunk_count = await process_document(doc.id, text, db)
        doc.status = "ready"
        doc.chunk_count = chunk_count
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
    await db.commit()
    await db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.post("/test-search", response_model=list[TestSearchResult])
async def test_search(request: TestSearchRequest):
    return [TestSearchResult(content="开发中", score=0.0, document_name="")]
```

- [ ] **Step 2: 创建任务审计路由**

写入 `backend/app/api/task.py`：

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.schemas.task import TaskLogOut, TaskLogDetailOut, TaskLogListResponse
from app.models.task_log import TaskLog

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskLogListResponse)
async def list_tasks(
    status: str | None = Query(None),
    tool_name: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(TaskLog).order_by(TaskLog.created_at.desc())
    count_query = select(func.count(TaskLog.id))

    if status:
        query = query.where(TaskLog.status == status)
        count_query = count_query.where(TaskLog.status == status)
    if tool_name:
        query = query.where(TaskLog.tool_name == tool_name)
        count_query = count_query.where(TaskLog.tool_name == tool_name)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return TaskLogListResponse(
        items=[TaskLogOut.model_validate(t) for t in result.scalars().all()],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskLogDetailOut)
async def get_task_detail(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskLog).where(TaskLog.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskLogDetailOut.model_validate(task)
```

- [ ] **Step 3: 创建审批路由**

写入 `backend/app/api/approval.py`：

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.schemas.approval import ApprovalOut, ApprovalActionRequest, ApprovalListResponse
from app.models.approval import Approval

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(Approval).order_by(Approval.created_at.desc())
    count_query = select(func.count(Approval.id))

    if status:
        query = query.where(Approval.status == status)
        count_query = count_query.where(Approval.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return ApprovalListResponse(
        items=[ApprovalOut.model_validate(a) for a in result.scalars().all()],
        total=total,
    )


@router.post("/{approval_id}/approve")
async def approve(approval_id: str, request: ApprovalActionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    approval.status = "approved"
    approval.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "已批准"}


@router.post("/{approval_id}/reject")
async def reject(approval_id: str, request: ApprovalActionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    approval.status = "rejected"
    approval.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "已驳回"}
```

- [ ] **Step 4: 在 main.py 中注册新路由**

编辑 `backend/app/main.py`，在 `app.include_router(chat.router)` 后添加：

```python
from app.api import knowledge, task, approval

app.include_router(knowledge.router)
app.include_router(task.router)
app.include_router(approval.router)
```

- [ ] **Step 5: 验证路由注册**

Run: `cd backend && timeout 3 python -c "
from app.main import app
routes = [r.path for r in app.routes if hasattr(r, 'path')]
print('\n'.join(routes))
" 2>&1 || true`
Expected: 包含 `/api/health`, `/api/chat`, `/api/knowledge/list`, `/api/tasks`, `/api/approvals` 等路径

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/knowledge.py backend/app/api/task.py backend/app/api/approval.py backend/app/main.py
git commit -m "feat: add knowledge, task, approval API routes"
```

---

### Task 6: 文件处理和知识库服务

**Files:**
- Create: `backend/app/services/knowledge_service.py`

- [ ] **Step 1: 创建 knowledge_service.py**

写入 `backend/app/services/knowledge_service.py`：

```python
import uuid
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge_base import Document, DocumentChunk


async def extract_text_from_file(content: bytes, file_type: str) -> str:
    """从文件内容中提取文字"""
    if file_type == "pdf":
        return _extract_pdf_text(content)
    elif file_type == "docx":
        return _extract_docx_text(content)
    elif file_type == "xlsx":
        return _extract_xlsx_text(content)
    elif file_type == "image":
        return _extract_image_text(content)
    return ""


def _extract_pdf_text(content: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"[PDF 提取失败: {e}]"


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[DOCX 提取失败: {e}]"


def _extract_xlsx_text(content: bytes) -> str:
    try:
        from openpyxl import load_workbook
        wb = load_workbook(BytesIO(content), read_only=True)
        texts = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                texts.append(" | ".join(str(c) for c in row if c is not None))
        return "\n".join(texts)
    except Exception as e:
        return f"[XLSX 提取失败: {e}]"


def _extract_image_text(content: bytes) -> str:
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        result = ocr.ocr(tmp_path)
        texts = []
        for line_group in result or []:
            for line in line_group or []:
                texts.append(line[1][0])
        import os
        os.unlink(tmp_path)
        return "\n".join(texts)
    except Exception as e:
        return f"[OCR 提取失败: {e}]"


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """将文本切分为固定大小的块"""
    if not text.strip():
        return []
    import re
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < chunk_size:
            current += para + "\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n"
    if current:
        chunks.append(current.strip())
    return chunks or [text.strip()]


async def process_document(doc_id: uuid.UUID, text: str, db: AsyncSession) -> int:
    """处理文档：切片并存入数据库（省略 ChromaDB 向量化，后续集成）"""
    chunks = _chunk_text(text)
    for i, chunk_content in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=doc_id,
            content=chunk_content,
            chunk_index=i,
        )
        db.add(chunk)
    await db.commit()
    return len(chunks)
```

- [ ] **Step 2: 验证服务导入**

Run: `cd backend && python -c "from app.services.knowledge_service import extract_text_from_file, process_document, _chunk_text; print('OK')"`

- [ ] **Step 3: 创建 services/__init__.py 更新**

写入 `backend/app/services/__init__.py`：

```python
from app.services.knowledge_service import extract_text_from_file, process_document

__all__ = ["extract_text_from_file", "process_document"]
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/
git commit -m "feat: add file processing and knowledge service"
```

---

### Task 7: MCP Base + DB Server

**Files:**
- Create: `backend/app/mcp_servers/base.py`
- Create: `backend/app/mcp_servers/__init__.py`
- Create: `backend/app/mcp_servers/db_server.py`

- [ ] **Step 1: 创建 MCP Server 基类**

写入 `backend/app/mcp_servers/base.py`：

```python
"""MCP Server 基类，提供通用启动逻辑"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server


class MCPServer:
    def __init__(self, name: str):
        self.server = Server(name)
        self._register_tools()

    def _register_tools(self):
        raise NotImplementedError

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
```

- [ ] **Step 2: 创建 __init__.py**

写入 `backend/app/mcp_servers/__init__.py`：

```python
from app.mcp_servers.base import MCPServer

__all__ = ["MCPServer"]
```

- [ ] **Step 3: 创建 DB Server**

写入 `backend/app/mcp_servers/db_server.py`：

```python
"""MCP-DB Server: 提供数据库查询工具"""

import asyncio
import asyncpg
from mcp.types import Tool, TextContent

from app.mcp_servers.base import MCPServer
from app.core.config import settings


class DBServer(MCPServer):
    def __init__(self):
        super().__init__("db-server")

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="query_database",
                    description="对业务数据库执行只读 SQL 查询，仅支持 SELECT 语句",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "SQL 查询语句，仅支持 SELECT"
                            }
                        },
                        "required": ["sql"]
                    }
                ),
                Tool(
                    name="list_tables",
                    description="列出数据库中所有可查询的表名和字段信息",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "query_database":
                sql = arguments["sql"].strip()
                if not sql.upper().startswith("SELECT"):
                    return [TextContent(type="text", text="错误：只允许执行 SELECT 查询")]
                conn = await asyncpg.connect(settings.DATABASE_URL.replace("+asyncpg", ""))
                try:
                    rows = await conn.fetch(sql)
                    result = "\n".join(str(dict(r)) for r in rows) if rows else "查询结果为空"
                    return [TextContent(type="text", text=result)]
                finally:
                    await conn.close()
            elif name == "list_tables":
                conn = await asyncpg.connect(settings.DATABASE_URL.replace("+asyncpg", ""))
                try:
                    rows = await conn.fetch("""
                        SELECT table_name, column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        ORDER BY table_name, ordinal_position
                    """)
                    result = "\n".join(f"{r['table_name']}.{r['column_name']} ({r['data_type']})" for r in rows)
                    return [TextContent(type="text", text=result or "无表")]
                finally:
                    await conn.close()
            return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    server = DBServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: 验证 DB Server 导入**

Run: `cd backend && python -c "from app.mcp_servers.db_server import DBServer; print('DB Server OK')"`
Expected: `DB Server OK`

- [ ] **Step 5: Commit**

```bash
git add backend/app/mcp_servers/
git commit -m "feat: add MCP base class and DB Server"
```

---

### Task 8: MCP Mail Server + File Server

**Files:**
- Create: `backend/app/mcp_servers/mail_server.py`
- Create: `backend/app/mcp_servers/file_server.py`

- [ ] **Step 1: 创建 Mail Server**

写入 `backend/app/mcp_servers/mail_server.py`：

```python
"""MCP-Mail Server: 提供邮件发送/读取工具"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from mcp.types import Tool, TextContent

from app.mcp_servers.base import MCPServer
from app.core.config import settings


class MailServer(MCPServer):
    def __init__(self):
        super().__init__("mail-server")

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="send_email",
                    description="发送电子邮件。此操作需要人工审批。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "收件人邮箱地址"},
                            "subject": {"type": "string", "description": "邮件主题"},
                            "body": {"type": "string", "description": "邮件正文"},
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="read_inbox",
                    description="读取收件箱最新邮件",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "读取数量", "default": 10}
                        }
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "send_email":
                msg = MIMEText(arguments["body"], "plain", "utf-8")
                msg["Subject"] = arguments["subject"]
                msg["To"] = arguments["to"]
                msg["From"] = "agent@enterprise.com"

                try:
                    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as s:
                        s.send_message(msg)
                    return [TextContent(type="text", text=f"邮件已发送至 {arguments['to']}")]
                except Exception as e:
                    return [TextContent(type="text", text=f"发送失败: {e}")]

            elif name == "read_inbox":
                return [TextContent(type="text", text="收件箱读取功能需要配置 IMAP 服务器（开发中）")]

            return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    server = MailServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 创建 File Server**

写入 `backend/app/mcp_servers/file_server.py`：

```python
"""MCP-File Server: 提供文件处理和 OCR 文字提取工具"""

import asyncio
from mcp.types import Tool, TextContent

from app.mcp_servers.base import MCPServer
from app.services.knowledge_service import extract_text_from_file


class FileServer(MCPServer):
    def __init__(self):
        super().__init__("file-server")

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="extract_text_from_file",
                    description="从已上传的图片/PDF/Word/Excel 文件中提取文字，不保存到知识库",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "通过 POST /api/files/upload-temp 上传后返回的文件标识"
                            }
                        },
                        "required": ["file_id"]
                    }
                ),
                Tool(
                    name="ocr_image",
                    description="对图片进行 OCR 识别，返回结构化文字",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "上传后的文件标识"}
                        },
                        "required": ["file_id"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            file_id = arguments.get("file_id", "")
            # 从临时存储读取文件内容（简化实现：需要配合 API 路由）
            from app.services.temp_file_store import read_temp_file
            file_data = await read_temp_file(file_id)
            if file_data is None:
                return [TextContent(type="text", text=f"文件 {file_id} 不存在或已过期")]

            content, file_type = file_data
            text = await extract_text_from_file(content, file_type)
            return [TextContent(type="text", text=text)]


async def main():
    server = FileServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: 创建临时文件存储服务**

写入 `backend/app/services/temp_file_store.py`：

```python
"""临时文件存储（内存中），用于文件提取场景"""

import uuid
import time
from typing import Tuple

_temp_store: dict[str, Tuple[bytes, str, float]] = {}  # file_id -> (content, file_type, expires_at)
TTL_SECONDS = 86400  # 24 小时


async def save_temp_file(content: bytes, file_type: str) -> str:
    file_id = uuid.uuid4().hex[:16]
    _temp_store[file_id] = (content, file_type, time.time() + TTL_SECONDS)
    return file_id


async def read_temp_file(file_id: str) -> Tuple[bytes, str] | None:
    entry = _temp_store.get(file_id)
    if entry is None:
        return None
    content, file_type, expires_at = entry
    if time.time() > expires_at:
        del _temp_store[file_id]
        return None
    return content, file_type


def cleanup_expired():
    now = time.time()
    expired = [k for k, v in _temp_store.items() if now > v[2]]
    for k in expired:
        del _temp_store[k]
```

- [ ] **Step 4: 创建临时文件上传 API**

写入 `backend/app/api/files.py`：

```python
from fastapi import APIRouter, UploadFile, File
from app.schemas.file import FileUploadResponse
from app.services.temp_file_store import save_temp_file
from app.services.knowledge_service import extract_text_from_file

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload-temp", response_model=FileUploadResponse)
async def upload_temp_file(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
    type_map = {"pdf": "pdf", "docx": "docx", "doc": "docx", "xlsx": "xlsx", "xls": "xlsx",
                "png": "image", "jpg": "image", "jpeg": "image", "bmp": "image"}
    file_type = type_map.get(ext, "unknown")

    content = await file.read()
    file_id = await save_temp_file(content, file_type)

    text = await extract_text_from_file(content, file_type)

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        text=text,
        storage_type="temp",
    )
```

- [ ] **Step 5: 注册 files 路由**

编辑 `backend/app/main.py`，在 `app.include_router(knowledge.router)` 前添加：

```python
from app.api import files
app.include_router(files.router)
```

- [ ] **Step 6: 验证**

Run: `cd backend && python -c "from app.mcp_servers.mail_server import MailServer; from app.mcp_servers.file_server import FileServer; print('MCP Servers OK')"`
Expected: `MCP Servers OK`

- [ ] **Step 7: Commit**

```bash
git add backend/app/mcp_servers/mail_server.py backend/app/mcp_servers/file_server.py backend/app/services/temp_file_store.py backend/app/api/files.py backend/app/main.py
git commit -m "feat: add MCP Mail, File servers and temp file API"
```

---

### Task 9: MCP RPA Server（Playwright 浏览器自动化）

**Files:**
- Create: `backend/app/mcp_servers/rpa_server.py`

- [ ] **Step 1: 创建 RPA Server**

写入 `backend/app/mcp_servers/rpa_server.py`：

```python
"""MCP-RPA Server: 基于 Playwright 的浏览器自动化工具"""

import asyncio
import base64
from mcp.types import Tool, TextContent
from playwright.async_api import async_playwright, Browser, Page

from app.mcp_servers.base import MCPServer


class RPABrowser:
    def __init__(self):
        self.browser: Browser | None = None
        self.page: Page | None = None
        self._page_cache: dict[str, str] = {}

    async def start(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(15000)

    async def close(self):
        if self.browser:
            await self.browser.close()

    async def navigate(self, url: str) -> str:
        await self.page.goto(url, wait_until="networkidle")
        if url in self._page_cache:
            return f"已导航到 {url}"
        self._page_cache[url] = url
        return f"已导航到 {url}"

    async def click(self, selector: str | None = None, text: str | None = None) -> str:
        if text:
            await self.page.click(f"text={text}")
        elif selector:
            await self.page.click(selector)
        else:
            return "错误：请提供 selector 或 text"
        return "已点击"

    async def fill_input(self, selector: str, value: str) -> str:
        await self.page.fill(selector, value)
        return f"已填写 {selector}"

    async def select_option(self, selector: str, value: str) -> str:
        await self.page.select_option(selector, value)
        return f"已选择 {selector}"

    async def extract_text(self, selector: str | None = None) -> str:
        if selector:
            return await self.page.inner_text(selector)
        return await self.page.inner_text("body")

    async def extract_page_info(self) -> str:
        info = await self.page.evaluate("""
            () => {
                const elements = [];
                document.querySelectorAll('input, button, a, select, textarea, [role=button]').forEach(el => {
                    elements.push({
                        tag: el.tagName,
                        type: el.type || null,
                        placeholder: el.placeholder || null,
                        text: el.innerText?.trim() || el.value || null,
                        id: el.id || null,
                        label: el.labels ? Array.from(el.labels).map(l => l.innerText).join('') : null
                    });
                });
                return elements;
            }
        """)
        lines = [f"{el['tag']}: {el['text'] or el['placeholder'] or el['id'] or ''}" for el in info]
        return "\n".join(lines[:100])

    async def screenshot(self) -> str:
        data = await self.page.screenshot(type="png")
        return base64.b64encode(data).decode()


class RPAServer(MCPServer):
    def __init__(self):
        super().__init__("rpa-server")
        self.browser = RPABrowser()

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(name="navigate", description="导航到指定 URL",
                     inputSchema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}),
                Tool(name="click", description="点击页面上的元素",
                     inputSchema={"type": "object", "properties": {
                         "selector": {"type": "string", "description": "CSS 选择器"},
                         "text": {"type": "string", "description": "元素文本内容"}
                     }}),
                Tool(name="fill_input", description="在输入框中填写内容",
                     inputSchema={"type": "object", "properties": {
                         "selector": {"type": "string"},
                         "value": {"type": "string"}
                     }, "required": ["selector", "value"]}),
                Tool(name="select_option", description="选择下拉框选项",
                     inputSchema={"type": "object", "properties": {
                         "selector": {"type": "string"},
                         "value": {"type": "string"}
                     }, "required": ["selector", "value"]}),
                Tool(name="extract_text", description="提取页面上的文本内容",
                     inputSchema={"type": "object", "properties": {
                         "selector": {"type": "string", "description": "CSS 选择器，默认提取全部"}
                     }}),
                Tool(name="extract_page_info", description="提取当前页面的交互元素信息（表单、按钮、链接等）",
                     inputSchema={"type": "object", "properties": {}}),
                Tool(name="screenshot", description="截取当前页面截图（返回 base64 编码的 PNG）",
                     inputSchema={"type": "object", "properties": {}}),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                handlers = {
                    "navigate": lambda: self.browser.navigate(arguments["url"]),
                    "click": lambda: self.browser.click(arguments.get("selector"), arguments.get("text")),
                    "fill_input": lambda: self.browser.fill_input(arguments["selector"], arguments["value"]),
                    "select_option": lambda: self.browser.select_option(arguments["selector"], arguments["value"]),
                    "extract_text": lambda: self.browser.extract_text(arguments.get("selector")),
                    "extract_page_info": lambda: self.browser.extract_page_info(),
                    "screenshot": lambda: self.browser.screenshot(),
                }
                handler = handlers.get(name)
                if not handler:
                    return [TextContent(type="text", text=f"未知工具: {name}")]
                result = await handler()
                return [TextContent(type="text", text=str(result)[:5000])]
            except Exception as e:
                return [TextContent(type="text", text=f"RPA 执行失败: {e}")]


async def main():
    server = RPAServer()
    await server.browser.start()
    try:
        await server.run()
    finally:
        await server.browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 验证 RPA Server 导入**

Run: `cd backend && python -c "from app.mcp_servers.rpa_server import RPAServer; print('RPA Server OK')"`
Expected: `RPA Server OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/mcp_servers/rpa_server.py
git commit -m "feat: add MCP RPA Server with Playwright browser automation"
```

---

### Task 10: MCP Client 管理器 + Agent 编排引擎

**Files:**
- Create: `backend/app/agent/mcp_client.py`
- Create: `backend/app/agent/prompts.py`
- Create: `backend/app/agent/engine.py`
- Create: `backend/app/agent/rag.py`
- Create: `backend/app/agent/__init__.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 MCP Client 管理器**

写入 `backend/app/agent/mcp_client.py`：

```python
"""MCP Client 管理器：管理 MCP Server 子进程生命周期和通信"""

import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPServerConnection:
    def __init__(self, name: str, command: str):
        self.name = name
        self.server_params = StdioServerParameters(command="python", args=command.split()[1:])
        self.session = None
        self.exit_stack = None

    async def connect(self):
        self.exit_stack = asyncio.ExitStack()
        transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        read, write = transport
        from mcp.client.session import ClientSession
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def list_tools(self):
        if not self.session:
            return []
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: dict):
        if not self.session:
            raise RuntimeError("MCP Server 未连接")
        result = await self.session.call_tool(name, arguments)
        return result.content

    async def close(self):
        if self.exit_stack:
            await self.exit_stack.aclose()


class MCPClientManager:
    def __init__(self):
        self.servers: dict[str, MCPServerConnection] = {}

    def register_server(self, name: str, command: str):
        self.servers[name] = MCPServerConnection(name, command)

    async def start_all(self):
        for name, server in self.servers.items():
            try:
                await server.connect()
                print(f"[MCP] {name} 已连接")
            except Exception as e:
                print(f"[MCP] {name} 连接失败: {e}")

    async def get_all_tools(self) -> list[dict]:
        all_tools = []
        for name, server in self.servers.items():
            try:
                tools = await server.list_tools()
                for tool in tools:
                    all_tools.append({
                        "server": name,
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    })
            except Exception:
                pass
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        server = self.servers.get(server_name)
        if not server:
            raise ValueError(f"未知 MCP Server: {server_name}")
        return await server.call_tool(tool_name, arguments)

    async def shutdown_all(self):
        for name, server in self.servers.items():
            try:
                await server.close()
                print(f"[MCP] {name} 已关闭")
            except Exception:
                pass
```

- [ ] **Step 2: 创建 prompts.py**

写入 `backend/app/agent/prompts.py`：

```python
"""系统提示词模板"""

SYSTEM_PROMPT = """你是企业智能服务 Agent，一个为企业内部打造的全能 AI 助理。

## 你的能力

1. **知识库问答**：基于企业内部文档（制度文件、手册等）回答员工问题
2. **OCR 图文提取**：从图片、扫描件中提取文字信息
3. **工具调用**：根据用户意图自动选择合适的工具执行任务
4. **RPA 自动化**：通过浏览器自动化操作企业内外部系统

## 行为准则

- 使用工具前先向用户说明你要做什么
- 工具执行结果返回后，用自然语言向用户解释结果
- 对于敏感操作（发邮件、提交数据等），先确认用户意图
- 如果不确定用户的意图，主动追问
- 仅使用提供的工具，不要虚构不存在的功能

## 工具使用

你可以使用以下 MCP 工具来帮助用户：
{tools_description}

请根据用户的请求，选择合适的工具来完成操作。
"""
```

- [ ] **Step 3: 创建 RAG 检索模块**

写入 `backend/app/agent/rag.py`：

```python
"""RAG 检索封装（ChromaDB）"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


async def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """在知识库中搜索与 query 相关的内容"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="enterprise_knowledge")
        results = collection.query(query_texts=[query], n_results=top_k)
        documents = []
        for i, doc in enumerate(results["documents"][0]):
            documents.append({
                "content": doc,
                "score": results["distances"][0][i] if results["distances"] else 0,
            })
        return documents
    except Exception as e:
        return [{"content": f"检索失败: {e}", "score": 0}]


async def add_to_knowledgebase(text: str, document_id: str, chunk_index: int):
    """将文本切片添加到知识库"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="enterprise_knowledge")
        collection.add(
            documents=[text],
            ids=[f"{document_id}_{chunk_index}"],
            metadatas=[{"document_id": document_id, "chunk_index": chunk_index}],
        )
        return f"{document_id}_{chunk_index}"
    except Exception as e:
        raise RuntimeError(f"向量化失败: {e}")
```

- [ ] **Step 4: 创建 Agent 引擎**

写入 `backend/app/agent/engine.py`：

```python
"""Agent 编排引擎"""

import json
import uuid
from datetime import datetime

from app.agent.mcp_client import MCPClientManager
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.rag import search_knowledge


class EnterpriseAgent:
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp_manager = mcp_manager

    async def get_tools_description(self) -> str:
        tools = await self.mcp_manager.get_all_tools()
        lines = []
        for t in tools:
            params = json.dumps(t.get("input_schema", {}).get("properties", {}), ensure_ascii=False)
            lines.append(f"- {t['name']}（来自 {t['server']}）：{t['description']}")
            lines.append(f"  参数: {params}")
        return "\n".join(lines)

    async def process_message(self, message: str, conversation_history: list | None = None) -> str:
        tools_desc = await self.get_tools_description()
        prompt = SYSTEM_PROMPT.format(tools_description=tools_desc)

        rag_results = await search_knowledge(message)
        context = "\n".join(r["content"] for r in rag_results if r["score"] < 1.5)

        full_prompt = f"{prompt}\n\n相关知识库内容:\n{context}\n\n用户: {message}"
        return f"[Agent 处理结果]: {full_prompt[:200]}...\n\n（完整 Agent 将在 LLM 集成后生效）"
```

- [ ] **Step 5: 创建 agent/__init__.py**

写入 `backend/app/agent/__init__.py`：

```python
from app.agent.engine import EnterpriseAgent
from app.agent.mcp_client import MCPClientManager
from app.agent.rag import search_knowledge, add_to_knowledgebase

__all__ = ["EnterpriseAgent", "MCPClientManager", "search_knowledge", "add_to_knowledgebase"]
```

- [ ] **Step 6: 集成 MCP Client 到 main.py**

编辑 `backend/app/main.py`，在 `lifespan` 中添加 MCP Client 启动逻辑，并在全局暴露 agent：

```python
from app.agent.mcp_client import MCPClientManager
from app.agent.engine import EnterpriseAgent
from app.core.config import settings

mcp_manager = MCPClientManager()
agent: EnterpriseAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # 注册 MCP Server
    mcp_manager.register_server("db", settings.MCP_DB_SERVER_CMD)
    mcp_manager.register_server("mail", settings.MCP_MAIL_SERVER_CMD)
    mcp_manager.register_server("rpa", settings.MCP_RPA_SERVER_CMD)
    mcp_manager.register_server("file", settings.MCP_FILE_SERVER_CMD)
    await mcp_manager.start_all()

    global agent
    agent = EnterpriseAgent(mcp_manager)

    yield

    await mcp_manager.shutdown_all()
```

- [ ] **Step 7: 验证 Agent 模块导入**

Run: `cd backend && python -c "from app.agent import EnterpriseAgent, MCPClientManager; print('Agent OK')"`
Expected: `Agent OK`

- [ ] **Step 8: Commit**

```bash
git add backend/app/agent/
git commit -m "feat: add MCP Client manager, RAG module, and Agent engine"
```

---

### Task 11: Vue 3 前端 — 项目骨架和布局

**Files:**
- Modify: `frontend/src/main.js`（创建）
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/layouts/MainLayout.vue`

- [ ] **Step 1: 创建 main.js**

写入 `frontend/src/main.js`：

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.use(createPinia())
app.mount('#app')
```

- [ ] **Step 2: 创建 App.vue**

写入 `frontend/src/App.vue`：

```vue
<template>
  <router-view />
</template>

<script setup>
</script>
```

- [ ] **Step 3: 创建 router/index.js**

写入 `frontend/src/router/index.js`：

```javascript
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/chat' },
      { path: 'chat', name: 'Chat', component: () => import('../views/chat/ChatView.vue') },
      { path: 'knowledge', name: 'Knowledge', component: () => import('../views/knowledge/KnowledgeList.vue') },
      { path: 'knowledge/upload', name: 'KnowledgeUpload', component: () => import('../views/knowledge/KnowledgeUpload.vue') },
      { path: 'tasks', name: 'Tasks', component: () => import('../views/tasks/TaskAudit.vue') },
      { path: 'approvals', name: 'Approvals', component: () => import('../views/approvals/ApprovalList.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/settings/SettingsView.vue') },
    ],
  },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
```

- [ ] **Step 4: 创建 MainLayout.vue**

写入 `frontend/src/layouts/MainLayout.vue`：

```vue
<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" style="background-color: #304156">
      <div class="logo">企业智能 Agent</div>
      <el-menu
        :default-active="route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能对话</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Document /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务审计</span>
        </el-menu-item>
        <el-menu-item index="/approvals">
          <el-icon><CircleCheck /></el-icon>
          <span>审批待办</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: flex-end">
        <span>管理员</span>
      </el-header>
      <el-main style="background: #f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ChatDotRound, Document, List, CircleCheck, Setting } from '@element-plus/icons-vue'
const route = useRoute()
</script>

<style scoped>
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}
</style>
```

- [ ] **Step 5: 验证前端构建**

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Expected: build 成功，无错误

- [ ] **Step 6: Commit**

```bash
git add frontend/src/main.js frontend/src/App.vue frontend/src/router/index.js frontend/src/layouts/MainLayout.vue
git commit -m "feat: add Vue 3 frontend skeleton with layout and routing"
```

---

### Task 12: Vue 3 前端 — 核心页面（Chat + 知识库）

**Files:**
- Create: `frontend/src/views/chat/ChatView.vue`
- Create: `frontend/src/api/chat.js`
- Create: `frontend/src/stores/chat.js`
- Create: `frontend/src/components/MessageBubble.vue`
- Create: `frontend/src/components/ToolCallCard.vue`
- Create: `frontend/src/views/knowledge/KnowledgeList.vue`
- Create: `frontend/src/views/knowledge/KnowledgeUpload.vue`
- Create: `frontend/src/api/knowledge.js`
- Create: `frontend/src/stores/knowledge.js`

- [ ] **Step 1: 创建 Chat API 封装**

写入 `frontend/src/api/chat.js`：

```javascript
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function sendMessage(conversationId, message) {
  const res = await api.post('/chat', { conversation_id: conversationId, message })
  return res.data
}

export async function listConversations() {
  const res = await api.get('/chat/conversations')
  return res.data
}

export function createWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/api/chat/ws`
  return new WebSocket(wsUrl)
}
```

- [ ] **Step 2: 创建 Chat Store**

写入 `frontend/src/stores/chat.js`：

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentMessages = ref([])
  const isProcessing = ref(false)

  function addMessage(msg) {
    currentMessages.value.push(msg)
  }

  function setMessages(msgs) {
    currentMessages.value = msgs
  }

  function setProcessing(val) {
    isProcessing.value = val
  }

  return { conversations, currentMessages, isProcessing, addMessage, setMessages, setProcessing }
})
```

- [ ] **Step 3: 创建 MessageBubble 组件**

写入 `frontend/src/components/MessageBubble.vue`：

```vue
<template>
  <div :class="['message-bubble', role]">
    <div class="avatar">
      <el-avatar :icon="role === 'user' ? 'UserFilled' : 'ChatDotRound'" :style="role === 'user' ? {} : { background: '#409EFF' }" />
    </div>
    <div class="content" v-html="renderedContent" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  role: { type: String, default: 'user' },
  content: { type: String, default: '' },
})

const renderedContent = computed(() => marked(props.content))
</script>

<style scoped>
.message-bubble { display: flex; margin-bottom: 16px; gap: 12px; }
.message-bubble.user { flex-direction: row-reverse; }
.content {
  max-width: 70%; padding: 12px 16px; border-radius: 8px; line-height: 1.6;
  background: v-bind('props.role === "user" ? "#409EFF" : "#fff"');
  color: v-bind('props.role === "user" ? "#fff" : "#333"');
  border: v-bind('props.role === "user" ? "none" : "1px solid #e6e6e6"');
}
.content :deep(pre) { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; }
.content :deep(code) { font-size: 14px; }
</style>
```

- [ ] **Step 4: 创建 ToolCallCard 组件**

写入 `frontend/src/components/ToolCallCard.vue`：

```vue
<template>
  <div class="tool-call-card">
    <div class="header">
      <el-tag type="warning" size="small">工具调用</el-tag>
      <span class="tool-name">{{ toolName }}</span>
      <el-tag :type="status === 'success' ? 'success' : 'danger'" size="small">{{ status }}</el-tag>
    </div>
    <div class="body" v-if="params">
      <div class="label">参数:</div>
      <pre>{{ params }}</pre>
    </div>
    <div class="body" v-if="result">
      <div class="label">结果:</div>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
defineProps({
  toolName: String,
  params: String,
  result: String,
  status: { type: String, default: 'success' },
})
</script>

<style scoped>
.tool-call-card {
  background: #fafafa; border: 1px solid #e6e6e6; border-radius: 8px;
  padding: 12px; margin: 8px 0; font-size: 13px;
}
.header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.tool-name { font-weight: bold; color: #e6a23c; }
.body { margin-top: 4px; }
.label { color: #999; font-size: 12px; }
pre { background: #f5f5f5; padding: 8px; border-radius: 4px; font-size: 12px; white-space: pre-wrap; }
</style>
```

- [ ] **Step 5: 创建 ChatView.vue**

写入 `frontend/src/views/chat/ChatView.vue`：

```vue
<template>
  <div class="chat-container">
    <div class="message-list" ref="messageListRef">
      <MessageBubble v-for="(msg, i) in chatStore.currentMessages" :key="i" :role="msg.role" :content="msg.content" />
      <ToolCallCard v-for="(tc, i) in toolCalls" :key="'tc-'+i" v-bind="tc" />
    </div>
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息，或拖拽文件到这里..."
        @keydown.enter.exact.prevent="send"
        @dragover.prevent
        @drop.prevent="handleDrop"
      />
      <el-button type="primary" @click="send" :loading="chatStore.isProcessing" style="margin-top: 8px">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '../../stores/chat'
import MessageBubble from '../../components/MessageBubble.vue'
import ToolCallCard from '../../components/ToolCallCard.vue'
import { createWebSocket } from '../../api/chat'

const chatStore = useChatStore()
const inputMessage = ref('')
const messageListRef = ref(null)
const toolCalls = ref([])

function send() {
  if (!inputMessage.value.trim()) return
  chatStore.addMessage({ role: 'user', content: inputMessage.value })
  const msg = inputMessage.value
  inputMessage.value = ''
  chatStore.setProcessing(true)

  const ws = createWebSocket()
  ws.onopen = () => ws.send(JSON.stringify({ message: msg }))
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'message') {
      chatStore.addMessage({ role: 'assistant', content: data.content })
      chatStore.setProcessing(false)
      ws.close()
    }
  }
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) {
    const formData = new FormData()
    formData.append('file', file)
    fetch('/api/files/upload-temp', { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        chatStore.addMessage({ role: 'user', content: `[文件] ${data.filename}` })
        chatStore.addMessage({ role: 'assistant', content: `提取的文字:\n${data.text}` })
      })
  }
}
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 120px); }
.message-list { flex: 1; overflow-y: auto; padding: 16px; }
.input-area { padding: 16px; background: #fff; border-top: 1px solid #e6e6e6; }
</style>
```

- [ ] **Step 6: 创建 Knowledge API 封装**

写入 `frontend/src/api/knowledge.js`：

```javascript
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/knowledge/upload', formData)
  return res.data
}

export async function listDocuments() {
  const res = await api.get('/knowledge/list')
  return res.data
}

export async function deleteDocument(id) {
  const res = await api.delete(`/knowledge/${id}`)
  return res.data
}

export async function testSearch(query) {
  const res = await api.post('/knowledge/test-search', { query })
  return res.data
}
```

- [ ] **Step 7: 创建 Knowledge Store**

写入 `frontend/src/stores/knowledge.js`：

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listDocuments, deleteDocument } from '../api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const documents = ref([])
  const loading = ref(false)

  async function fetchDocuments() {
    loading.value = true
    documents.value = await listDocuments()
    loading.value = false
  }

  async function removeDocument(id) {
    await deleteDocument(id)
    documents.value = documents.value.filter(d => d.id !== id)
  }

  return { documents, loading, fetchDocuments, removeDocument }
})
```

- [ ] **Step 8: 创建 KnowledgeList.vue**

写入 `frontend/src/views/knowledge/KnowledgeList.vue`：

```vue
<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; gap: 12px">
      <el-button type="primary" @click="$router.push('/knowledge/upload')">上传文档</el-button>
      <el-button @click="showQuickExtract = true">快速提取文字</el-button>
      <el-button @click="showTestSearch = true">测试检索</el-button>
    </div>

    <el-table :data="store.documents" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="filename" label="文件名" />
      <el-table-column prop="file_type" label="类型" width="80" />
      <el-table-column prop="file_size" label="大小" width="100">
        <template #default="{ row }">{{ (row.file_size / 1024).toFixed(1) }} KB</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 'ready' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="切片数" width="80" />
      <el-table-column prop="created_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button text type="primary" @click="viewChunks(row)">切片</el-button>
          <el-button text type="danger" @click="store.removeDocument(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 快速提取文字对话框 -->
    <el-dialog v-model="showQuickExtract" title="快速提取文字" width="600px">
      <el-upload drag :auto-upload="false" :on-change="handleQuickExtract">
        <el-icon><UploadFilled /></el-icon>
        <div>拖拽文件到此处，或点击上传</div>
      </el-upload>
      <pre v-if="extractedText" style="margin-top: 12px; background: #f5f5f5; padding: 12px; max-height: 300px; overflow-y: auto">{{ extractedText }}</pre>
    </el-dialog>

    <!-- 测试检索对话框 -->
    <el-dialog v-model="showTestSearch" title="测试检索" width="500px">
      <el-input v-model="searchQuery" placeholder="输入测试文字" />
      <el-button @click="doTestSearch" style="margin-top: 8px">检索</el-button>
      <div v-for="r in searchResults" :key="r.content" style="margin-top: 8px; padding: 8px; background: #f5f5f5; border-radius: 4px">
        <div>{{ r.content }}</div>
        <el-tag size="small">得分: {{ r.score.toFixed(3) }}</el-tag>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useKnowledgeStore } from '../../stores/knowledge'
import { uploadDocument, testSearch } from '../../api/knowledge'
import { UploadFilled } from '@element-plus/icons-vue'

const store = useKnowledgeStore()
const showQuickExtract = ref(false)
const extractedText = ref('')
const showTestSearch = ref(false)
const searchQuery = ref('')
const searchResults = ref([])

onMounted(() => store.fetchDocuments())

function viewChunks(row) { /* 后续实现 */ }

async function handleQuickExtract(file) {
  const formData = new FormData()
  formData.append('file', file.raw)
  const res = await fetch('/api/files/upload-temp', { method: 'POST', body: formData })
  const data = await res.json()
  extractedText.value = data.text
}

async function doTestSearch() {
  searchResults.value = await testSearch(searchQuery.value)
}
</script>
```

- [ ] **Step 9: 创建 KnowledgeUpload.vue**

写入 `frontend/src/views/knowledge/KnowledgeUpload.vue`：

```vue
<template>
  <div>
    <el-upload
      drag
      :auto-upload="false"
      :on-change="handleUpload"
      multiple
      accept=".pdf,.docx,.doc,.xlsx,.xls,.png,.jpg,.jpeg,.bmp"
    >
      <el-icon><UploadFilled /></el-icon>
      <div>拖拽文件到此处，或点击上传</div>
      <template #tip>
        <div>支持 PDF、Word、Excel、图片格式</div>
      </template>
    </el-upload>

    <div v-for="item in uploadList" :key="item.filename" style="margin-top: 12px; padding: 12px; background: #f5f5f5; border-radius: 4px">
      <div>{{ item.filename }} <el-tag :type="item.status === 'ready' ? 'success' : 'warning'" size="small">{{ item.status }}</el-tag></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadDocument } from '../../api/knowledge'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const uploadList = ref([])

async function handleUpload(file) {
  uploadList.value.push({ filename: file.name, status: 'uploading' })
  try {
    const doc = await uploadDocument(file.raw)
    uploadList.value = uploadList.value.map(item =>
      item.filename === file.name ? { ...item, status: doc.status } : item
    )
  } catch {
    uploadList.value = uploadList.value.map(item =>
      item.filename === file.name ? { ...item, status: 'failed' } : item
    )
  }
}
</script>
```

- [ ] **Step 10: 验证前端构建**

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Expected: build 成功

- [ ] **Step 11: Commit**

```bash
git add frontend/src/views/chat/ frontend/src/api/chat.js frontend/src/stores/chat.js frontend/src/components/ frontend/src/views/knowledge/ frontend/src/api/knowledge.js frontend/src/stores/knowledge.js
git commit -m "feat: add Chat and Knowledge pages with WebSocket and drag-drop file support"
```

---

### Task 13: Vue 3 前端 — 任务审计、审批、设置页面

**Files:**
- Create: `frontend/src/views/tasks/TaskAudit.vue`
- Create: `frontend/src/views/approvals/ApprovalList.vue`
- Create: `frontend/src/views/settings/SettingsView.vue`
- Create: `frontend/src/api/task.js`
- Create: `frontend/src/stores/task.js`

- [ ] **Step 1: 创建 Task API**

写入 `frontend/src/api/task.js`：

```javascript
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function listTasks(params = {}) {
  const res = await api.get('/tasks', { params })
  return res.data
}

export async function getTaskDetail(taskId) {
  const res = await api.get(`/tasks/${taskId}`)
  return res.data
}

export async function listApprovals(params = {}) {
  const res = await api.get('/approvals', { params })
  return res.data
}

export async function approveApproval(id, comment) {
  const res = await api.post(`/approvals/${id}/approve`, { comment })
  return res.data
}

export async function rejectApproval(id, comment) {
  const res = await api.post(`/approvals/${id}/reject`, { comment })
  return res.data
}
```

- [ ] **Step 2: 创建 Task Store**

写入 `frontend/src/stores/task.js`：

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listTasks, listApprovals } from '../api/task'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const total = ref(0)
  const loading = ref(false)
  const approvals = ref([])
  const approvalTotal = ref(0)

  async function fetchTasks(params) {
    loading.value = true
    const data = await listTasks(params)
    tasks.value = data.items
    total.value = data.total
    loading.value = false
  }

  async function fetchApprovals(params) {
    const data = await listApprovals(params)
    approvals.value = data.items
    approvalTotal.value = data.total
  }

  return { tasks, total, loading, approvals, approvalTotal, fetchTasks, fetchApprovals }
})
```

- [ ] **Step 3: 创建 TaskAudit.vue**

写入 `frontend/src/views/tasks/TaskAudit.vue`：

```vue
<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="状态">
        <el-select v-model="filter.status" clearable placeholder="全部" @change="search">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="待审批" value="pending_approval" />
        </el-select>
      </el-form-item>
      <el-form-item label="工具">
        <el-input v-model="filter.tool_name" placeholder="工具名称" @keyup.enter="search" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="store.tasks" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="task_id" label="任务 ID" width="160" />
      <el-table-column prop="action" label="操作" width="200" />
      <el-table-column prop="tool_name" label="工具" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration_ms" label="耗时(ms)" width="100" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="store.total"
      :page-size="20"
      layout="prev, pager, next"
      @change="search"
      style="margin-top: 16px"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useTaskStore } from '../../stores/task'

const store = useTaskStore()
const page = ref(1)
const filter = reactive({ status: '', tool_name: '' })

onMounted(() => search())

function search() {
  store.fetchTasks({ ...filter, page: page.value })
}
</script>
```

- [ ] **Step 4: 创建 ApprovalList.vue**

写入 `frontend/src/views/approvals/ApprovalList.vue`：

```vue
<template>
  <div>
    <el-table :data="store.approvals" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="task_id" label="任务 ID" width="160" />
      <el-table-column prop="tool_name" label="工具" width="120" />
      <el-table-column prop="reason" label="原因" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'approved' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" v-if="hasPending">
        <template #default="{ row }">
          <el-button type="success" size="small" @click="handleAction(row.id, 'approve')">批准</el-button>
          <el-button type="danger" size="small" @click="handleAction(row.id, 'reject')">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useTaskStore } from '../../stores/task'
import { approveApproval, rejectApproval } from '../../api/task'

const store = useTaskStore()
const hasPending = computed(() => store.approvals.some(a => a.status === 'pending'))

onMounted(() => store.fetchApprovals({}))

async function handleAction(id, action) {
  if (action === 'approve') await approveApproval(id, '')
  else await rejectApproval(id, '')
  store.fetchApprovals({})
}
</script>
```

- [ ] **Step 5: 创建 SettingsView.vue**

写入 `frontend/src/views/settings/SettingsView.vue`：

```vue
<template>
  <div style="max-width: 600px">
    <el-card>
      <template #header>LLM 配置</template>
      <el-form label-width="120px">
        <el-form-item label="API Base URL">
          <el-input v-model="settings.baseUrl" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="settings.apiKey" type="password" show-password />
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="settings.model">
            <el-option label="GPT-4o" value="gpt-4o" />
            <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
            <el-option label="DeepSeek-V3" value="deepseek-chat" />
            <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="save">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const settings = reactive({
  baseUrl: localStorage.getItem('llm_base_url') || '',
  apiKey: localStorage.getItem('llm_api_key') || '',
  model: localStorage.getItem('llm_model') || 'gpt-4o',
})

function save() {
  localStorage.setItem('llm_base_url', settings.baseUrl)
  localStorage.setItem('llm_api_key', settings.apiKey)
  localStorage.setItem('llm_model', settings.model)
  ElMessage.success('保存成功')
}
</script>
```

- [ ] **Step 6: 验证前端构建**

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Expected: build 成功

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/tasks/ frontend/src/views/approvals/ frontend/src/views/settings/ frontend/src/api/task.js frontend/src/stores/task.js
git commit -m "feat: add TaskAudit, ApprovalList, Settings pages"
```

---

### Task 14: 模拟 CRM（Mock CRM）

**Files:**
- Create: `mock-crm/app.py`
- Create: `mock-crm/templates/login.html`
- Create: `mock-crm/templates/dashboard.html`
- Create: `mock-crm/templates/customers.html`
- Create: `mock-crm/templates/customer_form.html`
- Create: `mock-crm/templates/orders.html`
- Create: `mock-crm/templates/order_form.html`
- Create: `mock-crm/data.json`
- Create: `mock-crm/requirements.txt`
- Create: `mock-crm/Dockerfile`

- [ ] **Step 1: 创建 Flask 应用**

写入 `mock-crm/app.py`：

```python
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "mock-crm-demo-key"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"customers": [], "orders": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "demo123":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="用户名或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("dashboard.html", customer_count=len(data["customers"]), order_count=len(data["orders"]))


@app.route("/customers")
def customers():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("customers.html", customers=data["customers"])


@app.route("/customers/new", methods=["GET", "POST"])
def customer_new():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        data = load_data()
        customer = {
            "id": len(data["customers"]) + 1,
            "name": request.form["name"],
            "phone": request.form.get("phone", ""),
            "email": request.form.get("email", ""),
            "company": request.form.get("company", ""),
        }
        data["customers"].append(customer)
        save_data(data)
        return redirect(url_for("customers"))
    return render_template("customer_form.html")


@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("orders.html", orders=data["orders"])


@app.route("/orders/new", methods=["GET", "POST"])
def order_new():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    if request.method == "POST":
        order = {
            "id": len(data["orders"]) + 1,
            "customer_name": request.form["customer_name"],
            "product": request.form.get("product", ""),
            "amount": request.form.get("amount", "0"),
            "status": "新建",
        }
        data["orders"].append(order)
        save_data(data)
        return redirect(url_for("orders"))
    return render_template("order_form.html", customers=data["customers"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

- [ ] **Step 2: 创建登录页模板**

写入 `mock-crm/templates/login.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>CRM 登录</title>
<style>
body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.login-box { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,.1); width: 320px; }
h2 { text-align: center; margin-bottom: 24px; }
label { display: block; margin-bottom: 6px; color: #333; }
input { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 16px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background: #409EFF; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; text-align: center; margin-bottom: 12px; }
</style></head>
<body>
<div class="login-box">
  <h2>CRM 登录</h2>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="post">
    <label>用户名</label><input name="username" id="username" placeholder="请输入用户名" />
    <label>密码</label><input name="password" id="password" type="password" placeholder="请输入密码" />
    <button type="submit" id="login-btn">登 录</button>
  </form>
</div>
</body>
</html>
```

- [ ] **Step 3: 创建仪表盘模板**

写入 `mock-crm/templates/dashboard.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>CRM 仪表盘</title>
<style>
body { font-family: Arial; margin: 0; background: #f0f2f5; }
.header { background: #304156; color: #fff; padding: 16px 24px; display: flex; justify-content: space-between; }
.header a { color: #fff; text-decoration: none; font-size: 14px; }
.container { max-width: 800px; margin: 24px auto; }
.card { background: #fff; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.card h3 { margin-top: 0; }
.stat { font-size: 32px; font-weight: bold; color: #409EFF; }
nav a { display: inline-block; margin-right: 16px; color: #409EFF; text-decoration: none; }
</style></head>
<body>
<div class="header"><span>CRM 管理系统</span><a href="/logout">退出</a></div>
<div class="container">
  <nav><a href="/">仪表盘</a><a href="/customers">客户管理</a><a href="/orders">订单管理</a></nav>
  <div class="card"><h3>客户数</h3><div class="stat">{{ customer_count }}</div></div>
  <div class="card"><h3>订单数</h3><div class="stat">{{ order_count }}</div></div>
</div>
</body>
</html>
```

- [ ] **Step 4: 创建客户列表模板**

写入 `mock-crm/templates/customers.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>客户管理</title>
<style>/* same as dashboard */</style></head>
<body>
<div class="header"><span>CRM 管理系统</span><a href="/logout">退出</a></div>
<div class="container">
  <nav><a href="/">仪表盘</a><a href="/customers">客户管理</a><a href="/orders">订单管理</a></nav>
  <div style="margin-bottom:16px"><a href="/customers/new" style="background:#409EFF;color:#fff;padding:8px 16px;text-decoration:none;border-radius:4px">新建客户</a></div>
  <table style="width:100%;background:#fff;border-collapse:collapse">
    <tr><th>ID</th><th>姓名</th><th>电话</th><th>邮箱</th><th>公司</th></tr>
    {% for c in customers %}
    <tr><td>{{ c.id }}</td><td>{{ c.name }}</td><td>{{ c.phone }}</td><td>{{ c.email }}</td><td>{{ c.company }}</td></tr>
    {% endfor %}
  </table>
</div>
</body>
</html>
```

- [ ] **Step 5: 创建客户表单模板**

写入 `mock-crm/templates/customer_form.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>新建客户</title></head>
<body>
<div class="header"><span>CRM 管理系统</span><a href="/logout">退出</a></div>
<div class="container">
  <h2>新建客户</h2>
  <form method="post" style="background:#fff;padding:24px;border-radius:8px;max-width:500px">
    <label>客户名称</label><input name="name" id="name" required /><br/>
    <label>电话</label><input name="phone" id="phone" /><br/>
    <label>邮箱</label><input name="email" id="email" /><br/>
    <label>公司</label><input name="company" id="company" /><br/>
    <button type="submit" id="submit-btn" style="margin-top:12px">提交</button>
  </form>
</div>
</body>
</html>
```

- [ ] **Step 6: 创建订单列表和表单模板**

写入 `mock-crm/templates/orders.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>订单管理</title></head>
<body>
<div class="header"><span>CRM 管理系统</span><a href="/logout">退出</a></div>
<div class="container">
  <nav><a href="/">仪表盘</a><a href="/customers">客户管理</a><a href="/orders">订单管理</a></nav>
  <div style="margin-bottom:16px"><a href="/orders/new" style="background:#409EFF;color:#fff;padding:8px 16px;text-decoration:none;border-radius:4px">新建订单</a></div>
  <table style="width:100%;background:#fff;border-collapse:collapse">
    <tr><th>ID</th><th>客户</th><th>产品</th><th>金额</th><th>状态</th></tr>
    {% for o in orders %}
    <tr><td>{{ o.id }}</td><td>{{ o.customer_name }}</td><td>{{ o.product }}</td><td>{{ o.amount }}</td><td>{{ o.status }}</td></tr>
    {% endfor %}
  </table>
</div>
</body>
</html>
```

写入 `mock-crm/templates/order_form.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>新建订单</title></head>
<body>
<div class="header"><span>CRM 管理系统</span><a href="/logout">退出</a></div>
<div class="container">
  <h2>新建订单</h2>
  <form method="post" style="background:#fff;padding:24px;border-radius:8px;max-width:500px">
    <label>客户名称</label>
    <select name="customer_name" id="customer_name">
      {% for c in customers %}<option value="{{ c.name }}">{{ c.name }}</option>{% endfor %}
    </select><br/>
    <label>产品</label><input name="product" id="product" /><br/>
    <label>金额</label><input name="amount" id="amount" /><br/>
    <button type="submit" id="submit-btn" style="margin-top:12px">提交</button>
  </form>
</div>
</body>
</html>
```

- [ ] **Step 7: 创建 data.json、requirements.txt、Dockerfile**

写入 `mock-crm/data.json`：

```json
{"customers": [], "orders": []}
```

写入 `mock-crm/requirements.txt`：

```
flask==3.1.0
```

写入 `mock-crm/Dockerfile`：

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

- [ ] **Step 8: 验证 Mock CRM 启动**

Run: `cd mock-crm && timeout 3 python app.py 2>&1 || true`
Expected: Flask 服务启动信息（Werkzeug 等），无导入错误

- [ ] **Step 9: Commit**

```bash
git add mock-crm/
git commit -m "feat: add Mock CRM Flask app for RPA demonstration"
```

---

### Task 15: Docker Compose 编排 + 最终集成

**Files:**
- Modify: `docker-compose.yml`
- Create: `backend/app/api/__init__.py`

- [ ] **Step 1: 创建 api/__init__.py**

写入 `backend/app/api/__init__.py`：

```python
# API 路由包
```

- [ ] **Step 2: 更新 docker-compose.yml**

写入 `docker-compose.yml`（覆盖现有文件）：

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: enterprise-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-agent}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-agent123}
      POSTGRES_DB: ${POSTGRES_DB:-enterprise_agent}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent -d enterprise_agent"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: enterprise-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  chroma:
    image: chromadb/chroma:latest
    container_name: enterprise-chroma
    restart: unless-stopped
    volumes:
      - chroma-data:/chroma/chroma
    environment:
      IS_PERSISTENT: TRUE
      ANONYMIZED_TELEMETRY: FALSE
    ports:
      - "8001:8000"

  backend:
    build:
      context: ./backend
    container_name: enterprise-backend
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-agent}:${POSTGRES_PASSWORD:-agent123}@postgres:5432/${POSTGRES_DB:-enterprise_agent}
      REDIS_URL: redis://redis:6379/0
      CHROMA_PERSIST_DIR: /app/data/chroma
      LLM_API_KEY: ${LLM_API_KEY:-}
      LLM_BASE_URL: ${LLM_BASE_URL:-https://api.openai.com/v1}
      LLM_MODEL: ${LLM_MODEL:-gpt-4o}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend-data:/app/data
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  mock-crm:
    build:
      context: ./mock-crm
    container_name: enterprise-mock-crm
    restart: unless-stopped
    ports:
      - "5000:5000"

  frontend:
    build:
      context: ./frontend
    container_name: enterprise-frontend
    restart: unless-stopped
    depends_on:
      - backend
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000}
    ports:
      - "80:80"
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres-data:
  redis-data:
  chroma-data:
  backend-data:
```

- [ ] **Step 3: 验证 docker-compose 配置**

Run: `docker-compose config 2>&1 | head -5`
Expected: 显示 docker-compose 配置（需要 Docker 环境，如果没有则可跳过）

- [ ] **Step 4: 最终集成验证 — 后端导入检查**

Run:
```bash
cd backend && python -c "
from app.main import app
from app.models import User, Document, Conversation, TaskLog, Approval
from app.api import chat, knowledge, task, approval, files
from app.agent import EnterpriseAgent, MCPClientManager
from app.services.knowledge_service import extract_text_from_file
from app.mcp_servers.db_server import DBServer
from app.mcp_servers.mail_server import MailServer
from app.mcp_servers.rpa_server import RPAServer
from app.mcp_servers.file_server import FileServer
print('All modules loaded successfully')
"
```

- [ ] **Step 5: 最终前端构建验证**

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Expected: build 成功

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml backend/app/api/__init__.py
git commit -m "feat: final Docker Compose orchestration with all 6 services"
```

---

## 后续扩展项（不在当前计划范围内）

- Task 服务（task_service.py）和 Approval 服务（approval_service.py）的完整实现
- LangChain Agent 与 LLM 的真正集成（需要 API Key）
- 完整 ChromaDB 向量化集成到 process_document
- Alembic 数据库迁移脚本
- 用户认证（JWT/login API）
- WebSocket 流式输出的完整实现
- MCP Server 子进程自动重连机制
- 单元测试和集成测试
