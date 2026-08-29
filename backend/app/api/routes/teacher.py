"""教师端监控 API（T6 雏形）

- GET /dashboard                全班学生总览（辩论参与度、核验情况、方案/报告产出）
- GET /student/{user_id}/debate-sessions   某学生的辩论会话列表
- GET /debate-session/{session_id}         辩论时间线回放（含教师留言）
- GET /student/{user_id}/verifications     某学生的核验记录（含完整清单）
教师介入留言复用 POST /api/debate/session/{id}/teacher-note。
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, require_teacher
from app.models.user import User
from app.models.debate import DebateSession, DebateMessage
from app.models.verification import VerificationRecord
from app.models.report import ReportRecord
from app.models.optimizer import OptimizationRecord
from app.models.activity_log import ActivityLog

router = APIRouter(prefix="/api/path-planning/teacher", tags=["教师端监控"])

STAGE_NAMES = {
    "hypothesis": "假设提出", "verify": "验证分析",
    "rebut": "反驳交锋", "rebuild": "重构优化", "completed": "闭环完成",
}


@router.get("/dashboard")
def teacher_dashboard(current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    """全班总览：每个学生的辩理论参与、核验质量、产出数量"""
    students = db.query(User).filter(User.role == "student").order_by(User.class_name, User.student_no).all()

    # ── 聚合各业务表（课堂规模 ≤ 百人，直接分组统计）──
    deb_count, deb_last = {}, {}
    for uid, cnt, last in (
        db.query(DebateSession.user_id, func.count(DebateSession.id), func.max(DebateSession.created_at))
        .group_by(DebateSession.user_id).all()
    ):
        deb_count[uid], deb_last[uid] = cnt, last

    ver_rows = (
        db.query(
            VerificationRecord.user_id,
            func.count(VerificationRecord.id),
            func.avg(VerificationRecord.score),
            func.avg(VerificationRecord.consistency),
        )
        .group_by(VerificationRecord.user_id).all()
    )
    ver_count, ver_score, ver_cons = {}, {}, {}
    for uid, cnt, score, cons in ver_rows:
        ver_count[uid] = cnt
        ver_score[uid] = round(score or 0, 1)
        ver_cons[uid] = round(cons or 0, 1)

    plan_count = dict(db.query(OptimizationRecord.user_id, func.count(OptimizationRecord.id)).group_by(OptimizationRecord.user_id).all())
    report_count = dict(db.query(ReportRecord.user_id, func.count(ReportRecord.id)).group_by(ReportRecord.user_id).all())

    items = []
    for s in students:
        items.append({
            "user_id": s.id,
            "username": s.username,
            "student_no": s.student_no or "",
            "class_name": s.class_name or "",
            "group_no": s.group_no or "",
            "plan_count": plan_count.get(s.id, 0),
            "report_count": report_count.get(s.id, 0),
            "verification_count": ver_count.get(s.id, 0),
            "avg_verification_score": ver_score.get(s.id) if s.id in ver_count else None,
            "avg_consistency": ver_cons.get(s.id) if s.id in ver_count else None,
            "debate_session_count": deb_count.get(s.id, 0),
            "last_debate_at": deb_last[s.id].strftime("%m-%d %H:%M") if s.id in deb_last and deb_last[s.id] else None,
        })

    return {
        "students": items,
        "summary": {
            "student_total": len(items),
            "with_verification": sum(1 for i in items if i["verification_count"] > 0),
            "with_debate": sum(1 for i in items if i["debate_session_count"] > 0),
            "class_avg_score": round(sum(i["avg_verification_score"] for i in items if i["avg_verification_score"]) /
                                     max(1, sum(1 for i in items if i["avg_verification_score"])), 1)
            if any(i["avg_verification_score"] for i in items) else None,
        },
    }


@router.get("/student/{user_id}/verifications")
def student_verifications(user_id: int, limit: int = Query(20, ge=1, le=50), current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    """某学生的核验记录（完整清单，用于教学回放）"""
    records = (
        db.query(VerificationRecord)
        .filter(VerificationRecord.user_id == user_id)
        .order_by(VerificationRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "records": [
            {
                "id": r.id,
                "score": r.score,
                "consistency": r.consistency,
                "mismatch_count": r.mismatch_count,
                "verdict": r.verdict,
                "plan_record_id": r.plan_record_id,
                "checklist": json.loads(r.checklist) if r.checklist else [],
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            }
            for r in records
        ]
    }


@router.get("/student/{user_id}/debate-sessions")
def student_debate_sessions(user_id: int, current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    """某学生的辩论会话列表"""
    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    sessions = (
        db.query(DebateSession)
        .filter(DebateSession.user_id == user_id)
        .order_by(DebateSession.created_at.desc())
        .limit(30)
        .all()
    )
    return {
        "student": {"id": student.id, "username": student.username, "group_no": student.group_no or ""},
        "sessions": [
            {
                "id": s.id,
                "group_name": s.group_name,
                "stage": s.stage,
                "stage_name": STAGE_NAMES.get(s.stage, s.stage),
                "status": s.status,
                "message_count": db.query(func.count(DebateMessage.id)).filter(DebateMessage.session_id == s.id).scalar(),
                "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else None,
            }
            for s in sessions
        ],
    }


@router.get("/debate-session/{session_id}")
def debate_replay(session_id: int, current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    """辩论时间线回放：完整消息流 + 各消息的评判维度"""
    session = db.query(DebateSession).filter(DebateSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(DebateMessage)
        .filter(DebateMessage.session_id == session_id)
        .order_by(DebateMessage.id.asc())
        .all()
    )
    return {
        "session": {
            "id": session.id,
            "user_id": session.user_id,
            "group_name": session.group_name,
            "stage": session.stage,
            "status": session.status,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M") if session.created_at else None,
        },
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "stage": m.stage,
                "challenge_type": getattr(m, "challenge_type", None),
                "judgment_dimensions": m.judgment_dimensions if isinstance(m.judgment_dimensions, list) else [],
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else None,
            }
            for m in messages
        ],
    }


# ─── 交互日志（T8）───

ACTION_META = {
    "方案生成": {"icon": "🧭", "color": "#409eff"},
    "报告生成": {"icon": "📄", "color": "#67c23a"},
    "择优决策": {"icon": "🏆", "color": "#e6a23c"},
    "合规核验": {"icon": "✅", "color": "#409eff"},
    "反向质询": {"icon": "💬", "color": "#f56c6c"},
    "派生重生成": {"icon": "↻", "color": "#909399"},
}


@router.get("/student/{user_id}/activities")
def student_activities(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """某学生的全流程学习时间线（交互日志）"""
    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        .limit(limit)
        .all()
    )

    items = []
    for lg in logs:
        meta = ACTION_META.get(lg.action, {"icon": "•", "color": "#909399"})
        detail = {}
        if lg.payload:
            try:
                detail = json.loads(lg.payload)
            except Exception:
                detail = {}
        # 生成一行人类可读摘要
        summary = _activity_summary(lg.action, detail)
        items.append({
            "id": lg.id,
            "action": lg.action,
            "icon": meta["icon"],
            "color": meta["color"],
            "summary": summary,
            "payload": detail,
            "plan_record_id": lg.plan_record_id,
            "created_at": lg.created_at.strftime("%m-%d %H:%M") if lg.created_at else None,
        })

    # 动作分布统计（供评估参考）
    stats = dict(
        db.query(ActivityLog.action, func.count(ActivityLog.id))
        .filter(ActivityLog.user_id == user_id)
        .group_by(ActivityLog.action)
        .all()
    )

    return {
        "student": {"id": student.id, "username": student.username, "group_no": student.group_no or ""},
        "activities": items,
        "stats": stats,
    }


def _activity_summary(action: str, d: dict) -> str:
    """把 payload 摘要转成一句话描述"""
    if action == "方案生成":
        dist = d.get("total_distance")
        trips = d.get("total_trips")
        if dist is not None:
            return f"生成航线方案（总距离 {dist:.0f}m · {trips} 趟次）"
        return "生成航线方案"
    if action == "报告生成":
        return f"生成方案报告「{d.get('filename', '')}」"
    if action == "择优决策":
        return f"选定最终方案「{d.get('filename', '')}」"
    if action == "合规核验":
        return f"提交核验：{d.get('score', '?')} 分 · {d.get('verdict', '')}（差异 {d.get('mismatch_count', 0)} 项）"
    if action == "反向质询":
        if d.get("event") == "创建会话":
            return "开启反向质询会话"
        dims = d.get("dimensions") or []
        dim_txt = f"，评判维度：{'/'.join(dims)}" if dims else ""
        return f"提交辩论陈述（{d.get('stage', '')} 阶段{dim_txt}）"
    if action == "派生重生成":
        return "从报告回填参数重新规划"
    return json.dumps(d, ensure_ascii=False) if d else action
