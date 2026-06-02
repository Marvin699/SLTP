"""DroneState — 无人机调度状态"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class DroneState:
    """无人机在调度过程中的状态"""
    drone_id: str
    drone_type: str
    max_payload: float
    max_range: float
    max_speed: float  # km/h

    # 调度状态
    busy_until: float = 0.0              # 忙碌到什么时间(min)
    current_location: int = 0            # 当前位置节点索引(0=depot)
    current_load: float = 0.0            # 当前载重
    remaining_range: float = 0.0         # 剩余航程

    # 累计统计
    total_distance: float = 0.0
    total_time: float = 0.0
    total_trips: int = 0
    villages_served: set = field(default_factory=set)

    def __post_init__(self):
        self.remaining_range = self.max_range

    def is_available(self, time: float) -> bool:
        """在指定时间是否可用"""
        return time >= self.busy_until

    def effective_range(self, load: float) -> float:
        """根据载重计算有效航程（分段线性插值）"""
        if self.max_payload <= 0:
            return self.max_range
        ratio = load / self.max_payload
        if ratio <= 0:
            return self.max_range
        elif ratio >= 1:
            return self.max_range * 0.3
        else:
            return self.max_range * (1.0 - 0.7 * ratio)

    def can_serve(self, distance: float, load: float) -> bool:
        """能否完成一次往返运输"""
        eff_range = self.effective_range(load)
        return distance * 2 <= eff_range

    def complete_trip(self, distance: float, time: float, load: float, village: str):
        """完成一次运输任务"""
        self.total_distance += distance * 2  # 往返
        self.total_time += time
        self.total_trips += 1
        self.villages_served.add(village)
        self.busy_until += time
        self.current_location = 0  # 回到 depot
        self.current_load = 0
        # 回 depot 后航程恢复
        self.remaining_range = self.max_range

    def to_dict(self) -> dict:
        return {
            "drone_id": self.drone_id,
            "drone_type": self.drone_type,
            "max_payload": self.max_payload,
            "max_range": self.max_range,
            "max_speed": self.max_speed,
            "total_distance": round(self.total_distance, 2),
            "total_time": round(self.total_time, 2),
            "total_trips": self.total_trips,
            "villages_served": sorted(list(self.villages_served)),
        }
