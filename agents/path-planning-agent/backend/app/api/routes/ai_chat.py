"""AI助教对话 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/ai-chat", tags=["AI助教对话"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None


@router.post("/chat")
def chat(req: ChatRequest):
    """AI助教对话接口"""
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
        for m in req.messages:
            full_messages.append({"role": m.role, "content": m.content})

        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=2048,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        return {"success": True, "reply": content}
    except Exception as e:
        return {"success": False, "message": f"AI助教响应异常: {str(e)}"}
