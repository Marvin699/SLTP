"""方案诊断服务 - 提供规则评估和AI评估能力"""
import json
import math
from collections import Counter
from typing import Dict, Any, Optional
from pathlib import Path
from app.services.llm_service import chat, load_agent_prompt, is_configured


def get_range_by_weight(weight: float, uav: dict) -> float:
    """根据载重计算最大航程(km) - 分段线性插值(与蚁群算法保持一致)"""
    points = uav.get('range_points', [])
    max_payload = uav.get('max_payload', 0)
    max_range = uav.get('range_km', uav.get('max_range', 20))
    
    if not points:
        if max_payload <= 0:
            return max_range
        if weight <= 0:
            return max_range
        if weight >= max_payload:
            return max_range * 0.3
        return max_range * (1 - 0.7 * weight / max_payload)
    
    if weight <= 0:
        return points[0][1]
    if weight >= max_payload:
        return points[-1][1]
    
    for i in range(len(points) - 1):
        w1, r1 = points[i]
        w2, r2 = points[i + 1]
        if w1 <= weight <= w2:
            t = (weight - w1) / (w2 - w1) if w2 != w1 else 0
            return r1 + (r2 - r1) * t
    return points[-1][1]


def _extract_uav_specs_from_trips(trips: list, task_uavs: list) -> dict:
    """
    从航次数据和任务配置中提取无人机规格映射
    
    策略：
    1. 首先尝试精确匹配 drone_id
    2. 如果找不到，尝试按 drone_name/drone_type 匹配
    3. 如果还找不到，从航次数据中推断规格（按drone_name分组）
    """
    uav_spec = {}
    
    # 先建立任务配置中的映射
    task_uav_map = {}
    for u in task_uavs:
        task_uav_map[u.get('id', '')] = u
    
    # 收集所有唯一的无人机类型（按drone_name分组，而不是drone_id）
    # drone_id可能包含序号如"fy-ark80-1", "fy-ark80-2"，但它们属于同一种无人机
    drone_types = {}
    for trip in trips:
        drone_id = trip.get('drone_id', '')
        drone_name = trip.get('drone_name', '') or trip.get('drone_type', '')

        # 使用drone_name作为类型标识（如果没有则从drone_id推断）
        # drone_id格式: "fy-ark80-1" → 类型 "fy-ark80"
        if drone_name:
            type_key = drone_name
        elif '-' in drone_id:
            # 去掉最后的数字后缀，保留型号部分
            parts = drone_id.rsplit('-', 1)
            type_key = parts[0] if len(parts) > 1 and parts[-1].isdigit() else drone_id
        else:
            type_key = drone_id
        
        if type_key:
            if type_key not in drone_types:
                drone_types[type_key] = {'name': drone_name, 'ids': set(), 'max_load': 0}
            drone_types[type_key]['ids'].add(drone_id)
            # 记录该类型无人机的最大载重
            load = trip.get('load', 0)
            if load > drone_types[type_key]['max_load']:
                drone_types[type_key]['max_load'] = load
    
    # 为每种无人机类型匹配规格
    for type_key, info in drone_types.items():
        matched_uav = None
        
        # 1. 尝试按名称匹配任务配置中的无人机
        for task_id, task_uav in task_uav_map.items():
            task_name = task_uav.get('name', '')
            # 精确匹配: type_key 完全匹配 task_id 或 task_name
            if type_key == task_id or type_key == task_name:
                matched_uav = task_uav
                break
            # 前缀匹配: task_id 是 type_key 的前缀（如 "fy-ark80" 匹配 "fy-ark80-1"）
            if type_key.startswith(task_id + '-') or task_id.startswith(type_key + '-'):
                matched_uav = task_uav
                break
            # 名称包含匹配
            if info['name'] and (info['name'] in task_name or task_name in info['name']):
                matched_uav = task_uav
                break
        
        # 2. 如果没有匹配到，从航次数据推断规格
        if not matched_uav:
            max_load = info['max_load']
            
            # 计算该类型无人机的最大实际飞行距离
            max_actual_distance = 0
            for trip in trips:
                trip_drone_name = trip.get('drone_name', '') or trip.get('drone_type', '')
                trip_type_key = trip_drone_name if trip_drone_name else trip.get('drone_id', '').split('-')[0] if '-' in trip.get('drone_id', '') else trip.get('drone_id', '')
                if trip_type_key == type_key:
                    dist = trip.get('total_distance', 0)
                    if dist > max_actual_distance:
                        max_actual_distance = dist
            
            # 根据载重和实际飞行距离推断无人机类型
            if max_load > 100:
                # 大载重无人机（如JDX-500）
                inferred_payload = 120
                inferred_range = 1800
            elif max_load > 50:
                # 中等载重无人机（如ARK80）
                inferred_payload = 80
                inferred_range = 20
            else:
                # 小载重无人机 - 根据实际飞行距离判断类型
                if max_actual_distance > 20:
                    # 可能是长航程小型无人机
                    inferred_payload = 65
                    inferred_range = max(max_actual_distance * 1.5, 30)
                else:
                    # 短航程小型无人机（如FlyCart 100）
                    inferred_payload = 65
                    inferred_range = 12
            
            # 确保推断的载重能力至少比实际载重大15%，避免误判超载或接近上限
            if max_load > inferred_payload * 0.85:
                inferred_payload = max(max_load * 1.15, inferred_payload)
            
            # 确保航程至少比实际飞行距离大20%
            if max_actual_distance > inferred_range * 0.8:
                inferred_range = max_actual_distance * 1.5
            
            # 构建航程点：空载时满航程，满载时航程减半
            range_points = [
                [0, inferred_range],
                [inferred_payload * 0.5, inferred_range * 0.75],
                [inferred_payload, inferred_range * 0.5]
            ]
            
            matched_uav = {
                'id': type_key,
                'name': info['name'] or type_key,
                'max_payload': inferred_payload,
                'range_km': inferred_range,
                'max_range': inferred_range,
                'range_points': range_points,
                'battery_capacity': 100,
                'max_speed': 60,
            }
        
        # 为该类型的所有drone_id添加映射
        for drone_id in info['ids']:
            uav_spec[drone_id] = matched_uav

    # 补充 range_points：如果 task UAV 没有 range_points，尝试从数据库加载
    enriched = set()
    for drone_id, uav in uav_spec.items():
        if not uav.get('range_points') and drone_id not in enriched:
            type_key = uav.get('id', '')
            # 从 type_key 推断 model_id（如 "fy-ark80" 从 "fy-ark80-1"）
            model_id = type_key
            if '-' in type_key:
                parts = type_key.rsplit('-', 1)
                if len(parts) > 1 and parts[-1].isdigit():
                    model_id = parts[0]
            try:
                from app.core.database import SessionLocal
                from app.models.uav_param import UavParam
                db = SessionLocal()
                db_uav = db.query(UavParam).filter(UavParam.model_id == model_id).first()
                if db_uav and db_uav.range_points:
                    import json as _json
                    rp = _json.loads(db_uav.range_points)
                    uav['range_points'] = rp
                    enriched.add(drone_id)
                db.close()
            except Exception:
                pass

    return uav_spec


