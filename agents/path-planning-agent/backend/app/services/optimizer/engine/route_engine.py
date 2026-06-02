"""路径引擎 — 协调 ACO 求解全流程"""
from app.services.optimizer.models.task_model import Task, parse_task
from app.services.optimizer.models.route_model import OptimizationResult
from app.services.optimizer.algorithms.aco.solver import solve, get_default_params


def run_optimization(task: Task, aco_params: dict = None) -> OptimizationResult:
    """
    运行路径优化。

    参数:
        task: 解析后的任务对象
        aco_params: ACO 参数（可选）

    返回:
        OptimizationResult
    """
    return solve(task, aco_params)


def get_default_aco_params(task: Task) -> dict:
    """获取默认 ACO 参数"""
    return get_default_params(task)
