"""
环节三评分维度改名迁移：安全性/操作规范性/用时效率/团队配合
→ 教师评分/企业导师评分/Ai评分/学生评分

范围限定：仅处理 section_id='section3' 的评分会话及其打分记录。
注意「团队配合」在环节一/二也在使用，必须通过 session_token 过滤，
不能全局替换。脚本幂等，可重复执行。

用法：cd backend && python3 scripts/migrate_section3_dims.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.score_session import ScoreSession, ScoreRecord

RENAME_MAP = {
    "安全性": "教师评分",
    "操作规范性": "企业导师评分",
    "用时效率": "Ai评分",
    "团队配合": "学生评分",
}

NEW_DIMENSIONS = ["教师评分", "企业导师评分", "Ai评分", "学生评分"]


def main():
    db = SessionLocal()
    try:
        tokens = [
            t for (t,) in db.query(ScoreSession.token).filter(
                ScoreSession.section_id == "section3"
            ).all()
        ]
        if not tokens:
            print("没有 section3 的评分会话，无需迁移")
            return

        rec_total = 0
        for token in tokens:
            records = db.query(ScoreRecord).filter(
                ScoreRecord.session_token == token
            ).all()
            for r in records:
                if r.dimension in RENAME_MAP:
                    r.dimension = RENAME_MAP[r.dimension]
                    rec_total += 1

        sess_total = 0
        sessions = db.query(ScoreSession).filter(
            ScoreSession.section_id == "section3"
        ).all()
        for s in sessions:
            dims = s.dimensions
            if isinstance(dims, str):
                dims = json.loads(dims)
            if isinstance(dims, list) and any(d in RENAME_MAP for d in dims):
                s.dimensions = json.dumps(NEW_DIMENSIONS, ensure_ascii=False)
                sess_total += 1

        db.commit()
        print(f"迁移完成：{len(tokens)} 个 section3 会话，更新打分记录 {rec_total} 条，更新会话维度配置 {sess_total} 个")
        for old, new in RENAME_MAP.items():
            print(f"  {old} → {new}")
    except Exception as e:
        db.rollback()
        print(f"迁移失败，已回滚：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
