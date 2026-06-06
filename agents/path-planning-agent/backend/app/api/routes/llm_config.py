"""系统管理 - 大模型配置 API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.llm_config import LLMConfig
from app.core.config import settings

router = APIRouter(prefix="/api/path-planning/llm", tags=["系统管理-大模型配置"])


class LLMConfigCreate(BaseModel):
    name: str
    model_id: str
    base_url: str
    api_key: str
    description: Optional[str] = None
    is_default: bool = False


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    model_id: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    id: int
    name: str
    model_id: str
    base_url: str
    api_key: str  # 返回完整key，前端需要显示
    description: Optional[str]
    is_active: bool
    is_default: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/configs", response_model=List[LLMConfigResponse])
def get_llm_configs(db: Session = Depends(get_db)):
    """获取所有大模型配置"""
    configs = db.query(LLMConfig).order_by(LLMConfig.created_at.desc()).all()
    return configs


@router.post("/configs", response_model=LLMConfigResponse)
def create_llm_config(config: LLMConfigCreate, db: Session = Depends(get_db)):
    """添加大模型配置"""
    # 如果设置为默认，取消其他默认
    if config.is_default:
        db.query(LLMConfig).update({LLMConfig.is_default: False})
    
    db_config = LLMConfig(
        name=config.name,
        model_id=config.model_id,
        base_url=config.base_url,
        api_key=config.api_key,
        description=config.description,
        is_default=config.is_default,
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    # 如果是第一个模型或设置为默认，自动激活
    if config.is_default or db.query(LLMConfig).count() == 1:
        activate_llm_config_internal(db_config.id, db)
    
    return db_config


@router.put("/configs/{config_id}", response_model=LLMConfigResponse)
def update_llm_config(config_id: int, config: LLMConfigUpdate, db: Session = Depends(get_db)):
    """更新大模型配置"""
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果设置为默认，取消其他默认
    if config.is_default:
        db.query(LLMConfig).update({LLMConfig.is_default: False})
    
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db_config.updated_at = datetime.now()
    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/configs/{config_id}")
def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    """删除大模型配置"""
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果删除的是当前激活的模型，需要重新激活一个
    was_active = db_config.is_active
    
    db.delete(db_config)
    db.commit()
    
    # 如果删除的是激活的模型，自动激活默认模型或第一个模型
    if was_active:
        default_config = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
        if default_config:
            activate_llm_config_internal(default_config.id, db)
        else:
            first_config = db.query(LLMConfig).first()
            if first_config:
                activate_llm_config_internal(first_config.id, db)
    
    return {"success": True, "message": "配置已删除"}


@router.post("/configs/{config_id}/activate")
def activate_llm_config(config_id: int, db: Session = Depends(get_db)):
    """激活指定大模型配置"""
    result = activate_llm_config_internal(config_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "message": "模型已激活", "config": result}


def activate_llm_config_internal(config_id: int, db: Session):
    """内部方法：激活指定配置并更新全局设置"""
    # 取消所有激活状态
    db.query(LLMConfig).update({LLMConfig.is_active: False})
    
    # 激活指定配置
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        return None
    
    config.is_active = True
    db.commit()
    db.refresh(config)
    
    # 更新全局设置
    settings.LLM_API_KEY = config.api_key
    settings.LLM_BASE_URL = config.base_url
    settings.LLM_MODEL = config.model_id
    
    return config


@router.get("/active", response_model=Optional[LLMConfigResponse])
def get_active_config(db: Session = Depends(get_db)):
    """获取当前激活的大模型配置"""
    config = db.query(LLMConfig).filter(LLMConfig.is_active == True).first()
    return config


@router.post("/test")
def test_llm_connection(config_id: int, db: Session = Depends(get_db)):
    """测试大模型连接"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=30.0,
        )
        
        # 发送简单测试消息
        response = client.chat.completions.create(
            model=config.model_id,
            messages=[
                {"role": "user", "content": "你好，请回复'连接成功'"}
            ],
            max_tokens=50,
        )
        
        content = response.choices[0].message.content
        return {
            "success": True,
            "message": "连接成功",
            "response": content,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"连接失败: {str(e)}",
        }


@router.post("/init-default")
def init_default_config(db: Session = Depends(get_db)):
    """初始化默认大模型配置（从环境变量）"""
    # 检查是否已有配置
    existing = db.query(LLMConfig).first()
    if existing:
        return {"message": "已有配置，跳过初始化"}
    
    # 从环境变量创建默认配置
    if settings.LLM_API_KEY:
        default_config = LLMConfig(
            name="DeepSeek-Chat",
            model_id=settings.LLM_MODEL or "deepseek-chat",
            base_url=settings.LLM_BASE_URL or "https://api.deepseek.com",
            api_key=settings.LLM_API_KEY,
            description="默认DeepSeek模型",
            is_default=True,
            is_active=True,
        )
        db.add(default_config)
        db.commit()
        db.refresh(default_config)
        return {"message": "默认配置已初始化", "config_id": default_config.id}
    
    return {"message": "环境变量未配置，跳过初始化"}