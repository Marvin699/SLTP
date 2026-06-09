import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import func as sql_func

from app.core.database import SessionLocal
from app.models.score_session import ScoreSession, ScoreRecord
from app.schemas.score_session import (
    ScoreSessionCreate, ScoreSessionResponse,
    ScoreSubmitRequest, GroupSummary
)

router = APIRouter(prefix="/api/score", tags=["评分会话"])

DEFAULT_GROUPS = ["逐日组", "揽星组", "御风组", "长空组", "凌云组", "巡天组"]

# 三个环节及其专属评分维度（统一4维度+权重）
SECTION_CONFIG = {
    "section1": {
        "id": "section1",
        "name": "环节一：运输方案汇报与知识深化",
        "short_name": "方案汇报",
        "time_range": "0-10min",
        "description": "小组汇报运输方案，教师/企业导师提问，AI词云与风险分析",
        "dimensions": ["方案完整性", "表达展示", "操作规范", "团队配合"],
        "weights": {"方案完整性": 0.35, "表达展示": 0.35, "操作规范": 0.15, "团队配合": 0.15},
    },
    "section2": {
        "id": "section2",
        "name": "环节二：无预案应急推演",
        "short_name": "应急推演",
        "time_range": "10-20min",
        "description": "突发应急场景，使用路径规划智能体进行无预案推演",
        "dimensions": ["决策速度", "方案可行性", "风险评估", "团队配合"],
        "weights": {"决策速度": 0.35, "方案可行性": 0.35, "风险评估": 0.15, "团队配合": 0.15},
    },
    "section3": {
        "id": "section3",
        "name": "环节三：飞行前准备应急演练比拼",
        "short_name": "应急演练",
        "time_range": "21-36min",
        "description": "限时飞行前检查、双电转单电操作、团队协作应急演练",
        "dimensions": ["安全性", "操作规范性", "用时效率", "团队配合"],
        "weights": {"安全性": 0.35, "操作规范性": 0.35, "用时效率": 0.15, "团队配合": 0.15},
    },
}


def _json_loads(val, default=None):
    if val is None:
        return default
    if isinstance(val, str):
        return json.loads(val)
    return val


def _calc_weighted_avg(dim_scores, weights):
    """根据维度分数和权重计算加权平均分"""
    total = 0
    weight_sum = 0
    for dim, score in dim_scores.items():
        w = weights.get(dim, 0)
        total += score * w
        weight_sum += w
    return round(total / weight_sum, 2) if weight_sum > 0 else 0


@router.get("/sections")
def list_sections():
    """获取三个环节的配置信息"""
    return list(SECTION_CONFIG.values())


@router.get("/sessions")
def list_sessions(section_id: str = None):
    """获取所有评分会话，可按环节筛选"""
    db = SessionLocal()
    try:
        query = db.query(ScoreSession)
        if section_id:
            query = query.filter(ScoreSession.section_id == section_id)
        sessions = query.order_by(ScoreSession.section_id, ScoreSession.created_at).all()
        result = []
        for s in sessions:
            sec = SECTION_CONFIG.get(s.section_id, {})
            result.append({
                "id": s.id,
                "token": s.token,
                "section_id": s.section_id,
                "section_name": sec.get("short_name", s.section_id),
                "title": s.title,
                "groups": _json_loads(s.groups, DEFAULT_GROUPS),
                "dimensions": _json_loads(s.dimensions, []),
                "weights": sec.get("weights", {}),
                "start_time": s.start_time,
                "end_time": s.end_time,
                "is_active": s.is_active,
                "created_at": s.created_at,
            })
        return result
    finally:
        db.close()


