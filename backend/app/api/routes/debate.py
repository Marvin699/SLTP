"""反向质询辩论 API —— AI 辩论伙伴

设计理念（"人机双向奔赴"）：
- AI 定位为辩论伙伴而非答案提供者：只质询、不给答案
- 结构化记录学生评判逻辑（维度 + 置信度 + 陈述）
- 追问类型限定四种：假设 / 风险 / 替代 / 标准
- 形成"假设-验证-反驳-重构"四阶段深度学习闭环
"""
import json
import random
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.debate import DebateSession, DebateMessage
from app.services import llm_service

router = APIRouter(prefix="/api/debate", tags=["反向质询辩论"])

# ─── 阶段定义 ───
STAGES = ["hypothesis", "verify", "rebut", "rebuild"]
STAGE_NAMES = {
    "hypothesis": "假设提出",
    "verify": "验证分析",
    "rebut": "反驳交锋",
    "rebuild": "重构优化",
    "completed": "闭环完成",
}

DIMENSION_NAMES = {
    "safety": "安全性",
    "timeliness": "时效性",
    "economy": "经济性",
    "feasibility": "可行性",
    "compliance": "合规性",
    "load": "载重匹配",
    "airspace": "空域合规",
    "cold_chain": "冷链时限",
}

CHALLENGE_NAMES = {
    "assumption": "假设质询",
    "risk": "风险质询",
    "alternative": "替代质询",
    "standard": "标准质询",
}

# ─── 辩论人设 System Prompt ───
DEBATE_SYSTEM_PROMPT = """你是一名严格但善意的"辩论伙伴"考官，面向学习《无人机应急物流运输》课程的高职学生。

你的任务不是给出答案，而是针对学生对应急运输方案的陈述进行"反向质询"——用追问迫使学生检查自己的推理漏洞。

必须遵守的规则：
1. 绝不直接给出正确答案、修改步骤或你自己的完整方案
2. 每次回复只提出 1~2 个针对性追问，聚焦学生陈述中最薄弱的假设
3. 追问类型限定四种（在开头标注）：
   【假设质询】—— 你这个结论建立在什么假设上？依据是什么？
   【风险质询】—— 如果出现突发情况（天气/载荷/延误），你的方案哪个环节最先失效？
   【替代质询】—— 有没有其他可能？换个参数/机型/航线会不会更好？副作用是什么？
   【标准质询】—— 该结论对照哪条行业规范或评估指标？1+X标准、审定指南、航线规范？
4. 语气专业、犀利但尊重，用中文，每次回复不超过 180 字
5. 如果学生的论证确实严密，先用一句话肯定关键亮点，再提出更深一层的追问
6. 结合方案具体数据（四维分数、总距离、无人机数量、载重等）追问，不要泛泛而谈

输出格式（严格遵守）：
【追问类型：假设质询|风险质询|替代质询|标准质询】
追问内容"""


# ─── Pydantic 模型 ───
class CreateSessionRequest(BaseModel):
    plan_record_id: Optional[int] = None
    plan_summary: str = ""
    group_name: Optional[str] = None


class ChallengeRequest(BaseModel):
    content: str
    stage: str = "hypothesis"
    judgment_dimensions: List[str] = []
    judgment_confidence: int = 50


class CompleteRequest(BaseModel):
    final_verdict: str = ""


class TeacherNoteRequest(BaseModel):
    content: str


# ─── 工具函数 ───
def _session_to_dict(s: DebateSession, db: Session) -> dict:
    msg_count = db.query(DebateMessage).filter(DebateMessage.session_id == s.id).count()
    student_count = db.query(DebateMessage).filter(
        DebateMessage.session_id == s.id, DebateMessage.role == "student"
    ).count()
    return {
        "id": s.id,
        "plan_record_id": s.plan_record_id,
        "plan_summary": s.plan_summary,
        "group_name": s.group_name,
        "stage": s.stage,
        "stage_name": STAGE_NAMES.get(s.stage, s.stage),
        "status": s.status,
        "final_verdict": s.final_verdict,
        "message_count": msg_count,
        "student_statement_count": student_count,
        "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else None,
    }


