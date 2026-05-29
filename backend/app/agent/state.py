"""全局 Agent 单例"""
from app.agent.mcp_client import MCPClientManager
from app.agent.engine import EnterpriseAgent

mcp_manager = MCPClientManager()
agent: EnterpriseAgent | None = None
