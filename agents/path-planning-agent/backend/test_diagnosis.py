#!/usr/bin/env python3
"""
使用项目规则诊断服务实际测试方案（改进版）
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

# 村庄距离数据
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
    """根据载重计算有效航程"""
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

# 构建任务数据
def build_task(uav_configs):
    """构建任务配置"""
    uav_specs = {u['id']: u for u in module03['all_models']}
    
    # 构建无人机列表
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
    
    # 需求点
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

# 构建真实的方案
def build_real_solution(task):
    """构建真实的配送方案"""
    trips = []
    trip_id = 0
    
    # 按优先级排序需求点
    sorted_demand = sorted(task['demand_points'], key=lambda x: {
        'urgent': 0, 'high': 1, 'medium': 2, 'low': 3
    }.get(x.get('priority', 'medium'), 2))
    
    # 为每个需求点分配无人机
    for dp in sorted_demand:
        village_name = dp['name']
        demand = dp['total_weight']
        distance = village_distances.get(village_name, 5)
        
        # 找到能覆盖这个村庄的无人机
        suitable_uavs = []
        for uav in task['uavs']:
            # 检查航程是否足够
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
                    "latitude": next(d['latitude'] for d in task['demand_points'] if d['name'] == village_name),
                    "longitude": next(d['longitude'] for d in task['demand_points'] if d['name'] == village_name),
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

# 测试方案
def test_plan(name, uav_configs):
    """测试单个方案"""
    print(f"\n{'='*70}")
    print(f"测试方案: {name}")
    print('='*70)
    
    # 构建任务和方案
    task = build_task(uav_configs)
    solution = build_real_solution(task)
    
    # 导入诊断服务
    try:
        from app.services.ai.diagnosis_service import run_rule_diagnosis
        
        # 执行规则诊断
        result = run_rule_diagnosis(task, solution)
        
        print(f"\n📊 规则诊断结果:")
        print(f"   综合评分: {result.get('score', 0)}")
        print(f"   可行性: {result.get('feasible', False)}")
        
        scores = result.get('four_dimensional_scores', {})
        print(f"\n   四维评分:")
        print(f"     安全性: {scores.get('safety', 0)}")
        print(f"     时效性: {scores.get('timeliness', 0)}")
        print(f"     经济性: {scores.get('economy', 0)}")
        print(f"     可行性: {scores.get('feasibility', 0)}")
        
        # 输出问题和警告
        issues = result.get('issues', [])
        warnings = result.get('warnings', [])
        
        if issues:
            print(f"\n   ❌ 问题:")
            for issue in issues[:3]:
                print(f"     - {issue}")
        
        if warnings:
            print(f"\n   ⚠️ 警告:")
            for warning in warnings[:5]:
                print(f"     - {warning}")
        
        return result.get('score', 0) >= 80, result
    
    except Exception as e:
        import traceback
        print(f"❌ 诊断失败: {e}")
        traceback.print_exc()
        return False, None

# 7种方案
plans = [
    {"name": "方案一：全JDX-500(8架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 8}]},
    {"name": "方案二：全JDX-500(10架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 10}]},
    {"name": "方案三：全JDX-500(12架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 12}]},
    {"name": "方案四：全JDX-500(14架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 14}]},
    {"name": "方案五：JDX-500(6架)+ARK80(6架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 6}, {"model_id": "fy-ark80", "quantity": 6}]},
    {"name": "方案六：JDX-500(7架)+ARK80(7架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 7}, {"model_id": "fy-ark80", "quantity": 7}]},
    {"name": "方案七：JDX-500(5架)+ARK80(8架)", "uavs": [{"model_id": "jd-jdx500", "quantity": 5}, {"model_id": "fy-ark80", "quantity": 8}]},
]

# 测试所有方案
print("🚀 使用规则诊断服务测试方案（改进版）")
print("="*70)

high_score_plans = []
for plan in plans:
    success, result = test_plan(plan['name'], plan['uavs'])
    if success:
        high_score_plans.append((plan, result))

# 输出结果
print(f"\n{'='*70}")
print(f"✅ 评分>=80的方案: {len(high_score_plans)}/{len(plans)}")
print('='*70)

for plan, result in high_score_plans:
    print(f"\n{plan['name']}")
    print(f"   综合评分: {result['score']}")
    for uav in plan['uavs']:
        specs = next(m for m in module03['all_models'] if m['id'] == uav['model_id'])
        print(f"   - {specs['model']}: {uav['quantity']}架")
