import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import SessionLocal
from app.models.image_config import ImageConfig

router = APIRouter(prefix="/api/image-config", tags=["图片配置"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ImageConfigResponse(BaseModel):
    group_id: int
    slot: int
    image_url: Optional[str] = None
    alpha: str
    beta: str
    rho: str


class SaveConfigRequest(BaseModel):
    group_id: int
    slot: int
    alpha: str = "0.5"
    beta: str = "0.3"
    rho: str = "0.8"


@router.get("/all", response_model=List[ImageConfigResponse])
def get_all_configs():
    db = SessionLocal()
    try:
        configs = db.query(ImageConfig).all()
        result = []
        for config in configs:
            image_url = f"/api/image-config/image/{config.image_path}" if config.image_path else None
            result.append({
                "group_id": config.group_id,
                "slot": config.slot,
                "image_url": image_url,
                "alpha": config.alpha,
                "beta": config.beta,
                "rho": config.rho,
            })
        return result
    finally:
        db.close()


@router.get("/{group_id}/{slot}", response_model=ImageConfigResponse)
def get_config(group_id: int, slot: int):
    db = SessionLocal()
    try:
        config = db.query(ImageConfig).filter(
            ImageConfig.group_id == group_id,
            ImageConfig.slot == slot
        ).first()
        if not config:
            return {
                "group_id": group_id,
                "slot": slot,
                "image_url": None,
                "alpha": "0.5",
                "beta": "0.3",
                "rho": "0.8",
            }
        image_url = f"/api/image-config/image/{config.image_path}" if config.image_path else None
        return {
            "group_id": config.group_id,
            "slot": slot,
            "image_url": image_url,
            "alpha": config.alpha,
            "beta": config.beta,
            "rho": config.rho,
        }
    finally:
        db.close()


@router.post("/save")
async def save_config(
    group_id: int = ...,
    slot: int = ...,
    alpha: str = "0.5",
    beta: str = "0.3",
    rho: str = "0.8",
    file: Optional[UploadFile] = File(None)
):
    db = SessionLocal()
    try:
        config = db.query(ImageConfig).filter(
            ImageConfig.group_id == group_id,
            ImageConfig.slot == slot
        ).first()

        if config:
            config.alpha = alpha
            config.beta = beta
            config.rho = rho
        else:
            config = ImageConfig(
                group_id=group_id,
                slot=slot,
                alpha=alpha,
                beta=beta,
                rho=rho,
            )
            db.add(config)

        if file:
            file_ext = os.path.splitext(file.filename)[1] or ".png"
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            config.image_path = filename

        db.commit()
        return {"status": "ok", "message": "保存成功"}
    finally:
        db.close()


@router.delete("/{group_id}/{slot}")
def delete_config(group_id: int, slot: int):
    db = SessionLocal()
    try:
        config = db.query(ImageConfig).filter(
            ImageConfig.group_id == group_id,
            ImageConfig.slot == slot
        ).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        if config.image_path:
            file_path = os.path.join(UPLOAD_DIR, config.image_path)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.delete(config)
        db.commit()
        return {"status": "ok", "message": "删除成功"}
    finally:
        db.close()


@router.get("/image/{filename}")
def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(file_path)
