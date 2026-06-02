"""模块四：路径规划 API 路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.optimizer.optimizer_service import run_optimizer
from app.services.optimizer.algorithms.aco.solver import get_default_params
from app.services.optimizer.models.task_model import parse_task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.engine.distance_matrix import build_distance_matrix
from app.services.optimizer.algorithms.aco.colony import solve_with_aco
from app.services.optimizer.outputs.excel_exporter import export_excel
from app.core.database import SessionLocal
from app.models.optimizer import OptimizationRecord
import json
from datetime import datetime

router = APIRouter(prefix="/api/optimizer", tags=["模块四-路径规划"])


class OptimizeRequest(BaseModel):
    task: Dict[str, Any]
    aco_params: Optional[Dict[str, Any]] = None


class DefaultParamsRequest(BaseModel):
    task: Dict[str, Any]


@router.post("/run")
def run_optimize(req: OptimizeRequest):
    """
    运行路径优化。

    请求体:
        task: 任务 JSON（包含 depot、demand_points、distance_matrix、uavs）
        aco_params: ACO 参数（可选，不传则使用默认智能参数）

    返回:
        优化结果（summary、route_table、village_table、drone_table、geojson）
    """
    if not req.task.get("demand_points"):
        raise HTTPException(status_code=400, detail="任务必须包含需求点")
    if not req.task.get("uavs"):
        raise HTTPException(status_code=400, detail="任务必须包含至少一架无人机")

    try:
        result = run_optimizer(req.task, req.aco_params)
        
        # 保存优化记录到数据库
        try:
            db = SessionLocal()
            summary = result.get("summary", {})
            record = OptimizationRecord(
                task_config=json.dumps(req.task, ensure_ascii=False),
                solution_data=json.dumps(result, ensure_ascii=False),
                aco_params=json.dumps(req.aco_params, ensure_ascii=False) if req.aco_params else None,
                summary=json.dumps(summary, ensure_ascii=False),
                total_distance=summary.get("total_distance", 0),
                total_energy=summary.get("total_energy", 0),
                total_trips=summary.get("total_trips", 0),
                village_count=summary.get("village_count", 0),
                drone_count=summary.get("drone_count", 0),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
        except Exception as e:
            print(f"[Optimizer] 保存记录失败: {e}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路径优化失败: {type(e).__name__}: {str(e)}")


@router.post("/params/default")
def get_default(req: DefaultParamsRequest):
    """获取默认 ACO 参数"""
    try:
        task = parse_task(req.task)
        params = get_default_params(task)
        return params
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/excel")
def export_excel_endpoint(req: OptimizeRequest):
    """
    导出 Excel 运输汇总（4个Sheet）。

    返回: Excel 文件流
    """
    if not req.task.get("demand_points"):
        raise HTTPException(status_code=400, detail="任务必须包含需求点")

    try:
        task = parse_task(req.task)
        aco_params = req.aco_params or get_default_params(task)
        distance_matrix = build_distance_matrix(task)
        solution = solve_with_aco(task, aco_params, distance_matrix)
        excel_bytes = export_excel(task, solution)

        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=transport_plan.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {type(e).__name__}: {str(e)}")


# ─── 历史记录 CRUD ───

@router.get("/history")
def get_optimization_history(limit: int = 20):
    """
    获取路径规划历史记录
    
    参数:
        limit: 返回记录数量（默认20条）
    
    返回:
        优化记录列表
    """
    try:
        db = SessionLocal()
        records = db.query(OptimizationRecord).order_by(
            OptimizationRecord.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for record in records:
            result.append({
                "id": record.id,
                "total_distance": record.total_distance,
                "total_energy": record.total_energy,
                "total_trips": record.total_trips,
                "village_count": record.village_count,
                "drone_count": record.drone_count,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            })
        
        db.close()
        return {"records": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/{record_id}")
def get_optimization_detail(record_id: int):
    """
    获取单个优化记录详情
    
    参数:
        record_id: 记录ID
    
    返回:
        优化记录详情（包含完整方案数据）
    """
    try:
        db = SessionLocal()
        record = db.query(OptimizationRecord).filter(OptimizationRecord.id == record_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="记录不存在")
        
        result = {
            "id": record.id,
            "task_config": json.loads(record.task_config) if record.task_config else None,
            "solution_data": json.loads(record.solution_data) if record.solution_data else None,
            "aco_params": json.loads(record.aco_params) if record.aco_params else None,
            "summary": json.loads(record.summary) if record.summary else None,
            "total_distance": record.total_distance,
            "total_energy": record.total_energy,
            "total_trips": record.total_trips,
            "village_count": record.village_count,
            "drone_count": record.drone_count,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        
        db.close()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记录详情失败: {str(e)}")


@router.delete("/{record_id}")
def delete_optimization(record_id: int):
    """
    删除优化记录
    
    参数:
        record_id: 记录ID
    
    返回:
        删除结果
    """
    try:
        db = SessionLocal()
        record = db.query(OptimizationRecord).filter(OptimizationRecord.id == record_id).first()
        
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
