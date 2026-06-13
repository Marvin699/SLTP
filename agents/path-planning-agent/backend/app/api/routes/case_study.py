"""案例管理 - 案例管理 API"""
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.case_study import CaseStudy

router = APIRouter(prefix="/api/path-planning/case", tags=["教学管理-案例管理"])


class CaseStudyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    center_data: dict
    demand_points: list
    material_data: Optional[dict] = None
    solution_data: Optional[dict] = None
    is_default: bool = False


class CaseStudyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    center_data: Optional[dict] = None
    demand_points: Optional[list] = None
    material_data: Optional[dict] = None
    solution_data: Optional[dict] = None
    is_default: Optional[bool] = None


class CaseStudyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    center_data: dict
    demand_points: list
    material_data: Optional[dict]
    solution_data: Optional[dict]
    is_default: bool
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/studies", response_model=List[CaseStudyResponse])
def get_case_studies(db: Session = Depends(get_db)):
    """获取所有案例"""
    cases = db.query(CaseStudy).filter(CaseStudy.is_active == True).order_by(
        CaseStudy.is_default.desc(),
        CaseStudy.created_at.desc()
    ).all()
    
    result = []
    for case in cases:
        result.append({
            "id": case.id,
            "name": case.name,
            "description": case.description,
            "center_data": json.loads(case.center_data),
            "demand_points": json.loads(case.demand_points),
            "material_data": json.loads(case.material_data) if case.material_data else None,
            "solution_data": json.loads(case.solution_data) if case.solution_data else None,
            "is_default": case.is_default,
            "is_active": case.is_active,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        })
    return result


@router.get("/studies/{case_id}", response_model=CaseStudyResponse)
def get_case_study(case_id: int, db: Session = Depends(get_db)):
    """获取单个案例详情"""
    case = db.query(CaseStudy).filter(CaseStudy.id == case_id, CaseStudy.is_active == True).first()
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    return {
        "id": case.id,
        "name": case.name,
        "description": case.description,
        "center_data": json.loads(case.center_data),
        "demand_points": json.loads(case.demand_points),
        "material_data": json.loads(case.material_data) if case.material_data else None,
        "solution_data": json.loads(case.solution_data) if case.solution_data else None,
        "is_default": case.is_default,
        "is_active": case.is_active,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
    }


@router.post("/studies", response_model=CaseStudyResponse)
def create_case_study(case: CaseStudyCreate, db: Session = Depends(get_db)):
    """创建新案例"""
    if case.is_default:
        db.query(CaseStudy).update({CaseStudy.is_default: False})
    
    db_case = CaseStudy(
        name=case.name,
        description=case.description,
        center_data=json.dumps(case.center_data, ensure_ascii=False),
        demand_points=json.dumps(case.demand_points, ensure_ascii=False),
        material_data=json.dumps(case.material_data, ensure_ascii=False) if case.material_data else None,
        solution_data=json.dumps(case.solution_data, ensure_ascii=False) if case.solution_data else None,
        is_default=case.is_default,
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    return {
        "id": db_case.id,
        "name": db_case.name,
        "description": db_case.description,
        "center_data": case.center_data,
        "demand_points": case.demand_points,
        "material_data": case.material_data,
        "solution_data": case.solution_data,
        "is_default": db_case.is_default,
        "is_active": db_case.is_active,
        "created_at": db_case.created_at.isoformat(),
        "updated_at": db_case.updated_at.isoformat(),
    }


@router.put("/studies/{case_id}", response_model=CaseStudyResponse)
def update_case_study(case_id: int, case: CaseStudyUpdate, db: Session = Depends(get_db)):
    """更新案例"""
    db_case = db.query(CaseStudy).filter(CaseStudy.id == case_id, CaseStudy.is_active == True).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="案例不存在")

    if case.is_default:
        db.query(CaseStudy).update({CaseStudy.is_default: False})

    update_data = case.dict(exclude_unset=True)

    if "center_data" in update_data:
        update_data["center_data"] = json.dumps(update_data["center_data"], ensure_ascii=False)
    if "demand_points" in update_data:
        update_data["demand_points"] = json.dumps(update_data["demand_points"], ensure_ascii=False)
    if "material_data" in update_data:
        update_data["material_data"] = json.dumps(update_data["material_data"], ensure_ascii=False) if update_data["material_data"] else None
    if "solution_data" in update_data:
        update_data["solution_data"] = json.dumps(update_data["solution_data"], ensure_ascii=False) if update_data["solution_data"] else None
    
    for field, value in update_data.items():
        setattr(db_case, field, value)
    
    db_case.updated_at = datetime.now()
    db.commit()
    db.refresh(db_case)
    
    return {
        "id": db_case.id,
        "name": db_case.name,
        "description": db_case.description,
        "center_data": json.loads(db_case.center_data),
        "demand_points": json.loads(db_case.demand_points),
        "material_data": json.loads(db_case.material_data) if db_case.material_data else None,
        "solution_data": json.loads(db_case.solution_data) if db_case.solution_data else None,
        "is_default": db_case.is_default,
        "is_active": db_case.is_active,
        "created_at": db_case.created_at.isoformat(),
        "updated_at": db_case.updated_at.isoformat(),
    }


