"""无人机参数数据库模型 — 持久化存储可编辑的无人机参数"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UavParam(Base):
    __tablename__ = "uav_params"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_id = Column(String(50), nullable=False, unique=True, index=True, comment="型号标识(dji-fc100等)")
    brand = Column(String(50), nullable=False, comment="品牌")
    brand_en = Column(String(50), nullable=True, comment="品牌英文")
    model = Column(String(100), nullable=False, comment="型号名称")
    max_payload = Column(Float, nullable=False, default=10, comment="最大载重(kg)")
    range_km = Column(Float, nullable=False, default=20, comment="航程(km)")
    max_speed = Column(Float, nullable=False, default=60, comment="最大速度(km/h)")
    cabin_volume = Column(Float, nullable=True, comment="货舱容积(L)")
    wind_resist = Column(Integer, nullable=True, comment="抗风等级(级)")
    ip_rating = Column(String(20), nullable=True, comment="防护等级")
    drop_mode = Column(String(100), nullable=True, comment="投放方式")
    features = Column(Text, nullable=True, comment="特性(JSON数组)")
    suitable_for = Column(Text, nullable=True, comment="适用场景(JSON数组)")
    description = Column(Text, nullable=True, comment="描述")
    range_points = Column(Text, nullable=True, comment="载重-航程点JSON(分段线性插值)")
    raw_params = Column(Text, nullable=True, comment="原始参数JSON(来自用户文件)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
