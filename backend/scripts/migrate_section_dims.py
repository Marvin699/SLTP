"""
三个环节评分维度统一改名迁移：旧评分标准 → 评分来源
- 环节一：方案完整性/表达展示/操作规范/团队配合
- 环节二：决策速度/方案可行性/风险评估/团队配合
- 环节三：安全性/操作规范性/用时效率/团队配合
统一改为：教师评分 / 企业导师评分 / Ai评分 / 学生评分（权重结构不变 0.35/0.35/0.15/0.15）

各环节旧维度名互不重复，可安全全局映射。脚本幂等，可重复执行。

用法：cd backend && python3 scripts/migrate_section_dims.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.score_session import ScoreSession, ScoreRecord

RENAME_MAP = {
    # → 教师评分
    "方案完整性": "教师评分",
    "决策速度": "教师评分",
    "安全性": "教师评分",
    # → 企业导师评分
    "表达展示": "企业导师评分",
    "方案可行性": "企业导师评分",
    "操作规范性": "企业导师评分",
    # → Ai评分
    "操作规范": "Ai评分",
    "风险评估": "Ai评分",
    "用时效率": "Ai评分",
    # → 学生评分（三个环节共用）
    "团队配合": "学生评分",
}

NEW_DIMENSIONS = ["教师评分", "企业导师评分", "Ai评分", "学生评分"]


def main():
    db = SessionLocal()
    try:
        sessions = db.query(ScoreSession).all()
        if not sessions:
            print("没有评分会话，无需迁移")
            return

        rec_total = 0
        for r in db.query(ScoreRecord).all():
            if r.dimension in RENAME_MAP:
                r.dimension = RENAME_MAP[r.dimension]
                rec_total += 1

        sess_total = 0
        for s in sessions:
            dims = s.dimensions
            if isinstance(dims, str):
                dims = json.loads(dims)
            if isinstance(dims, list) and any(d in RENAME_MAP for d in dims):
                s.dimensions = json.dumps(NEW_DIMENSIONS, ensure_ascii=False)
                sess_total += 1

        db.commit()
        print(f"迁移完成：共 {len(sessions)} 个会话，更新打分记录 {rec_total} 条，更新会话维度配置 {sess_total} 个")
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
