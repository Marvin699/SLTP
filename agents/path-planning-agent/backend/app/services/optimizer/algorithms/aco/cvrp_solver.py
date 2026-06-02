"""CVRP/MTSP 求解器 — 带载重-航程动态约束的多无人机配送路径规划

支持"必须直飞"和"可选联飞"两种模式：
- 必须直飞：独立处理，智能匹配无人机
- 可选联飞：使用贪心+局部搜索算法求解
"""
import random
import math
import copy
from typing import List, Dict, Any, Tuple
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.models.trip import Trip

# 配送模式枚举
class DeliveryMode:
    DIRECT = "direct"      # 必须直飞
    OPTIONAL = "optional"  # 可选联飞


def solve_cvrp_with_greedy(
    task: Task,
    aco_params: dict,
    distance_matrix: List[List[float]],
) -> Solution:
    """使用改进算法求解CVRP/MTSP问题（支持直飞/联飞分离）"""
    print(f"=== CVRP求解器调试 ===")
    print(f"需求点数量: {len(task.demand_points)}")
    print(f"无人机数量: {len(task.uavs)}")
    
    # 1. 准备无人机配置
    drone_configs = []
    for uav in task.uavs:
        # 获取数量 - 支持两种格式：
        # 1. 前端已展开：quantity=1（每个对象代表一架无人机）
        # 2. 聚合格式：quantity>1（需要展开）
        quantity = getattr(uav, 'quantity', 1)
        
        # 提取无人机型号（从 id 中提取，如 "JDX-500-1" -> "JDX-500"）
        drone_model = uav.id.split('-')[0] if '-' in uav.id else uav.id
        
        for idx in range(quantity):
            range_points = uav.range_points if hasattr(uav, 'range_points') else []
            if isinstance(range_points, str):
                import json
                try:
                    range_points = json.loads(range_points)
                except:
                    range_points = []
            
            drone_configs.append({
                'id': f"{uav.id}-{idx + 1}" if quantity > 1 else uav.id,
                'type': drone_model,  # 使用型号作为 type
                'name': uav.name,
                'max_capacity': uav.max_payload,
                'speed': uav.max_speed,
                'range_points': range_points,
                'max_range': uav.max_range if hasattr(uav, 'max_range') else 20,
                'is_cold_chain': hasattr(uav, 'is_cold_chain') and uav.is_cold_chain,
            })
    
    print(f"可用无人机总数: {len(drone_configs)}")
    if not drone_configs:
        return Solution(trips=[], task_id="no_drones")
    
    print(f"无人机配置: {[(d['type'], d['name'], d['id']) for d in drone_configs]}")
    
    # 2. 准备需求数据，分离直飞和联飞需求点
    demands_direct = {}   # 必须直飞的需求 {village_id: weight}
    demands_optional = {}  # 可选联飞的需求 {village_id: weight}
    demand_points_info = {}  # 需求点详细信息
    
    for i, dp in enumerate(task.demand_points):
        vid = i + 1
        weight = dp.total_weight if hasattr(dp, 'total_weight') else 0
        
        # 获取配送模式
        delivery_mode = getattr(dp, 'delivery_mode', DeliveryMode.OPTIONAL)
        if delivery_mode == DeliveryMode.DIRECT:
            demands_direct[vid] = weight
        else:
            demands_optional[vid] = weight
        
        demand_points_info[vid] = {
            'name': dp.name,
            'priority': getattr(dp, 'priority_value', 3),
            'delivery_mode': delivery_mode,
            'weight': weight,
        }
    
    print(f"必须直飞: {list(demands_direct.keys())}")
    print(f"可选联飞: {list(demands_optional.keys())}")
    
    # 3. 处理必须直飞的需求（智能匹配无人机）
    trips_direct = []
    remaining_direct = dict(demands_direct)
    
    if remaining_direct:
        print("\n=== 处理必须直飞需求 ===")
        trips_direct = handle_direct_delivery(
            drone_configs, remaining_direct, demand_points_info, distance_matrix
        )
    
    # 4. 处理可选联飞的需求（贪心+局部搜索）
    trips_optional = []
    remaining_optional = dict(demands_optional)
    
    if remaining_optional:
        print("\n=== 处理可选联飞需求 ===")
        trips_optional = handle_optional_delivery(
            drone_configs, remaining_optional, demand_points_info, distance_matrix
        )
    
    # 5. 合并航次
    all_trips = trips_direct + trips_optional
    
    # 6. 局部搜索优化
    print("\n=== 执行局部搜索优化 ===")
    optimize_solution(all_trips, drone_configs, distance_matrix)
    
    # 7. 转换为Trip对象
    trip_objects = convert_to_trips(all_trips, drone_configs, task, distance_matrix)
    
    print(f"\n=== 规划完成 ===")
    print(f"总航次: {len(trip_objects)}")
    print(f"  - 必须直飞: {len(trips_direct)}趟")
    print(f"  - 可选联飞: {len(trips_optional)}趟")
    
    return Solution(trips=trip_objects, task_id="cvrp_greedy")


