"""模块三：无人机选择服务 — 数据库驱动 + 适配性评估"""
import json
from typing import List, Optional

# ─── 默认无人机参数（首次启动时写入数据库）───
# range_points: 分段线性插值点 [(载重kg, 航程km), ...]
DEFAULT_UAV_MODELS = [
    {
        "model_id": "dji-fc100",
        "brand": "大疆",
        "brand_en": "DJI",
        "model": "FlyCart 100",
        "max_payload": 65,
        "range_km": 12,
        "max_speed": 72,
        "cabin_volume": 120,
        "wind_resist": 6,
        "ip_rating": "IP55",
        "drop_mode": "箱式空投 / 绞盘吊挂",
        "features": ["激光雷达+毫米波雷达+五目鱼眼视觉", "全向避障", "标配降落伞", "9分钟极速快充"],
        "suitable_for": ["重载", "普通", "抢修", "安置保障"],
        "description": "大疆旗舰运载无人机，最大有效载重80kg(单电)/65kg(双电)，120L大货舱，支持箱式空投和绞盘吊挂双模式",
        "raw_params": "飞行速度: 水平最大20m/s(72km/h); 最大起飞重量: 149.9kg; 最大飞行距离: 空载26km/单电80kg载重6km/双电65kg载重12km; 最大有效载重: 80kg(单电)/65kg(双电); 抗风能力: 12m/s; 防护等级: IP55",
        "range_points": [[0, 12], [30, 12], [50, 12], [65, 12]],
    },
    {
        "model_id": "dji-fc30",
        "brand": "大疆",
        "brand_en": "DJI",
        "model": "FlyCart 30",
        "max_payload": 40,
        "range_km": 28,
        "max_speed": 72,
        "cabin_volume": 70,
        "wind_resist": 6,
        "ip_rating": "IP55",
        "drop_mode": "箱式空投 / 绞盘吊挂",
        "features": ["雷达避障", "双电池冗余"],
        "suitable_for": ["重载", "普通", "抢修", "安置保障"],
        "description": "大疆首款运载无人机，最大有效载重40kg(单电)/30kg(双电)，满载30kg航程16km",
        "raw_params": "飞行速度: 最大水平飞行速度20m/s(载重30kg); 最大起飞重量: 95kg; 最大飞行距离: 空载28km(双电)/满载30kg→16km(双电)/40kg→8km(单电); 最大有效载重: 40kg(单电)/30kg(双电); 抗风能力: 12m/s",
        "range_points": [[0, 28], [30, 16], [40, 8]],
    },
    {
        "model_id": "fy-ark80",
        "brand": "丰翼",
        "brand_en": "Fengyi",
        "model": "方舟 ARK80",
        "max_payload": 30,
        "range_km": 90,
        "max_speed": 90,
        "cabin_volume": 144,
        "wind_resist": 5,
        "ip_rating": "—",
        "drop_mode": "箱式空投",
        "features": ["升力翼多旋翼构型", "多冗余传感器", "单动力失效保护", "标配整机降落伞"],
        "suitable_for": ["医疗", "冷链", "精密", "普通"],
        "description": "丰翼中大型物流无人机，30kg载重，满载30kg航程30km，载重20kg航程60km，全球首张升力翼多旋翼型号合格证",
        "raw_params": "最大巡航速度: 90km/h; 最大有效载重: 30kg; 最大飞行距离: 满载30kg→30km/载重20kg→60km; 货舱容积: 144L(模块化货舱); 构型特点: 升力翼多旋翼",
        "range_points": [[0, 90], [20, 60], [30, 30]],
    },
    {
        "model_id": "fy-ark40",
        "brand": "丰翼",
        "brand_en": "Fengyi",
        "model": "方舟 ARK40",
        "max_payload": 10,
        "range_km": 20,
        "max_speed": 50,
        "cabin_volume": 96,
        "wind_resist": 7,
        "ip_rating": "—",
        "drop_mode": "箱式空投",
        "features": ["毫米波雷达+双目视觉", "智能避障", "厘米级精准降落"],
        "suitable_for": ["医疗", "冷链", "精密", "普通"],
        "description": "丰翼轻型物流无人机，10kg载重，4轴8旋翼垂直起降，全国首张中型多旋翼无人机特殊适航证",
        "raw_params": "最大巡航速度: 平均50km/h(最大14m/s); 最大有效载重: 10kg; 最大飞行距离: 20km(满电); 货舱容积: 超96L; 抗风能力: 可抵御7级风力; 构型特点: 4轴8旋翼垂直起降",
        "range_points": [[0, 20], [10, 12]],
    },
    {
        "model_id": "jd-jdx500",
        "brand": "京东",
        "brand_en": "JD",
        "model": "JDX-500 京蜓",
        "max_payload": 120,
        "range_km": 1800,
        "max_speed": 60,
        "cabin_volume": 0,
        "wind_resist": 5,
        "ip_rating": "—",
        "drop_mode": "短距起降",
        "features": ["自转旋翼构型", "短距起降"],
        "suitable_for": ["重载", "普通", "抢修", "安置保障"],
        "description": "京东大型物流无人机，120kg重载，半径450km(最大航程1800km)，自转旋翼构型短距起降，适合中短距物流运输",
        "raw_params": "最大有效载重: 120kg; 飞行半径/航程: 半径450km(最大航程1800km); 构型特点: 自转旋翼构型短距起降; 适用场景: 中短距物流运输",
        "range_points": [[0, 1800], [120, 900]],
    },
    {
        "model_id": "jd-jdx50",
        "brand": "京东",
        "brand_en": "JD",
        "model": "JDX-50 京燕",
        "max_payload": 15,
        "range_km": 30,
        "max_speed": 54,
        "cabin_volume": 50,
        "wind_resist": 5,
        "ip_rating": "—",
        "drop_mode": "箱式空投",
        "features": ["多旋翼", "模块化设计"],
        "suitable_for": ["普通", "医疗", "抢修"],
        "description": "京东中型物流无人机，15kg载重，半径15km，模块化设计，适合末端配送、山区及跨江运输、应急配送",
        "raw_params": "最大有效载重: 15kg; 飞行半径/航程: 半径15km; 构型特点: 多旋翼模块化设计; 适用场景: 末端配送、山区及跨江运输、应急配送",
        "range_points": [[0, 30], [15, 15]],
    },
    {
        "model_id": "jd-jdx20",
        "brand": "京东",
        "brand_en": "JD",
        "model": "JDX-20 京鹊",
        "max_payload": 10,
        "range_km": 48,
        "max_speed": 98,
        "cabin_volume": 20,
        "wind_resist": 6,
        "ip_rating": "—",
        "drop_mode": "箱式空投",
        "features": ["多旋翼", "流线型全封闭外壳"],
        "suitable_for": ["普通", "医疗", "精密"],
        "description": "京东轻型末端配送无人机，10kg载重，最大速度98km/h，半径24km，可中雨中雪6级大风夜间运行",
        "raw_params": "最大飞行速度: 98km/h; 最大有效载重: 10kg; 飞行半径/航程: 半径24km; 构型特点: 多旋翼流线型全封闭外壳; 抗环境能力: 中雨中雪6级大风及夜间运行",
        "range_points": [[0, 48], [10, 24]],
    },
]


