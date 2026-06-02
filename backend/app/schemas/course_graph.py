from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any
from datetime import datetime
import json


class CourseProjectCreate(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=10, description="项目编号")
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    hours: int = Field(0, ge=0, description="总学时")
    task_count: int = Field(0, ge=0, description="任务数")
    description: Optional[str] = Field(None, description="项目描述")
    certifications: Optional[List[str]] = Field(None, description="关联证书和大赛")
    sub_projects: Optional[Any] = Field(None, description="子项目数据结构")
    knowledge_graph: Optional[Any] = Field(None, description="知识图谱数据")
    capability_graph: Optional[Any] = Field(None, description="能力图谱数据")
    problem_graph: Optional[Any] = Field(None, description="问题图谱数据")
    ideological_graph: Optional[Any] = Field(None, description="思政图谱数据")


class CourseProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    hours: Optional[int] = Field(None, ge=0)
    task_count: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    certifications: Optional[List[str]] = None
    sub_projects: Optional[Any] = None
    knowledge_graph: Optional[Any] = None
    capability_graph: Optional[Any] = None
    problem_graph: Optional[Any] = None
    ideological_graph: Optional[Any] = None
    is_active: Optional[bool] = None


class CourseProjectResponse(BaseModel):
    id: int
    project_id: str
    name: str
    hours: int
    task_count: int
    description: Optional[str] = None
    certifications: Optional[List[str]] = None
    sub_projects: Optional[Any] = None
    knowledge_graph: Optional[Any] = None
    capability_graph: Optional[Any] = None
    problem_graph: Optional[Any] = None
    ideological_graph: Optional[Any] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def parse_json_fields(cls, data):
        """将数据库中的JSON字符串字段解析为Python对象"""
        json_fields = ['certifications', 'sub_projects', 'knowledge_graph', 'capability_graph', 'problem_graph', 'ideological_graph']
        for field in json_fields:
            val = getattr(data, field, None) if hasattr(data, field) else (data.get(field) if isinstance(data, dict) else None)
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(data, dict):
                        data[field] = parsed
                    else:
                        setattr(data, field, parsed)
                except (json.JSONDecodeError, TypeError):
                    pass
        return data


class CourseProjectBrief(BaseModel):
    """列表页用的简要信息"""
    id: int
    project_id: str
    name: str
    hours: int
    task_count: int
    is_active: bool

    class Config:
        from_attributes = True