def handle_direct_delivery(drone_configs, demands, demand_info, distance_matrix):
    """处理必须直飞的需求 - 智能匹配无人机（支持无人机重复使用）"""
    trips = []
    remaining = dict(demands)
    
    # 按优先级和难度排序需求点
    def difficulty(v):
        info = demand_info[v]
        dist = distance_matrix[0][v]
        weight = remaining[v]
        priority_weight = {1: 2.5, 2: 2.0, 3: 1.5, 4: 1.0, 5: 0.5}.get(info['priority'], 1.0)
        return dist * weight * priority_weight
    
    sorted_villages = sorted(remaining.keys(), key=lambda v: -difficulty(v))
    
    for v in sorted_villages:
        weight = remaining[v]
        if weight <= 0:
            continue
        
        # 无人机可以重复使用，直到需求完成
        while remaining[v] > 0.001:
            # 找到最适合的无人机
            best_drone = None
            best_score = -1
            best_load = 0
            
            for drone in drone_configs:
                max_load = find_max_delivery(v, drone, distance_matrix)
                if max_load <= 0:
                    continue
                
                # 计算匹配度：航程覆盖度 * 载重利用率
                dist = distance_matrix[0][v]
                range_util = min(max_load / remaining[v], 1.0) if remaining[v] > 0 else 0
                load_util = remaining[v] / max_load if max_load > 0 else 0
                
                # 优先使用能刚好满足需求的无人机
                score = range_util * load_util * 1000 + max_load
                
                if score > best_score:
                    best_score = score
                    best_drone = drone
                    best_load = min(max_load, remaining[v])
            
            if best_drone is None or best_load <= 0:
                print(f"警告: 村庄{v}剩余{remaining[v]}kg无法配送!")
                break
            
            # 创建直飞航次 - 无人机可以重复使用
            trips.append({
                'drone_id': best_drone['id'],
                'drone_type': best_drone['type'],
                'drone_name': best_drone['name'],
                'route': [0, v, 0],
                'loads': {v: best_load},
                'delivery_mode': DeliveryMode.DIRECT,
            })
            
            remaining[v] -= best_load
    
    print(f"必须直飞航次: {len(trips)}趟")
    for t in trips:
        villages = [demand_info.get(v, {}).get('name', f'v{v}') for v in t['route'] if v != 0]
        print(f"  - {t['drone_name']}({t['drone_id']}): {' → '.join(villages)}, 载重{t['loads']}")
    
    return trips


