"""无人机运行时状态模型 — 动态载重/能耗跟踪"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class UAVState:
    """无人机在配送过程中的实时状态"""
    uav_id: str
    uav_name: str
    max_payload: float
    max_range: float
    battery_capacity: float

    # 运行时状态
    current_load: float = 0.0
    total_distance: float = 0.0
    total_energy: float = 0.0
    remaining_range: float = 0.0
    visited_points: List[str] = field(default_factory=list)
    path: List[str] = field(default_factory=list)  # 节点ID序列

    def __post_init__(self):
        self.remaining_range = self.max_range

    def can_carry(self, weight: float) -> bool:
        """能否承载额外重量"""
        return self.current_load + weight <= self.max_payload

    def can_reach(self, distance: float) -> bool:
        """能否到达指定距离（含返航）"""
        return distance <= self.remaining_range

    def load_at_depot(self, weight: float):
        """在配送中心装载物资"""
        self.current_load += weight

    def deliver(self, point_id: str, distance: float, weight: float):
        """到达需求点并投送物资"""
        # 计算能耗（动态载重）
        energy = distance * (1 + self.current_load / self.max_payload) if self.max_payload > 0 else distance
        self.total_distance += distance
        self.total_energy += energy
        self.remaining_range -= distance
        self.current_load -= weight
        if self.current_load < 0:
            self.current_load = 0
        self.visited_points.append(point_id)
        self.path.append(point_id)

    def return_to_depot(self, distance: float):
        """返回配送中心"""
        energy = distance * (1 + self.current_load / self.max_payload) if self.max_payload > 0 else distance
        self.total_distance += distance
        self.total_energy += energy
        self.remaining_range -= distance
        self.current_load = 0
        # 重置剩余航程（回到 depot 后电池充满/补给完成）
        self.remaining_range = self.max_range
        self.path.append("depot")

    @property
    def load_ratio(self) -> float:
        """当前载重比"""
        return self.current_load / self.max_payload if self.max_payload > 0 else 0

    @property
    def range_ratio(self) -> float:
        """已用航程比"""
        used = self.max_range - self.remaining_range
        return used / self.max_range if self.max_range > 0 else 0
