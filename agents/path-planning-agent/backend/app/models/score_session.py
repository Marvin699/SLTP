from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ScoreSession(Base):
    """评分课时会话"""
    __tablename__ = "score_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(32), unique=True, nullable=False, index=True, comment="链接token")
    section_id = Column(String(20), nullable=False, comment="环节ID: section1/section2/section3")
    title = Column(String(200), nullable=False, comment="环节标题")
    groups = Column(Text, nullable=False, comment="JSON: 小组列表")
    dimensions = Column(Text, nullable=False, comment="JSON: 评分维度列表")
    start_time = Column(DateTime, nullable=True, comment="生效时间")
    end_time = Column(DateTime, nullable=True, comment="失效时间")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class ScoreRecord(Base):
    """打分记录"""
    __tablename__ = "score_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_token = Column(String(32), nullable=False, index=True, comment="关联课时token")
    scorer_role = Column(String(50), nullable=False, comment="评分角色: teacher/expert/小组名")
    scorer_name = Column(String(50), nullable=True, comment="打分人姓名（可选）")
    group_id = Column(String(50), nullable=False, comment="小组名称")
    dimension = Column(String(50), nullable=False, comment="评分维度")
    score = Column(Float, nullable=False, comment="分数0-100")
    created_at = Column(DateTime, server_default=func.now())
