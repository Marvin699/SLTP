"""调度器 — 多无人机并行调度，计算时间线"""
from typing import List, Dict, Any
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.drone_state import DroneState
from app.services.optimizer.models.trip import Trip


def create_drone_states(task: Task) -> List[DroneState]:
    """从任务创建无人机状态列表"""
    drones = []
    for uav in task.uavs:
        drones.append(DroneState(
            drone_id=uav.id,
            drone_type=uav.name,
            max_payload=uav.max_payload,
            max_range=uav.max_range,
            max_speed=uav.max_speed,
        ))
    return drones


def assign_trip_to_drone(
    drone: DroneState,
    task_def: Dict[str, Any],
    distance: float,
) -> Trip:
    """
    将一个运输任务分配给指定无人机，计算实际飞行参数。

    参数:
        drone: 无人机状态
        task_def: 任务定义（来自 task_generator）
        distance: 单程距离(km)

    返回:
        Trip 对象
    """
    load = task_def["weight"]

    # 计算飞行时间（分钟）：距离(km) / 速度(km/h) * 60
    speed = drone.max_speed if drone.max_speed > 0 else 60.0
    one_way_time = (distance / speed) * 60  # 单程时间(min)
    round_trip_time = one_way_time * 2       # 往返时间(min)

    # 检查可行性
    feasible = drone.can_serve(distance, load)

    # 创建 Trip
    trip = Trip(
        trip_id=task_def["task_id"],
        drone_id=drone.drone_id,
        drone_type=drone.drone_type,
        drone_name=getattr(drone, 'name', drone.drone_type),
        village_id=task_def["village_id"],
        village_name=task_def["village_name"],
        route=[0, task_def["village_idx"] + 1, 0],  # depot → village → depot
        load=load,
        total_distance=round(distance * 2, 2),  # 往返距离
        total_time=round(round_trip_time, 2),
        feasible=feasible,
        priority=task_def["priority"],
        cargo_type=task_def.get("cargo_type", ""),
        cold_chain=task_def.get("cold_chain", False),
        start_time=round(drone.busy_until, 2),
        end_time=round(drone.busy_until + round_trip_time, 2),
    )

    # 更新无人机状态
    if feasible:
        drone.complete_trip(distance, round_trip_time, load, task_def["village_name"])

    return trip


def schedule_solution(
    task: Task,
    trip_assignments: List[Dict[str, Any]],
    distance_matrix: List[List[float]],
) -> List[Trip]:
    """
    根据任务分配方案，调度所有 Trip，计算时间线。

    参数:
        task: 原始任务
        trip_assignments: [{"task_def": {...}, "drone_idx": int}, ...]
        distance_matrix: 距离矩阵

    返回:
        Trip 列表（含时间信息）
    """
    drones = create_drone_states(task)
    trips = []

    for assignment in trip_assignments:
        task_def = assignment["task_def"]
        drone_idx = assignment["drone_idx"]

        if drone_idx >= len(drones):
            continue

        drone = drones[drone_idx]
        village_idx = task_def["village_idx"]

        # depot 到该村的距离
        distance = distance_matrix[0][village_idx + 1] if distance_matrix else 0

        trip = assign_trip_to_drone(drone, task_def, distance)
        trips.append(trip)

    return trips
