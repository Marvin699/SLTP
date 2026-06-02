"""任务生成器 — 将大重量需求自动拆分为多个运输任务"""
from typing import List, Dict, Any
from app.services.optimizer.models.task_model import Task, DemandPoint


def generate_transport_tasks(task: Task) -> List[Dict[str, Any]]:
    """
    将每个村庄的需求拆分为多个运输任务。

    例如：坡乐村 2200kg，最大载重 40kg → 55 个运输任务。

    返回:
        [
            {
                "task_id": int,
                "village_idx": int,       # 需求点在 task.demand_points 中的索引
                "village_id": str,
                "village_name": str,
                "weight": float,          # 本趟运载重量
                "priority": int,
                "cargo_type": str,
                "cold_chain": bool,
            },
            ...
        ]
    """
    all_tasks = []
    task_id = 0

    # 获取最大无人机载重（用于任务拆分）
    max_payload = max((u.max_payload for u in task.uavs), default=40.0)

    # 按优先级排序（urgent=1 最先）
    sorted_points = sorted(
        enumerate(task.demand_points),
        key=lambda x: x[1].priority_value,
    )

    for village_idx, dp in sorted_points:
        total_weight = dp.total_weight
        if total_weight <= 0:
            continue

        # 判断是否冷链
        cold_chain = any(
            "冷链" in m.type or "冷藏" in m.type or "胰岛素" in m.type or "疫苗" in m.type
            for m in dp.materials
        )

        # 拆分任务
        remaining = total_weight
        while remaining > 0:
            # 本趟运载量（不超过最大载重）
            load = min(remaining, max_payload)

            all_tasks.append({
                "task_id": task_id,
                "village_idx": village_idx,
                "village_id": dp.id,
                "village_name": dp.name,
                "weight": load,
                "priority": dp.priority_value,
                "cargo_type": ", ".join(m.type for m in dp.materials),
                "cold_chain": cold_chain,
            })

            remaining -= load
            task_id += 1

    return all_tasks
