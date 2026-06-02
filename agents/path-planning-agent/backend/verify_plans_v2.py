#!/usr/bin/env python3
"""
验证7种高分方案 - 基于规则诊断评分机制（修正版）
"""
import json
from pathlib import Path

# 加载数据
work_dir = Path(__file__).parent.parent / "work"
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
    
    if not points:
        max_range = uav.get('range_km', 20)
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

def calculate_score(plan_name, uav_configs):
    """计算方案评分"""
    print(f"\n{'='*70}")
    print(f"方案: {plan_name}")
    print('='*70)
    
    # 获取无人机规格
    uav_specs = {uav['id']: uav for uav in module03['all_models']}
    
    total_demand = sum(v['demand'] for v in village_data.values())
    theoretical_distance = sum(v['distance'] * 2 for v in village_data.values())
    
    # 统计
    all_drone_ids = []
    total_capacity = 0
    total_trips = 0
    total_distance = 0
    
    for config in uav_configs:
        model_id = config['model_id']
        quantity = config['quantity']
        uav = uav_specs.get(model_id)
        
        if not uav:
            continue
        
        # 生成无人机ID
        for i in range(quantity):
            drone_id = f"{model_id}-{i+1}"
            all_drone_ids.append(drone_id)
        
        max_payload = uav['max_payload']
        avg_load = max_payload * 0.8  # 80%载重
        
        # 计算需要的趟数（假设一架无人机执行完所有任务）
        trips_needed = total_demand / avg_load
        total_trips += trips_needed
        total_capacity += quantity * max_payload
        
        # 计算总距离（简化：按平均距离估算）
        avg_round_trip = theoretical_distance / len(village_data)
        total_distance += trips_needed * avg_round_trip * quantity
    
    # 评分
    scores = {
        "safety": 100,
        "timeliness": 100,
        "economy": 100,
        "feasibility": 100
    }
    
    # 安全性：检查航程约束
    for config in uav_configs:
        model_id = config['model_id']
        uav = uav_specs.get(model_id)
        if not uav:
            continue
        
        max_range = uav['range_km']
        max_payload = uav['max_payload']
        
        # 检查最远的村庄
        for village, info in village_data.items():
            distance = info['distance']
            demand = info['demand']
            
            # 计算往返距离
            round_trip = distance * 2
            
            # 检查不同载重下的航程
            for load_pct in [0.5, 0.8, 1.0]:
                load = max_payload * load_pct
                eff_range = get_range_by_weight(load, uav)
                
                if round_trip > eff_range:
                    print(f"❌ {village} 往返{_trip}km超过有效航程{eff_range}km")
                    scores["safety"] -= 15
                    break
    
    # 效率比
    efficiency_ratio = total_distance / theoretical_distance if theoretical_distance > 0 else 1
    
    if efficiency_ratio > 1.5:
        scores["economy"] -= 15
    elif efficiency_ratio > 1.2:
        scores["economy"] -= 8
    
    # 可行性
    if total_capacity * 0.8 < total_demand:
        scores["feasibility"] = int(100 * total_capacity * 0.8 / total_demand)
    
    # 时效性（简化：假设高优先级会先配送）
    scores["timeliness"] = 100
    
    # 综合评分
    weighted_score = (
        0.35 * scores["safety"] +
        0.35 * scores["timeliness"] +
        0.15 * scores["economy"] +
        0.15 * scores["feasibility"]
    )
    
    print(f"\n📦 无人机配置:")
    for config in uav_configs:
        model_id = config['model_id']
        uav = uav_specs.get(model_id)
        if uav:
            print(f"   - {uav['model']}: {config['quantity']}架")
    
    print(f"\n📊 方案统计:")
    print(f"   总需求: {total_demand}kg")
    print(f"   总运力: {total_capacity:.0f}kg")
    print(f"   理论最优距离: {theoretical_distance:.1f}km")
    print(f"   预计总距离: {total_distance:.1f}km")
    print(f"   效率比: {efficiency_ratio:.2f}")
    
    print(f"\n📈 评分:")
    print(f"   安全性: {scores['safety']}")
    print(f"   时效性: {scores['timeliness']}")
    print(f"   经济性: {scores['economy']}")
    print(f"   可行性: {scores['feasibility']}")
    print(f"   综合评分: {weighted_score:.1f}")
    
    return scores, weighted_score

# 7种可行方案
plans = [
    {"name": "方案一：JDX-500最小配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 8}]},
    {"name": "方案二：JDX-500标准配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 9}]},
    {"name": "方案三：JDX-500均衡配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 10}]},
    {"name": "方案四：JDX-500充裕配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 11}]},
    {"name": "方案五：JDX-500充足配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 12}]},
    {"name": "方案六：JDX-500最优配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 13}]},
    {"name": "方案七：JDX-500豪华配置", "uavs": [{"model_id": "jd-jdx500", "quantity": 14}]},
]

# 计算所有方案
print("🚀 无人机配置方案评分分析（修正版）")
print("="*70)

results = []
for plan in plans:
    scores, score = calculate_score(plan['name'], plan['uavs'])
    results.append((plan, scores, score))

# 按分数排序
results.sort(key=lambda x: x[2], reverse=True)

print(f"\n{'='*70}")
print("📋 可行方案排名（按评分）:")
print('='*70)

for i, (plan, scores, score) in enumerate(results, 1):
    print(f"\n{i}. {plan['name']} (综合: {score:.1f})")
    print(f"   安全性: {scores['safety']} | 时效性: {scores['timeliness']} | 经济性: {scores['economy']} | 可行性: {scores['feasibility']}")
    for config in plan['uavs']:
        specs = next(m for m in module03['all_models'] if m['id'] == config['model_id'])
        print(f"   - {specs['model']}: {config['quantity']}架")

print(f"\n{'='*70}")
print("✅ 评分>=90的方案:")
print('='*70)
high_score = [r for r in results if r[2] >= 90]
for plan, scores, score in high_score:
    print(f"\n{plan['name']} (评分: {score:.1f})")
    for config in plan['uavs']:
        specs = next(m for m in module03['all_models'] if m['id'] == config['model_id'])
        print(f"   - {specs['model']}: {config['quantity']}架")
