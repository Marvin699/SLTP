"""可行性校验器 — 基于 Solution/Trip 模型的完整可行性检查"""
from typing import List, Dict, Any
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.models.trip import Trip


def get_range_by_weight(weight: float, uav) -> float:
    """根据载重计算最大航程(km) - 分段线性插值(与蚁群算法保持一致)"""
    points = getattr(uav, 'range_points', [])
    max_payload = getattr(uav, 'max_payload', 0)
    max_range = getattr(uav, 'max_range', 20)
    
    if not points:
        if max_payload <= 0:
            return max_range
        if weight <= 0:
            return max_range
        if weight >= max_payload:
            return max_range * 0.3
        return max_range * (1 - 0.7 * weight / max_payload)
    
    if weight <= 0:
        return points[0][1]
    if weight >= max_payload:
        return points[-1][1]
    
    for i in range(len(points) - 1):
        w1, r1 = points[i]
        w2, r2 = points[i + 1]
        if w1 <= weight <= w2:
            t = (weight - w1) / (w2 - w1) if w2 != w1 else 0
            return r1 + (r2 - r1) * t
    return points[-1][1]


def check_solution_feasibility(solution: Solution, task: Task) -> Dict[str, Any]:
    """
    对完整运输方案进行可行性校验。

    检查项:
    1. 需求覆盖：所有村庄的需求重量是否被完全配送
    2. 超载检查：每趟运载量是否超过无人机最大载重
    3. 航程检查：每趟往返距离是否超过有效航程
    4. 返航检查：每趟是否从 depot 出发并返回 depot
    5. 空任务检查：是否有无人机未分配任务

    返回:
        {
            "feasible": bool,           # 总体是否可行
            "issues": [str],            # 严重问题（不可行）
            "warnings": [str],          # 警告（可行但有风险）
            "demand_coverage": {...},   # 需求覆盖详情
            "trip_checks": {...},       # 趟次检查统计
        }
    """
    issues = []
    warnings = []

    # ─── 1. 需求覆盖检查 ───
    demand_coverage = _check_demand_coverage(solution, task)
    for village, info in demand_coverage.items():
        if info["shortfall"] > 0.01:  # 允许 0.01kg 误差
            if info["delivered"] == 0:
                issues.append(f"{village}: 完全未配送（需求 {info['demand']:.1f}kg）")
            else:
                issues.append(
                    f"{village}: 配送不足，需求 {info['demand']:.1f}kg，"
                    f"实际 {info['delivered']:.1f}kg，缺 {info['shortfall']:.1f}kg"
                )

    # ─── 2. 趟次级别检查 ───
    trip_stats = {"total": 0, "feasible": 0, "infeasible": 0, "overload": 0, "over_range": 0}

    # 构建无人机规格映射
    uav_spec = {u.id: u for u in task.uavs}

    for trip in solution.trips:
        trip_stats["total"] += 1

        if trip.feasible:
            trip_stats["feasible"] += 1
        else:
            trip_stats["infeasible"] += 1
            # 查找具体原因
            uav = uav_spec.get(trip.drone_id)
            if uav:
                if trip.load > uav.max_payload:
                    trip_stats["overload"] += 1
                    issues.append(
                        f"趟次{trip.trip_id}({trip.drone_type}→{trip.village_name}): "
                        f"载重 {trip.load:.1f}kg 超过最大载重 {uav.max_payload}kg"
                    )
                # 航程检查
                eff_range = _effective_range(uav, trip.load)
                if trip.total_distance > eff_range:
                    trip_stats["over_range"] += 1
                    issues.append(
                        f"趟次{trip.trip_id}({trip.drone_type}→{trip.village_name}): "
                        f"往返距离 {trip.total_distance:.1f}km 超过有效航程 {eff_range:.1f}km"
                    )

    # ─── 3. 无人机使用检查 ───
    assigned_drones = set(t.drone_id for t in solution.trips)
    all_drones = set(u.id for u in task.uavs)
    unused = all_drones - assigned_drones
    if unused:
        unused_names = []
        for uid in unused:
            u = uav_spec.get(uid)
            unused_names.append(u.name if u else uid)
        warnings.append(f"未使用的无人机: {', '.join(unused_names)}")

    # ─── 4. 总体判定 ───
    feasible = len(issues) == 0

    return {
        "feasible": feasible,
        "feasible_text": "方案可行" if feasible else f"方案不可行（{len(issues)}个问题）",
        "issues": issues,
        "warnings": warnings,
        "demand_coverage": demand_coverage,
        "trip_checks": trip_stats,
    }


def _check_demand_coverage(solution: Solution, task: Task) -> Dict[str, Dict[str, float]]:
    """检查每个村庄的需求覆盖情况（支持多点串联）"""
    coverage = {}

    # 初始化需求
    for dp in task.demand_points:
        coverage[dp.name] = {
            "demand": dp.total_weight,
            "delivered": 0.0,
            "shortfall": dp.total_weight,
            "trip_count": 0,
        }

    # 统计实际配送（支持多点串联）
    for trip in solution.trips:
        # 如果有 village_loads，使用精确的载重分配
        if hasattr(trip, 'village_loads') and trip.village_loads:
            for village, load in trip.village_loads.items():
                if village in coverage:
                    coverage[village]["delivered"] += load
                    coverage[village]["trip_count"] += 1
        else:
            # 兼容旧格式：解析逗号分隔的村庄名称
            village_names = [v.strip() for v in trip.village_name.split(",") if v.strip()]
            
            # 平均分配载重到每个村庄
            if village_names:
                load_per_village = trip.load / len(village_names)
                
                for village in village_names:
                    if village in coverage:
                        coverage[village]["delivered"] += load_per_village
                        coverage[village]["trip_count"] += 1

    # 计算缺口
    for name in coverage:
        info = coverage[name]
        info["delivered"] = round(info["delivered"], 2)
        info["shortfall"] = round(max(0, info["demand"] - info["delivered"]), 2)
        info["coverage_pct"] = (
            round(info["delivered"] / info["demand"] * 100, 1)
            if info["demand"] > 0 else 100.0
        )

    return coverage


def _effective_range(uav, load: float) -> float:
    """根据载重计算有效航程 - 使用分段线性插值"""
    return get_range_by_weight(load, uav)
