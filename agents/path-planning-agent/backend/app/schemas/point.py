from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PointType(str, Enum):
    CENTER = "center"
    DEMAND = "demand"


class DeliveryMode(str, Enum):
    DIRECT = "direct"      # 必须直飞
    OPTIONAL = "optional"  # 可选直飞或联飞


class PointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="点位名称")
    point_type: PointType = Field(..., description="点位类型")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    demand_weight: Optional[float] = Field(0, ge=0, description="需求重量(kg)")
    demand_priority: Optional[int] = Field(3, ge=1, le=5, description="需求优先级")
    delivery_mode: Optional[DeliveryMode] = Field(DeliveryMode.OPTIONAL, description="配送模式")
    supply_type: Optional[str] = Field(None, max_length=50, description="物资类型")
    note: Optional[str] = Field(None, max_length=500, description="备注")


class PointCreate(PointBase):
    pass


class PointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="点位名称")
    point_type: Optional[PointType] = Field(None, description="点位类型")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="经度")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="纬度")
    demand_weight: Optional[float] = Field(None, ge=0, description="需求重量(kg)")
    demand_priority: Optional[int] = Field(None, ge=1, le=5, description="需求优先级")
    delivery_mode: Optional[DeliveryMode] = Field(None, description="配送模式")
    supply_type: Optional[str] = Field(None, max_length=50, description="物资类型")
    note: Optional[str] = Field(None, max_length=500, description="备注")


class PointResponse(PointBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict


class GeoJSONCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class GeoJSONSaveRequest(BaseModel):
    geojson: GeoJSONCollection = Field(..., description="GeoJSON数据")


class BatchPointCreate(BaseModel):
    points: List[PointCreate] = Field(..., min_length=1, description="批量点位数据")


class DistanceMatrixResponse(BaseModel):
    labels: List[str] = Field(..., description="点位名称标签列表")
    matrix: List[List[float]] = Field(..., description="距离矩阵（km）")
    return_distances: List[float] = Field(..., description="各点回配送中心距离（km）")
