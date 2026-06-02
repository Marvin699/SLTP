#!/usr/bin/env python3
"""
真实测试项目优化器，使用默认配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from pathlib import Path

# 加载数据
work_dir = Path(__file__).parent.parent / "work"
module01 = json.load(open(work_dir / "module01.json", "r", encoding="utf-8"))
module02 = json.load(open(work_dir / "module02.json", "r", encoding="utf-8"))
module03 = json.load(open(work_dir / "module03.json", "r", encoding="utf-8"))

# 村庄坐标和距离数据
village_coords = {
    "东风村": {"latitude": 23.30904, "longitude": 106.32015, "distance": 0.34},
    "新和村": {"latitude": 23.295, "longitude": 106.335, "distance": 2.5},
    "怀渠村": {"latitude": 23.345, "longitude": 106.285, "distance": 5.05},
    "怀书村": {"latitude": 23.340, "longitude": 106.290, "distance": 5.06},
    "雅力村": {"latitude": 23.250, "longitude": 106.380, "distance": 9.29},
    "古桥村": {"latitude": 23.200, "longitude": 106.350, "distance": 12.74},
    "坡乐村": {"latitude": 23.090, "longitude": 106.420, "distance": 26.96},
    "塘麻村": {"latitude": 23.085, "longitude": 106.425, "distance": 27.39},
}

def build_task():
    """构建任务数据（和 module03.json 中的默认配置一致）"""
    
    # 无人机配置：FlyCart 100 5架 + JDX-500 8架（和 module03.json 一致）
    uavs = []
    uav_specs = {u['id']: u for u in module03['all_models']}
    
    # FlyCart 100 5架
    fc100_spec = uav_specs['dji-fc100']
    for i in range(5):
        uavs.append({
            "id": f"dji-fc100-{i+1}",
            "name": fc100_spec['model'],
            "max_payload": fc100_spec['max_payload'],
            "max_range": fc100_spec['range_km'],
            "battery_capacity": 100,
            "max_speed": fc100_spec['max_speed'],
            "range_points": fc100_spec['range_points'],
        })
    
    # JDX-500 8架
    jdx500_spec = uav_specs['jd-jdx500']
    for i in range(8):
        uavs.append({
            "id": f"jd-jdx500-{i+1}",
            "name": jdx500_spec['model'],
            "max_payload": jdx500_spec['max_payload'],
            "max_range": jdx500_spec['range_km'],
            "battery_capacity": 100,
            "max_speed": jdx500_spec['max_speed'],
            "range_points": jdx500_spec['range_points'],
        })
    
    # 需求点
    demand_points = []
    for assignment in module02.get('assignments', []):
        point_name = assignment['point_name']
        coords = village_coords.get(point_name, {"latitude": 0, "longitude": 0})
        
        # 转换优先级
        priority_map = {1: 'urgent', 2: 'high', 3: 'medium', 4: 'low'}
        priority = priority_map.get(assignment.get('priority', 3), 'medium')
        
        demand_points.append({
            "id": assignment['point_id'],
            "name": point_name,
            "longitude": coords['longitude'],
            "latitude": coords['latitude'],
            "total_weight": assignment['total_weight'],
            "priority": priority,
            "delivery_mode": assignment.get('delivery_mode', 'optional'),
            "special_requirements": assignment.get('special_requirements', ''),
        })
    
    return {
        "depot": module01.get('center', {}),
        "demand_points": demand_points,
        "uavs": uavs,
        "distance_matrix": module01.get('distance_matrix', []),
    }

def main():
    print("🚀 测试项目优化器 - 默认配置 (FlyCart 100 5架 + JDX-500 8架)")
    print("="*80)
    
    # 构建任务
    task_data = build_task()
    print(f"\n📦 无人机配置 ({len(task_data['uavs'])}架):")
    for uav in task_data['uavs']:
        print(f"   - {uav['name']} ({uav['id']}): 载重={uav['max_payload']}kg, 航程={uav['max_range']}km")
    
    print(f"\n📋 需求点 ({len(task_data['demand_points'])}个):")
    for dp in task_data['demand_points']:
        coords = village_coords.get(dp['name'], {"distance": 0})
        print(f"   - {dp['name']}: {dp['total_weight']}kg, {dp['priority']}, 距离={coords['distance']}km")
    
    # 调用项目优化器
    from app.services.optimizer.optimizer_service import run_optimizer
    
    print(f"\n🔍 开始运行优化...")
    result = run_optimizer(task_data)
    
    print(f"\n✅ 优化完成!")
    print(f"   总趟数: {result['summary']['total_trips']}")
    print(f"   总距离: {result['summary']['total_distance']}km")
    print(f"   可行: {result['feasibility']['feasible']}")
    
    # 输出问题
    issues = result['feasibility'].get('issues', [])
    warnings = result['feasibility'].get('warnings', [])
    
    if issues:
        print(f"\n❌ 问题 ({len(issues)}个):")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}个):")
        for warning in warnings[:10]:
            print(f"   - {warning}")
    
    # 输出村庄覆盖情况（直接从 solution 中看）
    print(f"\n📊 村庄覆盖详情:")
    trips = result['solution']['trips']
    village_delivered = {}
    for trip in trips:
        village = trip['village_name']
        if village not in village_delivered:
            village_delivered[village] = 0
        village_delivered[village] += trip['load']
    
    for dp in task_data['demand_points']:
        village = dp['name']
        delivered = village_delivered.get(village, 0)
        demand = dp['total_weight']
        coverage = (delivered / demand * 100) if demand > 0 else 0
        print(f"   - {village}: 配送={delivered}kg/需求={demand}kg, 覆盖率={coverage:.1f}%")
    
    # 输出无人机分配
    print(f"\n🚁 无人机分配:")
    drone_trips = {}
    for trip in trips:
        drone = trip['drone_name']
        if drone not in drone_trips:
            drone_trips[drone] = {'trips': 0, 'load': 0}
        drone_trips[drone]['trips'] += 1
        drone_trips[drone]['load'] += trip['load']
    
    for drone, data in sorted(drone_trips.items()):
        print(f"   - {drone}: 趟数={data['trips']}, 总载重={data['load']}kg")
    
    # 规则诊断
    print(f"\n🔧 运行规则诊断...")
    from app.services.ai.diagnosis_service import run_rule_diagnosis
    diag_result = run_rule_diagnosis(task_data, {
        "solution": result['solution'],
        "feasibility": result['feasibility']
    })
    
    print(f"\n📈 规则诊断结果:")
    print(f"   综合评分: {diag_result['score']}")
    print(f"   四维评分: 安全={diag_result['four_dimensional_scores']['safety']} "
          f"时效={diag_result['four_dimensional_scores']['timeliness']} "
          f"经济={diag_result['four_dimensional_scores']['economy']} "
          f"可行={diag_result['four_dimensional_scores']['feasibility']}")
    
    if diag_result.get('issues'):
        print(f"\n❌ 诊断问题:")
        for issue in diag_result['issues']:
            print(f"   - {issue}")
    
    if diag_result.get('warnings'):
        print(f"\n⚠️ 诊断警告:")
        for warning in diag_result['warnings']:
            print(f"   - {warning}")

if __name__ == "__main__":
    main()
