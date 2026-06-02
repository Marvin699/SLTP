"""多目标成本评估器"""
from typing import List
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.route_model import UAVRoute


def compute_total_cost(
    task: Task,
    uav_routes: List[UAVRoute],
    visited_points: List[int],
    w_distance: float = 0.4,
    w_energy: float = 0.3,
    w_priority: float = 0.2,
    w_balance: float = 0.1,
) -> float:
    """
    计算多目标综合成本。

    cost = w1×总距离 + w2×总能耗 + w3×优先级惩罚 + w4×负载均衡

    成本越低越好。
    """
    if not uav_routes:
        return float("inf")

    # 1. 总距离（归一化）
    total_distance = sum(r.total_distance for r in uav_routes)
    norm_distance = total_distance / 100.0  # 简单归一化

    # 2. 总能耗（归一化）
    total_energy = sum(r.total_energy for r in uav_routes)
    norm_energy = total_energy / 100.0

    # 3. 高优先级延迟惩罚
    priority_penalty = _compute_priority_penalty(task, uav_routes, visited_points)

    # 4. 负载均衡度（各无人机服务点数的方差）
    balance_penalty = _compute_balance_penalty(uav_routes)

    cost = (
        w_distance * norm_distance
        + w_energy * norm_energy
        + w_priority * priority_penalty
        + w_balance * balance_penalty
    )

    return cost


def _compute_priority_penalty(
    task: Task,
    uav_routes: List[UAVRoute],
    visited_points: List[int],
) -> float:
    """
    计算优先级惩罚。
    高优先级点越晚被访问，惩罚越大。
    """
    penalty = 0.0

    # 按访问顺序给每个点一个位置
    position_map = {}
    pos = 0
    for idx in visited_points:
        if idx not in position_map:
            position_map[idx] = pos
            pos += 1

    for dp_idx, dp in enumerate(task.demand_points):
        if dp_idx in position_map:
            pos = position_map[dp_idx]
            # 高优先级点位置越靠后惩罚越大
            if dp.priority_value <= 2:  # urgent/high
                penalty += pos * 0.5
            elif dp.priority_value <= 3:  # medium
                penalty += pos * 0.1

    return penalty


def _compute_balance_penalty(uav_routes: List[UAVRoute]) -> float:
    """
    计算负载均衡惩罚。
    各无人机服务点数的方差越大，惩罚越大。
    """
    if len(uav_routes) <= 1:
        return 0.0

    counts = [r.points_served for r in uav_routes]
    mean = sum(counts) / len(counts)
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    return variance
