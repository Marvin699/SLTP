import sqlite3, json

conn = sqlite3.connect('path_planning_data.db')
cursor = conn.cursor()

cursor.execute("SELECT sub_projects FROM course_projects WHERE project_id = 'P5'")
row = cursor.fetchone()
if not row:
    print('P5 not found')
    exit(1)

data = json.loads(row[0])

for sp in data:
    for task in sp.get('tasks', []):
        if task['id'] == 8:
            for pt in task.get('points', []):
                if pt['id'] == '8-3':
                    pt['name'] = '飞行前准备应急综合演练'
            has_87 = any(p['id'] == '8-7' for p in task.get('points', []))
            if not has_87:
                task['points'].append({
                    'id': '8-7',
                    'name': '物资投送应急综合演练',
                    'type': 'skill',
                    'standard': '1+X（高级）、审定指南§4.2(f)',
                    'desc': '包含物资装载、航线规划、精准投放等场景'
                })
            print('Updated task 8 points:')
            for p in task['points']:
                print(f"  {p['id']}: {p['name']}")

new_json = json.dumps(data, ensure_ascii=False)
cursor.execute("UPDATE course_projects SET sub_projects = ? WHERE project_id = 'P5'", (new_json,))
conn.commit()
conn.close()
print('Database updated successfully')
