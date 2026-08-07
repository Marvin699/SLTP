"""密码哈希 + JWT 工具"""
import os
import jwt
from datetime import datetime, timedelta, timezone
import bcrypt


# JWT 密钥（生产环境应放到 .env，这里给一个默认值方便首次启动）
JWT_SECRET = os.environ.get("JWT_SECRET", "sltp_secret_key_2026_change_me_in_production")
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