def _message_to_dict(m: DebateMessage) -> dict:
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "stage": m.stage,
        "stage_name": STAGE_NAMES.get(m.stage, m.stage) if m.stage else None,
        "judgment_dimensions": json.loads(m.judgment_dimensions) if m.judgment_dimensions else [],
        "judgment_confidence": m.judgment_confidence,
        "challenge_type": m.challenge_type,
        "challenge_name": CHALLENGE_NAMES.get(m.challenge_type, m.challenge_type) if m.challenge_type else None,
        "created_at": m.created_at.strftime("%H:%M") if m.created_at else None,
    }


def _parse_challenge_type(reply: str) -> str:
    """从 AI 回复中解析追问类型，解析失败时按启发式猜测"""
    for key, name in CHALLENGE_NAMES.items():
        if name in reply:
            return key
    m = re.search(r"【追问类型[:：]\s*([^】]+)】", reply)
    if m:
        raw = m.group(1).strip()
        for key, name in CHALLENGE_NAMES.items():
            if key in raw or name in raw:
                return key
    if any(w in reply for w in ["假设", "依据", "凭什么"]):
        return "assumption"
    if any(w in reply for w in ["风险", "失效", "突发", "如果.*天气"]):
        return "risk"
    if any(w in reply for w in ["替代", "换个", "其他方案", "副作用"]):
        return "alternative"
    if any(w in reply for w in ["标准", "规范", "指标", "审定"]):
        return "standard"
    return "assumption"


# LLM 不可用时的兜底追问（保证课堂演示不中断）
FALLBACK_CHALLENGES = [
    ("assumption", "【追问类型：假设质询】\n你这个方案总距离最短的结论，是建立在所有需求点时效窗口宽松的假设上吗？如果 #D03 的物资是急救类，这个假设还成立吗？"),
    ("risk", "【追问类型：风险质询】\n如果配送当天区域风速从 4 级升到 6 级，你的无人机编队哪个环节最先失效？载重冗余还够吗？"),
    ("alternative", "【追问类型：替代质询】\n你选择用 11 架中小型无人机而非 5 架重载机型，有没有算过等载重下的单位能耗差？换机型会不会反而更经济？"),
    ("standard", "【追问类型：标准质询】\n你说方案「合规」，具体对照的是 1+X 物流标准还是《物流无人机运行审定指南》的哪一条？冷链物资的时限要求是多少？"),
]


def _build_challenge_prompt(session: DebateSession, history: List[DebateMessage], req: ChallengeRequest) -> str:
    """拼接质询 user prompt：方案摘要 + 对话历史 + 学生本次陈述"""
    parts = []
    if session.plan_summary:
        parts.append(f"【学生当前分析的方案】\n{session.plan_summary}\n")

    if history:
        lines = []
        for m in history[-6:]:  # 最近 6 条防止 prompt 过长
            role_name = "学生" if m.role == "student" else "辩论伙伴"
            lines.append(f"{role_name}：{m.content[:300]}")
        parts.append("【之前的对话】\n" + "\n".join(lines) + "\n")

    dims = "、".join(DIMENSION_NAMES.get(d, d) for d in req.judgment_dimensions) or "未选择"
    parts.append(
        f"【学生本次陈述】（阶段：{STAGE_NAMES.get(req.stage, req.stage)}；"
        f"评判维度：{dims}；自评置信度：{req.judgment_confidence}%）\n{req.content}"
    )
    return "\n".join(parts)


