import math
from typing import List, Tuple
from app.models.point import DeliveryPoint


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点之间的Haversine距离（公里）"""
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


def build_distance_matrix(
    points: List[DeliveryPoint],
) -> dict:
    """
    构建距离矩阵。
    返回格式：
    {
      "labels": ["C:配送中心", "需求点1", ...],
      "matrix": [[0, 5.83, ...], [5.83, 0, ...], ...],
      "return_distances": [0, 5.83, ...]  # 各需求点回配送中心距离
    }
    """
    # 按照 center 排前面，demand 排后面
    centers = [p for p in points if p.point_type.value == "center"]
    demands = [p for p in points if p.point_type.value == "demand"]
    ordered = centers + demands

    n = len(ordered)
    labels = []
    for i, p in enumerate(ordered):
        if p.point_type.value == "center":
            labels.append(f"C:{p.name}")
        else:
            labels.append(p.name)

    # 构建矩阵
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0.0)
            else:
                d = haversine(
                    ordered[i].latitude,
                    ordered[i].longitude,
                    ordered[j].latitude,
                    ordered[j].longitude,
                )
                row.append(round(d, 2))
        matrix.append(row)

    # 回程距离：各需求点 → 第一个配送中心
    return_distances = [0.0] * n
    if centers:
        c = centers[0]
        for i, p in enumerate(ordered):
            if p.point_type.value == "demand":
                return_distances[i] = round(
                    haversine(p.latitude, p.longitude, c.latitude, c.longitude), 2
                )

    return {
        "labels": labels,
        "matrix": matrix,
        "return_distances": return_distances,
    }
