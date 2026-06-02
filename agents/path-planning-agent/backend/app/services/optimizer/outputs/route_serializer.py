"""路径结果序列化器"""
from typing import List
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.route_model import UAVRoute


def compute_score(
    task: Task,
    uav_routes: List[UAVRoute],
    visited_points: List[int],
    best_cost: float,
) -> float:
    """
    计算优化评分（0-100）。

    评分因素:
    1. 覆盖率：所有需求点是否被服务
    2. 效率：总距离/能耗
    3. 均衡度：各无人机负载是否均衡
    """
    score = 100.0

    # 1. 覆盖率（权重 40%）
    required = set(range(len(task.demand_points)))
    visited = set(visited_points)
    coverage = len(visited) / len(required) if required else 1.0
    score_coverage = coverage * 40

    # 2. 效率（权重 40%）
    # 基于总距离与理论最短距离的比值
    total_distance = sum(r.total_distance for r in uav_routes)
    # 理论最短距离：所有需求点到 depot 距离之和的 2 倍（往返）
    theoretical_min = sum(
        min(row[0] for row in task.distance_matrix[1:]) if task.distance_matrix else 0
        for _ in task.demand_points
    ) * 2
    if theoretical_min > 0:
        efficiency = min(1.0, theoretical_min / total_distance)
    else:
        efficiency = 1.0
    score_efficiency = efficiency * 40

    # 3. 均衡度（权重 20%）
    if len(uav_routes) > 1:
        counts = [r.points_served for r in uav_routes]
        mean = sum(counts) / len(counts)
        if mean > 0:
            variance = sum((c - mean) ** 2 for c in counts) / len(counts)
            balance = max(0, 1.0 - variance / (mean ** 2))
        else:
            balance = 1.0
    else:
        balance = 1.0
    score_balance = balance * 20

    total_score = score_coverage + score_efficiency + score_balance
    return max(0, min(100, total_score))