@router.delete("/studies/{case_id}")
def delete_case_study(case_id: int, db: Session = Depends(get_db)):
    """删除案例（软删除）"""
    db_case = db.query(CaseStudy).filter(CaseStudy.id == case_id, CaseStudy.is_active == True).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    db_case.is_active = False
    db.commit()
    
    return {"success": True, "message": "案例已删除"}


@router.post("/studies/{case_id}/set-default")
def set_default_case(case_id: int, db: Session = Depends(get_db)):
    """设置为默认案例"""
    db_case = db.query(CaseStudy).filter(CaseStudy.id == case_id, CaseStudy.is_active == True).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    db.query(CaseStudy).update({CaseStudy.is_default: False})
    db_case.is_default = True
    db.commit()
    db.refresh(db_case)
    
    return {"success": True, "message": "已设置为默认案例"}


@router.get("/debug/material-data")
def debug_material_data(case_id: Optional[int] = None, db: Session = Depends(get_db)):
    """调试接口：查看案例的物资数据结构"""
    if case_id:
        cases = [db.query(CaseStudy).filter(CaseStudy.id == case_id, CaseStudy.is_active == True).first()]
    else:
        cases = db.query(CaseStudy).filter(CaseStudy.is_active == True).all()
    
    result = []
    for case in cases:
        if case:
            material_data = json.loads(case.material_data) if case.material_data else None
            result.append({
                "id": case.id,
                "name": case.name,
                "demand_points": [d["name"] for d in json.loads(case.demand_points)],
                "material_data_keys": list(material_data.keys()) if material_data else [],
                "material_data_structure": {k: {
                    "has_weight": "weight" in v or "total_weight" in v,
                    "has_items": "items" in v,
                    "has_supply_types": "supply_types" in v,
                    "sample": {
                        "weight": v.get("weight") or v.get("total_weight"),
                        "supply_types": v.get("supply_types"),
                        "items_count": len(v.get("items", []))
                    }
                } for k, v in material_data.items()} if material_data else {},
            })
    return {"cases": result}


