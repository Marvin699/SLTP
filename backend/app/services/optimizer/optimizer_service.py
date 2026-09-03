"""优化服务总入口 — 接收 API 请求，调用引擎，返回结果"""
import time
from typing import Dict, Any
from app.services.optimizer.models.task_model import parse_task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.engine.distance_matrix import build_distance_matrix
from app.services.optimizer.algorithms.aco.cvrp_solver import solve_cvrp_with_greedy
from app.services.optimizer.algorithms.aco.solver import get_default_params
from app.services.optimizer.outputs.table_builder import (
    build_summary_stats,
    build_route_summary_table,
    build_village_detail_table,
    build_drone_detail_table,
)
from app.services.optimizer.outputs.geojson_exporter import export_geojson
from app.services.optimizer.evaluators.feasibility_checker import check_solution_feasibility


def run_optimizer(task_data: dict, aco_params: dict = None) -> dict:
    """
    运行路径优化服务（CVRP/MTSP模式）

    参数:
        task_data: 前端传入的 task JSON
        aco_params: ACO 参数（可选）

    返回:
        优化结果 dict（包含3个表格数据）
    """
    # 1. 解析任务
    task = parse_task(task_data)

    # 2. 获取默认参数
    if aco_params is None:
        aco_params = get_default_params(task)

    # 3. 构建距离矩阵
    distance_matrix = build_distance_matrix(task)

    # 4. 运行CVRP优化（支持多点串联）
    start_time = time.time()
    solution = solve_cvrp_with_greedy(task, aco_params, distance_matrix)
    elapsed = time.time() - start_time

    # 5. 构建输出
    summary_stats = build_summary_stats(solution, task)
    route_table = build_route_summary_table(solution, task)
    village_table = build_village_detail_table(solution, task)
    drone_table = build_drone_detail_table(solution, task)

    # 6. 可行性校验
    feasibility = check_solution_feasibility(solution, task)

    # 7. GeoJSON
    # 从 solution.trips 构建航次级别的 LineString
    from app.services.optimizer.models.route_model import UAVRoute, RouteSegment
    uav_routes = _build_uav_routes_from_solution(solution, task, distance_matrix)
    geojson = export_geojson(task, uav_routes, solution.trips)

    return {
        "summary": summary_stats,
        "route_table": route_table,
        "village_table": village_table,
        "drone_table": drone_table,
        "feasibility": feasibility,
        "solution": solution.to_dict(),
        "geojson": geojson,
        "elapsed_seconds": round(elapsed, 1),
        "aco_params_used": aco_params,
    }


def recompute_manual(task_data: dict, manual_trips: list) -> dict:
    """
    手动调整配送顺序后重算（跳过ACO，直接按传入的 route 重建方案并输出全部表格）

    参数:
        task_data: 前端传入的 task JSON（与 /run 一致）
        manual_trips: 航次列表，每项 {route, drone_id, drone_type, drone_name, delivery_mode, village_loads}
    """
    from app.services.optimizer.algorithms.aco.cvrp_solver import convert_to_trips
    from app.services.optimizer.models.solution import Solution

    task = parse_task(task_data)
    distance_matrix = build_distance_matrix(task)

    # 构建无人机配置（与 cvrp_solver 保持一致）
    drone_configs = []
    for uav in task.uavs:
        quantity = getattr(uav, 'quantity', 1)
        drone_model = uav.id.split('-')[0] if '-' in uav.id else uav.id
        for idx in range(quantity):
            range_points = getattr(uav, 'range_points', []) or []
            if isinstance(range_points, str):
                import json
                try:
                    range_points = json.loads(range_points)
                except Exception:
                    range_points = []
            drone_configs.append({
                'id': f"{uav.id}-{idx + 1}" if quantity > 1 else uav.id,
                'type': drone_model,
                'name': uav.name,
                'max_capacity': uav.max_payload,
                'speed': uav.max_speed,
                'range_points': range_points,
                'max_range': getattr(uav, 'max_range', 20),
                'is_cold_chain': getattr(uav, 'is_cold_chain', False),
            })

    # 将前端传入的航次转换为内部格式（village_loads: 村庄名→重量 → loads: 节点索引→重量）
    trips_input = []
    for t in manual_trips:
        route = t.get('route') or []
        if len(route) < 3 or route[0] != 0 or route[-1] != 0:
            raise ValueError(f"航次路线格式非法: {route}")
        vloads = t.get('village_loads') or {}
        name_to_node = {}
        for node in route:
            if node != 0 and node - 1 < len(task.demand_points):
                name_to_node[task.demand_points[node - 1].name] = node
        loads = {node: w for name, w in vloads.items() if (node := name_to_node.get(name)) is not None}
        trips_input.append({
            'route': route,
            'loads': loads,
            'drone_id': t.get('drone_id') or t.get('drone_type') or '',
            'drone_type': t.get('drone_type') or '',
            'drone_name': t.get('drone_name') or '',
            'delivery_mode': t.get('delivery_mode', 'optional'),
        })

    trip_objs = convert_to_trips(trips_input, drone_configs, task, distance_matrix)
    for i, t in enumerate(trip_objs):
        t.trip_id = i
    solution = Solution(trips=trip_objs, task_id="manual")

    summary_stats = build_summary_stats(solution, task)
    route_table = build_route_summary_table(solution, task)
    village_table = build_village_detail_table(solution, task)
    drone_table = build_drone_detail_table(solution, task)
    feasibility = check_solution_feasibility(solution, task)
    uav_routes = _build_uav_routes_from_solution(solution, task, distance_matrix)
    geojson = export_geojson(task, uav_routes, solution.trips)

    return {
        "summary": summary_stats,
        "route_table": route_table,
        "village_table": village_table,
        "drone_table": drone_table,
        "feasibility": feasibility,
        "solution": solution.to_dict(),
        "geojson": geojson,
        "elapsed_seconds": 0.0,
        "aco_params_used": None,
        "manual": True,
    }


