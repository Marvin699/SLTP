#!/usr/bin/env python3
"""
修复后的诊断测试
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
village_data = {
    "东风村": {"distance": 0.34, "latitude": 23.30904, "longitude": 106.32015},
    "新和村": {"distance": 2.5, "latitude": 23.295, "longitude": 106.335},
    "怀渠村": {"distance": 5.05, "latitude": 23.345, "longitude": 106.285},
    "怀书村": {"distance": 5.06, "latitude": 23.340, "longitude": 106.290},
    "雅力村": {"distance": 9.29, "latitude": 23.250, "longitude": 106.380},
    "古桥村": {"distance": 12.74, "latitude": 23.200, "longitude": 106.350},
    "坡乐村": {"distance": 26.96, "latitude": 23.090, "longitude": 106.420},
    "塘麻村": {"distance": 27.39, "latitude": 23.085, "longitude": 106.425},
}

def get_range_by_weight(weight, uav):
    points = uav.get('range_points', [])
    max_payload = uav.get('max_payload', 0)
    max_range = uav.get('range_km', uav.get('max_range', 20))
    
    if not points:
        if weight <= 0:
            return max_range
        if weight >= max_payload:
            return max_range * 0.3
        return max_range * (1 - 0.7 * weight / max_payload)
    
    if weight <= 0:
        return points[0][1]
    if weight >= max_payload:
        return points[-1][1]
    
    for i in range(len(points) - 1):
        w1, r1 = points[i]
        w2, r2 = points[i + 1]
        if w1 <= weight <= w2:
            t = (weight - w1) / (w2 - w1) if w2 != w1 else 0
            return r1 + (r2 - r1) * t
    return points[-1][1]

def build_task(uav_configs):
    uav_specs = {u['id']: u for u in module03['all_models']}
    
    uavs = []
    for config in uav_configs:
        model_id = config['model_id']
        quantity = config['quantity']
        spec = uav_specs.get(model_id)
        
        if not spec:
            continue
        
        for i in range(quantity):
            uavs.append({
                "id": f"{model_id}-{i+1}",
                "name": spec['model'],
                "max_payload": spec['max_payload'],
                "max_range": spec.get('range_km', spec.get('max_range', 20)),
                "battery_capacity": 100,
                "max_speed": spec.get('max_speed', 60),
                "range_points": spec.get('range_points', []),
            })
    
    # 从assignments获取需求点数据
    demand_points = []
    for assignment in module02.get('assignments', []):
        point_name = assignment['point_name']
        coords = village_data.get(point_name, {"latitude": 0, "longitude": 0})
        
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
        "depot": module01.get('depot', {}),
        "demand_points": demand_points,
        "uavs": uavs,
    }

def build_real_solution(task):
    trips = []
    trip_id = 0
    
    # 按优先级排序需求点
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_demand = sorted(task['demand_points'], key=lambda x: priority_order.get(x.get('priority', 'medium'), 2))
    
    for dp in sorted_demand:
        village_name = dp['name']
        demand = dp['total_weight']
        distance = village_data.get(village_name, {}).get('distance', 5)
        
        # 找到能覆盖这个村庄的无人机
        suitable_uavs = []
        for uav in task['uavs']:
            round_trip = distance * 2
            eff_range = get_range_by_weight(uav['max_payload'] * 0.8, uav)
            if round_trip <= eff_range:
                suitable_uavs.append(uav)
        
        if not suitable_uavs:
            continue
        
        # 使用第一架合适的无人机
        uav = suitable_uavs[0]
        load_per_trip = uav['max_payload'] * 0.8
        round_trip = distance * 2
        
        # 创建多趟任务
        remaining = demand
        while remaining > 0:
            load = min(load_per_trip, remaining)
            
            trips.append({
                "trip_id": trip_id,
                "drone_id": uav['id'],
                "drone_name": uav['name'],
                "drone_type": uav['name'],
                "village_name": village_name,
                "load": load,
                "total_distance": round_trip,
                "feasible": True,
                "villages": [{
                    "name": village_name,
                    "latitude": dp['latitude'],
                    "longitude": dp['longitude'],
                }],
            })
            remaining -= load
            trip_id += 1
    
    # 计算需求覆盖
    demand_coverage = {}
    for dp in task['demand_points']:
        delivered = sum(t['load'] for t in trips if t['village_name'] == dp['name'])
        demand_coverage[dp['name']] = {
            "demand": dp['total_weight'],
            "delivered": delivered,
            "shortfall": max(0, dp['total_weight'] - delivered),
            "trip_count": sum(1 for t in trips if t['village_name'] == dp['name']),
        }
    
    return {
        "solution": {
            "trips": trips,
            "summary": {
                "total_trips": len(trips),
                "total_distance": sum(t.get('total_distance', 0) for t in trips),
            }
        },
        "feasibility": {
            "feasible": True,
            "issues": [],
            "warnings": [],
            "demand_coverage": demand_coverage,
        }
    }

def test_plan(name, uav_configs):
    print(f"\n{'='*70}")
    print(f"测试方案: {name}")
    print('='*70)
    
    task = build_task(uav_configs)
    solution = build_real_solution(task)
    
    print(f"\n📋 需求点 ({len(task['demand_points'])}个):")
    for dp in task['demand_points']:
        print(f"   - {dp['name']}: {dp['total_weight']}kg, {dp['priority']}")
    
    print(f"\n🚁 配送趟数: {len(solution['solution']['trips'])}")
    
    from app.services.ai.diagnosis_service import run_rule_diagnosis
    result = run_rule_diagnosis(task, solution)
    
    print(f"\n📊 规则诊断结果:")
    print(f"   综合评分: {result.get('score', 0)}")
    
    scores = result.get('four_dimensional_scores', {})
    print(f"   四维评分: 安全={scores.get('safety', 0)} 时效={scores.get('timeliness', 0)} 经济={scores.get('economy', 0)} 可行={scores.get('feasibility', 0)}")
    
    issues = result.get('issues', [])
    warnings = result.get('warnings', [])
    
    if issues:
        print(f"\n   ❌ 问题 ({len(issues)}个):")
        for issue in issues[:5]:
            print(f"     - {issue}")
    
    if warnings:
        print(f"\n   ⚠️ 警告 ({len(warnings)}个):")
        for warning in warnings[:5]:
            print(f"     - {warning}")
    
    return result.get('score', 0) >= 80, result

plans = [
    {"name": "方案一：全JDX-500(8架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 8}]},
    {"name": "方案二：全JDX-500(10架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 10}]},
    {"name": "方案三：全JDX-500(12架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 12}]},
    {"name": "方案四：JDX-500(6架)+ARK80(6架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 6}, {"model_id": "fy-ark80", "quantity": 6}]},
    {"name": "方案五：JDX-500(7架)+ARK80(7架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 7}, {"model_id": "fy-ark80", "quantity": 7}]},
    {"name": "方案六：JDX-500(5架)+ARK80(8架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 5}, {"model_id": "fy-ark80", "quantity": 8}]},
    {"name": "方案七：全ARK80(20架)", "uavs": [{"model_id": "fy-ark80", "quantity": 20}]},
]

print("🚀 使用规则诊断服务测试方案")
print("="*70)

high_score_plans = []
for plan in plans:
    success, result = test_plan(plan['name'], plan['uavs'])
    if success:
        high_score_plans.append((plan, result))

print(f"\n{'='*70}")
print(f"✅ 评分>=80的方案: {len(high_score_plans)}/{len(plans)}")
print('='*70)

for plan, result in high_score_plans:
    print(f"\n{plan['name']}")
    print(f"   综合评分: {result['score']}")
    for uav in plan['uavs']:
        specs = next(m for m in module03['all_models'] if m['id'] == uav['model_id'])
        print(f"   - {specs['model']}: {uav['quantity']}架")
