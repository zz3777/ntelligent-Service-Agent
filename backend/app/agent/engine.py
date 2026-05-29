"""Agent 编排引擎"""

import json
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.agent.mcp_client import MCPClientManager
from app.agent.prompts import SYSTEM_PROMPT
from app.core.config import settings


class EnterpriseAgent:
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp_manager = mcp_manager

    async def get_tools_description(self) -> str:
        tools = await self.mcp_manager.get_all_tools()
        return self._get_tools_description_from_list(tools)

    def _get_tools_description_from_list(self, tools: list[dict]) -> str:
        lines = []
        for t in tools:
            lines.append(f"- {t['name']}（来自 {t['server']}）：{t['description']}")
        return "\n".join(lines)

    def _build_openai_tools(self, tools: list[dict]) -> list[dict]:
        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": f"[{t['server']}] {t['description']}",
                    "parameters": t.get("input_schema", {}),
                },
            })
        return openai_tools

    def _find_tool_server(self, tool_name: str, tools: list[dict]) -> str | None:
        for t in tools:
            if t["name"] == tool_name:
                return t["server"]
        return None

    async def process_message(self, message: str, conversation_history: list | None = None) -> str:
        if not settings.LLM_API_KEY:
            return "请先在设置页面配置 LLM API Key"

        all_tools = await self.mcp_manager.get_all_tools()
        tools_desc = self._get_tools_description_from_list(all_tools)
        system = SYSTEM_PROMPT.format(tools_description=tools_desc)

        client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
        messages = [{"role": "system", "content": system}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        openai_tools = self._build_openai_tools(all_tools)

        reply = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            tools=openai_tools if openai_tools else None,
            tool_choice="auto" if openai_tools else None,
        )

        choice = reply.choices[0]
        msg = choice.message

        if msg.tool_calls:
            for tc in msg.tool_calls:
                func = tc.function
                try:
                    args = json.loads(func.arguments)
                    server_name = self._find_tool_server(func.name, all_tools)
                    if not server_name:
                        result_text = f"未知工具: {func.name}"
                    else:
                        content = await self.mcp_manager.call_tool(server_name, func.name, args)
                        result_text = "\n".join(c.text for c in content if hasattr(c, "text"))
                except Exception as e:
                    result_text = f"执行失败: {e}"

                messages.append(msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                })

            final_reply = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
            )
            return final_reply.choices[0].message.content or ""

        return msg.content or ""

    async def stream_process_message(
        self, message: str, conversation_history: list | None = None
    ) -> AsyncGenerator[str, None]:
        if not settings.LLM_API_KEY:
            yield "请先在设置页面配置 LLM API Key"
            return

        all_tools = await self.mcp_manager.get_all_tools()
        tools_desc = self._get_tools_description_from_list(all_tools)
        system = SYSTEM_PROMPT.format(tools_description=tools_desc)

        client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
        messages = [{"role": "system", "content": system}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        openai_tools = self._build_openai_tools(all_tools)

        reply = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            tools=openai_tools if openai_tools else None,
            tool_choice="auto" if openai_tools else None,
        )

        choice = reply.choices[0]
        msg = choice.message

        # 有工具调用：静默执行工具，然后流式输出最终回复
        if msg.tool_calls:
            for tc in msg.tool_calls:
                func = tc.function
                try:
                    args = json.loads(func.arguments)
                    server_name = self._find_tool_server(func.name, all_tools)
                    if not server_name:
                        result_text = f"未知工具: {func.name}"
                    else:
                        content = await self.mcp_manager.call_tool(server_name, func.name, args)
                        result_text = "\n".join(c.text for c in content if hasattr(c, "text"))
                except Exception as e:
                    result_text = f"执行失败: {e}"

                messages.append(msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                })

            # 流式输出最终回复
            stream = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return

        # 无工具调用：直接流式输出
        stream = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
