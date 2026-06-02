"""AI 选型结果数据库模型 — 持久化存储每次 AI 输出"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AiSelectionResult(Base):
    __tablename__ = "ai_selection_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    raw_text = Column(Text, nullable=False, comment="AI 原始输出（Markdown）")
    elapsed_seconds = Column(Float, nullable=True, comment="耗时(秒)")
    model_used = Column(String(100), nullable=True, comment="使用的模型")
    created_at = Column(DateTime, server_default=func.now())
