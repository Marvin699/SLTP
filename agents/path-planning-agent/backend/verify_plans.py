#!/usr/bin/env python3
"""
验证7种高分方案 - 基于规则诊断评分机制
"""
import json
from pathlib import Path

# 加载数据
work_dir = Path(__file__).parent.parent / "work"
module01 = json.load(open(work_dir / "module01.json", "r", encoding="utf-8"))
module02 = json.load(open(work_dir / "module02.json", "r", encoding="utf-8"))
module03 = json.load(open(work_dir / "module03.json", "r", encoding="utf-8"))

# 村庄数据
village_data = {
    "东风村": {"distance": 0.34, "demand": 250, "priority": "urgent"},
    "新和村": {"distance": 2.5, "demand": 20, "priority": "urgent"},
    "怀渠村": {"distance": 5.05, "demand": 100, "priority": "high"},
    "怀书村": {"distance": 5.06, "demand": 145, "priority": "medium"},
    "雅力村": {"distance": 9.29, "demand": 200, "priority": "high"},
    "古桥村": {"distance": 12.74, "demand": 61, "priority": "medium"},
    "坡乐村": {"distance": 26.96, "demand": 140, "priority": "high"},
    "塘麻村": {"distance": 27.39, "demand": 570, "priority": "medium"},
}

def get_range_by_weight(weight, uav):
    """根据载重计算有效航程"""
    points = uav.get('range_points', [])
    max_payload = uav.get('max_payload', 0)
    max_range = uav.get('range_km', 20)
    
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

def analyze_plan(plan_name, uav_configs):
    """分析方案得分"""
    print(f"\n{'='*70}")
    print(f"方案: {plan_name}")
    print('='*70)
    
    # 获取无人机规格
    uav_specs = {}
    for uav in module03['all_models']:
        uav_specs[uav['id']] = uav
    
    # 检查航程约束
    total_trips = 0
    total_distance = 0
    feasible = True
    
    for config in uav_configs:
        model_id = config['model_id']
        quantity = config['quantity']
        uav = uav_specs.get(model_id)
        
        if not uav:
            print(f"❌ 未知机型: {model_id}")
            feasible = False
            continue
        
        model = uav['model']
        max_payload = uav['max_payload']
        max_range = uav['range_km']
        
        # 计算80%载重时的有效航程
        eff_range_80 = get_range_by_weight(max_payload * 0.8, uav)
        
        print(f"\n📦 {model}: {quantity}架")
        print(f"   最大载重: {max_payload}kg, 标称航程: {max_range}km")
        print(f"   80%载重时有效航程: {eff_range_80:.1f}km")
        
        # 检查能覆盖哪些村庄
        coverable = []
        not_coverable = []
        avg_load_per_trip = max_payload * 0.8
        
        for village, info in village_data.items():
            distance = info['distance']
            demand = info['demand']
            round_trip = distance * 2
            trips_needed = (demand + avg_load_per_trip - 1) // avg_load_per_trip
            
            if round_trip <= eff_range_80:
                coverable.append(f"{village}({distance:.1f}km, {trips_needed}趟)")
                total_trips += trips_needed * quantity
                total_distance += trips_needed * round_trip * quantity
            else:
                not_coverable.append(f"{village}({distance:.1f}km)")
                feasible = False
        
        if coverable:
            print(f"   ✅ 可覆盖: {', '.join(coverable)}")
        if not_coverable:
            print(f"   ❌ 不可覆盖: {', '.join(not_coverable)}")
    
    # 计算理论最优距离
    theoretical_distance = sum(v['distance'] * 2 for v in village_data.values())
    
    # 计算效率比
    efficiency_ratio = total_distance / theoretical_distance if theoretical_distance > 0 else 0
    
    # 评分估算
    scores = {
        "safety": 100,
        "timeliness": 100,
        "economy": 100,
        "feasibility": 100
    }
    
    # 安全性扣分
    if not feasible:
        scores["safety"] -= 15
    if efficiency_ratio > 1.5:
        scores["economy"] -= 15
    elif efficiency_ratio > 1.2:
        scores["economy"] -= 8
    
    # 时效性
    scores["timeliness"] = 100  # 简化
    
    # 可行性
    total_capacity = sum(config['quantity'] * uav_specs[config['model_id']]['max_payload'] * 0.8 
                        for config in uav_configs if config['model_id'] in uav_specs)
    total_demand = sum(v['demand'] for v in village_data.values())
    
    if total_capacity >= total_demand:
        scores["feasibility"] = 100
    else:
        scores["feasibility"] = int(100 * total_capacity / total_demand)
    
    # 综合评分
    weighted_score = (
        0.35 * scores["safety"] +
        0.35 * scores["timeliness"] +
        0.15 * scores["economy"] +
        0.15 * scores["feasibility"]
    )
    
    print(f"\n📊 方案统计:")
    print(f"   总需求: {total_demand}kg")
    print(f"   总运力: {total_capacity:.0f}kg (80%利用率)")
    print(f"   理论最优距离: {theoretical_distance:.1f}km")
    print(f"   预计总距离: {total_distance:.1f}km")
    print(f"   效率比: {efficiency_ratio:.2f}")
    
    print(f"\n📈 评分估算:")
    print(f"   安全性: {scores['safety']}")
    print(f"   时效性: {scores['timeliness']}")
    print(f"   经济性: {scores['economy']}")
    print(f"   可行性: {scores['feasibility']}")
    print(f"   综合评分: {weighted_score:.1f}")
    
    return feasible, weighted_score