def handle_optional_delivery(drone_configs, demands, demand_info, distance_matrix):
    """处理可选联飞的需求 - 使用贪心+局部搜索（支持无人机重复使用）"""
    trips = []
    remaining = dict(demands)
    
    print(f"可用无人机数: {len(drone_configs)}")
    
    # 计算每个需求点的配送难度
    def calculate_difficulty(v):
        dist = distance_matrix[0][v]
        weight = remaining.get(v, 0)
        info = demand_info.get(v, {})
        priority_weight = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.8, 5: 0.5}.get(info.get('priority', 3), 1.0)
        return dist * weight * priority_weight
    
    sorted_villages = sorted(remaining.keys(), key=lambda v: -calculate_difficulty(v))
    
    # 计算无人机能力
    def calculate_capability(drone_config):
        max_range = drone_config.get('max_range', 20)
        if drone_config['range_points']:
            max_range = drone_config['range_points'][-1][1]
        return drone_config['max_capacity'] * max_range
    
    # 阶段1: 使用所有无人机处理所有需求点（无人机可重复使用，直到需求完成）
    # 为每个村庄循环分配配送，直到需求完成或没有无人机能到达
    drone_usage = {d['id']: 0 for d in drone_configs}
    demand_info_copy = {v: demand_info[v] for v in sorted_villages}
    
    # 调试：打印初始需求
    print(f"  初始需求:")
    for v in sorted_villages:
        village_name = demand_info_copy.get(v, {}).get('name', f'村庄{v}')
        print(f"    {village_name}: {remaining[v]:.1f}kg")
    
    for v in sorted_villages:
        village_name = demand_info_copy.get(v, {}).get('name', f'村庄{v}')
        original_demand = demand_info_copy.get(v, {}).get('weight', 0)
        delivered = 0
        
        # 处理这个村庄的所有需求
        while remaining[v] > 0.001:
            # 找出所有能到达这个村庄的无人机
            reachable_drones = []
            dist_to_village = distance_matrix[0][v] if v < len(distance_matrix[0]) else 9999
            
            for drone in drone_configs:
                max_load = find_max_delivery(v, drone, distance_matrix)
                if max_load > 0:
                    reachable_drones.append((drone, max_load))
                else:
                    # 调试：为什么无人机无法到达
                    drone_range = drone.get('max_range', 20)
                    print(f"      调试: {drone['name']} 无法到达 {village_name}, 距离={dist_to_village:.1f}km, 航程={drone_range}km")
            
            if not reachable_drones:
                print(f"    警告: {village_name} - 没有无人机能到达，剩余需求: {remaining[v]:.1f}kg, 距离: {dist_to_village:.1f}km")
                break
            
            # 优先选择使用次数少的无人机，其次考虑载重能力
            reachable_drones.sort(key=lambda x: (drone_usage[x[0]['id']], -x[1]))
            
            # 选择最合适的无人机
            drone, max_load = reachable_drones[0]
            load = min(max_load, remaining[v])
            
            # 添加航次
            trips.append({
                'drone_id': drone['id'],
                'drone_type': drone['type'],
                'drone_name': drone['name'],
                'route': [0, v, 0],
                'loads': {v: load},
                'delivery_mode': DeliveryMode.OPTIONAL,
            })
            remaining[v] -= load
            delivered += load
            drone_usage[drone['id']] += 1
            print(f"    {village_name}: {drone['name']}({drone['id']}) 配送 {load:.1f}kg, 剩余: {remaining[v]:.1f}kg")
        
        print(f"    {village_name} 完成: 需求 {original_demand:.1f}kg, 已配送 {delivered:.1f}kg, 缺口 {original_demand - delivered:.1f}kg")
    
    print(f"  无人机使用统计: {drone_usage}")
    
    # 检查未满足的需求
    unmet_demand = {v: remaining[v] for v in sorted_villages if remaining[v] > 0.001}
    if unmet_demand:
        print(f"  未满足的需求:")
        for v, weight in unmet_demand.items():
            village_name = demand_info_copy.get(v, {}).get('name', f'村庄{v}')
            print(f"    - {village_name}: {weight:.1f}kg")
            # 检查为什么无法满足
            print(f"      可用无人机尝试:")
            for drone in drone_configs:
                max_load = find_max_delivery(v, drone, distance_matrix)
                dist = distance_matrix[0][v] if v < len(distance_matrix[0]) else "未知"
                print(f"        {drone['name']}: 最大载重={max_load}kg, 距离={dist}km, 航程={drone.get('max_range', 20)}km")
    
    # 检查未使用的无人机
    unused_drones = [d for d in drone_configs if drone_usage[d['id']] == 0]
    if unused_drones:
        print(f"  未使用的无人机:")
        for d in unused_drones:
            print(f"    - {d['name']}({d['id']}), 载重: {d['max_capacity']}kg, 航程: {d.get('max_range', 20)}km")
            # 检查为什么未被使用
            for v in sorted_villages:
                if remaining.get(v, 0) > 0.001:
                    max_load = find_max_delivery(v, d, distance_matrix)
                    print(f"      -> 到村庄{v}最大载重: {max_load}kg")
    
    # 阶段2: 尝试联飞优化（合并邻近村庄，减少总趟次）
    print(f"  合并前航次总数: {len(trips)}")
    
    # 找出单村配送的航次，尝试两两合并
    single_village_indices = []
    for idx, t in enumerate(trips):
        if len(t['route']) == 3:
            single_village_indices.append((idx, t))
    
    print(f"  单村航次数量: {len(single_village_indices)}")
    
    # 按无人机型号分组（存储索引）
    drone_groups = {}
    for idx, t in single_village_indices:
        if t['drone_type'] not in drone_groups:
            drone_groups[t['drone_type']] = {'trips': []}
        drone_groups[t['drone_type']]['trips'].append((idx, t))
    
    # 尝试合并同型号无人机的航次
    removed_indices = set()
    used_as_first = set()  # 记录作为第一个航次被合并过的航次索引
    
    for drone_type, group in drone_groups.items():
        # 获取无人机配置
        dc = None
        for d in drone_configs:
            if d['type'] == drone_type:
                dc = d
                break
        if not dc:
            continue
        
        type_trips = group['trips']
        if len(type_trips) < 2:
            continue
        
        # 尝试合并航次
        for i in range(len(type_trips)):
            idx1, t1 = type_trips[i]
            
            # 如果这个航次已经被删除或已经作为第一个航次被合并过，则跳过
            if idx1 in removed_indices or idx1 in used_as_first:
                continue
            
            v1 = t1['route'][1]
            name1 = demand_info.get(v1, {}).get('name', f'村庄{v1}')
            
            merged = False  # 标记是否已经找到合并
            for j in range(i + 1, len(type_trips)):
                if merged:
                    break  # 已经找到合并，跳出j循环
                
                idx2, t2 = type_trips[j]
                
                # 如果这个航次已经被删除，则跳过
                if idx2 in removed_indices:
                    continue
                
                v2 = t2['route'][1]
                name2 = demand_info.get(v2, {}).get('name', f'村庄{v2}')
                
                # 检查是否可以合并
                total_load = t1['loads'][v1] + t2['loads'][v2]
                if total_load > dc['max_capacity']:
                    continue
                
                # 检查两种顺序是否可行
                loads = {v1: t1['loads'][v1], v2: t2['loads'][v2]}
                for order in [[0, v1, v2, 0], [0, v2, v1, 0]]:
                    ok, _, _ = check_route_feasible(order, dc, loads, distance_matrix)
                    if ok:
                        # 如果合并的是同一个村庄，需要合并载重
                        final_loads = loads.copy()
                        if v1 == v2:
                            # 同一个村庄，合并载重
                            final_loads[v1] = t1['loads'][v1] + t2['loads'][v2]
                        
                        # 合并这两个航次 - 使用原始航次的 drone_id
                        merged_trip = {
                            'drone_id': t1['drone_id'],  # 使用第一个航次的 drone_id
                            'drone_type': t1['drone_type'],
                            'drone_name': t1['drone_name'],
                            'route': order,
                            'loads': final_loads,
                            'delivery_mode': DeliveryMode.OPTIONAL,
                        }
                        
                        # 使用索引替换和标记移除
                        trips[idx1] = merged_trip
                        removed_indices.add(idx2)
                        used_as_first.add(idx1)  # 标记这个航次已经作为第一个航次被合并
                        print(f"    合并{name1}({v1})和{name2}({v2})的航次, idx1={idx1}, idx2={idx2}")
                        merged = True  # 标记已经找到合并
                        break  # 跳出order循环
    
    print(f"  移除的航次索引: {sorted(removed_indices)}")
    
    # 移除标记的航次（从后往前移除，保持索引正确）
    for idx in sorted(removed_indices, reverse=True):
        if idx < len(trips):
            del trips[idx]
    
    print(f"  合并后航次总数: {len(trips)}")
    
    print(f"可选联飞航次: {len(trips)}趟")
    for t in trips:
        villages = [demand_info.get(v, {}).get('name', f'v{v}') for v in t['route'] if v != 0]
        print(f"  - {t['drone_name']}({t.get('drone_id', t['drone_type'])}): {' → '.join(villages)}, 载重{sum(t['loads'].values()):.1f}kg")
    
    return trips


