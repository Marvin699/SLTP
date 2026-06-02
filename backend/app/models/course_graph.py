from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class CourseProject(Base):
    __tablename__ = "course_projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String(10), unique=True, nullable=False, comment="项目编号: P1-P5")
    name = Column(String(200), nullable=False, comment="项目名称")
    hours = Column(Integer, default=0, comment="总学时")
    task_count = Column(Integer, default=0, comment="任务数")
    description = Column(Text, nullable=True, comment="项目描述")
    certifications = Column(Text, nullable=True, comment="JSON: 关联证书和大赛")
    sub_projects = Column(Text, nullable=True, comment="JSON: 完整的子项目→任务→知识点结构")
    knowledge_graph = Column(Text, nullable=True, comment="JSON: 知识图谱数据")
    capability_graph = Column(Text, nullable=True, comment="JSON: 能力图谱数据")
    problem_graph = Column(Text, nullable=True, comment="JSON: 问题图谱数据")
    ideological_graph = Column(Text, nullable=True, comment="JSON: 思政图谱数据")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TeachingStatus(Base):
    """节点教学达成状态"""
    __tablename__ = "teaching_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String(10), nullable=False, comment="项目编号")
    node_id = Column(String(20), nullable=False, comment="节点ID: 任务ID如8")
    node_name = Column(String(200), nullable=True, comment="节点名称")
    status = Column(String(20), nullable=False, comment="达成状态: achieved/partial/not_achieved")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('project_id', 'node_id', name='uq_teaching_status_project_node'),
    )
