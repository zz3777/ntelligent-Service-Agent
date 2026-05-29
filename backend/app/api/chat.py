import json
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationListItem
from app.models.conversation import Conversation
from app.agent import state as agent_state

router = APIRouter(prefix="/api/chat", tags=["chat"])

MAX_HISTORY = 10


def _load_history(messages_json: str) -> list[dict]:
    try:
        msgs = json.loads(messages_json)
        return msgs[-MAX_HISTORY:]
    except (json.JSONDecodeError, TypeError):
        return []


def _save_history(messages_json: str, user_msg: str, assistant_msg: str) -> str:
    try:
        msgs = json.loads(messages_json)
    except (json.JSONDecodeError, TypeError):
        msgs = []
    msgs.append({"role": "user", "content": user_msg})
    msgs.append({"role": "assistant", "content": assistant_msg})
    msgs = msgs[-MAX_HISTORY * 2:]
    return json.dumps(msgs, ensure_ascii=False)


@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    conv_id = request.conversation_id or uuid.uuid4()
    task_id = f"T{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    if not request.conversation_id:
        conv = Conversation(id=conv_id, title=request.message[:64], messages="[]")
        db.add(conv)
        await db.commit()

    # 加载历史
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    history = _load_history(conv.messages) if conv else []

    if agent_state.agent:
        reply = await agent_state.agent.process_message(request.message, history)
    else:
        reply = "Agent 引擎未就绪"

    # 保存历史
    if conv:
        conv.messages = _save_history(conv.messages, request.message, reply)
        conv.updated_at = datetime.utcnow()
        await db.commit()

    return ChatResponse(conversation_id=conv_id, task_id=task_id, reply=reply)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    conv_id = request.conversation_id or uuid.uuid4()

    async def event_generator():
        from app.core.db import async_session_factory

        async with async_session_factory() as db:
            # 创建新会话
            if not request.conversation_id:
                conv = Conversation(id=conv_id, title=request.message[:64], messages="[]")
                db.add(conv)
                await db.commit()

            # 加载历史
            result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
            conv = result.scalar_one_or_none()
            history = _load_history(conv.messages) if conv else []

        full_reply = []
        if agent_state.agent:
            async for chunk in agent_state.agent.stream_process_message(request.message, history):
                full_reply.append(chunk)
                yield f"data: {json.dumps({'content': chunk, 'conversation_id': str(conv_id)}, ensure_ascii=False)}\n\n"
        else:
            yield f"data: {json.dumps({'content': 'Agent 引擎未就绪', 'conversation_id': str(conv_id)})}\n\n"

        # 保存历史（新 session）
        final_text = "".join(full_reply)
        async with async_session_factory() as db:
            result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
            conv = result.scalar_one_or_none()
            if conv:
                conv.messages = _save_history(conv.messages, request.message, final_text)
                conv.updated_at = datetime.utcnow()
                await db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc()).limit(50)
    )
    convs = result.scalars().all()
    return [ConversationListItem.model_validate(c) for c in convs]


@router.get("/conversations/{conv_id}/messages")
async def get_conversation_messages(conv_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        return []
    return _load_history(conv.messages)


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        return {"message": "不存在"}
    await db.delete(conv)
    await db.commit()
    return {"message": "已删除"}


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            await websocket.send_json({"type": "status", "content": "处理中..."})

            if agent_state.agent:
                reply = await agent_state.agent.process_message(msg.get("message", ""))
            else:
                reply = "Agent 引擎未就绪"

            await websocket.send_json({"type": "message", "content": reply})
    except WebSocketDisconnect:
        pass