def plan_for_drone_type(drone_config, count, villages, remaining, distance_matrix, drones=None):
    """为单一型号的无人机规划联飞路径（考虑无人机数量限制）"""
    trips = []
    max_cap = drone_config['max_capacity']
    
    # 无人机索引跟踪
    drone_index = 0
    
    def make_trip(route, loads):
        nonlocal drone_index
        # 获取下一个可用的无人机ID
        drone_id = f"{drone_config['type']}-{drone_index + 1}"
        if drones and drone_index < len(drones):
            drone_id = drones[drone_index]['id']
        drone_index += 1
        
        return {
            'drone_id': drone_id,
            'drone_type': drone_config['type'],
            'drone_name': drone_config['name'],
            'route': route,
            'loads': loads,
            'delivery_mode': DeliveryMode.OPTIONAL,
        }
    
    # 获取当前已分配的趟次数量
    def get_current_trip_count():
        return len([t for t in trips])
    
    # 阶段1: 尝试合并邻近村庄（优先使用较少趟次完成更多配送）
    village_pairs = []
    for i, v1 in enumerate(villages):
        for j in range(i + 1, len(villages)):
            v2 = villages[j]
            if remaining.get(v1, 0) > 0.001 and remaining.get(v2, 0) > 0.001:
                dist = distance_matrix[v1][v2]
                village_pairs.append((dist, v1, v2))
    
    village_pairs.sort(key=lambda x: x[0])
    
    for dist, v1, v2 in village_pairs:
        if get_current_trip_count() >= count:
            break
            
        if remaining.get(v1, 0) <= 0.001 or remaining.get(v2, 0) <= 0.001:
            continue
        
        max_w1 = min(int(remaining[v1] + 1), max_cap)
        found = False
        
        for w1 in range(max_w1, 0, -1):
            remaining_cap = max_cap - w1
            if remaining_cap <= 0:
                continue
            max_w2 = min(int(remaining[v2] + 1), remaining_cap)
            
            for w2 in range(max_w2, 0, -1):
                loads = {v1: w1, v2: w2}
                
                for order in [[0, v1, v2, 0], [0, v2, v1, 0]]:
                    ok, _, _ = check_route_feasible(order, drone_config, loads, distance_matrix)
                    if ok:
                        trips.append(make_trip(order, loads))
                        remaining[v1] -= w1
                        remaining[v2] -= w2
                        found = True
                        break
                if found:
                    break
            if found:
                break
    
    # 阶段2: 处理剩余需求（每个无人机最多执行一趟）
    for v in villages:
        if get_current_trip_count() >= count:
            break
            
        while remaining.get(v, 0) > 0.001:
            max_load = find_max_delivery(v, drone_config, distance_matrix)
            if max_load <= 0:
                break
            
            amount = min(max_load, remaining[v])
            trips.append(make_trip([0, v, 0], {v: amount}))
            remaining[v] -= amount
            
            if get_current_trip_count() >= count:
                break
    
    print(f"  ├─ {drone_config['name']} x {count}架: 生成 {len(trips)} 趟")
    return trips


