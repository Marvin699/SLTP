"""物资需求数据与服务 — 基于渠洋镇案例真实数据"""

# 5 大物资类别，常见物资从案例提取
MATERIAL_CATEGORIES = [
    {
        "id": "repair",
        "name": "抢修类",
        "icon": "🔧",
        "color": "#ff6b35",
        "items": [
            {"name": "柴油发电机", "unit_weight": 45, "qty": 2},
            {"name": "电缆线盘", "unit_weight": 25, "qty": 3},
            {"name": "抽水泵", "unit_weight": 35, "qty": 2},
            {"name": "电焊机", "unit_weight": 20, "qty": 1},
            {"name": "维修工具箱", "unit_weight": 15, "qty": 2},
        ],
        "total_weight": 160,
        "priority": 1,
        "special": "重载、精密",
        "risk": "精密设备需防震包装，起降区需平整硬化地面",
    },
    {
        "id": "life",
        "name": "生活保障类",
        "icon": "🍚",
        "color": "#00d4ff",
        "items": [
            {"name": "矿泉水(箱)", "unit_weight": 12, "qty": 15},
            {"name": "方便食品(箱)", "unit_weight": 8, "qty": 20},
            {"name": "棉被", "unit_weight": 10, "qty": 15},
            {"name": "帐篷(大)", "unit_weight": 30, "qty": 5},
            {"name": "照明设备", "unit_weight": 5, "qty": 10},
        ],
        "total_weight": 690,
        "priority": 3,
        "special": "普通配送",
        "risk": "注意防水包装，避免受潮",
    },
    {
        "id": "medical",
        "name": "医疗救援类",
        "icon": "🏥",
        "color": "#ff4757",
        "items": [
            {"name": "急救包", "unit_weight": 5, "qty": 20},
            {"name": "消毒物资套装", "unit_weight": 5, "qty": 15},
            {"name": "担架", "unit_weight": 8, "qty": 5},
            {"name": "医用口罩(箱)", "unit_weight": 10, "qty": 10},
        ],
        "total_weight": 350,
        "priority": 1,
        "special": "医疗优先",
        "risk": "优先配送，需确认接收人身份，避免交叉污染",
    },
    {
        "id": "cold",
        "name": "冷链医疗类",
        "icon": "❄️",
        "color": "#70a1ff",
        "items": [
            {"name": "胰岛素(冷藏箱)", "unit_weight": 3, "qty": 3},
            {"name": "疫苗(冷藏箱)", "unit_weight": 2, "qty": 5},
            {"name": "血浆(冷藏箱)", "unit_weight": 5, "qty": 1},
        ],
        "total_weight": 25,
        "priority": 1,
        "special": "冷链运输",
        "risk": "全程2-8°C温控，需专用冷链无人机配送",
    },
    {
        "id": "settle",
        "name": "安置保障类",
        "icon": "🏕",
        "color": "#7bed9f",
        "items": [
            {"name": "大型帐篷", "unit_weight": 50, "qty": 10},
            {"name": "折叠床", "unit_weight": 15, "qty": 30},
            {"name": "御寒衣物(包)", "unit_weight": 10, "qty": 20},
            {"name": "防潮垫", "unit_weight": 5, "qty": 20},
        ],
        "total_weight": 1260,
        "priority": 2,
        "special": "体量较大",
        "risk": "大体量物资需分批多趟运输",
    },
]