def _build_uav_routes_from_solution(solution, task, distance_matrix):
    """从 Solution 构建 UAVRoute 列表（用于 GeoJSON 导出）"""
    from app.services.optimizer.models.route_model import UAVRoute, RouteSegment

    # 按无人机分组
    drone_trips = {}
    for trip in solution.trips:
        if trip.drone_id not in drone_trips:
            drone_trips[trip.drone_id] = []
        drone_trips[trip.drone_id].append(trip)

    uav_routes = []
    for drone_id, trips in drone_trips.items():
        # 合并所有 trip 为一条路径
        path = ["0"]
        path_names = [task.depot.name]
        segments = []
        total_distance = 0
        total_energy = 0
        points_served = set()
        
        # 获取配送模式（所有 trip 的模式应该相同）
        delivery_mode = trips[0].delivery_mode if trips else 'optional'

        for trip in trips:
            v_idx = trip.route[1]
            # 找到对应的村庄
            village = None
            for dp in task.demand_points:
                if str(task.demand_points.index(dp) + 1) == str(v_idx):
                    village = dp
                    break

            v_name = village.name if village else f"点{v_idx}"
            one_way_dist = trip.total_distance / 2

            # 去程段
            segments.append(RouteSegment(
                from_id="depot",
                from_name=task.depot.name,
                to_id=trip.village_id,
                to_name=v_name,
                distance=one_way_dist,
                energy=one_way_dist * 1.5,
                load_before=trip.load,
                load_after=0,
            ))

            # 返程段
            segments.append(RouteSegment(
                from_id=trip.village_id,
                from_name=v_name,
                to_id="depot",
                to_name=task.depot.name,
                distance=one_way_dist,
                energy=one_way_dist,
                load_before=0,
                load_after=0,
            ))

            path.extend([str(v_idx), "0"])
            path_names.extend([v_name, task.depot.name])
            total_distance += trip.total_distance
            total_energy += trip.total_distance * 1.2
            points_served.add(trip.village_name)

        # 查找无人机信息（支持模糊匹配，因为 drone_id 可能包含索引如 "JDX-500-1"）
        uav = None
        for u in task.uavs:
            if drone_id.startswith(u.id.split('-')[0]):
                uav = u
                break
        
        uav_routes.append(UAVRoute(
            uav_id=drone_id,
            uav_name=uav.name if uav else drone_id,
            path=path,
            path_names=path_names,
            segments=segments,
            total_distance=total_distance,
            total_energy=total_energy,
            points_served=len(points_served),
            initial_load=0,
            delivery_mode=delivery_mode,
        ))

    return uav_routes
