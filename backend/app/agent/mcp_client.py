"""MCP Client 管理器：管理 MCP Server 子进程生命周期和通信"""

import json
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPServerConnection:
    def __init__(self, name: str, command: str):
        self.name = name
        self.server_params = StdioServerParameters(command="python", args=command.split()[1:])
        self.session = None
        self.exit_stack = None

    async def connect(self):
        self.exit_stack = AsyncExitStack()
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
