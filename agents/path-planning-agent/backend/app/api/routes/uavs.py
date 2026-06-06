"""模块三：无人机选择 API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.uav_service import (
    get_all_brands,
    get_all_models,
    get_model_by_id,
    update_model,
    assess_selection,
    assess_with_llm,
)
from app.services.llm_service import is_configured
from app.core.database import SessionLocal
from app.models.ai_result import AiSelectionResult

router = APIRouter(prefix="/api/path-planning/uavs", tags=["模块三-无人机选择"])


class UAVSelection(BaseModel):
    model_id: str
    quantity: int = 1


class DemandPoint(BaseModel):
    name: str
    total_weight: float = 0
    priority: int = 3
    special_requirements: Optional[str] = ""
    distance_km: float = 0


class AssessRequest(BaseModel):
    selections: list[UAVSelection]
    demands: list[DemandPoint]


class UAVParamUpdate(BaseModel):
    max_payload: Optional[float] = None
    range_km: Optional[float] = None
    max_speed: Optional[float] = None
    cabin_volume: Optional[float] = None
    wind_resist: Optional[int] = None
    ip_rating: Optional[str] = None
    drop_mode: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    raw_params: Optional[str] = None
    features: Optional[list] = None
    suitable_for: Optional[list] = None


@router.get("/brands")
def list_brands():
    """获取所有无人机品牌"""
    return get_all_brands()


@router.get("/models")
def list_models():
    """获取所有无人机型号（从数据库读取，支持编辑后的最新数据）"""
    return get_all_models()


@router.get("/models/{model_id}")
def get_model(model_id: str):
    """获取单个无人机型号详情"""
    model = get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="未找到该无人机型号")
    return model


@router.put("/models/{model_id}")
def update_uav_model(model_id: str, data: UAVParamUpdate):
    """更新无人机型号参数（实时保存到数据库）"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的字段")
    result = update_model(model_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="未找到该无人机型号")
    return result


@router.get("/llm-status")
def llm_status():
    """检查大模型是否已配置"""
    return {"configured": is_configured()}


@router.post("/assess")
def assess(req: AssessRequest):
    """规则引擎评估（使用数据库中的最新无人机参数）"""
    if not req.selections:
        raise HTTPException(status_code=400, detail="请至少选择一种无人机")
    if not req.demands:
        raise HTTPException(status_code=400, detail="请先设置需求点物资信息")

    selections = [s.model_dump() for s in req.selections]
    demands = [d.model_dump() for d in req.demands]

    result = assess_selection(selections, demands)
    result["llm_used"] = False
    return result


@router.post("/assess-ai")
def assess_ai():
    """AI 智能选型（调用Agent，读取任务配置信息.md）"""
    if not is_configured():
        raise HTTPException(status_code=400, detail="未配置大模型API Key，请在 .env 中设置 LLM_API_KEY")
    try:
        result = assess_with_llm()
        # 自动保存到数据库
        db = SessionLocal()
        try:
            record = AiSelectionResult(
                raw_text=result.get("raw_text", ""),
                elapsed_seconds=result.get("elapsed_seconds", 0),
                model_used=result.get("model_used", ""),
            )
            db.add(record)
            db.commit()
            result["saved_id"] = record.id
        except Exception:
            pass
        finally:
            db.close()
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI选型异常: {type(e).__name__}: {str(e)}")


@router.get("/ai-results")
def list_ai_results():
    """获取所有已保存的 AI 选型结果（按时间倒序）"""
    db = SessionLocal()
    try:
        rows = db.query(AiSelectionResult).order_by(AiSelectionResult.created_at.desc()).all()
        return [
            {
                "id": row.id,
                "raw_text": row.raw_text,
                "elapsed_seconds": row.elapsed_seconds,
                "model_used": row.model_used,
                "created_at": row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/ai-results/{result_id}")
def get_ai_result(result_id: int):
    """获取单条 AI 选型结果"""
    db = SessionLocal()
    try:
        row = db.query(AiSelectionResult).filter(AiSelectionResult.id == result_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="未找到该结果")
        return {
            "id": row.id,
            "raw_text": row.raw_text,
            "elapsed_seconds": row.elapsed_seconds,
            "model_used": row.model_used,
            "created_at": row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
        }
    finally:
        db.close()


@router.delete("/ai-results/{result_id}")
def delete_ai_result(result_id: int):
    """删除单条 AI 选型结果"""
    db = SessionLocal()
    try:
        row = db.query(AiSelectionResult).filter(AiSelectionResult.id == result_id).first()
        if row:
            db.delete(row)
            db.commit()
        return {"status": "ok"}
    finally:
        db.close()
