"""仿真视频模型 — 应急规划智能体「虚拟仿真」模块"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func

from app.core.database import Base


class SimulationVideo(Base):
    __tablename__ = "simulation_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="视频标题")
    group_no = Column(String(50), nullable=True, index=True, comment="对应小组编号（1~6，空为通用）")
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_ext = Column(String(20), nullable=False, comment="扩展名")
    file_path = Column(String(255), nullable=False, comment="相对 uploads 的存储路径")
    file_size = Column(BigInteger, nullable=True, comment="文件大小（字节）")
    uploader_id = Column(Integer, nullable=True, comment="上传教师 ID")
    uploader_name = Column(String(100), nullable=True, comment="上传教师姓名")
    created_at = Column(DateTime, server_default=func.now())
