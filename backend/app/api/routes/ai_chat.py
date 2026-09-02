"""AI助教对话 API

增强版：
- 绑定当前登录学生（user_id）
- 保存对话历史到 chat_histories 表
- 支持查询历史对话
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token  # noqa: F401 (保持兼容)
from app.models.user import User
from app.models.chat_history import ChatHistory

router = APIRouter(prefix="/api/ai-chat", tags=["AI助教对话"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None


@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI助教对话接口（绑定学生身份，自动保存历史）

    优先走 pydantic-ai 工具调用智能体（可查方案/核验/统计/手册），
    异常时自动降级为纯对话模式，保证课堂不中断。
    """
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    if not msgs:
        return {"success": False, "message": "消息为空"}

    # ── 优先：工具调用智能体 ──
    try:
        from app.services.wing_agent import run_wing_chat

        result = await run_wing_chat(msgs, current_user, db)
        _save_history(db, current_user, msgs, result["reply"])
        return result
    except Exception:
        pass  # 静默降级

    # ── 降级：纯对话模式（原逻辑） ──
    try:
        from openai import OpenAI
        from app.core.config import settings

        api_key = settings.LLM_API_KEY
        base_url = settings.LLM_BASE_URL
        model = settings.LLM_MODEL

        if not api_key:
            return {"success": False, "message": "AI助教未配置，请先在系统管理中配置大模型"}

        client = OpenAI(api_key=api_key, base_url=base_url, timeout=60.0)

        system_msg = req.system_prompt or (
            "你是智慧低空应急运输教学平台的AI助教，你的名字叫'小翼'。"
            "你擅长无人机物流、航线规划、应急运输、装箱优化等领域的教学辅导。"
            "请用简洁专业的中文回答学生的问题，必要时给出实际案例或操作建议。"
            "在自我介绍时请使用'小翼'这个名字。"
        )

        full_messages = [{"role": "system", "content": system_msg}]
        for m in msgs:
            full_messages.append({"role": m["role"], "content": m["content"]})

        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=2048,
            temperature=0.7,
        )

        content = response.choices[0].message.content

        # 保存对话历史：保存最后一条 user 消息 + assistant 回复
        _save_history(db, current_user, msgs, content)

        return {"success": True, "reply": content, "tools_used": []}
    except Exception as e:
        return {"success": False, "message": f"AI助教响应异常: {str(e)}"}


def _save_history(db: Session, current_user: User, msgs: list, reply: str):
    """保存最后一条 user 消息 + assistant 回复"""
    last_user_msg = next((m for m in reversed(msgs) if m["role"] == "user"), None)
    if last_user_msg:
        db.add(ChatHistory(user_id=current_user.id, role="user", content=last_user_msg["content"]))
        db.add(ChatHistory(user_id=current_user.id, role="assistant", content=reply))
        db.commit()


@router.get("/history")
def get_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前学生的对话历史"""
    records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.id.desc()).limit(limit).all()

    # 反转为时间正序
    records = list(reversed(records))
    return {
        "success": True,
        "messages": [
            {"role": r.role, "content": r.content, "time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None}
            for r in records
        ],
    }


@router.delete("/history")
def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空当前学生的对话历史"""
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    return {"success": True, "message": "对话历史已清空"}
