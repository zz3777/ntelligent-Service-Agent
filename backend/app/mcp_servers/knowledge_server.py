"""MCP-Knowledge Server: 提供知识库入库和检索工具"""

import asyncio
import uuid
from mcp.types import Tool, TextContent

from app.mcp_servers.base import MCPServer


class KnowledgeServer(MCPServer):
    def __init__(self):
        super().__init__("knowledge-server")

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="add_to_knowledge",
                    description="将文本内容添加到企业知识库（向量化存储），可用于添加书籍、制度、文档摘要等",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "要入库的文本内容"
                            },
                            "title": {
                                "type": "string",
                                "description": "内容标题（可选），如书名、制度名"
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="search_knowledge",
                    description="在企业知识库中搜索相关内容，支持语义搜索",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词或问题"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "返回结果数量，默认5",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "add_to_knowledge":
                content = arguments.get("content", "")
                title = arguments.get("title", "")
                if not content.strip():
                    return [TextContent(type="text", text="错误：内容不能为空")]

                try:
                    from app.agent.rag import add_to_knowledgebase
                    doc_id = str(uuid.uuid4())
                    await add_to_knowledgebase(content, title or doc_id, 0)
                    return [TextContent(type="text", text=f"已成功入库：{title or '未命名内容'}")]
                except Exception as e:
                    return [TextContent(type="text", text=f"入库失败: {e}")]

            elif name == "search_knowledge":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 5)
                if not query.strip():
                    return [TextContent(type="text", text="错误：搜索内容不能为空")]

                try:
                    from app.agent.rag import search_knowledge
                    results = await search_knowledge(query, top_k)
                    if not results:
                        return [TextContent(type="text", text="未找到相关内容")]
                    lines = []
                    for i, r in enumerate(results, 1):
                        lines.append(f"[{i}] (相关度: {r['score']:.2f}) {r['content'][:200]}")
                    return [TextContent(type="text", text="\n\n".join(lines))]
                except Exception as e:
                    return [TextContent(type="text", text=f"搜索失败: {e}")]

            return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    server = KnowledgeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
