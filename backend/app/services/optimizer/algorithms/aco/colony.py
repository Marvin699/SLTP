"""ACO 蚁群求解器 — 多无人机运输调度优化"""
import random
import math
from typing import List, Dict, Any, Tuple
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.models.trip import Trip
from app.services.optimizer.models.drone_state import DroneState
from app.services.optimizer.engine.task_generator import generate_transport_tasks
from app.services.optimizer.engine.scheduler import create_drone_states, assign_trip_to_drone


def solve_with_aco(
    task: Task,
    aco_params: dict,
    distance_matrix: List[List[float]],
) -> Solution:
    """
    使用 ACO 算法求解多无人机运输调度。

    流程:
    1. 任务拆分：大需求 → 多个运输任务
    2. ACO 优化：为每个运输任务分配最优无人机
    3. 调度计算：计算时间线

    参数:
        task: 原始任务
        aco_params: ACO 参数
        distance_matrix: 距离矩阵

    返回:
        Solution 对象
    """
    # 1. 拆分任务
    transport_tasks = generate_transport_tasks(task)
    if not transport_tasks:
        return Solution(trips=[], task_id="empty")

    num_tasks = len(transport_tasks)
    num_drones = len(task.uavs)

    # 2. ACO 参数
    num_ants = int(aco_params.get("num_ants", 30))
    max_iterations = int(aco_params.get("max_iterations", 100))
    alpha = float(aco_params.get("alpha", 1.0))
    beta = float(aco_params.get("beta", 3.0))
    evaporation_rate = float(aco_params.get("evaporation_rate", 0.3))
    Q = float(aco_params.get("Q", 100))
    elite_ants = int(aco_params.get("elite_ants", 3))

    # 3. 初始化信息素矩阵 [task_idx][drone_idx]
    pheromone = [[0.1 for _ in range(num_drones)] for _ in range(num_tasks)]

    # 4. 计算启发式信息
    heuristic = _compute_heuristic_matrix(task, transport_tasks, distance_matrix)

    # 5. ACO 迭代
    best_solution = None
    best_makespan = float("inf")

    for iteration in range(max_iterations):
        iteration_solutions = []
        iteration_makespans = []

        for ant_idx in range(num_ants):
            # 每只蚂蚁生成一个分配方案
            assignments = _ant_generate_solution(
                task, transport_tasks, pheromone, heuristic,
                alpha, beta, distance_matrix, num_drones,
            )

            # 调度计算
            trips = _execute_assignments(task, transport_tasks, assignments, distance_matrix)
            solution = Solution(trips=trips, task_id=f"iter{iteration}_ant{ant_idx}")

            makespan = solution.makespan
            iteration_solutions.append((assignments, solution))
            iteration_makespans.append(makespan)

        # 找到本轮最优
        best_ant_idx = min(range(len(iteration_makespans)), key=lambda i: iteration_makespans[i])
        iter_best_makespan = iteration_makespans[best_ant_idx]
        iter_best_assignments, iter_best_solution = iteration_solutions[best_ant_idx]

        # 更新全局最优
        if iter_best_makespan < best_makespan:
            best_makespan = iter_best_makespan
            best_solution = iter_best_solution

        # 信息素挥发
        for i in range(num_tasks):
            for j in range(num_drones):
                pheromone[i][j] *= (1 - evaporation_rate)

        # 信息素更新（所有蚂蚁）
        for ant_idx in range(num_ants):
            assignments, _ = iteration_solutions[ant_idx]
            makespan = iteration_makespans[ant_idx]
            deposit = Q / max(makespan, 1.0)
            for task_idx, drone_idx in assignments:
                pheromone[task_idx][drone_idx] += deposit

        # 精英蚂蚁强化
        sorted_indices = sorted(range(len(iteration_makespans)), key=lambda i: iteration_makespans[i])
        for e in range(min(elite_ants, len(sorted_indices))):
            idx = sorted_indices[e]
            assignments, _ = iteration_solutions[idx]
            makespan = iteration_makespans[idx]
            elite_deposit = (Q / max(makespan, 1.0)) * (2.0 if e == 0 else 1.5)
            for task_idx, drone_idx in assignments:
                pheromone[task_idx][drone_idx] += elite_deposit

    return best_solution if best_solution else Solution(trips=[], task_id="no_solution")


