"""ACO 主求解器 — 迭代优化循环"""
from typing import Dict, List, Any
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.route_model import OptimizationResult
from app.services.optimizer.algorithms.aco.pheromone import PheromoneMatrix
from app.services.optimizer.algorithms.aco.ant import generate_ant_solution
from app.services.optimizer.engine.distance_matrix import build_distance_matrix
from app.services.optimizer.evaluators.cost_evaluator import compute_total_cost
from app.services.optimizer.outputs.geojson_exporter import export_geojson
from app.services.optimizer.outputs.route_serializer import compute_score


def get_default_params(task: Task) -> dict:
    """根据任务复杂度动态设置默认 ACO 参数"""
    num_points = len(task.demand_points)
    num_uavs = len(task.uavs)

    params = {
        "num_ants": 30,
        "max_iterations": 100,
        "alpha": 1.0,
        "beta": 5.0,
        "evaporation_rate": 0.5,
        "Q": 100,
        "elite_ants": 3,
    }

    # 根据需求点数量动态调整
    if num_points > 15:
        params["num_ants"] = 50
        params["max_iterations"] = 150
    if num_points > 25:
        params["num_ants"] = 80
        params["max_iterations"] = 200

    # 根据无人机数量调整
    if num_uavs > 4:
        params["num_ants"] += 10

    return params


def solve(task: Task, aco_params: dict = None) -> OptimizationResult:
    """
    运行 ACO 算法求解多无人机路径规划。

    参数:
        task: 解析后的任务对象
        aco_params: ACO 参数（可选，为 None 则使用默认）

    返回:
        OptimizationResult
    """
    # 1. 获取参数
    if aco_params is None:
        aco_params = get_default_params(task)

    num_ants = int(aco_params.get("num_ants", 30))
    max_iterations = int(aco_params.get("max_iterations", 100))
    alpha = float(aco_params.get("alpha", 1.0))
    beta = float(aco_params.get("beta", 5.0))
    evaporation_rate = float(aco_params.get("evaporation_rate", 0.5))
    Q = float(aco_params.get("Q", 100))
    elite_ants = int(aco_params.get("elite_ants", 3))

    # 2. 构建距离矩阵
    dist_matrix = build_distance_matrix(task)
    num_nodes = len(dist_matrix)  # depot + 需求点

    # 3. 初始化信息素
    pheromone = PheromoneMatrix(num_nodes, initial_value=0.1)

    # 4. 迭代优化
    best_cost = float("inf")
    best_routes = None
    best_visited = None
    best_uav_routes = None
    best_iteration = 0

    for iteration in range(max_iterations):
        iteration_costs = []
        iteration_solutions = []

        # 每只蚂蚁生成一个解
        for ant_idx in range(num_ants):
            routes_dict, all_visited, uav_routes = generate_ant_solution(
                task, pheromone, dist_matrix, alpha, beta,
            )

            # 计算成本
            cost = compute_total_cost(task, uav_routes, all_visited)
            iteration_costs.append(cost)
            iteration_solutions.append((routes_dict, all_visited, uav_routes))

        # 找到本轮最优
        best_ant_idx = min(range(len(iteration_costs)), key=lambda i: iteration_costs[i])
        iter_best_cost = iteration_costs[best_ant_idx]
        iter_best_routes, iter_best_visited, iter_best_uav_routes = iteration_solutions[best_ant_idx]

        # 更新全局最优
        if iter_best_cost < best_cost:
            best_cost = iter_best_cost
            best_routes = iter_best_routes
            best_visited = iter_best_visited
            best_uav_routes = iter_best_uav_routes
            best_iteration = iteration

        # 5. 信息素挥发
        pheromone.evaporate(evaporation_rate)

        # 6. 普通蚂蚁信息素更新
        for ant_idx in range(num_ants):
            if ant_idx == best_ant_idx:
                continue
            _, visited, uav_routes = iteration_solutions[ant_idx]
            cost = iteration_costs[ant_idx]
            # 将所有无人机路径合并为一个路径序列用于信息素更新
            full_path = _build_full_path(uav_routes)
            pheromone.deposit(full_path, cost, Q)

        # 7. 精英蚂蚁强化
        elite_path = _build_full_path(iter_best_uav_routes)
        pheromone.elite_deposit(elite_path, iter_best_cost, Q, elite_bonus=2.0)

        # 额外的精英蚂蚁
        if elite_ants > 1:
            sorted_indices = sorted(range(len(iteration_costs)), key=lambda i: iteration_costs[i])
            for e in range(1, min(elite_ants, len(sorted_indices))):
                idx = sorted_indices[e]
                _, visited, uav_routes = iteration_solutions[idx]
                cost = iteration_costs[idx]
                ep = _build_full_path(uav_routes)
                pheromone.elite_deposit(ep, cost, Q, elite_bonus=1.5)

    # 8. 构建最终结果
    if best_uav_routes is None:
        # 无可行解
        return OptimizationResult(
            routes=[],
            total_distance=0,
            total_energy=0,
            optimization_score=0,
            all_points_covered=False,
            iterations_used=0,
        )

    total_distance = sum(r.total_distance for r in best_uav_routes)
    total_energy = sum(r.total_energy for r in best_uav_routes)
    all_covered = len(set(best_visited)) >= len(task.demand_points)
    score = compute_score(task, best_uav_routes, best_visited, best_cost)
    geojson = export_geojson(task, best_uav_routes)

    return OptimizationResult(
        routes=best_uav_routes,
        total_distance=total_distance,
        total_energy=total_energy,
        optimization_score=score,
        all_points_covered=all_covered,
        iterations_used=best_iteration + 1,
        geojson=geojson,
    )


def _build_full_path(uav_routes) -> List[int]:
    """将多条无人机路径合并为单条路径序列（用于信息素更新）"""
    path = []
    for route in uav_routes:
        for node in route.path:
            path.append(int(node))
    return path
