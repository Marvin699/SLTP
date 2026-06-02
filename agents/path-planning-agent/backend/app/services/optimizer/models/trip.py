"""Trip 数据模型 — 表示单次运输任务"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Trip:
    """单次运输任务（一趟：depot → 村庄 → depot）"""
    trip_id: int
    drone_id: str
    drone_type: str
    village_id: str
    village_name: str
    route: List[int]            # 节点索引序列 [0, village_idx, 0]
    load: float                 # 本趟运载重量(kg)
    total_distance: float       # 本趟飞行距离(km)
    total_time: float           # 本趟飞行时间(min)
    drone_name: str = ""        # 无人机名称（如 "JDX-500 京蜓"）
    village_loads: Dict[str, float] = field(default_factory=dict)  # 每个村庄的具体载重 {village_name: weight}
    feasible: bool = True
    priority: int = 3
    cargo_type: str = ""
    cold_chain: bool = False
    start_time: float = 0.0    # 开始时间(min)
    end_time: float = 0.0      # 结束时间(min)
    delivery_mode: str = "optional"  # 配送模式: "direct"=必须直飞, "optional"=可选联飞

    def to_dict(self) -> dict:
        return {
            "trip_id": self.trip_id,
            "drone_id": self.drone_id,
            "drone_type": self.drone_type,
            "drone_name": self.drone_name,
            "village_id": self.village_id,
            "village_name": self.village_name,
            "route": self.route,
            "load": round(self.load, 2),
            "total_distance": round(self.total_distance, 2),
            "total_time": round(self.total_time, 2),
            "feasible": self.feasible,
            "priority": self.priority,
            "cargo_type": self.cargo_type,
            "cold_chain": self.cold_chain,
            "start_time": round(self.start_time, 2),
            "end_time": round(self.end_time, 2),
            "delivery_mode": self.delivery_mode,
        }
