import requests
import json

# 1. 先清空所有点位数据，创建新的需求点
print('=== 步骤1: 创建新需求点 ===')
points_data = {
    'points': [
        {'name': '中心', 'point_type': 'center', 'longitude': 108.0, 'latitude': 22.0},
        {'name': '01', 'point_type': 'demand', 'longitude': 108.1, 'latitude': 22.1},
    ]
}
res = requests.post('http://localhost:8000/api/path-planning/points/batch', json=points_data)
if res.status_code in [200, 201]:
    new_points = res.json()
    print(f'创建的需求点ID: {[p["id"] for p in new_points]}')
    print(f'创建的需求点名称: {[p["name"] for p in new_points]}')
    
    # 需求点ID应该是2（第一个是中心，ID=1；第二个是01，ID=2）
    demand_point_id = new_points[1]['id']
    
    # 2. 保存物资数据
    print(f'\n=== 步骤2: 保存物资数据 (point_id={demand_point_id}) ===')
    assignment_data = {
        'point_id': demand_point_id,
        'point_name': '01',
        'category_ids': ['repair'],
        'items': [
            {'name': '抢修', 'unit_weight': 30, 'qty': 2, 'subtotal': 60}
        ],
        'total_weight': 60,
        'priority': 3,
        'special_requirements': '',
        'risk_warnings': '',
        'supply_types': ['repair']
    }
    save_res = requests.post('http://localhost:8000/api/path-planning/materials/save', json=assignment_data)
    print(f'保存结果: {save_res.status_code}')
    if save_res.status_code not in [200, 201]:
        print(f'错误信息: {save_res.text}')
    
    # 3. 加载物资数据
    print('\n=== 步骤3: 加载物资数据 ===')
    load_res = requests.get('http://localhost:8000/api/path-planning/materials/saved')
    if load_res.status_code == 200:
        loaded_data = load_res.json()
        print(f'加载的数据keys: {list(loaded_data.keys())}')
        print(f'加载的数据: {json.dumps(loaded_data, indent=2, ensure_ascii=False)}')
        
        # 检查是否包含我们保存的point_id
        if str(demand_point_id) in loaded_data:
            print(f'\n✅ 测试成功！数据已正确保存和加载')
            print(f'   point_id={demand_point_id} 的数据存在')
        else:
            print(f'\n❌ 测试失败！数据没有正确保存')
            print(f'   期望 point_id={demand_point_id}，但实际 keys 是 {list(loaded_data.keys())}')
    else:
        print(f'加载失败: {load_res.status_code}')
        print(f'错误信息: {load_res.text}')
else:
    print(f'创建失败: {res.status_code}')
    print(f'错误信息: {res.text}')
