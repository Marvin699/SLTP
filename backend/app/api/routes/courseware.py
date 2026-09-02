"""我的课程 - 课件资料 API

上传仅限教师（require_teacher），浏览/下载所有登录用户可用。
文件存储在 backend/uploads/courseware/ 目录。
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_teacher
from app.models.courseware import Courseware
from app.models.user import User

router = APIRouter(prefix="/api/courseware", tags=["我的课程-课件资料"])

# 上传目录（backend/uploads/courseware）
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads", "courseware")

# 允许的扩展名（课件 + 常见资料格式）
ALLOWED_EXTS = {
    ".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx",
    ".mp4", ".mp3", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".rar", ".txt",
}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB


def _to_dict(c: Courseware) -> dict:
    return {
        "id": c.id,
        "course_name": c.course_name,
        "title": c.title,
        "file_type": c.file_type,
        "filename": c.filename,
        "file_ext": c.file_ext,
        "file_size": c.file_size,
        "uploader_name": c.uploader_name,
        "download_count": c.download_count,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None,
    }


@router.post("/upload", summary="上传课件/资料（仅教师）")
def upload_courseware(
    file: UploadFile = File(...),
    course_name: str = Form(...),
    title: Optional[str] = Form(None),
    file_type: str = Form("courseware"),
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    if file_type not in ("courseware", "material"):
        file_type = "other"

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{ext or '未知'}")

    # 读取内容并校验大小
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件过大，最大支持 200MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(content)

    record = Courseware(
        course_name=course_name.strip() or "未分类",
        title=(title or "").strip() or os.path.splitext(file.filename)[0],
        file_type=file_type,
        filename=file.filename,
        file_ext=ext,
        file_path=f"courseware/{stored_name}",
        file_size=len(content),
        uploader_id=current_user.id,
        uploader_name=current_user.username,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "上传成功", "data": _to_dict(record)}


@router.get("/list", response_model=List[dict], summary="课件列表")
def list_courseware(
    course_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Courseware)
    if course_name:
        query = query.filter(Courseware.course_name == course_name)
    items = query.order_by(Courseware.created_at.desc()).all()
    return [_to_dict(c) for c in items]


@router.get("/courses", response_model=List[str], summary="课程名列表")
def list_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(Courseware.course_name).distinct().all()
    return sorted({r[0] for r in rows if r[0]})


@router.get("/{item_id}/download", summary="下载课件（计数+1）")
def download_courseware(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(Courseware).filter(Courseware.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")
    abs_path = os.path.join(os.path.dirname(UPLOAD_DIR), record.file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="文件已丢失，请联系管理员")
    record.download_count += 1
    db.commit()
    return FileResponse(abs_path, filename=record.filename)


@router.delete("/{item_id}", summary="删除课件（仅教师）")
def delete_courseware(
    item_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    record = db.query(Courseware).filter(Courseware.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")
    abs_path = os.path.join(os.path.dirname(UPLOAD_DIR), record.file_path)
    if os.path.exists(abs_path):
        try:
            os.remove(abs_path)
        except Exception:
            pass  # 文件删除失败不阻断记录删除
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
