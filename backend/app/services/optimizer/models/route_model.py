"""路径结果数据模型"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RouteSegment:
    """路径中的一段"""
    from_id: str
    from_name: str
    to_id: str
    to_name: str
    distance: float
    energy: float
    load_before: float  # 出发时载重
    load_after: float   # 到达后载重


@dataclass
class UAVRoute:
    """单架无人机的路径结果"""
    uav_id: str
    uav_name: str
    path: List[str]           # 节点ID序列: ["depot", "point_1", "point_2", "depot"]
    path_names: List[str]     # 节点名称序列
    segments: List[RouteSegment]
    total_distance: float
    total_energy: float
    points_served: int
    initial_load: float
    delivery_mode: str = "optional"

    @property
    def cost(self) -> float:
        """综合成本"""
        return self.total_distance * 0.4 + self.total_energy * 0.6


@dataclass
class OptimizationResult:
    """整体优化结果"""
    routes: List[UAVRoute]
    total_distance: float
    total_energy: float
    optimization_score: float  # 0-100
    all_points_covered: bool
    iterations_used: int
    geojson: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "routes": [
                {
                    "uav_id": r.uav_id,
                    "uav_name": r.uav_name,
                    "path": r.path,
                    "path_names": r.path_names,
                    "segments": [
                        {
                            "from_id": s.from_id,
                            "from_name": s.from_name,
                            "to_id": s.to_id,
                            "to_name": s.to_name,
                            "distance": round(s.distance, 2),
                            "energy": round(s.energy, 2),
                            "load_before": round(s.load_before, 2),
                            "load_after": round(s.load_after, 2),
                        }
                        for s in r.segments
                    ],
                    "total_distance": round(r.total_distance, 2),
                    "total_energy": round(r.total_energy, 2),
                    "points_served": r.points_served,
                    "initial_load": round(r.initial_load, 2),
                }
                for r in self.routes
            ],
            "total_distance": round(self.total_distance, 2),
            "total_energy": round(self.total_energy, 2),
            "optimization_score": round(self.optimization_score, 1),
            "all_points_covered": self.all_points_covered,
            "iterations_used": self.iterations_used,
            "geojson": self.geojson,
        }
