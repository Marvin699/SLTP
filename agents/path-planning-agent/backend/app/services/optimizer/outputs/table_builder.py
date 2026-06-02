"""表格构建器 — 生成文档要求的3个表格"""
from typing import List, Dict, Any
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.solution import Solution
from app.services.optimizer.models.trip import Trip


def build_summary_stats(solution: Solution, task: Task) -> Dict[str, Any]:
    """构建总体统计（表格上方的统计卡片）"""
    return {
        "total_distance": round(solution.total_distance, 2),
        "total_time": round(solution.total_time, 2),
        "total_trips": solution.total_trips,
        "drone_count": len(solution.get_drone_ids()),
        "village_count": len(solution.get_village_names()),
        "feasible": solution.feasibility_check(),
    }


def build_route_summary_table(solution: Solution, task: Task) -> List[Dict[str, Any]]:
    """
    表格1：路径汇总（支持多点串联路径）

    列: 路径编号, 无人机, 路径, 途经村庄, 距离(km), 时间(min), 配送重量(kg), 状态
    """
    table = []
    route_id = 1

    for trip in solution.trips:
        # 多点路径显示
        if len(trip.route) > 3:
            # 多点串联路径: [0, 1, 2, 0] → "0→1→2→0"
            route_path = "→".join(str(n) for n in trip.route)
            # 途经村庄（排除depot）
            village_nodes = [n for n in trip.route if n != 0]
            village_names = []
            for node_idx in village_nodes:
                if 1 <= node_idx <= len(task.demand_points):
                    village_names.append(task.demand_points[node_idx - 1].name)
            village_name = "、".join(village_names) if village_names else "-"
        else:
            # 单点路径: [0, 1, 0]
            route_path = f"0→{trip.route[1]}→0" if len(trip.route) >= 3 else "0→0"
            village_name = trip.village_name

        table.append({
            "route_id": route_id,
            "drone_name": trip.drone_type,
            "route_path": route_path,
            "route_nodes": ",".join(str(n) for n in trip.route),
            "distance": round(trip.total_distance, 2),
            "time": round(trip.total_time, 2),
            "weight": round(trip.load, 2),
            "village_name": village_name,
            "trip_count": 1,
            "feasible": trip.feasible,
        })
        route_id += 1

    return table


def build_village_detail_table(solution: Solution, task: Task) -> List[Dict[str, Any]]:
    """
    表格2：村庄配送详情

    列: 村庄编号, 村庄名称, 需求重量(kg), 配送无人机, 无人机配送重量(kg), 趟次, 单程距离(km), 特殊要求
    """
    # 构建村庄信息映射
    village_info = {}
    for i, dp in enumerate(task.demand_points):
        village_info[dp.name] = {
            "village_id": i + 1,
            "village_name": dp.name,
            "demand_weight": dp.total_weight,
            "special_req": _get_special_req(dp),
        }

    # 按村庄分组 Trip
    village_drone_trips: Dict[str, Dict[str, List[Trip]]] = {}
    for trip in solution.trips:
        vname = trip.village_name
        did = trip.drone_id
        if vname not in village_drone_trips:
            village_drone_trips[vname] = {}
        if did not in village_drone_trips[vname]:
            village_drone_trips[vname][did] = []
        village_drone_trips[vname][did].append(trip)

    table = []
    for dp_idx, dp in enumerate(task.demand_points):
        vname = dp.name
        vinfo = village_info.get(vname, {})
        drone_trips_map = village_drone_trips.get(vname, {})

        if not drone_trips_map:
            # 无配送记录
            table.append({
                "village_id": vinfo.get("village_id", dp_idx + 1),
                "village_name": vname,
                "demand_weight": round(dp.total_weight, 2),
                "drone_name": "-",
                "drone_weight": 0,
                "trip_count": 0,
                "one_way_distance": 0,
                "special_req": vinfo.get("special_req", ""),
            })
            continue

        for drone_id, d_trips in drone_trips_map.items():
            drone_weight = sum(t.load for t in d_trips)
            trip_count = len(d_trips)
            one_way_dist = d_trips[0].total_distance / 2 if d_trips else 0

            table.append({
                "village_id": vinfo.get("village_id", dp_idx + 1),
                "village_name": vname,
                "demand_weight": round(dp.total_weight, 2),
                "drone_name": d_trips[0].drone_type,
                "drone_weight": round(drone_weight, 2),
                "trip_count": trip_count,
                "one_way_distance": round(one_way_dist, 2),
                "special_req": vinfo.get("special_req", ""),
            })

    return table


def build_drone_detail_table(solution: Solution, task: Task) -> List[Dict[str, Any]]:
    """
    表格3：无人机配送详情

    列: 无人机编号, 机型, 速度(m/s), 最大载重(kg), 总飞行距离(km), 总飞行时间(min), 总趟次, 服务村庄, 备注
    """
    # 按无人机分组
    drone_trips: Dict[str, List[Trip]] = {}
    for trip in solution.trips:
        key = trip.drone_id
        if key not in drone_trips:
            drone_trips[key] = []
        drone_trips[key].append(trip)

    # 无人机规格映射
    uav_spec = {u.id: u for u in task.uavs}

    table = []
    for uav in task.uavs:
        trips = drone_trips.get(uav.id, [])
        total_dist = sum(t.total_distance for t in trips)
        total_time = sum(t.total_time for t in trips)
        total_trips = len(trips)
        villages = sorted(set(t.village_name for t in trips))

        # 速度转换: km/h → m/s
        speed_ms = round(uav.max_speed / 3.6, 2) if uav.max_speed else 0

        # 备注
        note = _generate_drone_note(uav, trips)

        table.append({
            "drone_id": uav.id,
            "drone_type": uav.name,
            "speed_ms": speed_ms,
            "max_payload": uav.max_payload,
            "total_distance": round(total_dist, 2),
            "total_time": round(total_time, 2),
            "total_trips": total_trips,
            "villages": "、".join(villages) if villages else "-",
            "note": note,
        })

    # 总计行
    all_villages = set(t.village_name for t in solution.trips)
    table.append({
        "drone_id": "总计",
        "drone_type": "-",
        "speed_ms": "-",
        "max_payload": "-",
        "total_distance": round(solution.total_distance, 2),
        "total_time": round(solution.total_time, 2),
        "total_trips": solution.total_trips,
        "villages": f"{len(all_villages)}个村庄",
        "note": "-",
    })

    return table


def _get_special_req(dp) -> str:
    """获取需求点的特殊要求"""
    reqs = []
    if dp.priority_value <= 2:
        reqs.append("高优先级")
    for m in dp.materials:
        if "冷链" in m.type or "冷藏" in m.type or "胰岛素" in m.type or "疫苗" in m.type:
            reqs.append("冷链运输")
            break
    return "，".join(reqs) if reqs else "普通配送"


def _generate_drone_note(uav, trips: List[Trip]) -> str:
    """生成无人机备注"""
    if not trips:
        return "未使用"

    notes = []
    # 判断角色
    total_dist = sum(t.total_distance for t in trips)
    if total_dist > 100:
        notes.append("远距离主力")
    elif total_dist < 20:
        notes.append("近距离")

    # 判断载重
    max_load = max((t.load for t in trips), default=0)
    if max_load >= uav.max_payload * 0.8:
        notes.append("重载")
    elif max_load <= uav.max_payload * 0.3:
        notes.append("轻载")

    # 冷链
    if any(t.cold_chain for t in trips):
        notes.append("冷链专航")

    return "，".join(notes) if notes else "常规运输"
