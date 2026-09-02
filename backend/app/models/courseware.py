"""我的课程 - 课件资料模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base


class Courseware(Base):
    """课件/资料文件"""
    __tablename__ = "coursewares"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False, index=True)  # 所属课程名
    title = Column(String(200), nullable=False)                    # 课件标题
    file_type = Column(String(20), nullable=False, default="other")  # courseware=课件 / material=资料
    filename = Column(String(255), nullable=False)                 # 原始文件名
    file_ext = Column(String(20), nullable=True)                   # 扩展名（如 .pptx）
    file_path = Column(String(500), nullable=False)                # 存储路径（相对 backend/uploads）
    file_size = Column(Float, nullable=True)                       # 文件大小（字节）
    uploader_id = Column(Integer, nullable=True)                   # 上传者用户ID
    uploader_name = Column(String(50), nullable=True)              # 上传者姓名
    download_count = Column(Integer, nullable=False, default=0)    # 下载次数
    created_at = Column(DateTime, default=datetime.now, index=True)
