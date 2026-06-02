"""物资分配数据库模型 — 持久化存储每个需求点的物资配置"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class MaterialAssignment(Base):
    __tablename__ = "material_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    point_id = Column(Integer, nullable=False, unique=True, index=True, comment="关联 delivery_points.id")
    point_name = Column(String(100), nullable=False, comment="需求点名称")
    category_ids = Column(Text, nullable=True, comment="物资类别ID列表(JSON)")
    supply_types = Column(Text, nullable=True, comment="物资类型名称列表(JSON)")
    items = Column(Text, nullable=True, comment="物资明细(JSON)")
    total_weight = Column(Float, nullable=True, default=0, comment="总重量(kg)")
    priority = Column(Integer, nullable=True, default=3, comment="优先级 1-5")
    special_requirements = Column(String(500), nullable=True, comment="特殊要求")
    risk_warnings = Column(String(500), nullable=True, comment="风险提示")
    note = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
