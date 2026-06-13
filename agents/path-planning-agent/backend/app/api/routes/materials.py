"""物资需求 API 路由"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from app.services.material_service import (
    get_categories,
    get_category_by_id,
    compute_demand_info,
    get_default_case_materials,
    get_case_village,
    CASE_VILLAGE_MATERIALS,
)
from app.core.database import SessionLocal
from app.models.assignment import MaterialAssignment

router = APIRouter(prefix="/api/path-planning/materials", tags=["物资需求"])


# ── Schemas ──

class MaterialItem(BaseModel):
    name: str
    unit_weight: float
    qty: int
    category: Optional[str] = None


class MaterialAssign(BaseModel):
    point_id: int
    point_name: str
    category_ids: List[str]
    custom_items: Optional[List[MaterialItem]] = None


class MaterialAssignBatch(BaseModel):
    assignments: List[MaterialAssign]


# ── Routes ──

@router.get("/categories")
def list_categories():
    """获取所有物资类别（含默认物品列表）"""
    return get_categories()


@router.get("/categories/{cat_id}")
def get_category(cat_id: str):
    cat = get_category_by_id(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="物资类别不存在")
    return cat


@router.post("/compute")
def compute_materials(assign: MaterialAssign):
    """根据物资类别和可选的自定义物品列表计算需求信息"""
    for cid in assign.category_ids:
        if not get_category_by_id(cid):
            raise HTTPException(status_code=400, detail=f"未知物资类别: {cid}")
    custom = None
    if assign.custom_items:
        custom = [item.model_dump() for item in assign.custom_items]
    return compute_demand_info(assign.category_ids, custom)


@router.get("/default-case")
def default_case():
    """获取案例全部村庄的真实物资分配"""
    return get_default_case_materials()


@router.get("/default-case/{village_name}")
def default_case_village(village_name: str):
    result = get_case_village(village_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"案例中无此村庄: {village_name}")
    return result


@router.get("/case-villages")
def case_villages():
    """获取案例村庄名称列表"""
    return list(CASE_VILLAGE_MATERIALS.keys())


# ── 持久化存储 ──

class MaterialAssignmentSave(BaseModel):
    point_id: int
    point_name: str = ""
    category_ids: List[str] = []
    supply_types: Optional[List[str]] = []
    items: Optional[List[Dict]] = None
    total_weight: float = 0
    priority: int = 3
    special_requirements: Optional[str] = ""
    risk_warnings: Optional[str] = ""
    note: Optional[str] = ""


class MaterialAssignmentBatchSave(BaseModel):
    assignments: List[MaterialAssignmentSave]


@router.post("/save")
def save_assignment(assign: MaterialAssignmentSave):
    """保存单个需求点的物资分配到数据库"""
    db = SessionLocal()
    try:
        existing = db.query(MaterialAssignment).filter(
            MaterialAssignment.point_id == assign.point_id
        ).first()
        st_json = json.dumps(assign.supply_types or [], ensure_ascii=False)
        if existing:
            existing.point_name = assign.point_name
            existing.category_ids = json.dumps(assign.category_ids, ensure_ascii=False)
            existing.supply_types = st_json
            existing.items = json.dumps(assign.items, ensure_ascii=False) if assign.items else None
            existing.total_weight = assign.total_weight
            existing.priority = assign.priority
            existing.special_requirements = assign.special_requirements
            existing.risk_warnings = assign.risk_warnings
            existing.note = assign.note
        else:
            record = MaterialAssignment(
                point_id=assign.point_id,
                point_name=assign.point_name,
                category_ids=json.dumps(assign.category_ids, ensure_ascii=False),
                supply_types=st_json,
                items=json.dumps(assign.items, ensure_ascii=False) if assign.items else None,
                total_weight=assign.total_weight,
                priority=assign.priority,
                special_requirements=assign.special_requirements,
                risk_warnings=assign.risk_warnings,
                note=assign.note,
            )
            db.add(record)
        db.commit()
        return {"status": "ok", "point_id": assign.point_id}
    finally:
        db.close()


@router.post("/save-batch")
def save_assignments_batch(batch: MaterialAssignmentBatchSave):
    """批量保存物资分配到数据库"""
    db = SessionLocal()
    try:
        saved = 0
        for assign in batch.assignments:
            existing = db.query(MaterialAssignment).filter(
                MaterialAssignment.point_id == assign.point_id
            ).first()
            st_json = json.dumps(assign.supply_types or [], ensure_ascii=False)
            if existing:
                existing.point_name = assign.point_name
                existing.category_ids = json.dumps(assign.category_ids, ensure_ascii=False)
                existing.supply_types = st_json
                existing.items = json.dumps(assign.items, ensure_ascii=False) if assign.items else None
                existing.total_weight = assign.total_weight
                existing.priority = assign.priority
                existing.special_requirements = assign.special_requirements
                existing.risk_warnings = assign.risk_warnings
                existing.note = assign.note
            else:
                record = MaterialAssignment(
                    point_id=assign.point_id,
                    point_name=assign.point_name,
                    category_ids=json.dumps(assign.category_ids, ensure_ascii=False),
                    supply_types=st_json,
                    items=json.dumps(assign.items, ensure_ascii=False) if assign.items else None,
                    total_weight=assign.total_weight,
                    priority=assign.priority,
                    special_requirements=assign.special_requirements,
                    risk_warnings=assign.risk_warnings,
                    note=assign.note,
                )
                db.add(record)
            saved += 1
        db.commit()
        return {"status": "ok", "saved": saved}
    finally:
        db.close()


@router.get("/saved")
def load_saved_assignments():
    """从数据库加载所有已保存的物资分配"""
    db = SessionLocal()
    try:
        rows = db.query(MaterialAssignment).all()
        result = {}
        for row in rows:
            result[row.point_id] = {
                "point_id": row.point_id,
                "point_name": row.point_name,
                "category_ids": json.loads(row.category_ids) if row.category_ids else [],
                "supply_types": json.loads(row.supply_types) if row.supply_types else [],
                "items": json.loads(row.items) if row.items else [],
                "total_weight": row.total_weight or 0,
                "priority": row.priority or 3,
                "special_requirements": row.special_requirements or "",
                "risk_warnings": row.risk_warnings or "",
                "note": row.note or "",
            }
        return result
    finally:
        db.close()


@router.delete("/saved/{point_id}")
def delete_saved_assignment(point_id: int):
    """删除指定需求点的物资分配"""
    db = SessionLocal()
    try:
        row = db.query(MaterialAssignment).filter(MaterialAssignment.point_id == point_id).first()
        if row:
            db.delete(row)
            db.commit()
        return {"status": "ok"}
    finally:
        db.close()


@router.delete("/saved")
def delete_all_saved_assignments():
    """删除所有物资分配"""
    db = SessionLocal()
    try:
        db.query(MaterialAssignment).delete()
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()