# 案例 8 个需求点的真实物资数据（渠洋镇应急物资配送案例，重量与案例方案精确匹配）
CASE_VILLAGE_MATERIALS = {
    "怀渠村": {
        "category_ids": ["repair"],
        "weight": 100,
        "priority": 2,
        "note": "发电机2台（30kg/台）、电缆200米 — 重载，抢修点，陡坡",
        "items": [
            {"name": "柴油发电机", "unit_weight": 30, "qty": 2},
            {"name": "电缆(百米)", "unit_weight": 20, "qty": 2},
        ],
    },
    "塘麻村": {
        "category_ids": ["life"],
        "weight": 570,
        "priority": 3,
        "note": "矿泉水40箱、棉被30床 — 低洼积水区",
        "items": [
            {"name": "矿泉水(箱)", "unit_weight": 12, "qty": 40},
            {"name": "棉被", "unit_weight": 3, "qty": 30},
        ],
    },
    "坡乐村": {
        "category_ids": ["life", "settle"],
        "weight": 220,
        "priority": 2,
        "note": "大米20kg、折叠床80张 — 体量较大，乡政府广场，开阔",
        "items": [
            {"name": "大米(袋)", "unit_weight": 20, "qty": 1},
            {"name": "折叠床", "unit_weight": 15, "qty": 8},
        ],
    },
    "东风村": {
        "category_ids": ["medical"],
        "weight": 250,
        "priority": 1,
        "note": "急救包50个、消毒物资30箱 — 医疗优先，半山腰，起降困难",
        "items": [
            {"name": "急救包", "unit_weight": 2, "qty": 50},
            {"name": "消毒物资(箱)", "unit_weight": 5, "qty": 30},
        ],
    },
    "古桥村": {
        "category_ids": ["life"],
        "weight": 106,
        "priority": 3,
        "note": "方便食品50份、矿泉水80箱 — 桥头空地，狭窄",
        "items": [
            {"name": "方便食品(份)", "unit_weight": 0.5, "qty": 50},
            {"name": "矿泉水(箱)", "unit_weight": 12, "qty": 3},
        ],
    },
    "新和村": {
        "category_ids": ["cold"],
        "weight": 20,
        "priority": 1,
        "note": "冷链胰岛素30盒、疫苗50支 — 冷链运输，卫生所，有屋顶",
        "items": [
            {"name": "胰岛素(冷藏箱)", "unit_weight": 0.5, "qty": 30},
            {"name": "疫苗(冷藏箱)", "unit_weight": 0.1, "qty": 50},
        ],
    },
    "怀书村": {
        "category_ids": ["settle"],
        "weight": 170,
        "priority": 3,
        "note": "帐篷5顶、御寒衣物60套 — 山坡，不平整",
        "items": [
            {"name": "帐篷", "unit_weight": 15, "qty": 5},
            {"name": "御寒衣物(套)", "unit_weight": 2, "qty": 35},
        ],
    },
    "雅力村": {
        "category_ids": ["repair"],
        "weight": 200,
        "priority": 2,
        "note": "抽水泵2台（25kg/台）、电缆300米 — 重载+精密，河谷台地，易受气流干扰",
        "items": [
            {"name": "抽水泵", "unit_weight": 25, "qty": 2},
            {"name": "电缆(百米)", "unit_weight": 50, "qty": 3},
        ],
    },
}


def get_categories():
    """返回所有物资类别（含默认物品列表）"""
    return MATERIAL_CATEGORIES


def get_category_by_id(cat_id: str):
    for c in MATERIAL_CATEGORIES:
        if c["id"] == cat_id:
            return c
    return None


def compute_demand_info(category_ids: list, custom_items: list = None) -> dict:
    """根据物资类别或自定义物品列表计算需求点汇总信息"""
    specials = []
    risks = []
    supply_types = []
    priority = 5

    for cid in category_ids:
        cat = get_category_by_id(cid)
        if not cat:
            continue
        if cat["priority"] < priority:
            priority = cat["priority"]
        specials.append(cat["special"])
        risks.append(cat["risk"])
        supply_types.append(cat["name"])

    # 如果有自定义物品列表，用它来计算重量和物品明细
    if custom_items is not None:
        items_list = custom_items
    else:
        # 用类别默认物品
        items_list = []
        for cid in category_ids:
            cat = get_category_by_id(cid)
            if cat:
                for item in cat["items"]:
                    items_list.append({
                        "category": cat["name"],
                        "name": item["name"],
                        "unit_weight": item["unit_weight"],
                        "qty": item["qty"],
                        "subtotal": item["unit_weight"] * item["qty"],
                    })

    total_weight = sum(
        item.get("subtotal", item.get("unit_weight", 0) * item.get("qty", 0))
        for item in items_list
    )

    unique_specials = list(dict.fromkeys(specials))
    unique_risks = list(dict.fromkeys(risks))

    return {
        "total_weight": total_weight,
        "priority": priority,
        "special_requirements": "；".join(unique_specials),
        "risk_warnings": unique_risks,
        "supply_types": supply_types,
        "items": items_list,
    }


def get_case_village(village_name: str) -> dict:
    """获取案例中某个村庄的真实物资数据"""
    if village_name not in CASE_VILLAGE_MATERIALS:
        return None
    v = CASE_VILLAGE_MATERIALS[village_name]
    items_with_subtotal = []
    for item in v["items"]:
        items_with_subtotal.append({
            **item,
            "subtotal": item["unit_weight"] * item["qty"],
        })
    info = compute_demand_info(v["category_ids"], items_with_subtotal)
    # 优先使用案例中定义的优先级
    if "priority" in v:
        info["priority"] = v["priority"]
    return {
        "village": village_name,
        "category_ids": v["category_ids"],
        "note": v["note"],
        "weight": v["weight"],
        **info,
    }


def get_default_case_materials():
    """返回案例全部村庄的物资分配"""
    result = {}
    for name in CASE_VILLAGE_MATERIALS:
        result[name] = get_case_village(name)
    return result