@router.post("/init-default")
def init_default_case(db: Session = Depends(get_db)):
    """初始化默认案例（渠洋镇应急物资配送案例）"""
    existing = db.query(CaseStudy).filter(CaseStudy.is_default == True).first()
    if existing:
        return {"message": "已有默认案例，跳过初始化"}
    
    default_center = {"name": "渠洋村", "longitude": 106.317264, "latitude": 23.310533}
    default_demands = [
        {"name": "怀渠村", "longitude": 106.285000, "latitude": 23.345000},
        {"name": "塘麻村", "longitude": 106.425000, "latitude": 23.085000},
        {"name": "坡乐村", "longitude": 106.380000, "latitude": 23.075000},
        {"name": "东风村", "longitude": 106.320150, "latitude": 23.309040},
        {"name": "古桥村", "longitude": 106.350000, "latitude": 23.200000},
        {"name": "新和村", "longitude": 106.335000, "latitude": 23.295000},
        {"name": "怀书村", "longitude": 106.278670, "latitude": 23.339030},
        {"name": "雅力村", "longitude": 106.380000, "latitude": 23.250000},
    ]
    default_materials = {
        "怀渠村": {
            "weight": 100,
            "priority": 2,
            "supply_types": ["medicine", "daily"],
            "items": [
                {"name": "消毒酒精", "unit_weight": 5, "qty": 10},
                {"name": "感冒药", "unit_weight": 0.5, "qty": 20},
                {"name": "纱布绷带", "unit_weight": 0.5, "qty": 20}
            ]
        },
        "塘麻村": {
            "weight": 570,
            "priority": 2,
            "supply_types": ["food", "water"],
            "items": [
                {"name": "方便面", "unit_weight": 0.1, "qty": 500},
                {"name": "矿泉水", "unit_weight": 0.5, "qty": 100},
                {"name": "压缩饼干", "unit_weight": 0.2, "qty": 100}
            ]
        },
        "坡乐村": {
            "weight": 140,
            "priority": 3,
            "supply_types": ["daily"],
            "items": [
                {"name": "毛毯", "unit_weight": 2, "qty": 30},
                {"name": "毛巾", "unit_weight": 0.2, "qty": 50},
                {"name": "牙刷套装", "unit_weight": 0.2, "qty": 50}
            ]
        },
        "东风村": {
            "weight": 250,
            "priority": 2,
            "supply_types": ["medicine", "equipment"],
            "items": [
                {"name": "急救箱", "unit_weight": 10, "qty": 10},
                {"name": "体温计", "unit_weight": 0.2, "qty": 50},
                {"name": "口罩", "unit_weight": 0.02, "qty": 1000}
            ]
        },
        "古桥村": {
            "weight": 61,
            "priority": 4,
            "supply_types": ["daily"],
            "items": [
                {"name": "手电筒", "unit_weight": 0.3, "qty": 20},
                {"name": "电池", "unit_weight": 0.05, "qty": 20},
                {"name": "蜡烛", "unit_weight": 0.1, "qty": 100}
            ]
        },
        "新和村": {
            "weight": 20,
            "priority": 4,
            "supply_types": ["food"],
            "items": [
                {"name": "罐头食品", "unit_weight": 0.5, "qty": 40}
            ]
        },
        "怀书村": {
            "weight": 145,
            "priority": 3,
            "supply_types": ["medicine", "food"],
            "items": [
                {"name": "消炎药", "unit_weight": 0.1, "qty": 100},
                {"name": "止痛药", "unit_weight": 0.1, "qty": 100},
                {"name": "面包", "unit_weight": 0.25, "qty": 100}
            ]
        },
        "雅力村": {
            "weight": 200,
            "priority": 3,
            "supply_types": ["food", "daily"],
            "items": [
                {"name": "大米", "unit_weight": 5, "qty": 30},
                {"name": "食用油", "unit_weight": 5, "qty": 10},
                {"name": "洗衣粉", "unit_weight": 1, "qty": 10}
            ]
        }
    }
    
    default_case = CaseStudy(
        name="渠洋镇应急物资配送案例",
        description="靖西市渠洋镇无人机应急物资配送项目案例，包含8个需求村庄的物资配送需求",
        center_data=json.dumps(default_center, ensure_ascii=False),
        demand_points=json.dumps(default_demands, ensure_ascii=False),
        material_data=json.dumps(default_materials, ensure_ascii=False),
        is_default=True,
        is_active=True,
    )
    db.add(default_case)
    db.commit()
    db.refresh(default_case)
    
    return {"message": "默认案例已初始化", "case_id": default_case.id}