def diagnose_solution(task: dict, solution: dict, mode: str = "both") -> Dict[str, Any]:
    """
    执行方案诊断
    
    参数:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
        mode: 诊断模式（"rule" - 仅规则诊断, "ai" - 仅AI诊断, "both" - 两者都执行）
    
    返回:
        {
            "feasible": bool,
            "rule_report": {...},    # 规则评估报告
            "ai_report": str,        # AI评估报告（Markdown）
            "issues": [],            # 问题列表
            "warnings": [],          # 警告列表
            "suggestions": [],       # 建议列表
            "score": float,          # 综合评分
            "four_dimensional_scores": {
                "safety": 0-100,
                "timeliness": 0-100,
                "economy": 0-100,
                "feasibility": 0-100
            },
            "diagnosis_mode": str    # 诊断模式
        }
    """
    result = {}
    
    # 1. 规则评估
    if mode in ["rule", "both"]:
        rule_report = _rule_based_diagnosis(task, solution)
        result["rule_report"] = rule_report
        result["issues"] = rule_report.get("issues", [])
        result["warnings"] = rule_report.get("warnings", [])
        result["suggestions"] = rule_report.get("suggestions", [])
        four_d_scores = rule_report.get("four_dimensional_scores", {
            "safety": 70,
            "timeliness": 70,
            "economy": 70,
            "feasibility": 70
        })
        result["four_dimensional_scores"] = four_d_scores
        result["score"] = round(
            0.35 * four_d_scores.get("safety", 70) +
            0.35 * four_d_scores.get("timeliness", 70) +
            0.15 * four_d_scores.get("economy", 70) +
            0.15 * four_d_scores.get("feasibility", 70),
            1
        )
        # 基于评分和致命问题判定可行性（而非仅看 issues 列表长度）
        critical_issues = [i for i in result["issues"] if "❌" in str(i)]
        result["feasible"] = len(critical_issues) == 0 and result["score"] >= 60
    else:
        result["rule_report"] = None
        result["issues"] = []
        result["warnings"] = []
        result["suggestions"] = []
        result["feasible"] = True
        # AI诊断模式下，使用可行性检查结果作为默认评分
        result["four_dimensional_scores"] = {
            "safety": _calculate_ai_default_score(solution, "safety"),
            "timeliness": _calculate_ai_default_score(solution, "timeliness"),
            "economy": _calculate_ai_default_score(solution, "economy"),
            "feasibility": _calculate_ai_default_score(solution, "feasibility")
        }
        four_d = result["four_dimensional_scores"]
        result["score"] = round(
            0.35 * four_d["safety"] +
            0.35 * four_d["timeliness"] +
            0.15 * four_d["economy"] +
            0.15 * four_d["feasibility"],
            1
        )
    
    # 2. AI评估
    if mode in ["ai", "both"]:
        ai_report = _ai_based_diagnosis(task, solution)
        result["ai_report"] = ai_report
    else:
        result["ai_report"] = None
    
    # 任务摘要
    result["task_summary"] = {
        "demand_points_count": len(task.get("demand_points", [])),
        "uavs_count": len(task.get("uavs", [])),
        "total_trips": solution.get("summary", {}).get("total_trips", 0),
        "total_distance": solution.get("summary", {}).get("total_distance", 0),
    }
    
    result["diagnosis_mode"] = mode
    return result


