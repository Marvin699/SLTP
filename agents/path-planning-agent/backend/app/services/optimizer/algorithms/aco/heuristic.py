"""启发函数 — 综合距离、优先级、载重、航程的多因子启发值"""
import math
from typing import List
from app.services.optimizer.models.task_model import Task, DemandPoint
from app.services.optimizer.models.uav_model import UAVState


# 优先级权重映射
PRIORITY_WEIGHT = {
    "urgent": 5.0,
    "high": 3.0,
    "medium": 1.0,
    "low": 0.5,
    "normal": 0.3,
}


def compute_heuristic(
    task: Task,
    uav: UAVState,
    current_point_idx: int,
    candidate_point_idx: int,
    distance: float,
    return_distance: float,
    alpha: float = 1.0,
    beta: float = 5.0,
) -> float:
    """
    计算从当前点到候选点的启发值。

    综合因子:
    1. 距离因子: η_dist = 1 / distance（越近越好）
    2. 优先级因子: η_priority = priority_weight（高优先级更吸引）
    3. 载重因子: η_load = 1 - load_ratio（载重越轻越灵活）
    4. 航程因子: η_range = remaining_range / max_range（航程越充裕越好）

    η = β1×η_dist + β2×η_priority + β3×η_load + β4×η_range
    """
    if distance <= 0:
        return 0.0

    # 1. 距离因子
    eta_dist = 1.0 / distance

    # 2. 优先级因子
    candidate_dp = task.demand_points[candidate_point_idx] if candidate_point_idx < len(task.demand_points) else None
    if candidate_dp:
        priority_w = PRIORITY_WEIGHT.get(candidate_dp.priority, 1.0)
        eta_priority = priority_w / 5.0  # 归一化到 0~1
    else:
        eta_priority = 0.5

    # 3. 载重因子（载重越轻越灵活，更倾向选择）
    eta_load = 1.0 - uav.load_ratio

    # 4. 航程因子
    eta_range = uav.remaining_range / uav.max_range if uav.max_range > 0 else 0

    # 综合启发值
    eta = (
        0.4 * eta_dist
        + 0.3 * eta_priority
        + 0.15 * eta_load
        + 0.15 * eta_range
    )

    return max(eta, 1e-6)


def compute_transition_probability(
    pheromone: float,
    heuristic: float,
    alpha: float,
    beta: float,
) -> float:
    """
    计算转移概率。

    P = τ^α × η^β

    参数:
        pheromone: 信息素值 τ
        heuristic: 启发值 η
        alpha: 信息素重要度
        beta: 启发函数重要度
    """
    return (pheromone ** alpha) * (heuristic ** beta)
