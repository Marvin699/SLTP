from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PointType(str, enum.Enum):
    CENTER = "center"
    DEMAND = "demand"


class DeliveryMode(str, enum.Enum):
    DIRECT = "direct"      # 必须直飞
    OPTIONAL = "optional"  # 可选直飞或联飞


class DeliveryPoint(Base):
    __tablename__ = "delivery_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="点位名称")
    point_type = Column(
        SAEnum(PointType, name="point_type_enum"),
        nullable=False,
        comment="点位类型: center=配送中心, demand=需求点",
    )
    longitude = Column(Float, nullable=False, comment="经度")
    latitude = Column(Float, nullable=False, comment="纬度")
    demand_weight = Column(Float, nullable=True, default=0, comment="需求重量(kg)")
    demand_priority = Column(Integer, nullable=True, default=3, comment="需求优先级 1-5")
    delivery_mode = Column(
        SAEnum(DeliveryMode, name="delivery_mode_enum"),
        nullable=True,
        default=DeliveryMode.OPTIONAL,
        comment="配送模式: direct=必须直飞, optional=可选直飞或联飞",
    )
    supply_type = Column(String(50), nullable=True, comment="物资类型")
    note = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
