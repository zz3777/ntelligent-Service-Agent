"""Agent 编排引擎"""

import json
import re
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.agent.mcp_client import MCPClientManager
from app.agent.prompts import SYSTEM_PROMPT
from app.core.config import settings

MAX_TOOL_ROUNDS = 10


def _parse_text_tool_calls(text: str) -> list[dict]:
    """从文本中解析工具调用（兼容 DeepSeek DSML 等非标准格式）"""
    calls = []
    for match in re.finditer(r'invoke\s+name="([^"]+)"', text):
        tool_name = match.group(1)
        args = {}
        param_match = re.search(
            rf'invoke\s+name="{re.escape(tool_name)}"[^>]*>(.*?)</\s*invoke',
            text, re.DOTALL
        )
        if param_match:
            param_text = param_match.group(1).strip()
            if param_text:
                try:
                    args = json.loads(param_text)
                except json.JSONDecodeError:
                    kv_pairs = re.findall(r'(\w+)="([^"]*)"', param_text)
                    if kv_pairs:
                        args = dict(kv_pairs)
                    elif len(param_text) < 200:
                        if tool_name == "navigate":
                            args = {"url": param_text}
                        elif tool_name == "fill_input":
                            args = {"selector": param_text}
                        elif tool_name == "click":
                            args = {"text": param_text}
                        elif tool_name == "extract_text":
                            args = {"selector": param_text}
                        else:
                            args = {"input": param_text}
        calls.append({"name": tool_name, "arguments": args})
    return calls


def _extract_tool_calls(response) -> list[dict]:
    """从 LLM 响应中提取工具调用（标准格式 + 文本格式）"""
    msg = response.choices[0].message
    tool_calls = []

    # 标准格式
    if msg.tool_calls:
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, TypeError):
                args = {}
            tool_calls.append({"name": tc.function.name, "arguments": args, "id": tc.id, "raw_msg": msg})
        return tool_calls

    # 文本格式（DSML 等）
    if msg.content:
        text_calls = _parse_text_tool_calls(msg.content)
        for i, tc in enumerate(text_calls):
            tool_calls.append({"name": tc["name"], "arguments": tc["arguments"], "id": f"text_{i}", "raw_msg": None})

    return tool_calls


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

    async def _execute_tool(self, tc: dict, all_tools: list[dict]) -> str:
        """执行单个工具调用，返回结果文本"""
        try:
            server_name = self._find_tool_server(tc["name"], all_tools)
            if not server_name:
                return f"未知工具: {tc['name']}"
            content = await self.mcp_manager.call_tool(server_name, tc["name"], tc["arguments"])
            return "\n".join(c.text for c in content if hasattr(c, "text"))
        except Exception as e:
            return f"执行失败: {e}"

    def _append_tool_results(self, messages: list, tool_calls: list[dict], results: list[str]):
        """将一批工具调用和结果追加到消息列表"""
        if not tool_calls:
            return

        # 检查是否是标准格式（所有 tc 共享同一个 raw_msg）
        std_msg = tool_calls[0].get("raw_msg")
        if std_msg:
            # 标准格式：追加一次 assistant 消息 + 每个 tool 结果
            messages.append(std_msg)
            for tc, result_text in zip(tool_calls, results):
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result_text})
        else:
            # 文本格式：每个工具调用用 assistant + user 轮替
            for tc, result_text in zip(tool_calls, results):
                messages.append({"role": "assistant", "content": f"调用工具 {tc['name']}"})
                messages.append({"role": "user", "content": f"[系统] 工具 {tc['name']} 执行结果:\n{result_text}"})

    async def process_message(self, message: str, conversation_history: list | None = None) -> str:
        """非流式处理（单轮对话）"""
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

        # Agent Loop：循环执行工具，直到没有工具调用
        for _ in range(MAX_TOOL_ROUNDS):
            reply = await client.chat.completions.create(
                model=settings.LLM_MODEL, messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
            )
            tool_calls = _extract_tool_calls(reply)

            if not tool_calls:
                return reply.choices[0].message.content or ""

            results = []
            for tc in tool_calls:
                result_text = await self._execute_tool(tc, all_tools)
                results.append(result_text)
            self._append_tool_results(messages, tool_calls, results)

        # 超过轮数，返回最后一轮的文本
        return reply.choices[0].message.content or ""

    async def stream_process_message(
        self, message: str, conversation_history: list | None = None
    ) -> AsyncGenerator[str, None]:
        """流式处理：工具执行阶段非流式，最终回复流式输出"""
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

        # 阶段1：Agent Loop（非流式，执行工具）
        for round_num in range(MAX_TOOL_ROUNDS):
            reply = await client.chat.completions.create(
                model=settings.LLM_MODEL, messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
            )
            tool_calls = _extract_tool_calls(reply)

            if not tool_calls:
                # 没有工具调用，进入阶段2流式输出
                break

            print(f"[AGENT] Round {round_num+1}: executing {[tc['name'] for tc in tool_calls]}")
            results = []
            for tc in tool_calls:
                result_text = await self._execute_tool(tc, all_tools)
                results.append(result_text)
                print(f"[AGENT] {tc['name']} done, result_len={len(result_text)}")
            self._append_tool_results(messages, tool_calls, results)
        else:
            # 达到最大轮数
            print("[AGENT] Max rounds reached")

        # 阶段2：流式输出最终回复
        stream = await client.chat.completions.create(
            model=settings.LLM_MODEL, messages=messages, stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
