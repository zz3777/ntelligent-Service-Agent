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
