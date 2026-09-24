"""密码哈希 + JWT 工具"""
import secrets
import jwt
from datetime import datetime, timedelta, timezone
import bcrypt

from app.core.config import settings


# JWT 密钥：优先从 .env（经 settings）读取；未配置则每次启动随机生成（本地开发友好），
# 但正式部署必须配置 JWT_SECRET，否则重启后所有已签发 token 失效
_env_secret = (settings.JWT_SECRET or "").strip()
if not _env_secret:
    _env_secret = secrets.token_hex(32)
    print("[安全提醒] 未配置 JWT_SECRET（.env），本次已使用随机密钥；"
          "正式部署请在 .env 中固定 JWT_SECRET，否则重启后所有登录会失效")

JWT_SECRET = _env_secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # Token 有效期 7 天


def hash_password(password: str) -> str:
    """密码哈希（bcrypt）"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(user_id: int, username: str, role: str) -> str:
    """签发 JWT Token"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 JWT Token，返回 payload 或抛异常"""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