# ─── 接口 ───
@router.post("/session")
def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建辩论会话（绑定一个方案）"""
    session = DebateSession(
        user_id=current_user.id,
        username=current_user.username,
        group_name=req.group_name,
        plan_record_id=req.plan_record_id,
        plan_summary=req.plan_summary or "（未绑定方案，基于课堂陈述质询）",
        stage="hypothesis",
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 开场白：AI 先亮明辩论规则
    opener = (
        "【追问类型：假设质询】\n"
        f"欢迎进入反向质询环节。我是你的辩论伙伴，我只提问、不给答案。\n"
        f"请先陈述你对这个方案的初始判断（假设阶段）：你认为它最突出的优势是什么？"
        f"你的判断建立在哪些假设之上？"
    )
    db.add(DebateMessage(session_id=session.id, role="ai", content=opener, stage="hypothesis", challenge_type="assumption"))
    db.commit()

    return {"success": True, "session": _session_to_dict(session, db)}


@router.get("/sessions")
def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的辩论会话列表"""
    sessions = db.query(DebateSession).filter(
        DebateSession.user_id == current_user.id
    ).order_by(DebateSession.id.desc()).limit(limit).all()
    return {"success": True, "sessions": [_session_to_dict(s, db) for s in sessions]}


@router.get("/session/{session_id}")
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """会话详情（含全部消息，供回放）"""
    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="无权访问该会话")

    messages = db.query(DebateMessage).filter(
        DebateMessage.session_id == session_id
    ).order_by(DebateMessage.id.asc()).all()

    return {
        "success": True,
        "session": _session_to_dict(session, db),
        "messages": [_message_to_dict(m) for m in messages],
    }


@router.post("/session/{session_id}/challenge")
def challenge(
    session_id: int,
    req: ChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """学生提交陈述（含评判逻辑）→ AI 生成针对性追问"""
    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该会话")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="会话已结束，请创建新会话")
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="陈述内容不能为空")

    # 1. 保存学生消息（评判逻辑结构化落库）
    student_msg = DebateMessage(
        session_id=session_id,
        role="student",
        content=req.content.strip(),
        stage=req.stage if req.stage in STAGES else session.stage,
        judgment_dimensions=json.dumps(req.judgment_dimensions, ensure_ascii=False) if req.judgment_dimensions else None,
        judgment_confidence=req.judgment_confidence,
    )
    db.add(student_msg)

    # 2. 会话阶段前进
    session.stage = req.stage if req.stage in STAGES else session.stage

    # 3. 取历史消息（不含刚加的这条）供 prompt
    db.commit()
    db.refresh(student_msg)
    history = db.query(DebateMessage).filter(
        DebateMessage.session_id == session_id, DebateMessage.id < student_msg.id
    ).order_by(DebateMessage.id.asc()).all()

    # 4. 调 LLM 生成追问（失败兜底）
    reply = None
    try:
        reply = llm_service.chat(
            DEBATE_SYSTEM_PROMPT,
            _build_challenge_prompt(session, history, req),
            temperature=0.7,
        )
    except Exception as e:
        print(f"[Debate] LLM 调用失败，使用兜底追问: {e}")

    if not reply:
        ctype, fallback = random.choice(FALLBACK_CHALLENGES)
        reply = fallback
    else:
        ctype = _parse_challenge_type(reply)

    # 5. 保存 AI 追问消息
    ai_msg = DebateMessage(
        session_id=session_id,
        role="ai",
        content=reply.strip(),
        stage=session.stage,
        challenge_type=ctype,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "success": True,
        "student_message": _message_to_dict(student_msg),
        "ai_message": _message_to_dict(ai_msg),
        "stage": session.stage,
    }


@router.post("/session/{session_id}/complete")
def complete_session(
    session_id: int,
    req: CompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """结束会话：记录学生最终结论，闭环完成"""
    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该会话")

    session.status = "completed"
    session.stage = "completed"
    session.final_verdict = req.final_verdict or "（未填写最终结论）"
    db.commit()

    return {"success": True, "session": _session_to_dict(session, db)}


@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除会话（连同全部消息）"""
    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该会话")

    db.query(DebateMessage).filter(DebateMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()

    return {"success": True, "deleted": session_id}


@router.post("/session/{session_id}/teacher-note")
def teacher_note(
    session_id: int,
    req: TeacherNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """教师介入留言（教师端监控用，M3 期接入前端）"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可介入留言")

    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    msg = DebateMessage(
        session_id=session_id,
        role="teacher",
        content=f"👨‍🏫 教师介入：{req.content.strip()}",
        stage=session.stage,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return {"success": True, "message": _message_to_dict(msg)}