def get_range_by_weight(weight: float, drone_config: dict) -> float:
    """根据载重计算最大航程(km) - 分段线性插值"""
    points = drone_config.get('range_points', [])
    if not points:
        max_range = drone_config.get('max_range', 20)
        max_capacity = drone_config['max_capacity']
        if weight <= 0:
            return max_range
        if weight >= max_capacity:
            return max_range * 0.3
        return max_range * (1 - 0.7 * weight / max_capacity)
    
    if weight <= 0:
        return points[0][1]
    if weight >= drone_config['max_capacity']:
        return points[-1][1]
    
    for i in range(len(points) - 1):
        w1, r1 = points[i]
        w2, r2 = points[i + 1]
        if w1 <= weight <= w2:
            t = (weight - w1) / (w2 - w1) if w2 != w1 else 0
            return r1 + (r2 - r1) * t
    return points[-1][1]


def check_route_feasible(route, drone_config, load_assignment, distance_matrix):
    """检查路径是否满足动态航程约束"""
    current_load = sum(load_assignment.get(node, 0) for node in route if node != 0)
    max_capacity = drone_config['max_capacity']
    
    if current_load > max_capacity + 0.001:
        return False, float('inf'), current_load
    
    remaining_range = get_range_by_weight(current_load, drone_config)
    total_dist = 0.0
    
    for i in range(len(route) - 1):
        from_node = route[i]
        to_node = route[i + 1]
        dist = distance_matrix[from_node][to_node]
        
        if dist > remaining_range + 0.001:
            return False, float('inf'), current_load
        
        remaining_range -= dist
        total_dist += dist
        
        if to_node != 0:
            old_load = current_load
            current_load -= load_assignment.get(to_node, 0)
            current_load = max(0, current_load)
            old_range = get_range_by_weight(old_load, drone_config)
            new_range = get_range_by_weight(current_load, drone_config)
            range_increase = new_range - old_range
            remaining_range = min(remaining_range + range_increase, new_range)
    
    return True, total_dist, current_load


