"""虚拟仿真 - 仿真视频 API

上传/删除仅限教师（require_teacher），播放列表所有登录用户可用。
视频存储在 backend/uploads/simulations/ 目录，经 /uploads 静态挂载播放
（Starlette StaticFiles 支持 Range 请求，可拖动进度条）。
"""
import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_teacher
from app.models.simulation_video import SimulationVideo
from app.models.user import User

router = APIRouter(prefix="/api/simulations", tags=["虚拟仿真-仿真视频"])

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "uploads", "simulations",
)

# 仅允许视频格式
ALLOWED_EXTS = {".mp4", ".webm", ".ogg", ".mov"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


def _to_dict(v: SimulationVideo) -> dict:
    return {
        "id": v.id,
        "title": v.title,
        "group_no": v.group_no,
        "filename": v.filename,
        "file_ext": v.file_ext,
        "file_size": v.file_size,
        "url": f"/uploads/{v.file_path}",
        "uploader_name": v.uploader_name,
        "created_at": v.created_at.strftime("%Y-%m-%d %H:%M") if v.created_at else None,
    }


@router.post("/upload", summary="上传仿真视频（仅教师）")
def upload_simulation_video(
    file: UploadFile = File(...),
    group_no: str = Form(""),
    title: Optional[str] = Form(None),
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"仅支持视频格式：{'、'.join(sorted(ALLOWED_EXTS))}")

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件过大，最大支持 500MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, stored_name), "wb") as f:
        f.write(content)

    record = SimulationVideo(
        title=(title or "").strip() or os.path.splitext(file.filename or "仿真视频")[0],
        group_no=(group_no or "").strip() or None,
        filename=file.filename,
        file_ext=ext,
        file_path=f"simulations/{stored_name}",
        file_size=len(content),
        uploader_id=current_user.id,
        uploader_name=current_user.username,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "上传成功", "data": _to_dict(record)}


@router.get("/list", response_model=List[dict], summary="仿真视频列表")
def list_simulation_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(SimulationVideo).order_by(SimulationVideo.group_no, SimulationVideo.created_at.desc()).all()
    return [_to_dict(v) for v in items]


@router.delete("/{item_id}", summary="删除仿真视频（仅教师）")
def delete_simulation_video(
    item_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    record = db.query(SimulationVideo).filter(SimulationVideo.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="视频不存在")
    abs_path = os.path.join(os.path.dirname(UPLOAD_DIR), record.file_path)
    if os.path.exists(abs_path):
        try:
            os.remove(abs_path)
        except Exception:
            pass  # 文件删除失败不阻断记录删除
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
