"""距离矩阵处理 — 从 task JSON 构建可用于算法的距离矩阵"""
import math
from typing import List, Tuple
from app.services.optimizer.models.task_model import Task


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点之间的 Haversine 距离（公里）"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def build_distance_matrix(task: Task) -> List[List[float]]:
    """
    从 task 构建距离矩阵。
    如果 task 已包含 distance_matrix 则直接使用，
    否则根据经纬度用 Haversine 公式计算。

    矩阵索引: 0=depot, 1~N=demand_points
    """
    if task.distance_matrix and len(task.distance_matrix) > 0:
        return task.distance_matrix

    # 根据坐标计算
    points = [task.depot] + task.demand_points
    n = len(points)
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0.0)
            else:
                d = haversine(
                    points[i].latitude, points[i].longitude,
                    points[j].latitude, points[j].longitude,
                )
                row.append(round(d, 2))
        matrix.append(row)
    return matrix


def get_depot_to_point_distances(task: Task, matrix: List[List[float]]) -> List[float]:
    """获取 depot 到各需求点的距离（matrix 第一行，去掉自身）"""
    if len(matrix) > 0:
        return matrix[0][1:]  # 跳过 depot 自身
    return [0.0] * len(task.demand_points)


def get_return_distances(task: Task, matrix: List[List[float]]) -> List[float]:
    """获取各需求点返回 depot 的距离"""
    if len(matrix) > 0:
        return [matrix[i][0] for i in range(1, len(matrix))]
    return [0.0] * len(task.demand_points)