def _compute_heuristic_matrix(
    task: Task,
    transport_tasks: List[Dict],
    distance_matrix: List[List[float]],
) -> List[List[float]]:
    """
    计算启发式矩阵 [task_idx][drone_idx]。

    η = 优先级权重 × 距离因子 × 载重匹配度
    """
    num_tasks = len(transport_tasks)
    num_drones = len(task.uavs)
    matrix = []

    for t_idx, t in enumerate(transport_tasks):
        row = []
        village_idx = t["village_idx"]
        distance = distance_matrix[0][village_idx + 1] if distance_matrix else 1.0

        for d_idx, uav in enumerate(task.uavs):
            # 距离因子（越近越好）
            eta_dist = 1.0 / max(distance, 0.1)

            # 载重匹配度（载重利用率越高越好，但不能超载）
            if uav.max_payload > 0:
                load_ratio = t["weight"] / uav.max_payload
                if load_ratio > 1.0:
                    eta_load = 0.01  # 超载，极低启发值
                else:
                    eta_load = 0.5 + 0.5 * load_ratio  # 0.5 ~ 1.0
            else:
                eta_load = 0.5

            # 优先级权重
            priority_w = {1: 3.0, 2: 2.0, 3: 1.0, 4: 0.5}.get(t["priority"], 1.0)

            # 冷链约束
            cold_penalty = 1.0
            if t.get("cold_chain"):
                # 冷链物资需要适合冷链的无人机（简化：ARK80 适合冷链）
                if "ARK80" in uav.name or "ark80" in uav.id.lower():
                    cold_penalty = 2.0
                else:
                    cold_penalty = 0.3

            eta = priority_w * eta_dist * eta_load * cold_penalty
            row.append(max(eta, 1e-6))

        matrix.append(row)

    return matrix


def _ant_generate_solution(
    task: Task,
    transport_tasks: List[Dict],
    pheromone: List[List[float]],
    heuristic: List[List[float]],
    alpha: float,
    beta: float,
    distance_matrix: List[List[float]],
    num_drones: int,
) -> List[Tuple[int, int]]:
    """
    一只蚂蚁生成一个分配方案。

    返回: [(task_idx, drone_idx), ...]
    """
    # 创建临时无人机状态（用于约束检查）
    drones = create_drone_states(task)
    assignments = []

    # 按优先级排序任务
    task_order = sorted(range(len(transport_tasks)), key=lambda i: transport_tasks[i]["priority"])

    for t_idx in task_order:
        t = transport_tasks[t_idx]
        village_idx = t["village_idx"]
        distance = distance_matrix[0][village_idx + 1] if distance_matrix else 1.0

        # 计算每个无人机的选择概率
        candidates = []
        probabilities = []

        for d_idx in range(num_drones):
            drone = drones[d_idx]
            load = t["weight"]

            # 检查约束
            if not drone.can_serve(distance, load):
                continue

            tau = pheromone[t_idx][d_idx] ** alpha
            eta = heuristic[t_idx][d_idx] ** beta
            prob = tau * eta

            candidates.append(d_idx)
            probabilities.append(prob)

        if not candidates:
            # 没有可行无人机，随机选一个
            d_idx = random.randint(0, num_drones - 1)
            assignments.append((t_idx, d_idx))
            continue

        # 轮盘赌选择
        total = sum(probabilities)
        if total <= 0:
            d_idx = random.choice(candidates)
        else:
            r = random.random() * total
            cumulative = 0.0
            d_idx = candidates[-1]
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if cumulative >= r:
                    d_idx = candidates[i]
                    break

        assignments.append((t_idx, d_idx))

        # 更新临时无人机状态
        drone = drones[d_idx]
        speed = drone.max_speed if drone.max_speed > 0 else 60.0
        one_way_time = (distance / speed) * 60
        round_trip_time = one_way_time * 2
        drone.complete_trip(distance, round_trip_time, t["weight"], t["village_name"])

    return assignments


def _execute_assignments(
    task: Task,
    transport_tasks: List[Dict],
    assignments: List[Tuple[int, int]],
    distance_matrix: List[List[float]],
) -> List[Trip]:
    """根据分配方案执行调度，生成 Trip 列表"""
    drones = create_drone_states(task)
    trips = []

    for t_idx, d_idx in assignments:
        if d_idx >= len(drones):
            continue

        t = transport_tasks[t_idx]
        drone = drones[d_idx]
        village_idx = t["village_idx"]
        distance = distance_matrix[0][village_idx + 1] if distance_matrix else 0

        trip = assign_trip_to_drone(drone, t, distance)
        trips.append(trip)

    return trips
