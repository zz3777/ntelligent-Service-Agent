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
