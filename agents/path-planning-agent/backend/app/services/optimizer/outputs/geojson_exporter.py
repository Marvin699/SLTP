"""GeoJSON 导出器 — 将路径结果转为 GeoJSON FeatureCollection 供 Leaflet 展示"""
from typing import List, Dict, Any
from app.services.optimizer.models.task_model import Task
from app.services.optimizer.models.route_model import UAVRoute


def export_geojson(task: Task, uav_routes: List[UAVRoute] = None, trips: List = None) -> Dict[str, Any]:
    """
    将路径结果导出为 GeoJSON FeatureCollection。

    包含:
    1. 配送中心 Point
    2. 各需求点 Point
    3. 各航次路径 LineString（每个航次独立）
    """
    features = []

    # 1. 配送中心
    depot = task.depot
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [depot.longitude, depot.latitude],
        },
        "properties": {
            "id": depot.id,
            "name": depot.name,
            "feature_type": "depot",
            "marker_color": "#ff3d57",
        },
    })

    # 2. 需求点
    for dp in task.demand_points:
        priority_colors = {
            "urgent": "#ff3d57",
            "high": "#ffb300",
            "medium": "#00e5ff",
            "low": "#7a93bb",
            "normal": "#3d5a80",
        }
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [dp.longitude, dp.latitude],
            },
            "properties": {
                "id": dp.id,
                "name": dp.name,
                "feature_type": "demand",
                "priority": dp.priority,
                "total_weight": dp.total_weight,
                "marker_color": priority_colors.get(dp.priority, "#00e5ff"),
            },
        })

    # 3. 航次路径（每个航次一条 LineString）
    if trips:
        # 构建索引到坐标的映射
        coord_map = {
            "0": [task.depot.longitude, task.depot.latitude],
        }
        for i, dp in enumerate(task.demand_points):
            coord_map[str(i + 1)] = [dp.longitude, dp.latitude]
        coord_map[task.depot.id] = [task.depot.longitude, task.depot.latitude]
        for dp in task.demand_points:
            coord_map[dp.id] = [dp.longitude, dp.latitude]

        for trip_idx, trip in enumerate(trips):
            # 构建航次坐标
            coordinates = []
            for node in trip.route:
                node_str = str(node)
                if node_str in coord_map:
                    coordinates.append(coord_map[node_str])

            if len(coordinates) < 2:
                continue  # 跳过无效航次

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
                "properties": {
                    "feature_type": "route",
                    "trip_index": trip_idx,
                    "uav_id": trip.drone_id,
                    "uav_name": trip.drone_name,
                    "distance": round(trip.total_distance, 2),
                    "load": round(trip.load, 2),
                    "points_served": trip.points_served if hasattr(trip, 'points_served') else len(trip.route) - 2,
                    "delivery_mode": trip.delivery_mode,
                    "village_name": trip.village_name,
                },
            })

    return {
        "type": "FeatureCollection",
        "features": features,
    }
