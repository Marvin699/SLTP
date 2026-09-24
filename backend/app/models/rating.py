from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class RatingRecord(Base):
    """任务8·电子评量表评分记录

    v2：原实现把评分写入 media/ratings/*.json，多用户并发提交会互相覆盖丢分，
    改为落库（SQLite 已开 WAL），并发提交安全且重启不丢数据。
    """
    __tablename__ = "rating_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, nullable=False, index=True, comment="小组编号 1-6")
    name = Column(String(100), default="匿名", comment="评分人姓名")
    role = Column(String(50), default="student", comment="评分角色")
    dims = Column(Text, nullable=True, comment="JSON: [{\"label\": \"x\", \"val\": 80}]")
    total = Column(Integer, nullable=True, comment="总分（未传则由维度求和/留空）")
    created_at = Column(DateTime, server_default=func.now())