def find_max_delivery(village, drone_config, distance_matrix):
    """找到无人机单次能配送到某村庄的最大载重"""
    max_cap = drone_config['max_capacity']
    lo, hi = 0, max_cap
    best_w = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        ok, _, _ = check_route_feasible([0, village, 0], drone_config, {village: mid}, distance_matrix)
        if ok:
            best_w = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best_w


def optimize_solution(trips, drone_configs, distance_matrix):
    """局部搜索优化"""
    improved = True
    iterations = 0
    
    while improved and iterations < 100:
        improved = False
        iterations += 1
        
        improved |= try_merge_two_single_trips(trips, drone_configs, distance_matrix)
        improved |= try_2opt(trips, drone_configs, distance_matrix)


def try_merge_two_single_trips(trips, drone_configs, distance_matrix):
    """尝试将两个单村庄航次合并为一个双村庄航次"""
    drone_types = {dc['type']: dc for dc in drone_configs}
    
    for i in range(len(trips)):
        for j in range(i + 1, len(trips)):
            t1, t2 = trips[i], trips[j]
            
            if len(t1['route']) != 3 or len(t2['route']) != 3:
                continue
            if t1['drone_type'] != t2['drone_type']:
                continue
            
            v1, v2 = t1['route'][1], t2['route'][1]
            if v1 == v2:
                continue
            
            total_load = sum(t1['loads'].values()) + sum(t2['loads'].values())
            drone_config = drone_types.get(t1['drone_type'])
            if not drone_config or total_load > drone_config['max_capacity']:
                continue
            
            loads = {v1: t1['loads'][v1], v2: t2['loads'][v2]}
            dist1 = t1.get('total_distance', float('inf'))
            dist2 = t2.get('total_distance', float('inf'))
            
            for order in [[0, v1, v2, 0], [0, v2, v1, 0]]:
                ok, dist, _ = check_route_feasible(order, drone_config, loads, distance_matrix)
                if ok and dist < dist1 + dist2 - 0.001:
                    trips[i] = {
                        'drone_type': t1['drone_type'],
                        'drone_name': t1['drone_name'],
                        'route': order,
                        'loads': loads,
                        'total_distance': dist,
                        'delivery_mode': t1.get('delivery_mode', DeliveryMode.OPTIONAL),
                    }
                    trips.pop(j)
                    return True
    return False


