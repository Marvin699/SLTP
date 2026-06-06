import json
from typing import List, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.course_graph import CourseProject, TeachingStatus
from app.schemas.course_graph import (
    CourseProjectCreate, CourseProjectUpdate,
    CourseProjectResponse, CourseProjectBrief,
)

router = APIRouter(prefix="/api/course-graph", tags=["课程图谱-数据管理"])


# --- 简要响应（不含sub_projects大字段） ---
@router.get("/projects", response_model=List[CourseProjectResponse], summary="获取所有项目列表")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(CourseProject).filter(CourseProject.is_active == True).order_by(CourseProject.project_id).all()
    return projects


# --- 完整数据 ---
@router.get("/projects/{project_id}", response_model=CourseProjectResponse, summary="获取单个项目完整数据")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    return _to_response(project)


# --- 创建项目 ---
@router.post("/projects", response_model=CourseProjectResponse, status_code=201, summary="创建新项目")
def create_project(data: CourseProjectCreate, db: Session = Depends(get_db)):
    exists = db.query(CourseProject).filter(CourseProject.project_id == data.project_id).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"项目编号 {data.project_id} 已存在")
    project = CourseProject(
        project_id=data.project_id,
        name=data.name,
        hours=data.hours,
        task_count=data.task_count,
        description=data.description,
        certifications=json.dumps(data.certifications, ensure_ascii=False) if data.certifications else None,
        sub_projects=json.dumps(data.sub_projects, ensure_ascii=False) if data.sub_projects else None,
        knowledge_graph=json.dumps(data.knowledge_graph, ensure_ascii=False) if data.knowledge_graph else None,
        capability_graph=json.dumps(data.capability_graph, ensure_ascii=False) if data.capability_graph else None,
        problem_graph=json.dumps(data.problem_graph, ensure_ascii=False) if data.problem_graph else None,
        ideological_graph=json.dumps(data.ideological_graph, ensure_ascii=False) if data.ideological_graph else None,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_response(project)


# --- 更新项目 ---
@router.put("/projects/{project_id}", response_model=CourseProjectResponse, summary="更新项目")
def update_project(project_id: str, data: CourseProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    update_data = data.model_dump(exclude_unset=True)
    json_list_fields = ["certifications", "sub_projects", "knowledge_graph", "capability_graph", "problem_graph", "ideological_graph"]
    for field in json_list_fields:
        if field in update_data and update_data[field] is not None:
            update_data[field] = json.dumps(update_data[field], ensure_ascii=False)
    for field, value in update_data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _to_response(project)


# --- 删除项目 ---
@router.delete("/projects/{project_id}", status_code=204, summary="删除项目")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    db.delete(project)
    db.commit()
    return None


# --- 导入JSON数据 ---
class ImportDataRequest(BaseModel):
    sub_projects: Any
    task_count: int = 0


@router.post("/projects/{project_id}/import", response_model=CourseProjectResponse, summary="导入项目数据")
def import_project_data(project_id: str, data: ImportDataRequest, db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    project.sub_projects = json.dumps(data.sub_projects, ensure_ascii=False)
    if data.task_count > 0:
        project.task_count = data.task_count
    db.commit()
    db.refresh(project)
    return _to_response(project)


# --- 上传JSON文件导入 ---
@router.post("/projects/{project_id}/upload", response_model=CourseProjectResponse, summary="上传JSON文件导入数据")
async def upload_project_data(project_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.query(CourseProject).filter(CourseProject.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    content = await file.read()
    try:
        json_data = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="文件格式错误，请上传有效的JSON文件")
    # 支持两种格式：直接是数组，或者包含sub_projects字段
    if isinstance(json_data, list):
        sub_projects = json_data
    elif isinstance(json_data, dict) and "sub_projects" in json_data:
        sub_projects = json_data["sub_projects"]
    else:
        raise HTTPException(status_code=400, detail="JSON结构不正确，需要sub_projects数组或直接是数组")
    project.sub_projects = json.dumps(sub_projects, ensure_ascii=False)
    # 导入四个图谱数据（如果JSON中包含）
    if isinstance(json_data, dict):
        for field in ["knowledge_graph", "capability_graph", "problem_graph", "ideological_graph"]:
            if field in json_data and json_data[field]:
                setattr(project, field, json.dumps(json_data[field], ensure_ascii=False))
    # 自动计算任务数
    task_count = 0
    point_count = 0
    hours = 0
    for sp in sub_projects:
        tasks = sp.get("tasks", [])
        task_count += len(tasks)
        hours += sp.get("hours", 0)
        for t in tasks:
            point_count += len(t.get("points", []))
    project.task_count = task_count
    project.hours = hours
    db.commit()
    db.refresh(project)
    return _to_response(project)


def _to_response(project: CourseProject) -> CourseProjectResponse:
    return CourseProjectResponse.model_validate(project)


# === 教学达成状态 ===

class TeachingStatusUpdate(BaseModel):
    project_id: str
    node_id: str
    node_name: str = ""
    status: str  # achieved / partial / not_achieved


@router.get("/teaching-status/{project_id}")
def get_teaching_status(project_id: str, db: Session = Depends(get_db)):
    """获取某项目所有节点的教学达成状态"""
    rows = db.query(TeachingStatus).filter(TeachingStatus.project_id == project_id).all()
    return {str(r.node_id): {"status": r.status, "node_name": r.node_name, "updated_at": r.updated_at} for r in rows}


@router.put("/teaching-status")
def update_teaching_status(data: TeachingStatusUpdate, db: Session = Depends(get_db)):
    """更新某节点的教学达成状态"""
    row = db.query(TeachingStatus).filter(
        TeachingStatus.project_id == data.project_id,
        TeachingStatus.node_id == data.node_id,
    ).first()
    if row:
        row.status = data.status
        row.node_name = data.node_name
    else:
        row = TeachingStatus(
            project_id=data.project_id,
            node_id=data.node_id,
            node_name=data.node_name,
            status=data.status,
        )
        db.add(row)
    db.commit()
    return {"message": "状态已更新", "status": data.status}
