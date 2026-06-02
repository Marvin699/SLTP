"""蚂蚁路径生成 — 为多架无人机生成完整配送方案"""
import random
from typing import List, Optional, Tuple, Dict
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.uav_model import UAVState
from app.services.optimizer.models.route_model import UAVRoute, RouteSegment, OptimizationResult
from app.services.optimizer.algorithms.aco.pheromone import PheromoneMatrix
from app.services.optimizer.algorithms.aco.heuristic import compute_heuristic, compute_transition_probability
from app.services.optimizer.engine.distance_matrix import get_depot_to_point_distances, get_return_distances


def select_next_point(
    task: Task,
    uav: UAVState,
    current_point: int,
    unvisited: set,
    pheromone: PheromoneMatrix,
    dist_matrix: List[List[float]],
    return_distances: List[float],
    alpha: float,
    beta: float,
) -> Optional[int]:
    """
    使用轮盘赌选择下一个需求点。

    参数:
        current_point: 当前点索引（0=depot, 1~N=需求点）
        unvisited: 未访问的需求点索引集合（1~N）

    返回:
        选中的需求点索引，或 None（无可行点）
    """
    if not unvisited:
        return None

    candidates = []
    probabilities = []

    for next_idx in unvisited:
        # next_idx 是需求点在 task.demand_points 中的索引（0-based）
        # 矩阵中的索引是 next_idx + 1（因为 depot=0）
        matrix_j = next_idx + 1
        distance = dist_matrix[current_point][matrix_j]
        ret_dist = return_distances[next_idx]

        dp = task.demand_points[next_idx]

        # 检查约束
        # 1. 能否承载该点的物资
        if not uav.can_carry(dp.total_weight):
            continue
        # 2. 能否到达该点并返回
        if not uav.can_reach(distance + ret_dist):
            continue

        # 计算启发值
        eta = compute_heuristic(
            task, uav, current_point - 1 if current_point > 0 else -1,
            next_idx, distance, ret_dist, alpha, beta,
        )
        tau = pheromone.get(current_point, matrix_j)
        prob = compute_transition_probability(tau, eta, alpha, beta)

        candidates.append(next_idx)
        probabilities.append(prob)

    if not candidates:
        return None

    # 轮盘赌选择
    total = sum(probabilities)
    if total <= 0:
        return random.choice(candidates)

    r = random.random() * total
    cumulative = 0.0
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if cumulative >= r:
            return candidates[i]

    return candidates[-1]


def generate_ant_solution(
    task: Task,
    pheromone: PheromoneMatrix,
    dist_matrix: List[List[float]],
    alpha: float,
    beta: float,
) -> Tuple[Dict[int, List[int]], List[int], List[UAVRoute]]:
    """
    一只蚂蚁生成一组完整的多无人机配送方案。

    返回:
        routes_dict: {uav_idx: [point_idx, ...]} 各无人机访问的点
        all_visited: 所有已访问的点索引列表
        uav_routes: UAVRoute 列表
    """
    num_points = len(task.demand_points)
    unvisited = set(range(num_points))  # 0-based 需求点索引
    return_distances = get_return_distances(task, dist_matrix)

    routes_dict = {}
    all_visited = []
    uav_routes = []

    for uav_idx, uav_spec in enumerate(task.uavs):
        if not unvisited:
            break  # 所有点已服务

        # 创建无人机运行状态
        uav = UAVState(
            uav_id=uav_spec.id,
            uav_name=uav_spec.name,
            max_payload=uav_spec.max_payload,
            max_range=uav_spec.max_range,
            battery_capacity=uav_spec.battery_capacity,
        )

        path_indices = [0]  # 从 depot 开始（矩阵索引 0）
        path_names = [task.depot.name]
        segments = []
        current_matrix_idx = 0  # depot

        points_for_uav = []

        while unvisited:
            # 选择下一个点
            next_point = select_next_point(
                task, uav, current_matrix_idx, unvisited,
                pheromone, dist_matrix, return_distances, alpha, beta,
            )

            if next_point is None:
                # 无可行点：如果不在 depot，返回 depot 后重试
                if current_matrix_idx != 0:
                    ret_distance = dist_matrix[current_matrix_idx][0]
                    load_before = uav.current_load
                    energy_before = uav.total_energy
                    uav.return_to_depot(ret_distance)
                    segment_energy = uav.total_energy - energy_before

                    from_dp = task.demand_points[current_matrix_idx - 1]
                    segments.append(RouteSegment(
                        from_id=from_dp.id,
                        from_name=from_dp.name,
                        to_id=task.depot.id,
                        to_name=task.depot.name,
                        distance=ret_distance,
                        energy=segment_energy,
                        load_before=load_before,
                        load_after=0,
                    ))
                    path_indices.append(0)
                    path_names.append(task.depot.name)
                    current_matrix_idx = 0  # 回到 depot
                    continue  # 重新尝试从 depot 出发
                else:
                    break  # 已在 depot 仍无可行点，结束该无人机

            dp = task.demand_points[next_point]
            next_matrix_idx = next_point + 1
            distance = dist_matrix[current_matrix_idx][next_matrix_idx]

            # 装载该点的物资（无论从哪出发）
            uav.load_at_depot(dp.total_weight)

            # 记录出发时载重
            load_before = uav.current_load

            # 飞行到该点（deliver 内部计算能耗、扣减航程和载重）
            energy_before = uav.total_energy
            uav.deliver(dp.id, distance, dp.total_weight)
            segment_energy = uav.total_energy - energy_before

            # 记录路径段
            from_id = task.depot.id if current_matrix_idx == 0 else task.demand_points[current_matrix_idx - 1].id
            from_name = task.depot.name if current_matrix_idx == 0 else task.demand_points[current_matrix_idx - 1].name
            segments.append(RouteSegment(
                from_id=from_id,
                from_name=from_name,
                to_id=dp.id,
                to_name=dp.name,
                distance=distance,
                energy=segment_energy,
                load_before=load_before,
                load_after=uav.current_load,
            ))

            path_indices.append(next_matrix_idx)
            path_names.append(dp.name)
            points_for_uav.append(next_point)
            all_visited.append(next_point)
            unvisited.discard(next_point)
            current_matrix_idx = next_matrix_idx

        # 最终返回 depot（如果不在 depot）
        if current_matrix_idx != 0:
            ret_distance = dist_matrix[current_matrix_idx][0]
            load_before = uav.current_load

            energy_before = uav.total_energy
            uav.return_to_depot(ret_distance)
            segment_energy = uav.total_energy - energy_before

            from_dp = task.demand_points[current_matrix_idx - 1]
            segments.append(RouteSegment(
                from_id=from_dp.id,
                from_name=from_dp.name,
                to_id=task.depot.id,
                to_name=task.depot.name,
                distance=ret_distance,
                energy=segment_energy,
                load_before=load_before,
                load_after=0,
            ))

            path_indices.append(0)
            path_names.append(task.depot.name)

        routes_dict[uav_idx] = points_for_uav

        # 计算初始载重
        initial_load = sum(
            task.demand_points[p].total_weight for p in points_for_uav
        )

        uav_routes.append(UAVRoute(
            uav_id=uav_spec.id,
            uav_name=uav_spec.name,
            path=[str(i) for i in path_indices],
            path_names=path_names,
            segments=segments,
            total_distance=uav.total_distance,
            total_energy=uav.total_energy,
            points_served=len(points_for_uav),
            initial_load=initial_load,
        ))

    return routes_dict, all_visited, uav_routes
