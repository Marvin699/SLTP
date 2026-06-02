from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.models.point import DeliveryPoint
from app.schemas.point import (
    PointCreate,
    PointUpdate,
    PointResponse,
    GeoJSONCollection,
    GeoJSONSaveRequest,
    BatchPointCreate,
    DistanceMatrixResponse,
)
from app.services.geojson_service import points_to_geojson
from app.services.distance_service import build_distance_matrix

router = APIRouter(prefix="/api/points", tags=["配送点管理"])


@router.get("", response_model=List[PointResponse], summary="获取所有点位")
def get_all_points(db: Session = Depends(get_db)):
    """获取所有配送中心与需求点"""
    points = db.query(DeliveryPoint).order_by(DeliveryPoint.id).all()
    return points


# ── 固定路径必须在 /{point_id} 之前注册 ──

@router.get("/geojson/export", response_model=GeoJSONCollection, summary="导出GeoJSON")
def export_geojson(db: Session = Depends(get_db)):
    """将所有点位导出为标准GeoJSON FeatureCollection"""
    points = db.query(DeliveryPoint).order_by(DeliveryPoint.id).all()
    return points_to_geojson(points)


@router.get("/distance-matrix", response_model=DistanceMatrixResponse, summary="生成距离矩阵")
def get_distance_matrix(db: Session = Depends(get_db)):
    """根据当前所有点位生成Haversine距离矩阵"""
    points = db.query(DeliveryPoint).order_by(DeliveryPoint.id).all()
    if len(points) < 2:
        raise HTTPException(status_code=400, detail="至少需要2个点位才能生成距离矩阵")
    return build_distance_matrix(points)


@router.post("/batch", response_model=List[PointResponse], status_code=201, summary="批量创建点位")
def batch_create_points(data: BatchPointCreate, db: Session = Depends(get_db)):
    """批量创建点位，先清空旧数据再写入"""
    db.query(DeliveryPoint).delete()
    db.commit()

    created = []
    for pt_data in data.points:
        point = DeliveryPoint(
            name=pt_data.name,
            point_type=pt_data.point_type,
            longitude=pt_data.longitude,
            latitude=pt_data.latitude,
            demand_weight=pt_data.demand_weight or 0,
            demand_priority=pt_data.demand_priority or 3,
            supply_type=pt_data.supply_type,
            note=pt_data.note,
        )
        db.add(point)
        created.append(point)

    db.commit()
    for pt in created:
        db.refresh(pt)
    return created


@router.post("/geojson/import", response_model=List[PointResponse], summary="导入GeoJSON")
def import_geojson(data: GeoJSONSaveRequest, db: Session = Depends(get_db)):
    """从GeoJSON FeatureCollection导入点位数据"""
    imported = []
    for feature in data.geojson.features:
        props = feature.properties
        coords = feature.geometry.get("coordinates", [0, 0])
        point = DeliveryPoint(
            name=props.get("name", "未命名"),
            point_type=props.get("type", "demand"),
            longitude=coords[0],
            latitude=coords[1],
            demand_weight=props.get("demand_weight", 0),
            demand_priority=props.get("demand_priority", 3),
            supply_type=props.get("supply_type"),
            note=props.get("note"),
        )
        db.add(point)
        imported.append(point)

    db.commit()
    for pt in imported:
        db.refresh(pt)
    return imported


@router.get("/geocode/search", summary="地址搜索（高德地图）")
async def geocode_search(keyword: str):
    """通过高德地图API搜索地址，返回经纬度"""
    if not settings.AMAP_KEY:
        raise HTTPException(status_code=500, detail="高德地图API Key未配置，请在 .env 文件中设置 AMAP_KEY")

    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": keyword,
        "key": settings.AMAP_KEY,
        "output": "JSON",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
        if data.get("status") == "1" and data.get("geocodes"):
            results = []
            for g in data["geocodes"]:
                loc = g.get("location", "")
                if not loc:
                    continue
                lng, lat = loc.split(",")
                results.append({
                    "name": g.get("formatted_address", keyword),
                    "lng": float(lng),
                    "lat": float(lat),
                })
            return results
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"地址搜索失败: {str(e)}")


# ── 动态路径放在最后 ──

@router.get("/{point_id}", response_model=PointResponse, summary="获取单个点位")
def get_point(point_id: int, db: Session = Depends(get_db)):
    """根据ID获取点位详情"""
    point = db.query(DeliveryPoint).filter(DeliveryPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="点位不存在")
    return point


@router.post("", response_model=PointResponse, status_code=201, summary="创建点位")
def create_point(data: PointCreate, db: Session = Depends(get_db)):
    """创建新的配送中心或需求点"""
    point = DeliveryPoint(
        name=data.name,
        point_type=data.point_type,
        longitude=data.longitude,
        latitude=data.latitude,
        demand_weight=data.demand_weight,
        demand_priority=data.demand_priority,
        supply_type=data.supply_type,
        note=data.note,
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


@router.put("/{point_id}", response_model=PointResponse, summary="更新点位")
def update_point(point_id: int, data: PointUpdate, db: Session = Depends(get_db)):
    """更新点位信息"""
    point = db.query(DeliveryPoint).filter(DeliveryPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="点位不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(point, field, value)

    db.commit()
    db.refresh(point)
    return point


@router.delete("/{point_id}", status_code=204, summary="删除点位")
def delete_point(point_id: int, db: Session = Depends(get_db)):
    """删除指定点位"""
    point = db.query(DeliveryPoint).filter(DeliveryPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="点位不存在")
    db.delete(point)
    db.commit()
    return None
