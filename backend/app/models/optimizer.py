"""路径规划优化记录模型"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.core.database import Base
from datetime import datetime


class OptimizationRecord(Base):
    __tablename__ = "optimization_records"
    
    id = Column(Integer, primary_key=True, index=True)
    task_config = Column(Text)           # 任务配置JSON
    solution_data = Column(Text)         # 方案数据JSON
    aco_params = Column(Text)            # ACO参数JSON
    summary = Column(Text)               # 结果摘要JSON
    total_distance = Column(Float)       # 总距离
    total_energy = Column(Float)         # 总能耗
    total_trips = Column(Integer)        # 总趟次
    village_count = Column(Integer)      # 需求点数量
    drone_count = Column(Integer)        # 无人机数量
    created_at = Column(DateTime, default=datetime.now)
