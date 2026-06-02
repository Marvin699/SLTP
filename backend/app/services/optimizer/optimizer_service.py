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
