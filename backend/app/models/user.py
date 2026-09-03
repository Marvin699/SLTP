"""用户模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True, comment="用户名（学生为姓名，教师自定义）")
    password_hash = Column(String(255), nullable=False, comment="bcrypt 密码哈希")
    role = Column(String(20), nullable=False, default="student", comment="teacher / student")
    student_no = Column(String(50), nullable=True, index=True, comment="学号（教师为空）")
    class_name = Column(String(100), nullable=True, comment="班级")
    group_no = Column(String(50), nullable=True, comment="小组编号")
    teacher_id = Column(Integer, nullable=True, index=True, comment="指导教师ID（学生归属）")
    invite_code = Column(String(20), nullable=True, unique=True, index=True, comment="教师邀请码（仅教师使用，学生注册时填写）")
    must_change_password = Column(Boolean, default=False, comment="是否需要修改密码（批量导入默认 True）")
    avatar = Column(String(20), nullable=True, comment="头像（emoji 字符或图标标识），为空时显示姓名首字")
    is_active = Column(Boolean, default=True, comment="账号是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
