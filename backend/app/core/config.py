from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "企业智能服务 Agent"
    VERSION: str = "0.1.0"
    CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:80", "http://localhost:5173"]

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
    MCP_KNOWLEDGE_SERVER_CMD: str = "python -m app.mcp_servers.knowledge_server"

    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
