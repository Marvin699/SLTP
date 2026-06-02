#!/usr/bin/env python3
"""
调试诊断评分问题
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

village_distances = {
    "东风村": 0.34,
    "新和村": 2.5,
    "怀渠村": 5.05,
    "怀书村": 5.06,
    "雅力村": 9.29,
    "古桥村": 12.74,
    "坡乐村": 26.96,
    "塘麻村": 27.39,
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
    
    demand_points = []
    for dp in module02.get('demand_points', []):
        demand_points.append({
            "id": dp['id'],
            "name": dp['name'],
            "longitude": dp['longitude'],
            "latitude": dp['latitude'],
            "total_weight": dp['total_weight'],
            "priority": dp.get('priority', 'medium'),
            "delivery_mode": dp.get('delivery_mode', 'optional'),
        })
    
    return {
        "depot": module01.get('depot', {}),
        "demand_points": demand_points,
        "uavs": uavs,
    }

def build_real_solution(task):
    trips = []
    trip_id = 0
    
    sorted_demand = sorted(task['demand_points'], key=lambda x: {
        'urgent': 0, 'high': 1, 'medium': 2, 'low': 3
    }.get(x.get('priority', 'medium'), 2))
    
    for dp in sorted_demand:
        village_name = dp['name']
        demand = dp['total_weight']
        distance = village_distances.get(village_name, 5)
        
        suitable_uavs = []
        for uav in task['uavs']:
            round_trip = distance * 2
            eff_range = get_range_by_weight(uav['max_payload'] * 0.8, uav)
            if round_trip <= eff_range:
                suitable_uavs.append(uav)
        
        if not suitable_uavs:
            continue
        
        uav = suitable_uavs[0]
        load_per_trip = uav['max_payload'] * 0.8
        round_trip = distance * 2
        
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
                    "latitude": next(d['latitude'] for d in task['demand_points'] if d['name'] == village_name),
                    "longitude": next(d['longitude'] for d in task['demand_points'] if d['name'] == village_name),
                }],
            })
            remaining -= load
            trip_id += 1
    
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

# 测试方案
from app.services.ai.diagnosis_service import run_rule_diagnosis

# 测试方案一：全JDX-500(8架)
print("🚀 调试诊断评分问题")
print("="*70)

uav_configs = [{"model_id": "jd-jdx500", "quantity": 8}]
task = build_task(uav_configs)
solution = build_real_solution(task)

print(f"\n📦 无人机配置:")
for uav in task['uavs']:
    print(f"   - {uav['name']}: {uav['id']}, 载重: {uav['max_payload']}kg, 航程: {uav['max_range']}km")

print(f"\n📋 需求点:")
for dp in task['demand_points']:
    print(f"   - {dp['name']}: {dp['total_weight']}kg, 优先级: {dp.get('priority', 'medium')}")

print(f"\n🚁 配送方案:")
for trip in solution['solution']['trips'][:5]:  # 只显示前5趟
    print(f"   - 趟次{trip['trip_id']}: {trip['drone_name']} -> {trip['village_name']}, 载重: {trip['load']:.1f}kg, 距离: {trip['total_distance']:.1f}km")

print(f"\n📊 需求覆盖:")
for village, coverage in solution['feasibility']['demand_coverage'].items():
    status = "✅" if coverage['shortfall'] == 0 else "❌"
    print(f"   {status} {village}: {coverage['delivered']}/{coverage['demand']}kg")

result = run_rule_diagnosis(task, solution)

print(f"\n{'='*70}")
print("📊 诊断结果详情:")
print(f"   综合评分: {result.get('score', 0)}")
print(f"   可行性: {result.get('feasible', False)}")

scores = result.get('four_dimensional_scores', {})
print(f"\n   四维评分:")
print(f"     安全性: {scores.get('safety', 0)}")
print(f"     时效性: {scores.get('timeliness', 0)}")
print(f"     经济性: {scores.get('economy', 0)}")
print(f"     可行性: {scores.get('feasibility', 0)}")

issues = result.get('issues', [])
warnings = result.get('warnings', [])

if issues:
    print(f"\n   ❌ 问题 ({len(issues)}个):")
    for issue in issues:
        print(f"     - {issue}")

if warnings:
    print(f"\n   ⚠️ 警告 ({len(warnings)}个):")
    for warning in warnings[:10]:
        print(f"     - {warning}")

suggestions = result.get('suggestions', [])
if suggestions:
    print(f"\n   💡 建议 ({len(suggestions)}个):")
    for suggestion in suggestions[:5]:
        print(f"     - {suggestion}")
