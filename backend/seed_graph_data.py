"""将four-graph-data.json中的四图谱数据导入P5项目"""
import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "path_planning_data.db")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "four-graph-data.json")

def seed():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        return
    if not os.path.exists(DATA_PATH):
        print(f"数据文件不存在: {DATA_PATH}")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查P5是否存在
    cursor.execute("SELECT project_id FROM course_projects WHERE project_id = 'P5'")
    if not cursor.fetchone():
        print("P5项目不存在，请先创建")
        conn.close()
        return

    # 更新四个图谱字段
    fields = {
        "knowledge_graph": data.get("knowledge_graph"),
        "capability_graph": data.get("capability_graph"),
        "problem_graph": data.get("problem_graph"),
        "ideological_graph": data.get("ideological_graph"),
    }

    for field, value in fields.items():
        if value:
            json_str = json.dumps(value, ensure_ascii=False)
            cursor.execute(f"UPDATE course_projects SET {field} = ? WHERE project_id = 'P5'", (json_str,))
            print(f"  + 导入 {field}")

    conn.commit()
    conn.close()
    print("P5四图谱数据导入完成!")

if __name__ == "__main__":
    seed()
