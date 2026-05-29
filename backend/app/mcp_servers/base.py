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
