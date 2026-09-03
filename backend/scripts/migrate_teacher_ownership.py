"""一次性迁移：学生归属教师功能
1. users 表按模型补齐缺失列（SQLite 不支持 ORM 自动加列）
2. 为所有缺邀请码的教师生成邀请码
3. 若全平台仅一位教师，把未分配的历史学生划归该教师
可重复执行（幂等）。用法：cd backend && python3 scripts/migrate_teacher_ownership.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.core.database import engine, SessionLocal
from app.models.user import User

# 模型字段 → 建列 SQL 类型（与 app/models/user.py 保持同步）
COLUMN_DDL = {
    "teacher_id": "INTEGER",
    "invite_code": "VARCHAR(20)",
    "must_change_password": "BOOLEAN DEFAULT 0",
    "avatar": "VARCHAR(20)",
    "is_active": "BOOLEAN DEFAULT 1",
}

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def main():
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns("users")]
    with engine.begin() as conn:
        for name, ddl in COLUMN_DDL.items():
            if name not in cols:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl}"))
                print(f"已添加列 users.{name}")
        if "invite_code" not in cols:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_invite_code ON users (invite_code)"))

    db = SessionLocal()
    try:
        teachers = db.query(User).filter(User.role == "teacher").all()
        # 2. 补邀请码
        for t in teachers:
            if not t.invite_code:
                while True:
                    import secrets
                    code = "".join(secrets.choice(ALPHABET) for _ in range(6))
                    if not db.query(User).filter(User.invite_code == code).first():
                        break
                t.invite_code = code
                db.commit()
                print(f"教师「{t.username}」邀请码：{code}")

        # 3. 孤儿学生划归唯一教师
        orphans = db.query(User).filter(User.role == "student", User.teacher_id.is_(None)).all()
        if orphans:
            if len(teachers) == 1:
                for s in orphans:
                    s.teacher_id = teachers[0].id
                db.commit()
                print(f"已将 {len(orphans)} 名未分配学生划归教师「{teachers[0].username}」")
            else:
                print(f"存在 {len(orphans)} 名未分配学生，但教师不止一位，请教师在学生管理中手动认领")
        else:
            print("没有未分配的学生")
    finally:
        db.close()

    print("迁移完成")


if __name__ == "__main__":
    main()
