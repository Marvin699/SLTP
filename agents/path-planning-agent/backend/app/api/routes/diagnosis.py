"""模块五：方案诊断 API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.ai.diagnosis_service import diagnose_solution, run_rule_diagnosis, run_ai_diagnosis
from app.core.database import SessionLocal
from app.models.diagnosis import DiagnosisRecord
from datetime import datetime

router = APIRouter(prefix="/api/path-planning/diagnosis", tags=["模块五-方案诊断"])


class DiagnosisRequest(BaseModel):
    task: Dict[str, Any]
    solution: Dict[str, Any]


class DiagnosisResult(BaseModel):
    feasible: bool
    rule_report: Optional[Dict[str, Any]]
    ai_report: Optional[str]
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    score: float
    four_dimensional_scores: Dict[str, float]
    task_summary: Dict[str, Any]
    diagnosis_mode: str
    created_at: Optional[str] = None


@router.post("/run", response_model=DiagnosisResult)
def run_diagnosis(req: DiagnosisRequest):
    """
    执行方案诊断（同时执行规则诊断和AI诊断）
    
    请求体:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
    
    返回:
        诊断结果（可行性、问题列表、警告、建议、评分、AI报告）
    """
    return _run_diagnosis_internal(req, mode="both")


@router.post("/rule", response_model=DiagnosisResult)
def run_rule_only_diagnosis(req: DiagnosisRequest):
    """
    仅执行规则诊断（不调用AI，速度快）
    
    请求体:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
    
    返回:
        规则诊断结果（可行性、问题列表、警告、建议、四维评分）
    """
    return _run_diagnosis_internal(req, mode="rule")


@router.get("/test")
def test_endpoint():
    """测试端点"""
    return {
        "message": "API is working",
        "four_dimensional_scores": {
            "safety": 85,
            "timeliness": 75,
            "economy": 90,
            "feasibility": 95
        }
    }


@router.post("/ai", response_model=DiagnosisResult)
def run_ai_only_diagnosis(req: DiagnosisRequest):
    """
    仅执行AI诊断（基于任务配置信息.md）
    
    请求体:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
    
    返回:
        AI诊断结果（AI生成的诊断报告）
    """
    return _run_diagnosis_internal(req, mode="ai")


def _run_diagnosis_internal(req: DiagnosisRequest, mode: str = "both"):
    """
    内部诊断执行函数
    
    参数:
        req: 诊断请求
        mode: 诊断模式（"rule" - 仅规则, "ai" - 仅AI, "both" - 两者都执行）
    
    返回:
        诊断结果
    """
    if not req.task.get("demand_points"):
        raise HTTPException(status_code=400, detail="任务必须包含需求点")
    if not req.task.get("uavs"):
        raise HTTPException(status_code=400, detail="任务必须包含至少一架无人机")
    if not req.solution:
        raise HTTPException(status_code=400, detail="必须提供方案数据")
    
    try:
        if mode == "rule":
            result = run_rule_diagnosis(req.task, req.solution)
        elif mode == "ai":
            result = run_ai_diagnosis(req.task, req.solution)
        else:
            result = diagnose_solution(req.task, req.solution)
        
        result["created_at"] = datetime.now().isoformat()
        result["diagnosis_mode"] = mode
        
        # 保存诊断记录到数据库
        db = SessionLocal()
        four_d_scores = result.get("four_dimensional_scores", {})
        record = DiagnosisRecord(
            task_config=str(req.task),
            solution_data=str(req.solution),
            report=str(result),
            score=result["score"],
            issues_count=len(result["issues"]),
            warnings_count=len(result["warnings"]),
            diagnosis_mode=mode,
            safety_score=four_d_scores.get("safety", 0),
            timeliness_score=four_d_scores.get("timeliness", 0),
            economy_score=four_d_scores.get("economy", 0),
            feasibility_score=four_d_scores.get("feasibility", 0),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        db.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {type(e).__name__}: {str(e)}")


@router.get("/history")
def get_diagnosis_history(limit: int = 10):
    """
    获取诊断历史记录
    
    参数:
        limit: 返回记录数量（默认10条）
    
    返回:
        诊断记录列表
    """
    try:
        db = SessionLocal()
        records = db.query(DiagnosisRecord).order_by(
            DiagnosisRecord.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for record in records:
            result.append({
                "id": record.id,
                "score": record.score,
                "issues_count": record.issues_count,
                "warnings_count": record.warnings_count,
                "diagnosis_mode": record.diagnosis_mode,
                "safety_score": record.safety_score,
                "timeliness_score": record.timeliness_score,
                "economy_score": record.economy_score,
                "feasibility_score": record.feasibility_score,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            })
        
        db.close()
        return {"records": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/{record_id}")
def get_diagnosis_detail(record_id: int):
    """
    获取单个诊断记录详情
    
    参数:
        record_id: 记录ID
    
    返回:
        诊断记录详情
    """
    try:
        db = SessionLocal()
        record = db.query(DiagnosisRecord).filter(DiagnosisRecord.id == record_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="记录不存在")
        
        result = {
            "id": record.id,
            "task_config": record.task_config,
            "solution_data": record.solution_data,
            "report": record.report,
            "score": record.score,
            "issues_count": record.issues_count,
            "warnings_count": record.warnings_count,
            "diagnosis_mode": record.diagnosis_mode,
            "safety_score": record.safety_score,
            "timeliness_score": record.timeliness_score,
            "economy_score": record.economy_score,
            "feasibility_score": record.feasibility_score,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        
        db.close()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记录详情失败: {str(e)}")


@router.delete("/{record_id}")
def delete_diagnosis(record_id: int):
    """
    删除诊断记录
    
    参数:
        record_id: 记录ID
    
    返回:
        删除结果
    """
    try:
        db = SessionLocal()
        record = db.query(DiagnosisRecord).filter(DiagnosisRecord.id == record_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="记录不存在")
        
        db.delete(record)
        db.commit()
        db.close()
        
        return {"success": True, "message": "记录已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除记录失败: {str(e)}")