from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.api import chat, knowledge, task, approval, files, settings as settings_router
from app.agent.state import mcp_manager
from app.agent.engine import EnterpriseAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    mcp_manager.register_server("db", settings.MCP_DB_SERVER_CMD)
    mcp_manager.register_server("mail", settings.MCP_MAIL_SERVER_CMD)
    mcp_manager.register_server("rpa", settings.MCP_RPA_SERVER_CMD)
    mcp_manager.register_server("file", settings.MCP_FILE_SERVER_CMD)
    mcp_manager.register_server("knowledge", settings.MCP_KNOWLEDGE_SERVER_CMD)
    await mcp_manager.start_all()

    from app.agent import state
    state.agent = EnterpriseAgent(mcp_manager)

    yield

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
app.include_router(knowledge.router)
app.include_router(task.router)
app.include_router(approval.router)
app.include_router(files.router)
app.include_router(settings_router.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}
