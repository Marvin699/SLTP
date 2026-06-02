"""大模型配置模型"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.core.database import Base
from datetime import datetime


class LLMConfig(Base):
    __tablename__ = "llm_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 模型名称，如"DeepSeek-V3"
    model_id = Column(String(100), nullable=False)  # 模型ID，如"deepseek-chat"
    base_url = Column(String(500), nullable=False)  # API地址，如"https://api.deepseek.com"
    api_key = Column(String(500), nullable=False)  # API密钥
    description = Column(Text, nullable=True)  # 模型描述
    is_active = Column(Boolean, default=False)  # 是否当前选中
    is_default = Column(Boolean, default=False)  # 是否默认模型
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)