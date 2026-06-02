"""信息素管理 — 初始化、挥发、更新、精英强化"""
from typing import List, Tuple, Dict


class PheromoneMatrix:
    """信息素矩阵"""

    def __init__(self, num_nodes: int, initial_value: float = 0.1):
        """
        初始化信息素矩阵。

        参数:
            num_nodes: 节点数量（含 depot）
            initial_value: 初始信息素值
        """
        self.num_nodes = num_nodes
        self.initial_value = initial_value
        self.matrix = [[initial_value] * num_nodes for _ in range(num_nodes)]

    def get(self, i: int, j: int) -> float:
        """获取边 (i, j) 的信息素"""
        return self.matrix[i][j]

    def evaporate(self, evaporation_rate: float):
        """
        信息素挥发。

        τ_ij = (1 - ρ) × τ_ij
        """
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                self.matrix[i][j] *= (1 - evaporation_rate)

    def deposit(self, path: List[int], cost: float, Q: float):
        """
        在路径上沉积信息素。

        Δτ = Q / cost

        参数:
            path: 节点索引序列
            cost: 路径成本
            Q: 信息素强度常数
        """
        if cost <= 0:
            return
        delta = Q / cost
        for k in range(len(path) - 1):
            i, j = path[k], path[k + 1]
            self.matrix[i][j] += delta
            self.matrix[j][i] += delta  # 对称

    def elite_deposit(self, path: List[int], cost: float, Q: float, elite_bonus: float = 2.0):
        """
        精英蚂蚁额外强化。

        精英蚂蚁的信息素沉积量是普通蚂蚁的 elite_bonus 倍。
        """
        if cost <= 0:
            return
        delta = (Q / cost) * elite_bonus
        for k in range(len(path) - 1):
            i, j = path[k], path[k + 1]
            self.matrix[i][j] += delta
            self.matrix[j][i] += delta

    def get_matrix(self) -> List[List[float]]:
        """返回完整矩阵（用于调试）"""
        return [row[:] for row in self.matrix]
