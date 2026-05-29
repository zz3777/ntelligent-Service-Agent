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