def _get_db():
    """获取数据库会话"""
    from app.core.database import SessionLocal
    return SessionLocal()


def _seed_uav_params():
    """首次启动时将默认无人机参数写入数据库"""
    from app.models.uav_param import UavParam
    db = _get_db()
    try:
        count = db.query(UavParam).count()
        if count > 0:
            return
        for m in DEFAULT_UAV_MODELS:
            record = UavParam(
                model_id=m["model_id"],
                brand=m["brand"],
                brand_en=m.get("brand_en", ""),
                model=m["model"],
                max_payload=m["max_payload"],
                range_km=m["range_km"],
                max_speed=m["max_speed"],
                cabin_volume=m.get("cabin_volume"),
                wind_resist=m.get("wind_resist"),
                ip_rating=m.get("ip_rating"),
                drop_mode=m.get("drop_mode"),
                features=json.dumps(m.get("features", []), ensure_ascii=False),
                suitable_for=json.dumps(m.get("suitable_for", []), ensure_ascii=False),
                description=m.get("description", ""),
                raw_params=m.get("raw_params", ""),
                range_points=json.dumps(m.get("range_points", []), ensure_ascii=False),
            )
            db.add(record)
        db.commit()
        print(f"[UAV] 已初始化 {len(DEFAULT_UAV_MODELS)} 个无人机型号到数据库")
    finally:
        db.close()


def _row_to_dict(row) -> dict:
    """将数据库行转为字典"""
    return {
        "id": row.model_id,
        "model_id": row.model_id,
        "brand": row.brand,
        "brand_en": row.brand_en or "",
        "model": row.model,
        "max_payload": row.max_payload,
        "range_km": row.range_km,
        "max_speed": row.max_speed,
        "cabin_volume": row.cabin_volume or 0,
        "wind_resist": row.wind_resist or 0,
        "ip_rating": row.ip_rating or "",
        "drop_mode": row.drop_mode or "",
        "features": json.loads(row.features) if row.features else [],
        "suitable_for": json.loads(row.suitable_for) if row.suitable_for else [],
        "description": row.description or "",
        "raw_params": row.raw_params or "",
        "range_points": json.loads(row.range_points) if row.range_points else [],
    }


