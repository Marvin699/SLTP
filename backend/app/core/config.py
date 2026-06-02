from pydantic_settings import BaseSettings
from typing import List
import json
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./path_planning_data.db"
    CORS_ORIGINS: str = '["*"]'

    # LLM 大模型配置（OpenAI 兼容接口）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"

    # 高德地图API（地址搜索功能）
    AMAP_KEY: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
