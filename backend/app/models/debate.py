"""反向质询辩论系统数据模型

实现"人机双向奔赴"教学理念的数据底座：
- DebateSession：一次完整的"假设-验证-反驳-重构"深度学习闭环
- DebateMessage：结构化记录学生评判逻辑与 AI 追问
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class DebateSession(Base):
    """辩论会话"""
    __tablename__ = "debate_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50))                    # 学生姓名快照（教师端展示用）
    group_name = Column(String(50))                  # 小组名（可选）
    plan_record_id = Column(Integer, nullable=True)  # 关联 optimization_records.id
    plan_summary = Column(Text)                      # 方案摘要快照（名称/四维分数/关键指标）
    stage = Column(String(20), default="hypothesis") # hypothesis|verify|rebut|rebuild|completed
    status = Column(String(20), default="active")    # active|completed
    final_verdict = Column(Text)                     # 学生最终结论
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DebateMessage(Base):
    """辩论消息：比 ChatHistory 多结构化字段，支撑评判逻辑记录与思辨评估"""
    __tablename__ = "debate_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False)        # student|ai|teacher
    content = Column(Text, nullable=False)
    stage = Column(String(20))                       # 该消息所属阶段
    judgment_dimensions = Column(Text)               # 学生评判维度 JSON 数组，如 ["safety","timeliness"]
    judgment_confidence = Column(Integer)            # 学生自评置信度 0-100
    challenge_type = Column(String(30))              # AI 追问类型：assumption|risk|alternative|standard
    created_at = Column(DateTime, server_default=func.now())