def run_rule_diagnosis(task: dict, solution: dict) -> Dict[str, Any]:
    """
    仅执行规则诊断（不调用AI）
    
    参数:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
    
    返回:
        规则诊断结果
    """
    return diagnose_solution(task, solution, mode="rule")


def run_ai_diagnosis(task: dict, solution: dict) -> Dict[str, Any]:
    """
    仅执行AI诊断（基于任务配置信息.md）
    
    参数:
        task: 任务配置（depot, demand_points, uavs）
        solution: 方案数据（routes, trips, summary, feasibility）
    
    返回:
        AI诊断结果
    """
    return diagnose_solution(task, solution, mode="ai")


def _rule_based_diagnosis(task: dict, solution: dict) -> Dict[str, Any]:
    """
    基于规则引擎的诊断 - 四维评分体系

    四大诊断维度（对应教学常见问题）:
      1. 安全性(35%): 超载、航程超标、机型与任务不匹配
      2. 时效性(35%): 优先级错位、高优先级遗漏、无人机利用率
      3. 经济性(15%): 航线冗余、负载不均衡
      4. 可行性(15%): 需求覆盖、点位遗漏/重复配送

    feasible 判定: 仅当存在安全性致命问题（超载/航程超标）时才为 False
    """
    issues = []      # 致命问题（❌）— 仅安全性硬约束
    warnings = []    # 警告（⚠️）— 需要关注但不致命
    suggestions = [] # 建议（💡）— 优化方向（含教学反馈）
    _suggestion_set = set()  # 用于去重建议（按内容前50字符去重）

    def _add_suggestion(msg):
        """添加建议（自动去重，同类型建议只保留一条）"""
        key = msg[:50]
        if key not in _suggestion_set:
            _suggestion_set.add(key)
            suggestions.append(msg)

    uavs = task.get("uavs", [])
    demand_points = task.get("demand_points", [])
    trips = solution.get("solution", {}).get("trips", [])
    feasibility = solution.get("feasibility", {})

    uav_spec = _extract_uav_specs_from_trips(trips, uavs)
    drone_trips = {}

    # ═══════════════════════════════════════════
    # 一、安全性评分 (35%权重)
    # 检查: 超载、航程超标、机型与任务不匹配
    # ═══════════════════════════════════════════
    safety_score = 100
    safety_details = {"issues": 0, "warnings": 0, "strengths": [], "issue_items": [], "warning_items": []}

    if not trips:
        safety_score = 70
        safety_details["strengths"].append("航次数据未提供，使用可行性检查结果")
        if feasibility.get("issues"):
            for fi in feasibility["issues"]:
                if "超载" in fi:
                    msg = f"❌ {fi}"
                    issues.append(msg)
                    safety_details["issues"] += 1
                    safety_details["issue_items"].append(msg)
                    safety_score -= 20
                elif "航程" in fi:
                    msg = f"⚠️ {fi}"
                    warnings.append(msg)
                    safety_details["warnings"] += 1
                    safety_details["warning_items"].append(msg)
                    safety_score -= 10
    else:
        # 按机型分组统计
        type_loads = {}  # {type_key: [load_ratio, ...]}

        # 按无人机去重，避免每趟重复报告相同问题
        reported_overload = set()      # 已报告超载的 drone_id
        reported_range = set()         # 已报告航程超标的 drone_id
        reported_load_warn = set()     # 已报告载重接近上限的 drone_id
        reported_range_warn = set()    # 已报告航程余量不足的 drone_id

        for trip in trips:
            drone_id = trip.get("drone_id")
            uav = uav_spec.get(drone_id)
            if not uav:
                continue

            load = trip.get("load", 0)
            total_distance = trip.get("total_distance", 0)
            max_payload = uav.get("max_payload", 0)
            uav_name = uav.get("name", drone_id)

            # --- 规则3: 机型与任务不匹配 ---
            type_key = uav_name
            if type_key not in type_loads:
                type_loads[type_key] = {"loads": [], "distances": [], "max_payload": max_payload}
            if max_payload > 0:
                type_loads[type_key]["loads"].append(load / max_payload)
            type_loads[type_key]["distances"].append(total_distance)

            # --- 载重安全（每架无人机只报告最严重的一次） ---
            if max_payload > 0:
                load_ratio = load / max_payload
                if load_ratio > 1.0 and drone_id not in reported_overload:
                    reported_overload.add(drone_id)
                    safety_score -= 15
                    safety_details["issues"] += 1
                    msg = f"❌ {uav_name}({drone_id}): 严重超载 {load:.1f}kg > {max_payload}kg，存在飞行安全隐患"
                    issues.append(msg)
                    safety_details["issue_items"].append(msg)
                    _add_suggestion(f"💡 【超载纠正】{uav_name} 的最大载重为 {max_payload}kg，当前装载 {load:.1f}kg 已超出极限。超载会导致无人机无法正常爬升、续航骤降甚至坠机。请减少单次配送量或将物资拆分到多架无人机，确保每架载重不超过额定值。")
                elif load_ratio > 0.9 and drone_id not in reported_load_warn and drone_id not in reported_overload:
                    reported_load_warn.add(drone_id)
                    safety_score -= 5
                    safety_details["warnings"] += 1
                    msg = f"⚠️ {uav_name}({drone_id}): 载重接近上限 ({load_ratio*100:.0f}%)，安全余量不足"
                    warnings.append(msg)
                    safety_details["warning_items"].append(msg)
                    _add_suggestion(f"💡 【载重优化】{uav_name} 当前载重率 {load_ratio*100:.0f}%，安全余量极小。山区飞行需要预留突发阵风、绕障机动的载重裕度。建议减少单次配送量或更换更大载重机型，保持载重率在 80% 以内。")

            # --- 航程安全（每架无人机只报告最严重的一次） ---
            effective_range = get_range_by_weight(load, uav)
            if effective_range > 0:
                margin = (effective_range - total_distance) / effective_range * 100
                if total_distance > effective_range and drone_id not in reported_range:
                    reported_range.add(drone_id)
                    safety_score -= 15
                    safety_details["issues"] += 1
                    msg = f"❌ {uav_name}({drone_id}): 航程超标 {total_distance:.1f}km > {effective_range:.1f}km，无法安返"
                    issues.append(msg)
                    safety_details["issue_items"].append(msg)
                    _add_suggestion(f"💡 【航程纠正】{uav_name} 在当前载重下有效航程仅 {effective_range:.1f}km，但规划航路总长 {total_distance:.1f}km，无人机将无法返回出发点。请拆分配送任务、减少单次飞行距离，或更换续航更长的机型。山区远距离救灾场景必须预留至少 20% 的返航电量。")
                elif margin < 20 and drone_id not in reported_range_warn and drone_id not in reported_range:
                    reported_range_warn.add(drone_id)
                    safety_score -= 5
                    safety_details["warnings"] += 1
                    msg = f"⚠️ {uav_name}({drone_id}): 航程余量仅 {margin:.0f}%，续航紧张"
                    warnings.append(msg)
                    safety_details["warning_items"].append(msg)

        # --- 规则3汇总: 机型与任务不匹配 ---
        for type_key, info in type_loads.items():
            avg_load_ratio = sum(info["loads"]) / len(info["loads"]) if info["loads"] else 0
            max_distance = max(info["distances"]) if info["distances"] else 0
            max_payload = info["max_payload"]

            # 大载重机型飞短途（载重利用率<30%且距离短）
            if avg_load_ratio < 0.3 and max_distance < 10 and max_payload > 50:
                safety_score -= 8
                safety_details["warnings"] += 1
                msg = f"⚠️ {type_key}: 大载重机型({max_payload}kg)仅飞短途({max_distance:.1f}km)，平均载重利用率{avg_load_ratio*100:.0f}%，设备资源浪费"
                warnings.append(msg)
                safety_details["warning_items"].append(msg)
                _add_suggestion(f"💡 【机型匹配】{type_key} 是大载重机型（{max_payload}kg），却只飞 {max_distance:.1f}km 的短途，载重利用率仅 {avg_load_ratio*100:.0f}%，这是典型的「大材小用」。大载重机型续航长、运力强，应分配给远距离、大物资量的任务；短途轻量任务应使用小型无人机，既节省成本又提高灵活性。")

            # 小载重机型承载过重
            if avg_load_ratio > 0.85 and max_payload < 50:
                safety_score -= 10
                safety_details["warnings"] += 1
                msg = f"⚠️ {type_key}: 小载重机型({max_payload}kg)长期高负荷运行，平均载重率{avg_load_ratio*100:.0f}%"
                warnings.append(msg)
                safety_details["warning_items"].append(msg)
                _add_suggestion(f"💡 【机型匹配】{type_key} 是小载重机型（{max_payload}kg），长期处于高负荷状态（平均载重率 {avg_load_ratio*100:.0f}%），存在载重超限和飞行安全隐患。部分小组统一选用同款无人机，导致小机型承载过量物资。请根据各需求点的物资重量合理分配机型，将重载任务交给大载重机型。")

    safety_score = max(0, min(100, safety_score))

    # ═══════════════════════════════════════════
    # 二、时效性评分 (35%权重)
    # 检查: 优先级错位、高优先级遗漏、利用率不均
    # ═══════════════════════════════════════════
    timeliness_score = 100
    timeliness_details = {"issues": 0, "warnings": 0, "strengths": [], "issue_items": [], "warning_items": []}

    if not trips:
        timeliness_score = 70
        timeliness_details["strengths"].append("航次数据未提供，使用可行性检查结果")
    else:
        # 统计每架无人机的趟次
        for trip in trips:
            drone_id = trip.get("drone_id")
            drone_trips[drone_id] = drone_trips.get(drone_id, 0) + 1

        # --- 规则1: 应急优先级错位 ---
        high_priority = [dp for dp in demand_points if dp.get("priority") in ["urgent", "high", 1, 2]]
        low_priority = [dp for dp in demand_points if dp.get("priority") in ["low", "normal", 4, 5]]

        if high_priority and trips:
            # 检查高优先级是否在早期航次中被服务
            trip_order = []  # (village_name, trip_index)
            for idx, trip in enumerate(trips):
                # 优先从 villages 列表提取（多村庄趟次）
                vlist = trip.get("villages", [])
                if vlist:
                    for v in vlist:
                        vn = v.get("name", "")
                        if vn:
                            trip_order.append((vn, idx))
                else:
                    vn = trip.get("village_name", "")
                    if vn:
                        trip_order.append((vn, idx))

            high_priority_names = {dp.get("name") for dp in high_priority}
            low_priority_names = {dp.get("name") for dp in low_priority}

            high_served = [t for t in trip_order if t[0] in high_priority_names]
            low_served = [t for t in trip_order if t[0] in low_priority_names]

            if high_served and low_served:
                avg_high_idx = sum(t[1] for t in high_served) / len(high_served)
                avg_low_idx = sum(t[1] for t in low_served) / len(low_served)
                if avg_high_idx > avg_low_idx:
                    timeliness_score -= 15
                    timeliness_details["warnings"] += 1
                    msg = f"⚠️ 应急优先级错位: 高优先级需求点平均在第{avg_high_idx+1:.0f}趟才配送，低优先级反而更早（第{avg_low_idx+1:.0f}趟），违背\"先急后缓\"原则"
                    warnings.append(msg)
                    timeliness_details["warning_items"].append(msg)
                    _add_suggestion("💡 【优先级纠正】当前方案中，高优先级需求点反而在后期才被配送，低优先级需求点却更早获得物资。这违背了应急救灾「先急后缓」的核心原则——部分小组单纯按村庄坐标顺序规划航线，没有区分急救药品和生活物资的配送优先级。正确做法：先将急救药品、急需物资送到高优先级村庄，再配送生活物资到低优先级村庄。")

            # 高优先级未配送
            covered = {t[0] for t in trip_order}
            uncovered_high = high_priority_names - covered
            if uncovered_high:
                timeliness_score -= 20
                timeliness_details["issues"] += 1
                names = "、".join(uncovered_high)
                msg = f"⚠️ 高优先级需求点未配送: {names}，急需救援的村落配送滞后"
                warnings.append(msg)
                timeliness_details["warning_items"].append(msg)
                _add_suggestion(f"💡 【遗漏纠正】高优先级需求点 {names} 未被任何无人机配送，这些是急需救援的村落。请检查路径规划是否遗漏了这些点位，确保所有高优先级需求点都在第一批配送任务中。")

        # --- 无人机利用率 ---
        if drone_trips:
            avg_trips = sum(drone_trips.values()) / len(drone_trips)
            for drone_id, trip_count in drone_trips.items():
                uav = uav_spec.get(drone_id)
                uav_name = uav.get("name", drone_id) if uav else drone_id
                if trip_count > avg_trips * 1.5:
                    timeliness_score -= 8
                    timeliness_details["warnings"] += 1
                    msg = f"⚠️ {uav_name}: 任务过重（{trip_count}趟，平均{avg_trips:.1f}趟），调度不均衡"
                    warnings.append(msg)
                    timeliness_details["warning_items"].append(msg)
                    _add_suggestion(f"💡 【调度优化】{uav_name} 承担了 {trip_count} 趟配送（平均 {avg_trips:.1f} 趟），任务过重。部分小组单架无人机多点无序配送，导致单机负荷过大、其他无人机闲置。建议将任务拆分给多架无人机并行配送，既能缩短总配送时间，又能降低单机过载风险。")

        # 未使用的无人机
        assigned_drones = set(drone_trips.keys())
        all_drones = set(u["id"] for u in uavs)
        unused = all_drones - assigned_drones
        if unused and len(uavs) > 1:
            for uid in unused:
                uav = uav_spec.get(uid)
                msg = f"⚠️ 闲置无人机: {uav.get('name', uid) if uav else uid}，未参与任何配送"
                warnings.append(msg)
                timeliness_details["warning_items"].append(msg)
            timeliness_score -= 3 * len(unused)
            _add_suggestion("💡 【资源利用】存在闲置无人机未参与配送。多机协同是本课程的核心能力——8个村庄分散布局，应合理分配多架无人机各负责一片区域，而不是让单架无人机包揽所有任务。闲置无人机可分担高负荷无人机的任务，缩短总配送时间。")

    timeliness_score = max(0, min(100, timeliness_score))

    # ═══════════════════════════════════════════
    # 三、经济性评分 (15%权重)
    # 检查: 航线冗余、负载不均衡
    # ═══════════════════════════════════════════
    economy_score = 100
    economy_details = {"issues": 0, "warnings": 0, "strengths": [], "issue_items": [], "warning_items": []}

    if trips:
        # --- 规则2: 航线规划冗余 ---
        total_distance = sum(t.get("total_distance", 0) for t in trips)
        total_load = sum(t.get("load", 0) for t in trips)

        # 计算理论最短距离
        depot = task.get("depot", {})
        depot_lat = depot.get("latitude", 0)
        depot_lon = depot.get("longitude", 0)

        if depot_lat and depot_lon and demand_points:
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                return R * 2 * math.asin(math.sqrt(a))

            # 理论最优: 基于各村庄到 depot 的往返距离计算合理下界
            # 构建村庄名→坐标的映射
            village_coords = {}
            for dp in demand_points:
                vname = dp.get("name", "")
                if vname:
                    village_coords[vname] = (dp.get("latitude", 0), dp.get("longitude", 0))

            # 计算每趟的理论最短距离
            theoretical_total = 0
            for trip in trips:
                trip_villages = trip.get("villages", [])
                if trip_villages:
                    # 多村庄趟次：按最近邻计算理论路径
                    nodes = [(depot_lat, depot_lon)]
                    for v in trip_villages:
                        vlat = v.get("latitude", v.get("lat", 0))
                        vlon = v.get("longitude", v.get("lon", 0))
                        if vlat and vlon:
                            nodes.append((vlat, vlon))
                    if len(nodes) > 1:
                        nn_dist = 0
                        visited = [True] + [False] * (len(nodes) - 1)
                        current = 0
                        for _ in range(len(nodes) - 1):
                            best_dist = float('inf')
                            best_idx = -1
                            for j in range(len(nodes)):
                                if not visited[j]:
                                    d = haversine(nodes[current][0], nodes[current][1], nodes[j][0], nodes[j][1])
                                    if d < best_dist:
                                        best_dist = d
                                        best_idx = j
                            if best_idx >= 0:
                                nn_dist += best_dist
                                visited[best_idx] = True
                                current = best_idx
                        nn_dist += haversine(nodes[current][0], nodes[current][1], nodes[0][0], nodes[0][1])
                        theoretical_total += nn_dist
                else:
                    # 单村庄趟次：理论最短 = 往返距离
                    vname = trip.get("village_name", "")
                    if vname and vname in village_coords:
                        vlat, vlon = village_coords[vname]
                        round_trip = haversine(depot_lat, depot_lon, vlat, vlon) * 2
                        theoretical_total += round_trip

            # 如果无法计算理论值，用所有需求点的往返距离之和
            if theoretical_total <= 0:
                theoretical_total = sum(
                    haversine(depot_lat, depot_lon, dp.get("latitude", 0), dp.get("longitude", 0)) * 2
                    for dp in demand_points
                )

            if theoretical_total > 0 and total_distance > 0:
                efficiency_ratio = total_distance / theoretical_total
                if efficiency_ratio > 1.5:
                    economy_score -= 15
                    economy_details["warnings"] += 1
                    msg = f"⚠️ 航线规划冗余: 实际总距离 {total_distance:.1f}km 是理论最优 {theoretical_total:.1f}km 的 {efficiency_ratio:.1f} 倍，存在大量无效航程"
                    warnings.append(msg)
                    economy_details["warning_items"].append(msg)
                    _add_suggestion(f"💡 【航线优化】实际飞行距离是理论最优的 {efficiency_ratio:.1f} 倍，说明航线存在严重冗余。多数初始方案存在航线交叉、往返绕路、无效航程过长的问题——直接消耗无人机续航，导致单架无人机配送点位少、整体运输效率低。请检查：①是否有航线交叉（两段路线在地图上交叉）；②是否有不必要的返回配送中心再出发；③路径顺序是否按就近原则排列。建议使用最近邻算法或聚类分区后逐区配送。")
                elif efficiency_ratio > 1.2:
                    economy_score -= 8
                    economy_details["warnings"] += 1
                    msg = f"⚠️ 航线效率偏低: 实际距离/理论最优 = {efficiency_ratio:.1f}，仍有优化空间"
                    warnings.append(msg)
                    economy_details["warning_items"].append(msg)
                    _add_suggestion(f"💡 【航线优化】航线效率比为 {efficiency_ratio:.1f}，虽未严重冗余但仍有优化空间。建议检查路径顺序是否合理——相邻需求点应连续访问，避免折返跑。可以尝试按地理方位将需求点分组，每组内按最近邻顺序串联。")

                economy_details["strengths"].append(f"总配送距离: {total_distance:.1f}km")

        # 能效比
        if total_load > 0:
            energy_per_kg = total_distance / total_load
            economy_details["strengths"].append(f"能效比: {energy_per_kg:.2f} km/kg")

        # --- 负载均衡 ---
        if drone_trips and len(drone_trips) > 1:
            trips_values = list(drone_trips.values())
            max_trips = max(trips_values)
            min_trips = min(trips_values)
            balance_ratio = max_trips / max(min_trips, 1)
            if balance_ratio > 2.0:
                economy_score -= 10
                economy_details["warnings"] += 1
                msg = f"⚠️ 负载不均衡: 最忙无人机 {max_trips} 趟 vs 最闲 {min_trips} 趟（{balance_ratio:.1f}倍差距）"
                warnings.append(msg)
                economy_details["warning_items"].append(msg)
                _add_suggestion("💡 重新分配任务使各无人机工作量均衡，避免单机过载")
    else:
        economy_score = 70
        economy_details["strengths"].append("航次数据未提供")

    economy_score = max(0, min(100, economy_score))

    # ═══════════════════════════════════════════
    # 四、可行性评分 (15%权重)
    # 检查: 需求覆盖、点位遗漏/重复
    # ═══════════════════════════════════════════
    feasibility_score = 100
    feasibility_details = {"issues": 0, "warnings": 0, "strengths": [], "issue_items": [], "warning_items": []}

    # --- 规则4: 点位遗漏/重复配送 ---
    if trips and demand_points:
        served_villages = []
        for t in trips:
            # 优先从 villages 列表提取（多村庄趟次）
            vlist = t.get("villages", [])
            if vlist:
                for v in vlist:
                    vname = v.get("name", "")
                    if vname:
                        served_villages.append(vname)
            else:
                vn = t.get("village_name", "")
                if vn:
                    served_villages.append(vn)
        all_village_names = {dp.get("name") for dp in demand_points}
        served_set = set(served_villages)

        # 遗漏检查
        missed = all_village_names - served_set
        if missed:
            names = "、".join(missed)
            feasibility_score -= 15 * len(missed)
            feasibility_details["issues"] += len(missed)
            msg = f"⚠️ 点位遗漏: {names} 未被任何无人机配送，需求点覆盖不完整"
            warnings.append(msg)
            feasibility_details["warning_items"].append(msg)
            _add_suggestion("💡 检查是否有村庄被遗漏，确保所有需求点都被服务")

        # 重复配送检查
        village_counts = Counter(served_villages)
        duplicated = {v: c for v, c in village_counts.items() if c > 1 and v}
        if duplicated:
            for v, c in duplicated.items():
                feasibility_score -= 5
                feasibility_details["warnings"] += 1
                msg = f"⚠️ 重复配送: {v} 被配送了 {c} 次，存在资源浪费"
                warnings.append(msg)
                feasibility_details["warning_items"].append(msg)
            _add_suggestion("💡 检查是否存在点位重复配送，合并同一点位的配送任务")

        if not missed and not duplicated:
            feasibility_details["strengths"].append("所有需求点均已覆盖，无遗漏无重复")

    # --- 需求覆盖检查（从优化器可行性结果） ---
    demand_coverage = feasibility.get("demand_coverage", {})
    for village_name, coverage in demand_coverage.items():
        shortfall = coverage.get("shortfall", 0)
        if shortfall > 0.01:
            # 按严重程度分类: 差距大=警告，差距小=提示
            if shortfall > 5:
                feasibility_score -= 10
                feasibility_details["warnings"] += 1
                msg = f"⚠️ {village_name}: 配送缺口较大 {shortfall:.1f}kg，物资未完全送达"
                warnings.append(msg)
                feasibility_details["warning_items"].append(msg)
            else:
                feasibility_score -= 3
                feasibility_details["warnings"] += 1
                msg = f"ℹ️ {village_name}: 配送缺口 {shortfall:.1f}kg（轻微）"
                warnings.append(msg)
                feasibility_details["warning_items"].append(msg)

    if not demand_coverage:
        feasibility_details["strengths"].append("需求覆盖数据未提供")

    feasibility_score = max(0, min(100, feasibility_score))

    # ═══════════════════════════════════════════
    # 综合评分 & 可行性判定
    # ═══════════════════════════════════════════
    weighted_score = round(
        0.35 * safety_score +
        0.35 * timeliness_score +
        0.15 * economy_score +
        0.15 * feasibility_score,
        1
    )

    # 可行性: 仅当存在安全性致命问题（❌标记）时才判定不可行
    # 需求覆盖不足、优先级错位等降分但不影响可行性
    safety_critical = [i for i in issues if "❌" in i]
    feasible = len(safety_critical) == 0

    return {
        "feasible": feasible,
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "four_dimensional_scores": {
            "safety": safety_score,
            "timeliness": timeliness_score,
            "economy": economy_score,
            "feasibility": feasibility_score
        },
        "details": {
            "safety": safety_details,
            "timeliness": timeliness_details,
            "economy": economy_details,
            "feasibility": feasibility_details
        },
        "drone_trips": drone_trips,
        "demand_coverage": demand_coverage,
    }