def get_all_models() -> list:
    """获取所有无人机型号（从数据库读取）"""
    from app.models.uav_param import UavParam
    _seed_uav_params()
    db = _get_db()
    try:
        rows = db.query(UavParam).all()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_all_brands() -> list:
    """获取所有品牌"""
    models = get_all_models()
    brands = {}
    for m in models:
        if m["brand"] not in brands:
            brands[m["brand"]] = {
                "name": m["brand"],
                "name_en": m["brand_en"],
                "models": [],
            }
        brands[m["brand"]]["models"].append(m["model_id"])
    return list(brands.values())


def get_model_by_id(model_id: str) -> Optional[dict]:
    """根据ID获取无人机型号"""
    from app.models.uav_param import UavParam
    _seed_uav_params()
    db = _get_db()
    try:
        row = db.query(UavParam).filter(UavParam.model_id == model_id).first()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def update_model(model_id: str, data: dict) -> Optional[dict]:
    """更新无人机型号参数"""
    from app.models.uav_param import UavParam
    db = _get_db()
    try:
        row = db.query(UavParam).filter(UavParam.model_id == model_id).first()
        if not row:
            return None
        for key in ["max_payload", "range_km", "max_speed", "cabin_volume",
                     "wind_resist", "ip_rating", "drop_mode", "description", "raw_params"]:
            if key in data:
                setattr(row, key, data[key])
        if "features" in data:
            row.features = json.dumps(data["features"], ensure_ascii=False) if isinstance(data["features"], list) else data["features"]
        if "suitable_for" in data:
            row.suitable_for = json.dumps(data["suitable_for"], ensure_ascii=False) if isinstance(data["suitable_for"], list) else data["suitable_for"]
        if "range_points" in data:
            row.range_points = json.dumps(data["range_points"], ensure_ascii=False) if isinstance(data["range_points"], list) else data["range_points"]
        if "model" in data:
            row.model = data["model"]
        db.commit()
        db.refresh(row)
        return _row_to_dict(row)
    finally:
        db.close()


