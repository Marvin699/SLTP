"""约束检查器 — 检查路径方案是否满足所有约束"""
from typing import List
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.uav_model import UAVState


def check_load_constraint(uav: UAVState, weight: float) -> bool:
    """检查是否超载"""
    return uav.current_load + weight <= uav.max_payload


def check_range_constraint(uav: UAVState, distance: float, return_distance: float) -> bool:
    """检查是否超航程（含返航距离）"""
    return uav.remaining_range >= distance + return_distance


def check_return_possible(uav: UAVState, return_distance: float) -> bool:
    """检查能否返回 depot"""
    return uav.remaining_range >= return_distance


def check_all_points_covered(task: Task, all_visited: List[str]) -> bool:
    """检查所有需求点是否被覆盖"""
    required = {dp.id for dp in task.demand_points}
    visited = set(all_visited)
    return required.issubset(visited)


def check_priority_satisfied(task: Task, routes: dict) -> bool:
    """
    检查高优先级任务是否优先完成。
    urgent/high 优先级的点应该在 low/normal 之前被服务。
    """
    # 简化检查：urgent 和 high 优先级的点不应被排在最后
    for uav_id, route_list in routes.items():
        # route_list 是该无人机访问的点ID序列
        # 检查是否有低优先级点排在高优先级点之前
        high_priority_positions = []
        low_priority_positions = []
        for i, point_id in enumerate(route_list):
            # 从 task 找到对应的需求点
            dp = next((d for d in task.demand_points if d.id == point_id), None)
            if dp:
                if dp.priority_value <= 2:
                    high_priority_positions.append(i)
                elif dp.priority_value >= 4:
                    low_priority_positions.append(i)
        # 如果有低优先级点排在高优先级点之前，不满足
        for low_pos in low_priority_positions:
            for high_pos in high_priority_positions:
                if low_pos < high_pos:
                    return False
    return True


def validate_solution(task: Task, routes: dict, visited_points: List[str]) -> dict:
    """
    综合验证方案可行性。

    参数:
        task: 任务定义
        routes: {uav_id: [point_id, ...]} 各无人机访问的点
        visited_points: 所有已访问的点ID列表

    返回:
        {valid: bool, issues: [str]}
    """
    issues = []

    # 1. 检查覆盖率
    if not check_all_points_covered(task, visited_points):
        required = {dp.id for dp in task.demand_points}
        visited = set(visited_points)
        missing = required - visited
        issues.append(f"未覆盖需求点: {missing}")

    # 2. 检查优先级
    if not check_priority_satisfied(task, routes):
        issues.append("高优先级任务未优先完成")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }
