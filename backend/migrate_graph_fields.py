"""为course_projects表添加四个图谱字段"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "path_planning_data.db")

NEW_COLUMNS = [
    ("knowledge_graph", "TEXT"),
    ("capability_graph", "TEXT"),
    ("problem_graph", "TEXT"),
    ("ideological_graph", "TEXT"),
]

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}，跳过迁移")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取现有列
    cursor.execute("PRAGMA table_info(course_projects)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE course_projects ADD COLUMN {col_name} {col_type}")
            print(f"  + 添加列: {col_name}")
        else:
            print(f"  - 列已存在: {col_name}")

    conn.commit()
    conn.close()
    print("迁移完成!")

if __name__ == "__main__":
    migrate()
