"""合规性核验 API 路由

教学闭环：学生先自判核验清单 → 服务端复用规则诊断引擎交叉复核 →
差异高亮（学生判 pass 但引擎判 fail）→ 生成参数调整建议 → 回填重新规划。
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.verification import VerificationRecord
from app.services.ai.diagnosis_service import run_rule_diagnosis

router = APIRouter(prefix="/api/path-planning/verification", tags=["合规性核验"])

# ─── 标准核验模板（7 组指标） ───
# engine_key: 引擎可自动核验的关键字分类；None = 需学生定性判断（引擎不复核）
CHECKLIST_TEMPLATE = [
    {
        "group": "空域合规", "icon": "🛫", "items": [
            {"id": "airspace_01", "metric": "航线已规避标注的禁飞区/限飞区", "standard": "《航线规范》§5.2、审定指南§5.2", "engine_key": "airspace"},
            {"id": "airspace_02", "metric": "飞行真高不超过 120m 上限", "standard": "《航线规范》§4.2", "engine_key": None},
            {"id": "airspace_03", "metric": "已确认飞行空域报备/申请流程完成", "standard": "审定指南§2.3、1+X（飞行报备）", "engine_key": None},
        ],
    },
    {
        "group": "气象条件", "icon": "🌤", "items": [
            {"id": "weather_01", "metric": "配送时段风速在机型抗风等级内", "standard": "审定指南§4.3(b)", "engine_key": "weather"},
            {"id": "weather_02", "metric": "已制定降水/突变天气应对预案（备降点/返航策略）", "standard": "审定指南§5.2、附件4", "engine_key": None},
        ],
    },
    {
        "group": "载重匹配", "icon": "⚖️", "items": [
            {"id": "load_01", "metric": "每架无人机单趟实载 ≤ 额定载重", "standard": "京东标准（载重）、审定指南附件4", "engine_key": "overload"},
            {"id": "load_02", "metric": "物资装载考虑重心配平与固定方式", "standard": "《航线规范》附录A、京东初级§1.3", "engine_key": None},
        ],
    },
    {
        "group": "续航能力", "icon": "🔋", "items": [
            {"id": "range_01", "metric": "单趟航线距离 ≤ 无人机有效航程（含安全余量）", "standard": "审定指南§4.2(f)", "engine_key": "range"},
            {"id": "range_02", "metric": "多趟任务间已安排换电/充电时间", "standard": "京东中级§3.3", "engine_key": None},
        ],
    },
    {
        "group": "冷链时限", "icon": "🧊", "items": [
            {"id": "cold_01", "metric": "温控类物资（医药/冷链食品）在时效窗口内送达", "standard": "1+X（物流专项）、冷链运输规范", "engine_key": "cold_chain"},
            {"id": "cold_02", "metric": "温控物资包装满足全程保温要求", "standard": "货物包装规范§4-2", "engine_key": None},
        ],
    },
    {
        "group": "配送时效", "icon": "⏱", "items": [
            {"id": "time_01", "metric": "高优先级需求点（急救/紧急）被优先分配配送", "standard": "1+X（路线规划）、应急响应预案", "engine_key": "priority"},
            {"id": "time_02", "metric": "全部需求点均被覆盖，无遗漏/重复配送", "standard": "审定指南§6.1、需求覆盖检查", "engine_key": "coverage"},
        ],
    },
    {
        "group": "经济性", "icon": "💰", "items": [
            {"id": "econ_01", "metric": "无明显冗余趟次，机队负载均衡", "standard": "京东高级（调度）、经济性评估", "engine_key": "economy"},
            {"id": "econ_02", "metric": "机型数量与任务规模匹配，无过度配置", "standard": "京东标准（机型选择）", "engine_key": None},
        ],
    },
]

# 引擎关键字 → 归组映射（诊断 issue/warning 文本匹配）
ENGINE_KEYWORD_MAP = {
    "overload": ["超载"],
    "range": ["航程"],
    "airspace": ["禁飞", "空域"],
    "weather": ["风速", "气象", "降水", "大风", "天气"],
    "cold_chain": ["冷链", "温控"],
    "priority": ["优先级", "时效"],
    "coverage": ["遗漏", "重复", "覆盖"],
    "economy": ["冗余", "负载不均衡", "利用率", "空驶"],
}


class CheckItemIn(BaseModel):
    id: str
    student_judgment: str = "na"   # pass | fail | na
    remark: str = ""


class CheckRequest(BaseModel):
    task: Dict[str, Any]
    solution: Dict[str, Any]
    checklist: List[CheckItemIn] = []
    plan_record_id: Optional[int] = None


def _strip_marker(msg: str) -> str:
    """去掉诊断消息开头的 ❌⚠️💡 标记"""
    return msg.lstrip("❌⚠️💡 ").strip()


def _match_engine_flag(engine_key: Optional[str], issues: List[str], warnings: List[str]):
    """按关键字把引擎诊断消息归类到指标项，返回 (judgment, reason)"""
    if not engine_key:
        return None, ""
    keywords = ENGINE_KEYWORD_MAP.get(engine_key, [])
    for msg in issues:
        if any(k in msg for k in keywords):
            return "fail", _strip_marker(msg)
    for msg in warnings:
        if any(k in msg for k in keywords):
            return "warn", _strip_marker(msg)
    return "pass", ""


@router.get("/template")
def get_template():
    """下发标准核验模板（7 组指标，引擎可核验项带 engine_key 标识）"""
    return {"groups": CHECKLIST_TEMPLATE}


@router.post("/check")
def submit_check(req: CheckRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """提交核验：服务端跑规则诊断交叉复核 → 差异标记 → 算分落库"""
    try:
        rule = run_rule_diagnosis(req.task, req.solution)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断引擎执行失败: {type(e).__name__}: {e}")

    issues = rule.get("issues", [])
    warnings = rule.get("warnings", [])
    student_map = {c.id: c for c in req.checklist}

    # ─── 合并模板 + 学生判定 + 引擎复核 ───
    merged = []
    verifiable_scores = []
    mismatch_count = 0
    failed_keys = set()

    for group in CHECKLIST_TEMPLATE:
        g_out = {"group": group["group"], "icon": group["icon"], "items": []}
        for item in group["items"]:
            stu = student_map.get(item["id"])
            student_judgment = stu.student_judgment if stu else "na"
            remark = stu.remark if stu else ""

            engine_judgment, engine_reason = _match_engine_flag(item["engine_key"], issues, warnings)

            mismatch = False
            if item["engine_key"] and engine_judgment:
                # 教学评分：一致满分；单侧警告半分；方向相反零分
                if engine_judgment == "fail" and student_judgment == "pass":
                    s, mismatch = 0.0, True
                elif engine_judgment == "warn" and student_judgment == "pass":
                    s = 0.5
                elif student_judgment == "fail" and engine_judgment == "pass":
                    s = 0.5  # 过严误报，给部分分
                elif student_judgment == "na":
                    s = 0.5
                else:
                    s = 1.0
                verifiable_scores.append(s)
                if mismatch:
                    mismatch_count += 1
                    failed_keys.add(item["engine_key"])

            g_out["items"].append({
                **item,
                "student_judgment": student_judgment,
                "remark": remark,
                "engine_judgment": engine_judgment,
                "engine_reason": engine_reason,
                "mismatch": mismatch,
            })
        merged.append(g_out)

    # ─── 得分 / 一致率 / 判定 ───
    score = round((sum(verifiable_scores) / len(verifiable_scores) * 100) if verifiable_scores else 0, 1)
    consistent = sum(1 for s in verifiable_scores if s >= 1.0)
    consistency = round(consistent / len(verifiable_scores) * 100, 1) if verifiable_scores else 0

    if score >= 85 and mismatch_count == 0:
        verdict = "通过"
    elif score >= 60 and mismatch_count <= 3:
        verdict = "有条件通过"
    else:
        verdict = "需整改"

    # ─── 参数调整建议（供前端回填 ACO 参数面板） ───
    param_suggestions = {}
    regen_hints = []
    opt_fail = failed_keys & {"priority", "economy", "cold_chain"}
    hard_fail = failed_keys & {"overload", "range"}
    if opt_fail:
        param_suggestions.update({"max_iterations_delta": 80, "beta_delta": 0.5})
        regen_hints.append("存在时效/经济/冷链类不符项：建议增大迭代次数并提高 β（信息素启发权重），强化路径择优")
    if hard_fail:
        param_suggestions.update({"elite_ants_delta": 2})
        regen_hints.append("存在超载/航程硬约束风险：ACO 参数无法消除，需拆分趟次或更换更大载重/航程机型后再规划")

    record = VerificationRecord(
        user_id=current_user.id,
        plan_record_id=req.plan_record_id,
        checklist=json.dumps(merged, ensure_ascii=False),
        score=score,
        consistency=consistency,
        mismatch_count=mismatch_count,
        verdict=verdict,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "record_id": record.id,
        "score": score,
        "consistency": consistency,
        "mismatch_count": mismatch_count,
        "verdict": verdict,
        "checklist": merged,
        "rule_summary": {
            "issues": issues,
            "warnings": warnings,
            "four_dimensional_scores": rule.get("four_dimensional_scores", {}),
        },
        "param_suggestions": param_suggestions,
        "regen_hints": regen_hints,
    }


@router.get("/records")
def list_records(limit: int = Query(10, ge=1, le=50), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """我的核验历史"""
    records = (
        db.query(VerificationRecord)
        .filter(VerificationRecord.user_id == current_user.id)
        .order_by(VerificationRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "records": [
            {
                "id": r.id,
                "plan_record_id": r.plan_record_id,
                "score": r.score,
                "consistency": r.consistency,
                "mismatch_count": r.mismatch_count,
                "verdict": r.verdict,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            }
            for r in records
        ]
    }


@router.delete("/{record_id}")
def delete_record(record_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除核验记录"""
    record = db.query(VerificationRecord).filter(VerificationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该记录")
    db.delete(record)
    db.commit()
    return {"success": True, "deleted": record_id}
