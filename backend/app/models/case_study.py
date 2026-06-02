"""教学案例模型"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.core.database import Base
from datetime import datetime


class CaseStudy(Base):
    __tablename__ = "case_studies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 案例名称
    description = Column(Text, nullable=True)   # 案例描述
    center_data = Column(Text, nullable=False)  # 配送中心数据（JSON）
    demand_points = Column(Text, nullable=False) # 需求点数据（JSON）
    material_data = Column(Text, nullable=True)  # 物资分配数据（JSON）
    solution_data = Column(Text, nullable=True)  # 预设路线方案（JSON，教学示范用）
    is_default = Column(Boolean, default=False)  # 是否默认案例
    is_active = Column(Boolean, default=True)    # 是否启用
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)