# 7种可行方案
plans = [
    {
        "name": "方案一：JDX-500最优配置",
        "uavs": [{"model_id": "jd-jdx500", "quantity": 7}]
    },
    {
        "name": "方案二：JDX-500 + ARK40",
        "uavs": [
            {"model_id": "jd-jdx500", "quantity": 6},
            {"model_id": "fy-ark40", "quantity": 6}
        ]
    },
    {
        "name": "方案三：JDX-500 + ARK80",
        "uavs": [
            {"model_id": "jd-jdx500", "quantity": 5},
            {"model_id": "fy-ark80", "quantity": 8}
        ]
    },
    {
        "name": "方案四：全ARK80",
        "uavs": [{"model_id": "fy-ark80", "quantity": 20}]
    },
    {
        "name": "方案五：JDX-500 + FlyCart 30",
        "uavs": [
            {"model_id": "jd-jdx500", "quantity": 6},
            {"model_id": "dji-fc30", "quantity": 6}
        ]
    },
    {
        "name": "方案六：JDX-500 + ARK80 + ARK40",
        "uavs": [
            {"model_id": "jd-jdx500", "quantity": 5},
            {"model_id": "fy-ark80", "quantity": 5},
            {"model_id": "fy-ark40", "quantity": 5}
        ]
    },
    {
        "name": "方案七：JDX-500 + FlyCart 30 + ARK80",
        "uavs": [
            {"model_id": "jd-jdx500", "quantity": 4},
            {"model_id": "dji-fc30", "quantity": 6},
            {"model_id": "fy-ark80", "quantity": 5}
        ]
    }
]

# 分析所有方案
print("🚀 无人机配置方案评分分析")
print("="*70)

feasible_plans = []
for plan in plans:
    feasible, score = analyze_plan(plan['name'], plan['uavs'])
    if feasible and score >= 85:
        feasible_plans.append((plan, score))

# 按分数排序
feasible_plans.sort(key=lambda x: x[1], reverse=True)

print(f"\n{'='*70}")
print(f"✅ 可行高分方案（评分>=85）: {len(feasible_plans)} 个")
print('='*70)

# 输出简洁版本
print("\n📋 可行方案（型号 + 数量）:")
for i, (plan, score) in enumerate(feasible_plans, 1):
    print(f"\n{i}. {plan['name']} (评分: {score:.1f})")
    for uav in plan['uavs']:
        specs = next(m for m in module03['all_models'] if m['id'] == uav['model_id'])
        print(f"   - {specs['model']}: {uav['quantity']}架")
