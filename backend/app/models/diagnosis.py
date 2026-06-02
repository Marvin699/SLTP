"""诊断记录模型"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.core.database import Base
from datetime import datetime


class DiagnosisRecord(Base):
    __tablename__ = "diagnosis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    task_config = Column(Text)
    solution_data = Column(Text)
    report = Column(Text)
    score = Column(Float)
    issues_count = Column(Integer, default=0)
    warnings_count = Column(Integer, default=0)
    diagnosis_mode = Column(String(20), default="rule")  # 'rule' | 'ai' | 'both'
    safety_score = Column(Float, default=0)
    timeliness_score = Column(Float, default=0)
    economy_score = Column(Float, default=0)
    feasibility_score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)