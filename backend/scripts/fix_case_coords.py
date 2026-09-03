"""一次性迁移：将案例中落水/偏差的村庄坐标修正为高德实测坐标（2026-09）"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.case_study import CaseStudy

# 高德地理编码实测坐标（广西靖西市渠洋镇）
FIX = {
    "渠洋村": (106.321514, 23.308425),  # 配送中心
    "怀渠村": (106.380769, 23.336847),
    "塘麻村": (106.371466, 23.270673),
    "坡乐村": (106.333831, 23.299707),
    "东风村": (106.306132, 23.332874),
    "古桥村": (106.286954, 23.305080),
    "新和村": (106.283733, 23.383753),
    "怀书村": (106.278383, 23.339094),
    "雅力村": (106.226579, 23.399337),
}


def fix_points(points):
    changed = 0
    for p in points or []:
        if p.get("name") in FIX:
            lng, lat = FIX[p["name"]]
            if abs(p.get("longitude", 0) - lng) > 1e-6 or abs(p.get("latitude", 0) - lat) > 1e-6:
                p["longitude"], p["latitude"] = lng, lat
                changed += 1
    return changed


def main():
    db = SessionLocal()
    cases = db.query(CaseStudy).filter(CaseStudy.is_active == True).all()
    for case in cases:
        total = 0
        center = json.loads(case.center_data) if case.center_data else None
        if center and center.get("name") in FIX:
            lng, lat = FIX[center["name"]]
            if abs(center.get("longitude", 0) - lng) > 1e-6 or abs(center.get("latitude", 0) - lat) > 1e-6:
                center["longitude"], center["latitude"] = lng, lat
                total += 1
            case.center_data = json.dumps(center, ensure_ascii=False)

        demands = json.loads(case.demand_points) if case.demand_points else []
        total += fix_points(demands)
        case.demand_points = json.dumps(demands, ensure_ascii=False)

        if total:
            db.commit()
            print(f"案例[{case.id}] {case.name}: 修正 {total} 个点位")
        else:
            print(f"案例[{case.id}] {case.name}: 坐标已正确，跳过")
    db.close()


if __name__ == "__main__":
    main()
