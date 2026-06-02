"""配置信息 API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.config_service import list_configs, save_config, load_config, delete_config

router = APIRouter(prefix="/api/config", tags=["配置管理"])


class SaveRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=200, description="文件名")
    content: str = Field(..., description="Markdown 内容")


@router.get("/list")
def get_configs():
    """列出所有配置文件"""
    return list_configs()


@router.get("/load/{filename}")
def get_config(filename: str):
    """加载配置文件内容"""
    try:
        content = load_config(filename)
        return {'filename': filename, 'content': content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/save")
def post_save(req: SaveRequest):
    """保存配置文件"""
    result = save_config(req.filename, req.content)
    return result


@router.delete("/delete/{filename}")
def del_config(filename: str):
    """删除配置文件"""
    if delete_config(filename):
        return {'message': f'已删除: {filename}'}
    raise HTTPException(status_code=404, detail=f'文件不存在: {filename}')
