"""能耗模型 — 基于动态载重的能耗计算"""


def compute_energy(distance: float, current_load: float, max_payload: float) -> float:
    """
    计算一段飞行的能耗。

    公式: energy = distance × (1 + current_load / max_payload)

    载重越高，能耗越大。空载时能耗 = distance。
    """
    if max_payload <= 0:
        return distance
    return distance * (1 + current_load / max_payload)


def compute_energy_with_battery(
    distance: float,
    current_load: float,
    max_payload: float,
    battery_capacity: float,
    current_energy_used: float,
) -> float:
    """
    计算能耗并检查电池容量。

    返回: 能耗值。如果超出电池容量则返回 -1 表示不可行。
    """
    energy = compute_energy(distance, current_load, max_payload)
    if current_energy_used + energy > battery_capacity:
        return -1  # 电池不足
    return energy
