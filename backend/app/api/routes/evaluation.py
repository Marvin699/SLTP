"""T5.1 课前课中贯通 API

课中环节引用课前方案库（OptimizationRecord），
并基于真实方案数据（指标 + 四维评分 + 辩论记录）生成 AI 点评。

LLM 走 OpenAI 兼容协议（智谱/DeepSeek/通义等，由 .env 的
LLM_BASE_URL / LLM_MODEL / LLM_API_KEY 决定），
未配置或调用失败时自动降级为规则化点评，保证课堂不中断。
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import SessionLocal
from app.models.optimizer import OptimizationRecord
from app.models.report import ReportRecord
from app.models.debate import DebateSession, DebateMessage
from app.models.user import User
from app.services.llm_service import chat as llm_chat, is_configured

router = APIRouter(prefix="/api/evaluation", tags=["T5-课前课中贯通"])

DIM_NAMES = {"safety": "安全性", "timeliness": "时效性", "economy": "经济性", "feasibility": "可行性"}


def _latest_report_by_user(db):
    """每个用户最近一次报告的四维评分与择优标记"""
    result = {}
    reports = (
        db.query(ReportRecord)
        .filter(ReportRecord.user_id.isnot(None))
        .order_by(ReportRecord.created_at.desc())
        .all()
    )
    for r in reports:
        if r.user_id in result:
            continue
        scores = {}
        try:
            data = json.loads(r.report_data or "{}")
            scores = data.get("scores", {}) or {}
        except Exception:
            pass
        result[r.user_id] = {
            "scores": scores,
            "is_chosen": bool(r.is_chosen),
            "filename": r.filename,
        }
    return result


def _debate_brief_by_user(db):
    """每个用户最近一次辩论会话的简要信息（供 AI 点评参考）"""
    brief = {}
    sessions = (
        db.query(DebateSession)
        .order_by(DebateSession.updated_at.desc())
        .all()
    )
    for s in sessions:
        if s.user_id in brief:
            continue
        msg_count = db.query(DebateMessage).filter(DebateMessage.session_id == s.id).count()
        last_student = (
            db.query(DebateMessage)
            .filter(DebateMessage.session_id == s.id, DebateMessage.role == "student")
            .order_by(DebateMessage.created_at.desc())
            .first()
        )
        brief[s.user_id] = {
            "stage": s.stage,
            "message_count": msg_count,
            "final_verdict": (s.final_verdict or "")[:200] or None,
            "last_student_msg": (last_student.content if last_student else "")[:200] or None,
        }
    return brief


@router.get("/plans")
def list_plans(limit: int = 30, user_id: Optional[int] = None):
    """课前方案库列表（含学生姓名、四维评分、辩论概况），供课中环节引用"""
    db = SessionLocal()
    try:
        q = db.query(OptimizationRecord)
        if user_id:
            q = q.filter(OptimizationRecord.user_id == user_id)
        records = q.order_by(OptimizationRecord.created_at.desc()).limit(limit).all()

        users = {u.id: u for u in db.query(User).all()}
        scores_map = _latest_report_by_user(db)
        debate_map = _debate_brief_by_user(db)

        plans = []
        for rec in records:
            u = users.get(rec.user_id)
            rep = scores_map.get(rec.user_id, {})
            plans.append({
                "id": rec.id,
                "user_id": rec.user_id,
                "student_name": u.username if u else None,
                "total_distance": rec.total_distance,
                "total_energy": rec.total_energy,
                "total_trips": rec.total_trips,
                "village_count": rec.village_count,
                "drone_count": rec.drone_count,
                "scores": rep.get("scores", {}),
                "is_chosen": rep.get("is_chosen", False),
                "has_geojson": '"geojson"' in (rec.solution_data or ""),
                "debate": debate_map.get(rec.user_id),
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            })
        return {"plans": plans}
    finally:
        db.close()


class AiCommentRequest(BaseModel):
    plan_ids: List[int]


def _gather_plan_context(db, plan_ids):
    """收集参与点评的方案上下文（指标 + 评分 + 辩论摘要）"""
    users = {u.id: u for u in db.query(User).all()}
    scores_map = _latest_report_by_user(db)
    debate_map = _debate_brief_by_user(db)

    contexts = []
    for pid in plan_ids:
        rec = db.query(OptimizationRecord).filter(OptimizationRecord.id == pid).first()
        if not rec:
            continue
        u = users.get(rec.user_id)
        rep = scores_map.get(rec.user_id, {})
        contexts.append({
            "plan_id": rec.id,
            "student_name": (u.username if u else None) or f"方案#{rec.id}",
            "stats": {
                "total_distance": rec.total_distance,
                "total_energy": rec.total_energy,
                "total_trips": rec.total_trips,
                "village_count": rec.village_count,
                "drone_count": rec.drone_count,
            },
            "scores": rep.get("scores", {}),
            "debate": debate_map.get(rec.user_id),
        })
    return contexts


def _build_llm_prompt(contexts):
    """构造 AI 点评提示词（OpenAI 兼容协议，模型由配置决定）"""
    system = (
        "你是低空无人机应急运输教学平台的 AI 助教，负责课中环节一的方案点评。"
        "你将收到若干学生小组的课前方案数据（配送指标、四维评分、辩论表现）。"
        "请严格只输出如下 JSON（不要 markdown 代码块、不要多余文字）：\n"
        '{"groups":[{"plan_id":1,"name":"学生名","keywords":[{"text":"关键词","weight":90}],'
        '"conclusion":"高频出现\\"词1、词2、词3\\"","highlight":"胜在……（10字内）",'
        '"risks":[{"level":"high|medium|low","description":"具体风险描述"}],'
        '"rank":1,"tags":["亮点标签，4-8字，2-3个"],"comment":"综合点评，60字内"}]}\n'
        "要求：keywords 提取8-12个该方案的核心亮点词（weight 50-95，按重要性排序）；"
        "risks 1-3条，按数据推断（如某维度评分低、趟次多耗时长等）；"
        "rank 按 overall 综合表现排序；语言面向课堂投影展示，专业且简练。"
    )
    user = json.dumps(contexts, ensure_ascii=False, indent=1)
    return system, user


def _fallback_comment(contexts):
    """规则化点评（LLM 未配置/失败时降级，保证课堂不中断）"""
    all_scores = []
    for c in contexts:
        vals = [v for v in (c.get("scores") or {}).values() if isinstance(v, (int, float))]
        if vals:
            all_scores.append(sum(vals) / len(vals))
        else:
            all_scores.append(0)

    ranked = sorted(
        range(len(contexts)),
        key=lambda i: (all_scores[i], -(contexts[i]["stats"].get("total_distance") or 0)),
    )
    rank_of = {idx: rank + 1 for rank, idx in enumerate(ranked)}

    groups = []
    for i, c in enumerate(contexts):
        stats, scores, debate = c["stats"], c.get("scores") or {}, c.get("debate") or {}
        keywords = []
        if (stats.get("drone_count") or 0) >= 2:
            keywords.append({"text": "多机协同", "weight": 90})
        if (stats.get("village_count") or 0) >= 5:
            keywords.append({"text": "多点位覆盖", "weight": 85})
        if (stats.get("total_trips") or 0) >= 3:
            keywords.append({"text": "多趟次配送", "weight": 80})
        if (stats.get("total_distance") or 0) and stats["total_distance"] < 100:
            keywords.append({"text": "短距高效", "weight": 88})
        for key, name in (("safety", "安全优先"), ("timeliness", "时效优先"),
                          ("economy", "成本控制"), ("feasibility", "可落地")):
            if isinstance(scores.get(key), (int, float)) and scores[key] >= 80:
                keywords.append({"text": name, "weight": min(95, int(scores[key]))})
        if debate.get("message_count"):
            keywords.append({"text": "深度思辨", "weight": 82})
        keywords.append({"text": "ACO路径优化", "weight": 75})
        if len(keywords) < 6:
            keywords.append({"text": "分级配送", "weight": 65})

        # 风险：评分最低的维度
        risks = []
        scored = [(k, v) for k, v in scores.items() if isinstance(v, (int, float))]
        if scored:
            worst_key, worst_val = min(scored, key=lambda kv: kv[1])
            if worst_val < 80:
                risks.append({
                    "level": "medium" if worst_val >= 60 else "high",
                    "description": f"{DIM_NAMES.get(worst_key, worst_key)}评分偏低（{worst_val}分），汇报时需补充改进思路",
                })
        if (stats.get("total_trips") or 0) >= 4:
            risks.append({"level": "low", "description": "趟次较多，实际应急中可评估合并航线以压缩总耗时"})
        if not risks:
            risks.append({"level": "low", "description": "暂无明显风险项，建议汇报中主动说明方案的适用边界"})

        groups.append({
            "plan_id": c["plan_id"],
            "name": c["student_name"],
            "keywords": keywords[:12],
            "conclusion": "高频出现「" + "、".join(k["text"] for k in keywords[:3]) + "」",
            "highlight": "数据驱动" if all_scores[i] >= 80 else "稳步迭代",
            "risks": risks,
            "rank": rank_of[i],
            "tags": [k["text"] for k in keywords[:3]],
            "comment": (
                f"方案覆盖 {stats.get('village_count') or '—'} 个需求点，总距离 "
                f"{stats.get('total_distance') or '—'} km，投入 {stats.get('drone_count') or '—'} 架无人机共 "
                f"{stats.get('total_trips') or '—'} 趟；"
                + (f"四维评分均值 {all_scores[i]:.0f} 分。" if all_scores[i] else "")
                + (f"辩论环节发言 {debate.get('message_count')} 次，思辨参与度良好。" if debate.get("message_count") else "")
            ),
        })
    return {"groups": groups, "source": "rule"}


@router.post("/ai-comment")
def ai_comment(req: AiCommentRequest):
    """基于真实方案数据生成 AI 点评（词云/风险/综合点评），失败降级为规则点评"""
    if not req.plan_ids:
        raise HTTPException(status_code=400, detail="plan_ids 不能为空")

    db = SessionLocal()
    try:
        contexts = _gather_plan_context(db, req.plan_ids)
    finally:
        db.close()

    if not contexts:
        raise HTTPException(status_code=404, detail="方案不存在")

    # LLM 可用则走真实点评，否则/失败降级规则点评（免费模型限流常见，重试一次）
    if is_configured():
        try:
            system, user = _build_llm_prompt(contexts)
            content = None
            import time
            for attempt in range(2):
                try:
                    content = llm_chat(system, user, temperature=0.4)
                    break
                except Exception:
                    if attempt == 0:
                        time.sleep(2)
                    else:
                        raise
            if content:
                # 兼容模型偶尔包裹 ```json ``` 的情况
                text = content.strip()
                if text.startswith("```"):
                    text = text.strip("`")
                    if text.startswith("json"):
                        text = text[4:]
                data = json.loads(text)
                if isinstance(data, dict) and data.get("groups"):
                    data["source"] = "llm"
                    return data
        except Exception as e:
            print(f"[Evaluation] LLM 点评失败，降级规则点评: {type(e).__name__}: {e}")

    return _fallback_comment(contexts)