@router.post("/sessions", response_model=ScoreSessionResponse)
def create_session(data: ScoreSessionCreate):
    """创建评分会话（根据环节自动填充维度）"""
    section = SECTION_CONFIG.get(data.section_id)
    if not section:
        raise HTTPException(status_code=400, detail=f"无效的环节ID: {data.section_id}")

    db = SessionLocal()
    try:
        token = uuid.uuid4().hex[:12]
        dimensions = data.dimensions or section["dimensions"]
        groups = data.groups or DEFAULT_GROUPS

        session = ScoreSession(
            token=token,
            section_id=data.section_id,
            title=data.title or section["name"],
            groups=json.dumps(groups, ensure_ascii=False),
            dimensions=json.dumps(dimensions, ensure_ascii=False),
            start_time=data.start_time,
            end_time=data.end_time,
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return ScoreSessionResponse(
            id=session.id, token=session.token, section_id=session.section_id,
            title=session.title, groups=_json_loads(session.groups, DEFAULT_GROUPS),
            dimensions=_json_loads(session.dimensions, []),
            weights=section.get("weights", {}),
            start_time=session.start_time, end_time=session.end_time,
            is_active=session.is_active, created_at=session.created_at,
        )
    finally:
        db.close()


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int):
    """停用评分会话（链接失效，打分数据保留，成绩总览不受影响）"""
    db = SessionLocal()
    try:
        session = db.query(ScoreSession).filter(ScoreSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        session.is_active = False
        db.commit()
        return {"message": "链接已停用，已有打分数据保留"}
    finally:
        db.close()


@router.delete("/clear/{section_id}")
def clear_section_scores(section_id: str):
    """清空某环节下所有打分记录（保留评分链接）"""
    sec = SECTION_CONFIG.get(section_id)
    if not sec:
        raise HTTPException(status_code=400, detail=f"无效的环节ID: {section_id}")
    db = SessionLocal()
    try:
        sessions = db.query(ScoreSession).filter(ScoreSession.section_id == section_id).all()
        total_deleted = 0
        for s in sessions:
            count = db.query(ScoreRecord).filter(ScoreRecord.session_token == s.token).delete()
            total_deleted += count
        db.commit()
        return {"message": f"已清空 {len(sessions)} 个链接的打分数据，共删除 {total_deleted} 条记录"}
    finally:
        db.close()


@router.get("/session/{token}")
def get_session_by_token(token: str):
    """通过token获取会话信息（公开打分页面用）"""
    db = SessionLocal()
    try:
        session = db.query(ScoreSession).filter(ScoreSession.token == token).first()
        if not session:
            raise HTTPException(status_code=404, detail="链接无效")
        if not session.is_active:
            raise HTTPException(status_code=403, detail="该评分链接已停用")
        now = datetime.now()
        if session.end_time and now > session.end_time:
            raise HTTPException(status_code=403, detail="该评分链接已过期")

        sec = SECTION_CONFIG.get(session.section_id, {})
        return {
            "token": session.token,
            "section_id": session.section_id,
            "section_name": sec.get("name", session.section_id),
            "title": session.title,
            "groups": _json_loads(session.groups, DEFAULT_GROUPS),
            "dimensions": _json_loads(session.dimensions, []),
            "weights": sec.get("weights", {}),
            "start_time": session.start_time,
            "end_time": session.end_time,
        }
    finally:
        db.close()


@router.post("/submit")
def submit_scores(data: ScoreSubmitRequest):
    """提交打分"""
    db = SessionLocal()
    try:
        session = db.query(ScoreSession).filter(ScoreSession.token == data.session_token).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        if not session.is_active:
            raise HTTPException(status_code=403, detail="该评分链接已停用")

        now = datetime.now()
        if session.end_time and now > session.end_time:
            raise HTTPException(status_code=403, detail="该评分链接已过期，无法提交")

        # 检查是否已提交（同一角色+同一会话只能提交一次）
        existing = db.query(ScoreRecord).filter(
            ScoreRecord.session_token == data.session_token,
            ScoreRecord.scorer_role == data.scorer_role,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"该角色在该环节已提交过评分")

        # 批量插入
        records = []
        for item in data.scores:
            record = ScoreRecord(
                session_token=data.session_token,
                scorer_role=data.scorer_role,
                scorer_name=data.scorer_name,
                group_id=item.group_id,
                dimension=item.dimension,
                score=max(0, min(100, item.score)),
            )
            records.append(record)
        db.add_all(records)
        db.commit()
        return {"message": "评分提交成功", "count": len(records)}
    finally:
        db.close()


@router.get("/summary/{token}")
def get_summary(token: str):
    """获取会话评分汇总"""
    db = SessionLocal()
    try:
        session = db.query(ScoreSession).filter(ScoreSession.token == token).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        groups = _json_loads(session.groups, DEFAULT_GROUPS)
        dimensions = _json_loads(session.dimensions, [])
        sec = SECTION_CONFIG.get(session.section_id, {})
        weights = sec.get("weights", {})

        records = db.query(ScoreRecord).filter(ScoreRecord.session_token == token).all()

        # 按小组+维度聚合
        score_map = {}
        for r in records:
            key = (r.group_id, r.dimension)
            if key not in score_map:
                score_map[key] = []
            score_map[key].append(r.score)

        # 计算各小组各维度平均分
        group_summaries = []
        for group in groups:
            dim_scores = {}
            total_scores = []
            for dim in dimensions:
                scores = score_map.get((group, dim), [])
                avg = round(sum(scores) / len(scores), 2) if scores else 0
                dim_scores[dim] = avg
                total_scores.extend(scores)
            total_avg = round(sum(total_scores) / len(total_scores), 2) if total_scores else 0
            weighted_avg = _calc_weighted_avg(dim_scores, weights)
            scorer_count = len(set(r.scorer_role for r in records if r.group_id == group))
            group_summaries.append({
                "group_id": group,
                "dimension_scores": dim_scores,
                "total_avg": total_avg,
                "weighted_avg": weighted_avg,
                "score_count": scorer_count,
            })

        group_summaries.sort(key=lambda x: x["total_avg"], reverse=True)

        scorers = list(set(r.scorer_role for r in records))

        return {
            "section_id": session.section_id,
            "section_name": sec.get("name", session.section_id),
            "title": session.title,
            "groups": group_summaries,
            "dimensions": dimensions,
            "weights": weights,
            "total_scorers": len(scorers),
            "scorer_names": scorers,
        }
    finally:
        db.close()


@router.get("/scorer-status/{token}")
def get_scorer_status(token: str):
    """查询各打分角色的提交状态"""
    db = SessionLocal()
    try:
        records = db.query(ScoreRecord).filter(ScoreRecord.session_token == token).all()
        scorers = {}
        for r in records:
            if r.scorer_role not in scorers:
                scorers[r.scorer_role] = {"role": r.scorer_role, "submitted_at": r.created_at}
        return {"scorers": list(scorers.values())}
    finally:
        db.close()


@router.get("/dashboard/{section_id}")
def get_dashboard(section_id: str):
    """获取某环节的全组成绩仪表盘数据（聚合该环节下所有会话的打分）"""
    sec = SECTION_CONFIG.get(section_id)
    if not sec:
        raise HTTPException(status_code=400, detail=f"无效的环节ID: {section_id}")

    db = SessionLocal()
    try:
        sessions = db.query(ScoreSession).filter(ScoreSession.section_id == section_id).all()
        dimensions = sec["dimensions"]
        weights = sec["weights"]

        # 聚合该环节下所有会话的打分记录
        all_records = []
        for s in sessions:
            records = db.query(ScoreRecord).filter(ScoreRecord.session_token == s.token).all()
            all_records.extend(records)

        if not all_records:
            return {
                "section_id": section_id,
                "section_name": sec["name"],
                "dimensions": dimensions,
                "weights": weights,
                "groups": [],
                "total_scorers": 0,
                "scorer_names": [],
            }

        # 按小组+维度聚合平均分
        score_map = {}
        for r in all_records:
            key = (r.group_id, r.dimension)
            if key not in score_map:
                score_map[key] = []
            score_map[key].append(r.score)

        group_summaries = []
        for group in DEFAULT_GROUPS:
            dim_scores = {}
            total_scores = []
            for dim in dimensions:
                scores = score_map.get((group, dim), [])
                avg = round(sum(scores) / len(scores), 2) if scores else 0
                dim_scores[dim] = avg
                total_scores.extend(scores)
            total_avg = round(sum(total_scores) / len(total_scores), 2) if total_scores else 0
            weighted_avg = _calc_weighted_avg(dim_scores, weights)
            scorer_count = len(set(
                r.scorer_role for r in all_records if r.group_id == group
            ))
            group_summaries.append({
                "group_id": group,
                "dimension_scores": dim_scores,
                "total_avg": total_avg,
                "weighted_avg": weighted_avg,
                "score_count": scorer_count,
            })

        # 按平均分排序并附加排名
        group_summaries.sort(key=lambda x: x["total_avg"], reverse=True)
        for i, g in enumerate(group_summaries):
            g["rank"] = i + 1

        scorers = list(set(r.scorer_role for r in all_records))

        return {
            "section_id": section_id,
            "section_name": sec["name"],
            "dimensions": dimensions,
            "weights": weights,
            "groups": group_summaries,
            "total_scorers": len(scorers),
            "scorer_names": scorers,
        }
    finally:
        db.close()


@router.get("/overview")
def get_overview():
    """获取所有环节的整体概览（仪表盘用）"""
    db = SessionLocal()
    try:
        result = {}
        for sec_id, sec_cfg in SECTION_CONFIG.items():
            sessions = db.query(ScoreSession).filter(ScoreSession.section_id == sec_id).all()
            all_records = []
            for s in sessions:
                records = db.query(ScoreRecord).filter(ScoreRecord.session_token == s.token).all()
                all_records.extend(records)

            scorers = list(set(r.scorer_role for r in all_records))
            session_count = len(sessions)
            active_count = sum(1 for s in sessions if s.is_active)

            result[sec_id] = {
                "section_id": sec_id,
                "section_name": sec_cfg["name"],
                "short_name": sec_cfg["short_name"],
                "dimensions": sec_cfg["dimensions"],
                "weights": sec_cfg["weights"],
                "session_count": session_count,
                "active_session_count": active_count,
                "total_scorers": len(scorers),
                "scorer_names": scorers,
            }
        return result
    finally:
        db.close()
