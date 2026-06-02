#!/usr/bin/env python3
"""
测试多种无人机配置
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

# 村庄坐标和距离
village_coords = {
    "东风村": {"distance": 0.34, "latitude": 23.30904, "longitude": 106.32015},
    "新和村": {"distance": 2.5, "latitude": 23.295, "longitude": 106.335},
    "怀渠村": {"distance": 5.05, "latitude": 23.345, "longitude": 106.285},
    "怀书村": {"distance": 5.06, "latitude": 23.33903, "longitude": 106.27867},
    "雅力村": {"distance": 9.29, "latitude": 23.25, "longitude": 106.38},
    "古桥村": {"distance": 12.74, "latitude": 23.2, "longitude": 106.35},
    "坡乐村": {"distance": 26.96, "latitude": 23.075, "longitude": 106.38},
    "塘麻村": {"distance": 27.39, "latitude": 23.085, "longitude": 106.425},
}

def build_task(uav_configs):
    """构建任务数据"""
    # 无人机配置
    uav_specs = {u['id']: u for u in module03['all_models']}
    uavs = []
    idx = 1
    for model_id, count in uav_configs:
        spec = uav_specs[model_id]
        for i in range(count):
            uavs.append({
                "id": f"{model_id}-{idx}",
                "name": spec['model'],
                "max_payload": spec['max_payload'],
                "max_range": spec['range_km'],
                "battery_capacity": 100,
                "max_speed": spec.get('max_speed', 60),
                "range_points": spec.get('range_points', []),
            })
            idx += 1
    
    # 需求点
    demand_points = []
    for assignment in module02.get('assignments', []):
        point_name = assignment['point_name']
        coords = village_coords.get(point_name, {"latitude": 0, "longitude": 0})
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

def test_config(name, uav_configs):
    """测试单个配置"""
    print(f"\n{'='*80}")
    print(f"测试: {name}")
    print(f"{'='*80}")
    
    # 打印配置
    uav_specs = {u['id']: u for u in module03['all_models']}
    print(f"\n📦 配置:")
    total_uavs = 0
    for model_id, count in uav_configs:
        spec = uav_specs[model_id]
        print(f"   - {spec['model']}: {count}架 (载重={spec['max_payload']}kg, 航程={spec['range_km']}km)")
        total_uavs += count
    print(f"   总计: {total_uavs}架")
    
    # 构建任务
    task_data = build_task(uav_configs)
    
    # 运行优化
    from app.services.optimizer.optimizer_service import run_optimizer
    result = run_optimizer(task_data)
    
    # 计算覆盖率
    trips = result['solution']['trips']
    village_delivered = {}
    for trip in trips:
        village = trip['village_name']
        if village not in village_delivered:
            village_delivered[village] = 0
        village_delivered[village] += trip['load']
    
    full_coverage = True
    print(f"\n📊 覆盖:")
    for dp in task_data['demand_points']:
        village = dp['name']
        delivered = village_delivered.get(village, 0)
        demand = dp['total_weight']
        coverage = (delivered / demand * 100) if demand > 0 else 0
        if coverage < 100:
            full_coverage = False
        status = "✅" if coverage >= 100 else "❌"
        print(f"   {status} {village}: {delivered:.0f}kg/{demand}kg ({coverage:.1f}%)")
    
    # 规则诊断
    from app.services.ai.diagnosis_service import run_rule_diagnosis
    diag_result = run_rule_diagnosis(task_data, {
        "solution": result['solution'],
        "feasibility": result['feasibility'],
    })
    
    print(f"\n📈 评分: {diag_result['score']:.1f}")
    print(f"   安全={diag_result['four_dimensional_scores']['safety']} "
          f"时效={diag_result['four_dimensional_scores']['timeliness']} "
          f"经济={diag_result['four_dimensional_scores']['economy']} "
          f"可行={diag_result['four_dimensional_scores']['feasibility']}")
    
    # 打印主要问题
    issues = diag_result.get('issues', [])
    if issues:
        print(f"\n❌ 问题:")
        for issue in issues[:5]:
            print(f"   - {issue}")
    
    warnings = diag_result.get('warnings', [])
    if warnings:
        print(f"\n⚠️ 警告:")
        for warning in warnings[:5]:
            print(f"   - {warning}")
    
    return diag_result['score'], full_coverage

# 测试多种配置
configs_to_test = [
    ("全JDX-500(10架)", [("jd-jdx500", 10)]),
    ("全JDX-500(12架)", [("jd-jdx500", 12)]),
    ("全JDX-500(14架)", [("jd-jdx500", 14)]),
    ("JDX-500(6)+FlyCart30(6)", [("jd-jdx500", 6), ("dji-fc30", 6)]),
    ("JDX-500(8)+FlyCart30(8)", [("jd-jdx500", 8), ("dji-fc30", 8)]),
    ("JDX-500(6)+ARK80(8)", [("jd-jdx500", 6), ("fy-ark80", 8)]),
    ("JDX-500(8)+ARK80(6)", [("jd-jdx500", 8), ("fy-ark80", 6)]),
    ("全ARK80(25架)", [("fy-ark80", 25)]),
    ("JDX-500(8)+ARK80(8)", [("jd-jdx500", 8), ("fy-ark80", 8)]),
    ("JDX-500(10)+FlyCart100(6)", [("jd-jdx500", 10), ("dji-fc100", 6)]),
]

# 测试
results = []
for name, config in configs_to_test:
    score, full_coverage = test_config(name, config)
    results.append((score, full_coverage, name, config))

# 总结
print(f"\n{'='*80}")
print("📊 测试结果总结:")
print(f"{'='*80}")

# 按评分排序
results.sort(reverse=True, key=lambda x: x[0])

print(f"\n排名  评分  100%覆盖  配置")
for i, (score, full_coverage, name, config) in enumerate(results, 1):
    coverage = "✅" if full_coverage else "❌"
    print(f"{i:2d}.   {score:4.1f}    {coverage}       {name}")

print(f"\n{'='*80}")
print("🎯 推荐方案:")
print(f"{'='*80}")

# 显示高分方案
print(f"\n高分方案:")
for score, full_coverage, name, config in results[:3]:
    coverage = "✅" if full_coverage else "❌"
    print(f"\n{name} (评分={score:.1f} 覆盖={coverage}):")
    uav_specs = {u['id']: u for u in module03['all_models']}
    for model_id, count in config:
        spec = uav_specs[model_id]
        print(f"   - {spec['model']}: {count}架")

print(f"\n")
