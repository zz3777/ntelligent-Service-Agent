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
