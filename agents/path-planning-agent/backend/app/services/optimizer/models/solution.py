"""Solution 数据模型 — 表示完整运输方案"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.services.optimizer.models.trip import Trip


@dataclass
class Solution:
    """完整运输方案"""
    trips: List[Trip] = field(default_factory=list)
    task_id: str = ""

    @property
    def total_distance(self) -> float:
        return sum(t.total_distance for t in self.trips)

    @property
    def total_time(self) -> float:
        return sum(t.total_time for t in self.trips)

    @property
    def makespan(self) -> float:
        """总完成时间（所有无人机中最晚完成的时间）"""
        if not self.trips:
            return 0.0
        return max(t.end_time for t in self.trips)

    @property
    def total_trips(self) -> int:
        return len(self.trips)

    @property
    def total_delivered(self) -> float:
        return sum(t.load for t in self.trips)

    def utilization_rate(self) -> float:
        """无人机利用率 = 总飞行时间 / (makespan × 无人机数)"""
        drone_ids = set(t.drone_id for t in self.trips)
        if not drone_ids or self.makespan == 0:
            return 0.0
        return self.total_time / (self.makespan * len(drone_ids))

    def feasibility_check(self) -> bool:
        return all(t.feasible for t in self.trips)

    def get_drone_ids(self) -> set:
        return set(t.drone_id for t in self.trips)

    def get_village_names(self) -> set:
        village_names = set()
        for t in self.trips:
            # 处理联飞航次的村庄名称（逗号分隔）
            names = t.village_name.split(',')
            for name in names:
                name = name.strip()
                if name:
                    village_names.add(name)
        return village_names

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "trips": [t.to_dict() for t in self.trips],
            "total_distance": round(self.total_distance, 2),
            "total_time": round(self.total_time, 2),
            "makespan": round(self.makespan, 2),
            "total_trips": self.total_trips,
            "total_delivered": round(self.total_delivered, 2),
            "utilization_rate": round(self.utilization_rate(), 4),
            "feasible": self.feasibility_check(),
            "drone_count": len(self.get_drone_ids()),
            "village_count": len(self.get_village_names()),
        }