def assess_selection(selections: list, demands: list, distance_matrix: dict = None):
    """
    评估无人机选择方案（使用数据库中的最新参数）

    参数:
        selections: [{ model_id, quantity }] 用户选择的无人机
        demands: [{ name, total_weight, priority, special_requirements, distance_km }]
        distance_matrix: 可选的距离矩阵数据

    返回:
        {uavs: [...], summary: {...}, suggestions: [...]}
    """
    uav_details = []
    suggestions = []
    total_payload_capacity = 0
    total_demand_weight = sum(d.get("total_weight", 0) for d in demands)
    max_demand_distance = max((d.get("distance_km", 0) for d in demands), default=0)

    for sel in selections:
        model = get_model_by_id(sel["model_id"])
        if not model:
            continue
        qty = sel.get("quantity", 1)

        single_capacity = model["max_payload"]
        model_total_capacity = single_capacity * qty
        total_payload_capacity += model_total_capacity

        max_single_village_weight = max((d.get("total_weight", 0) for d in demands), default=0)
        if max_single_village_weight > single_capacity:
            load_status = "需要多趟"
            load_detail = f"单个村庄最大需求 {max_single_village_weight}kg 超过单架载重 {single_capacity}kg，每村需多趟配送"
        else:
            load_status = "满足"
            load_detail = f"单架载重 {single_capacity}kg 可满足单村最大需求 {max_single_village_weight}kg"

        max_one_way = model["range_km"] / 2
        if max_demand_distance > max_one_way:
            range_status = "不足"
            range_detail = f"最远需求点距离 {max_demand_distance}km 超出 {model['model']} 满载单程航程 {max_one_way}km，需更换机型或增设中转点"
        elif max_demand_distance > max_one_way * 0.8:
            range_status = "紧张"
            range_detail = f"最远需求点距离 {max_demand_distance}km 接近 {model['model']} 满载单程航程 {max_one_way}km，余量不足"
        else:
            range_status = "满足"
            range_detail = f"最远需求点距离 {max_demand_distance}km，在 {model['model']} 满载单程航程 {max_one_way}km 范围内"

        special_reqs = set()
        for d in demands:
            if d.get("special_requirements"):
                special_reqs.add(d["special_requirements"])

        fit_issues = []
        for req in special_reqs:
            if "冷链" in req and "冷链" not in model["suitable_for"]:
                fit_issues.append(f"该机型不支持冷链运输（需求：{req}）")
            if "医疗" in req and "医疗" not in model["suitable_for"]:
                fit_issues.append(f"该机型不适合医疗物资运输（需求：{req}）")
            if "精密" in req and "精密" not in model["suitable_for"]:
                fit_issues.append(f"该机型不适合精密仪器运输（需求：{req}）")

        fit_status = "适配" if not fit_issues else "部分适配"

        detail = {
            "model_id": model["model_id"],
            "brand": model["brand"],
            "model_name": model["model"],
            "quantity": qty,
            "max_payload": single_capacity,
            "total_payload": model_total_capacity,
            "range_km": model["range_km"],
            "max_speed": model["max_speed"],
            "load_status": load_status,
            "load_detail": load_detail,
            "range_status": range_status,
            "range_detail": range_detail,
            "fit_status": fit_status,
            "fit_issues": fit_issues,
        }
        uav_details.append(detail)

    # 总体载重评估
    if total_payload_capacity > 0:
        load_ratio = total_demand_weight / total_payload_capacity
        if load_ratio > 2:
            overall_load_status = "严重不足"
            overall_load_detail = f"需求总重 {total_demand_weight}kg 远超所有无人机总载重 {total_payload_capacity}kg（{load_ratio:.1f}倍），需大幅增加无人机或更换机型"
        elif load_ratio > 1:
            overall_load_status = "不足"
            overall_load_detail = f"需求总重 {total_demand_weight}kg 超过所有无人机总载重 {total_payload_capacity}kg，需增加数量或更换机型"
        else:
            overall_load_status = "满足"
            overall_load_detail = f"所有无人机总载重 {total_payload_capacity}kg 可满足需求总重 {total_demand_weight}kg，载重利用率 {load_ratio * 100:.1f}%，预计需要多趟配送"
    else:
        overall_load_status = "未知"
        overall_load_detail = "无法计算总载重"
        load_ratio = 0

    if total_demand_weight > total_payload_capacity:
        suggestions.append({
            "type": "warning",
            "content": f"当前所有无人机总载重 {total_payload_capacity}kg 不足以满足需求总重 {total_demand_weight}kg，建议增加无人机数量或更换更大载重机型",
        })
    else:
        suggestions.append({
            "type": "info",
            "content": f"所有无人机总载重 {total_payload_capacity}kg ≥ 需求总重 {total_demand_weight}kg，通过多趟往返可完成配送",
        })

    if max_demand_distance > 0:
        for d in uav_details:
            if d["range_status"] == "不足":
                suggestions.append({
                    "type": "warning",
                    "content": f"{d['model_name']} 航程不足以覆盖最远需求点，建议更换长航程机型或增设中转点",
                })

    has_load_issue = overall_load_status in ["不足", "严重不足"]
    has_range_issue = any(d["range_status"] == "不足" for d in uav_details)

    if not has_load_issue and not has_range_issue:
        suggestions.append({
            "type": "success",
            "content": "当前无人机选择方案基本可行，总载重和航程均满足需求",
        })

    for d in uav_details:
        if d["load_status"] == "需要多趟":
            suggestions.append({
                "type": "info",
                "content": f"{d['model_name']}×{d['quantity']} 需要多趟往返配送，路径规划将自动拆分任务",
            })

    all_ok = not has_load_issue and not has_range_issue and all(
        d["range_status"] in ["满足", "紧张"] for d in uav_details
    )

    summary = {
        "total_demand_weight": total_demand_weight,
        "total_payload_capacity": total_payload_capacity,
        "max_demand_distance": max_demand_distance,
        "load_ratio": round(load_ratio * 100, 1) if total_payload_capacity > 0 else 0,
        "overall_load_status": overall_load_status,
        "overall_load_detail": overall_load_detail,
        "feasible": all_ok,
        "feasible_text": "方案可行" if all_ok else "方案存在问题，需调整",
    }

    return {
        "uavs": uav_details,
        "summary": summary,
        "suggestions": suggestions,
    }


def assess_with_llm():
    """调用大模型进行无人机智能选型"""
    import time
    from app.services.llm_service import chat, load_agent_prompt, load_config_content, is_configured
    from app.core.config import settings

    system_prompt = load_agent_prompt("uavSEA.md")
    config_content = load_config_content("任务配置信息.md")
    if not config_content:
        raise RuntimeError("配置文件 LLM/任务配置信息.md 为空或不存在")

    user_prompt = f"以下是当前任务的完整配置信息（包含配送中心、需求点、距离矩阵、物资需求、无人机型号库），请根据你的专业规划能力，为本任务推荐最佳无人机组合方案。\n\n{config_content}"

    start_time = time.time()
    reply = chat(system_prompt, user_prompt, temperature=0.3)
    elapsed = time.time() - start_time

    if not reply:
        raise RuntimeError("大模型返回为空")

    return {
        "llm_used": True,
        "raw_text": reply,
        "elapsed_seconds": round(elapsed, 1),
        "model_used": settings.LLM_MODEL,
    }
