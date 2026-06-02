"""任务数据模型 — 解析前端传入的 task JSON"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Depot:
    id: str
    name: str
    longitude: float
    latitude: float


@dataclass
class Material:
    type: str
    weight: float


@dataclass
class DemandPoint:
    id: str
    name: str
    longitude: float
    latitude: float
    priority: str  # "urgent" | "high" | "medium" | "low" | "normal"
    delivery_mode: str = "optional"  # "direct" | "optional"
    materials: List[Material] = field(default_factory=list)
    _total_weight: float = 0.0  # 直接传入的总重量

    @property
    def total_weight(self) -> float:
        # 如果直接传入了总重量，优先使用它
        if self._total_weight > 0:
            return self._total_weight
        # 否则从物资列表计算
        return sum(m.weight for m in self.materials)

    @property
    def priority_value(self) -> int:
        """优先级数值（越小越优先）"""
        mapping = {"urgent": 1, "high": 2, "medium": 3, "low": 4, "normal": 5}
        return mapping.get(self.priority, 3)


@dataclass
class UAVSpec:
    id: str
    name: str
    max_payload: float
    max_range: float
    battery_capacity: float = 100.0
    max_speed: float = 60.0
    quantity: int = 1
    range_points: list = field(default_factory=list)


@dataclass
class Task:
    depot: Depot
    demand_points: List[DemandPoint]
    distance_matrix: List[List[float]]
    uavs: List[UAVSpec]

    @property
    def num_points(self) -> int:
        return len(self.demand_points)

    @property
    def total_demand_weight(self) -> float:
        return sum(dp.total_weight for dp in self.demand_points)


def parse_task(data: dict) -> Task:
    """从 dict 解析出 Task 对象"""
    depot_data = data["depot"]
    depot = Depot(
        id=depot_data["id"],
        name=depot_data["name"],
        longitude=depot_data["longitude"],
        latitude=depot_data["latitude"],
    )

    demand_points = []
    for dp_data in data.get("demand_points", []):
        materials = [
            Material(type=m["type"], weight=m["weight"])
            for m in dp_data.get("materials", [])
        ]
        demand_points.append(DemandPoint(
            id=dp_data["id"],
            name=dp_data["name"],
            longitude=dp_data["longitude"],
            latitude=dp_data["latitude"],
            priority=dp_data.get("priority", "medium"),
            delivery_mode=dp_data.get("delivery_mode", "optional"),
            materials=materials,
            _total_weight=dp_data.get("total_weight", 0.0),
        ))

    uavs = []
    for u_data in data.get("uavs", []):
        uavs.append(UAVSpec(
            id=u_data["id"],
            name=u_data["name"],
            max_payload=u_data["max_payload"],
            max_range=u_data["max_range"],
            battery_capacity=u_data.get("battery_capacity", 100.0),
            max_speed=u_data.get("max_speed", 60.0),
            quantity=u_data.get("quantity", 1),
            range_points=u_data.get("range_points", []),
        ))

    distance_matrix = data.get("distance_matrix", [])

    return Task(
        depot=depot,
        demand_points=demand_points,
        distance_matrix=distance_matrix,
        uavs=uavs,
    )
