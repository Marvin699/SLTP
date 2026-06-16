import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.image_config import ImageConfig

def init_fixed_data():
    db = SessionLocal()
    try:
        configs = [
            {"group_id": 1, "slot": 1, "alpha": "1.1", "beta": "7", "rho": "0.05"},
            {"group_id": 1, "slot": 2, "alpha": "1.2", "beta": "6", "rho": "0.3"},
        ]
        
        for cfg in configs:
            existing = db.query(ImageConfig).filter(
                ImageConfig.group_id == cfg["group_id"],
                ImageConfig.slot == cfg["slot"]
            ).first()
            
            if existing:
                existing.alpha = cfg["alpha"]
                existing.beta = cfg["beta"]
                existing.rho = cfg["rho"]
            else:
                new_config = ImageConfig(
                    group_id=cfg["group_id"],
                    slot=cfg["slot"],
                    alpha=cfg["alpha"],
                    beta=cfg["beta"],
                    rho=cfg["rho"],
                )
                db.add(new_config)
        
        db.commit()
        print("逐日组配置初始化成功")
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_fixed_data()