def _ai_based_diagnosis(task: dict, solution: dict) -> Optional[str]:
    """
    基于大模型的AI诊断 - 读取任务配置信息.md文件
    
    返回: AI生成的Markdown格式诊断报告
    """
    try:
        # 读取任务配置信息文件
        task_config_path = Path(__file__).parent.parent.parent / "LLM" / "任务配置信息.md"
        task_config_content = ""
        if task_config_path.exists():
            with open(task_config_path, "r", encoding="utf-8") as f:
                task_config_content = f.read()
        
        system_prompt = load_agent_prompt("diagnosis.md")
        
        user_prompt = f"""## 任务配置文件内容
{task_config_content}

## 任务配置
{json.dumps(task, ensure_ascii=False, indent=2)}

## 方案数据
{json.dumps(solution, ensure_ascii=False, indent=2)}

请对上述方案进行全面诊断，输出标准的诊断报告。
"""
        
        response = chat(system_prompt, user_prompt, temperature=0.3)
        return response
    except Exception as e:
        print(f"[Diagnosis] AI诊断失败: {e}")
        return None


def _calculate_ai_default_score(solution: dict, dimension: str) -> int:
    """
    AI诊断模式下，根据可行性检查结果计算默认四维评分
    
    参数:
        solution: 方案数据
        dimension: 维度名称 ("safety", "timeliness", "economy", "feasibility")
    
    返回:
        默认评分 (0-100)
    """
    feasibility = solution.get("feasibility", {})
    issues = feasibility.get("issues", [])
    warnings = feasibility.get("warnings", [])
    
    base_score = 100
    
    if dimension == "safety":
        # 安全性：检查超载和航程问题
        safety_issues = [i for i in issues if "超载" in i or "航程" in i]
        safety_warnings = [w for w in warnings if "载重" in w or "航程" in w]
        base_score -= len(safety_issues) * 20
        base_score -= len(safety_warnings) * 5
        
    elif dimension == "timeliness":
        # 时效性：检查优先级和无人机使用情况
        time_issues = [i for i in issues if "优先" in i or "未配送" in i]
        time_warnings = [w for w in warnings if "任务" in w or "未使用" in w]
        base_score -= len(time_issues) * 20
        base_score -= len(time_warnings) * 5
        
    elif dimension == "economy":
        # 经济性：检查负载均衡
        eco_warnings = [w for w in warnings if "均衡" in w or "距离" in w]
        base_score -= len(eco_warnings) * 10
        
    elif dimension == "feasibility":
        # 可行性：检查需求覆盖
        feasible = feasibility.get("feasible", True)
        if not feasible:
            base_score = 50
        else:
            coverage = feasibility.get("demand_coverage", {})
            for village, info in coverage.items():
                if info.get("shortfall", 0) > 0.01:
                    base_score -= 15
                elif info.get("coverage_pct", 100) < 100:
                    base_score -= 5
    
    return max(0, min(100, base_score))


def _calculate_score(issue_count: int, warning_count: int, suggestion_count: int, feasible: bool) -> float:
    """
    计算综合评分（保留用于兼容性）
    
    评分规则:
        - 基础分：100分
        - 每个严重问题扣20分
        - 每个警告扣5分
        - 每个建议扣2分（表示有改进空间）
        - 不可行方案最低分20分
    """
    score = 100
    score -= issue_count * 20
    score -= warning_count * 5
    score -= suggestion_count * 2
    
    if not feasible:
        score = max(20, score)
    
    return max(0, min(100, score))
