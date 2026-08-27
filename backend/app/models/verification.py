"""合规核验记录模型"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.core.database import Base
from datetime import datetime


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)                 # 提交核验的用户
    plan_record_id = Column(Integer, nullable=True)       # 关联方案库 OptimizationRecord
    checklist = Column(Text)                              # 核验清单 JSON（含学生判定 + 引擎复核）
    score = Column(Float, default=0)                      # 合规得分 0~100
    consistency = Column(Float, default=0)                # 学生判定与引擎一致率 %
    mismatch_count = Column(Integer, default=0)           # 学生判 pass 但引擎判 fail 的数量
    verdict = Column(String(20), default="需整改")         # 通过 | 有条件通过 | 需整改
    created_at = Column(DateTime, default=datetime.now)
