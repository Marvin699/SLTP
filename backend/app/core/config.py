from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json
import os

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
_ENV_FILE = os.path.abspath(_ENV_FILE)


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./path_planning_data.db"
    CORS_ORIGINS: str = '["*"]'

    # LLM 大模型配置（OpenAI 兼容接口）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    # 备用模型链（JSON 数组字符串）：主模型失败（429/超时/异常）时按顺序自动切换
    # 示例: LLM_FALLBACKS=[{"api_key":"sk-xxx","base_url":"https://api.deepseek.com","model":"deepseek-chat"}]
    LLM_FALLBACKS: str = "[]"

    # 高德地图API（地址搜索功能）
    AMAP_KEY: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except Exception:
            return ["*"]

    @property
    def llm_fallbacks_list(self) -> List[dict]:
        """解析备用模型链配置，返回 [{api_key, base_url, model}, ...]"""
        try:
            items = json.loads(self.LLM_FALLBACKS or "[]")
            return [
                {
                    "api_key": str(it.get("api_key", "")),
                    "base_url": str(it.get("base_url", "")),
                    "model": str(it.get("model", "")),
                }
                for it in items
                if isinstance(it, dict) and it.get("api_key") and it.get("model")
            ]
        except Exception:
            return []

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
print(f"[config] 加载 .env: {_ENV_FILE} (exists={os.path.exists(_ENV_FILE)})")
print(f"[config] AMAP_KEY={'已配置(' + str(len(settings.AMAP_KEY)) + ' chars)' if settings.AMAP_KEY else '未配置'}")