def try_2opt(trips, drone_configs, distance_matrix):
    """尝试2-opt交换优化"""
    drone_types = {dc['type']: dc for dc in drone_configs}
    
    for trip in trips:
        route = trip['route']
        if len(route) <= 4:
            continue
        
        drone_config = drone_types.get(trip['drone_type'])
        if not drone_config:
            continue
        
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if j - i == 1:
                    continue
                
                new_route = route[:i] + route[i:j][::-1] + route[j:]
                ok, new_dist, _ = check_route_feasible(
                    new_route, drone_config, trip['loads'], distance_matrix
                )
                
                old_dist = sum(distance_matrix[route[k]][route[k+1]] for k in range(len(route)-1))
                
                if ok and new_dist < old_dist - 0.001:
                    trip['route'] = new_route
                    trip['total_distance'] = new_dist
                    improved = True
                    break
            if improved:
                break
        
        if improved:
            return True
    
    return False


def convert_to_trips(trips, drone_configs, task, distance_matrix):
    """将内部航次格式转换为Trip对象"""
    trip_objects = []
    trip_id = 0
    drone_types = {dc['type']: dc for dc in drone_configs}
    
    for trip in trips:
        drone_config = drone_types.get(trip['drone_type'])
        if not drone_config:
            continue
        
        route = trip['route']
        loads = trip['loads']
        total_distance = 0.0
        
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]
        
        speed = drone_config['speed'] if drone_config['speed'] > 0 else 60.0
        total_time = (total_distance / speed) * 60
        
        villages = []
        village_ids = []
        priorities = []
        village_loads = {}  # 存储每个村庄的具体载重
        
        for node in route:
            if node != 0 and node - 1 < len(task.demand_points):
                dp = task.demand_points[node - 1]
                if dp.name not in villages:
                    villages.append(dp.name)
                    village_ids.append(str(dp.id))
                    # 从 loads 字典获取这个村庄的载重
                    if node in loads:
                        village_loads[dp.name] = loads[node]
                priorities.append(dp.priority_value if hasattr(dp, 'priority_value') else 3)
        
        feasible, _, _ = check_route_feasible(
            route, drone_config, loads, distance_matrix
        )
        
        # 获取配送模式
        delivery_mode = trip.get('delivery_mode', DeliveryMode.OPTIONAL)
        
        # 获取 drone_id（优先使用 trip 中的 drone_id，如果没有则使用 drone_type）
        drone_id = trip.get('drone_id', trip['drone_type'])
        
        # 调试：检查 village_loads 是否正确填充
        if len(village_loads) != len(villages):
            print(f"  警告: 村庄数量({len(villages)})与载重数量({len(village_loads)})不匹配")
            print(f"        villages: {villages}")
            print(f"        village_loads: {village_loads}")
            print(f"        loads: {loads}")
            print(f"        route: {route}")
            # 打印每个节点的处理
            print("        节点处理详情:")
            for node in route:
                if node != 0 and node - 1 < len(task.demand_points):
                    dp = task.demand_points[node - 1]
                    in_loads = node in loads
                    print(f"          节点{node}: 村庄={dp.name}, 在loads中={in_loads}, loads.get(node)={loads.get(node)}")
        
        trip_obj = Trip(
            trip_id=trip_id,
            drone_id=drone_id,
            drone_type=trip['drone_type'],
            drone_name=trip['drone_name'],
            village_id=",".join(village_ids),
            village_name=",".join(villages),
            route=route,
            load=round(sum(loads.values()), 2),
            village_loads=village_loads,
            total_distance=round(total_distance, 2),
            total_time=round(total_time, 2),
            feasible=feasible,
            priority=min(priorities) if priorities else 3,
            cargo_type="unknown",
            start_time=0,
            end_time=round(total_time, 2),
            delivery_mode=delivery_mode,
        )
        
        trip_objects.append(trip_obj)
        trip_id += 1
    
    return trip_objects
