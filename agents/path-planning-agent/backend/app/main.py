import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes.points import router as points_router
from app.api.routes.materials import router as materials_router
from app.api.routes.config import router as config_router
from app.api.routes.uavs import router as uavs_router
from app.api.routes.optimizer import router as optimizer_router
from app.api.routes.diagnosis import router as diagnosis_router
from app.api.routes.workspace import router as workspace_router
from app.api.routes.report import router as report_router
from app.api.routes.llm_config import router as llm_config_router
from app.api.routes.case_study import router as case_study_router
from app.api.routes.course_graph import router as course_graph_router
from app.api.routes.score_session import router as score_session_router
from app.api.routes.ai_chat import router as ai_chat_router

# 确保所有模型在 create_all 之前被导入（注册到 Base.metadata）
from app.models.assignment import MaterialAssignment  # noqa: F401
from app.models.uav_param import UavParam  # noqa: F401
from app.models.ai_result import AiSelectionResult  # noqa: F401
from app.models.diagnosis import DiagnosisRecord  # noqa: F401
from app.models.optimizer import OptimizationRecord  # noqa: F401
from app.models.report import ReportRecord  # noqa: F401
from app.models.llm_config import LLMConfig  # noqa: F401
from app.models.case_study import CaseStudy  # noqa: F401
from app.models.course_graph import CourseProject, TeachingStatus  # noqa: F401
from app.models.score_session import ScoreSession, ScoreRecord  # noqa: F401

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 轻量迁移：为旧数据库添加新列（SQLite ALTER TABLE IF NOT EXISTS 不支持，用 try/except）
def _migrate():
    import sqlalchemy
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE material_assignments ADD COLUMN supply_types TEXT"))
            conn.commit()
        except Exception:
            pass  # 列已存在则忽略
        
        # 为uav_params表添加range_points列
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE uav_params ADD COLUMN range_points TEXT"))
            conn.commit()
        except Exception:
            pass  # 列已存在则忽略
        
        # 为delivery_points表添加delivery_mode列
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE delivery_points ADD COLUMN delivery_mode VARCHAR(20)"))
            conn.commit()
        except Exception:
            pass  # 列已存在则忽略
        
        # 更新现有记录的delivery_mode为大写枚举值
        try:
            conn.execute(sqlalchemy.text("UPDATE delivery_points SET delivery_mode = 'OPTIONAL' WHERE delivery_mode IS NULL OR delivery_mode = ''"))
            conn.commit()
        except Exception:
            pass
        
        try:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE diagnosis_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_config TEXT,
                    solution_data TEXT,
                    report TEXT,
                    score FLOAT,
                    issues_count INTEGER DEFAULT 0,
                    warnings_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception:
            pass  # 表已存在则忽略
        
        # 创建优化记录表（如不存在）
        try:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE optimization_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_config TEXT,
                    solution_data TEXT,
                    aco_params TEXT,
                    summary TEXT,
                    total_distance FLOAT,
                    total_energy FLOAT,
                    total_trips INTEGER,
                    village_count INTEGER,
                    drone_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception:
            pass  # 表已存在则忽略
        
        # 创建报告记录表
        try:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE report_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_config TEXT,
                    solution_data TEXT,
                    diagnosis_data TEXT,
                    report_data TEXT,
                    word_path TEXT,
                    pdf_path TEXT,
                    filename TEXT,
                    scheme_type TEXT DEFAULT '运输方案',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception:
            pass  # 表已存在则忽略
        
        # 创建大模型配置表
        try:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE llm_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    model_id VARCHAR(100) NOT NULL,
                    base_url VARCHAR(500) NOT NULL,
                    api_key VARCHAR(500) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 0,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception:
            pass  # 表已存在则忽略

        # 为 case_studies 表添加 solution_data 列（如果不存在）
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE case_studies ADD COLUMN solution_data TEXT"))
            conn.commit()
        except Exception:
            pass  # 列已存在则忽略

        # 创建教学案例表
        try:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE case_studies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    center_data TEXT NOT NULL,
                    demand_points TEXT NOT NULL,
                    material_data TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception:
            pass  # 表已存在则忽略

        # 重建score_sessions表（去掉旧的session_hour列）
        try:
            # 检查是否有session_hour列
            cols = conn.execute(sqlalchemy.text("PRAGMA table_info(score_sessions)"))
            col_names = [row[1] for row in cols]
            if 'session_hour' in col_names:
                conn.execute(sqlalchemy.text('''
                    CREATE TABLE score_sessions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token VARCHAR(32) NOT NULL UNIQUE,
                        section_id VARCHAR(20) NOT NULL DEFAULT 'section1',
                        title VARCHAR(200) NOT NULL,
                        groups TEXT NOT NULL,
                        dimensions TEXT NOT NULL,
                        start_time DATETIME,
                        end_time DATETIME,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                conn.execute(sqlalchemy.text('''
                    INSERT INTO score_sessions_new (id, token, section_id, title, groups, dimensions, start_time, end_time, is_active, created_at)
                    SELECT id, token, COALESCE(section_id, 'section1'), title, groups, dimensions, start_time, end_time, is_active, created_at FROM score_sessions
                '''))
                conn.execute(sqlalchemy.text('DROP TABLE score_sessions'))
                conn.execute(sqlalchemy.text('ALTER TABLE score_sessions_new RENAME TO score_sessions'))
                conn.commit()
                print("[Migration] score_sessions表已重建（移除session_hour列）")
        except Exception as e:
            pass

        # 重建score_records表（添加scorer_role列，scorer_name改为可选）
        try:
            cols = conn.execute(sqlalchemy.text("PRAGMA table_info(score_records)"))
            col_names = [row[1] for row in cols]
            if 'scorer_role' not in col_names:
                conn.execute(sqlalchemy.text('''
                    CREATE TABLE score_records_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_token VARCHAR(32) NOT NULL,
                        scorer_role VARCHAR(50) NOT NULL,
                        scorer_name VARCHAR(50),
                        group_id VARCHAR(50) NOT NULL,
                        dimension VARCHAR(50) NOT NULL,
                        score FLOAT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                conn.execute(sqlalchemy.text('''
                    INSERT INTO score_records_new (id, session_token, scorer_role, scorer_name, group_id, dimension, score, created_at)
                    SELECT id, session_token, COALESCE(scorer_name, 'unknown'), scorer_name, group_id, dimension, score, created_at FROM score_records
                '''))
                conn.execute(sqlalchemy.text('DROP TABLE score_records'))
                conn.execute(sqlalchemy.text('ALTER TABLE score_records_new RENAME TO score_records'))
                conn.execute(sqlalchemy.text('CREATE INDEX idx_score_records_token ON score_records(session_token)'))
                conn.commit()
                print("[Migration] score_records表已重建（添加scorer_role列）")
        except Exception as e:
            pass

_migrate()

def _init_default_case():
    """初始化默认案例"""
    from app.core.database import SessionLocal
    from app.models.case_study import CaseStudy
    import json

    try:
        db = SessionLocal()
        existing = db.query(CaseStudy).filter(CaseStudy.is_default == True).first()
        if existing:
            db.close()
            return

        default_center = {"name": "渠洋村", "longitude": 106.317264, "latitude": 23.310533}
        default_demands = [
            {"name": "怀渠村", "longitude": 106.285000, "latitude": 23.345000},
            {"name": "塘麻村", "longitude": 106.425000, "latitude": 23.085000},
            {"name": "坡乐村", "longitude": 106.380000, "latitude": 23.075000},
            {"name": "东风村", "longitude": 106.320150, "latitude": 23.309040},
            {"name": "古桥村", "longitude": 106.350000, "latitude": 23.200000},
            {"name": "新和村", "longitude": 106.335000, "latitude": 23.295000},
            {"name": "怀书村", "longitude": 106.278670, "latitude": 23.339030},
            {"name": "雅力村", "longitude": 106.380000, "latitude": 23.250000},
        ]
        default_materials = {
            "怀渠村": {
                "weight": 100,
                "priority": 2,
                "supply_types": ["medicine", "daily"],
                "items": [
                    {"name": "消毒酒精", "unit_weight": 5, "qty": 10},
                    {"name": "感冒药", "unit_weight": 0.5, "qty": 20},
                    {"name": "纱布绷带", "unit_weight": 0.5, "qty": 20}
                ]
            },
            "塘麻村": {
                "weight": 570,
                "priority": 2,
                "supply_types": ["food", "water"],
                "items": [
                    {"name": "方便面", "unit_weight": 0.1, "qty": 500},
                    {"name": "矿泉水", "unit_weight": 0.5, "qty": 100},
                    {"name": "压缩饼干", "unit_weight": 0.2, "qty": 100}
                ]
            },
            "坡乐村": {
                "weight": 140,
                "priority": 3,
                "supply_types": ["daily"],
                "items": [
                    {"name": "毛毯", "unit_weight": 2, "qty": 30},
                    {"name": "毛巾", "unit_weight": 0.2, "qty": 50},
                    {"name": "牙刷套装", "unit_weight": 0.2, "qty": 50}
                ]
            },
            "东风村": {
                "weight": 250,
                "priority": 2,
                "supply_types": ["medicine", "equipment"],
                "items": [
                    {"name": "急救箱", "unit_weight": 10, "qty": 10},
                    {"name": "体温计", "unit_weight": 0.2, "qty": 50},
                    {"name": "口罩", "unit_weight": 0.02, "qty": 1000}
                ]
            },
            "古桥村": {
                "weight": 61,
                "priority": 4,
                "supply_types": ["daily"],
                "items": [
                    {"name": "手电筒", "unit_weight": 0.3, "qty": 20},
                    {"name": "电池", "unit_weight": 0.05, "qty": 20},
                    {"name": "蜡烛", "unit_weight": 0.1, "qty": 100}
                ]
            },
            "新和村": {
                "weight": 20,
                "priority": 4,
                "supply_types": ["food"],
                "items": [
                    {"name": "罐头食品", "unit_weight": 0.5, "qty": 40}
                ]
            },
            "怀书村": {
                "weight": 145,
                "priority": 3,
                "supply_types": ["medicine", "food"],
                "items": [
                    {"name": "消炎药", "unit_weight": 0.1, "qty": 100},
                    {"name": "止痛药", "unit_weight": 0.1, "qty": 100},
                    {"name": "面包", "unit_weight": 0.25, "qty": 100}
                ]
            },
            "雅力村": {
                "weight": 200,
                "priority": 3,
                "supply_types": ["food", "daily"],
                "items": [
                    {"name": "大米", "unit_weight": 5, "qty": 30},
                    {"name": "食用油", "unit_weight": 5, "qty": 10},
                    {"name": "洗衣粉", "unit_weight": 1, "qty": 10}
                ]
            }
        }

        default_case = CaseStudy(
            name="渠洋镇应急物资配送案例",
            description="靖西市渠洋镇无人机应急物资配送项目案例，包含8个需求村庄的物资配送需求",
            center_data=json.dumps(default_center, ensure_ascii=False),
            demand_points=json.dumps(default_demands, ensure_ascii=False),
            material_data=json.dumps(default_materials, ensure_ascii=False),
            is_default=True,
            is_active=True,
        )
        db.add(default_case)
        db.commit()
        db.close()
        print("[Startup] 默认案例初始化成功")
    except Exception as e:
        print(f"初始化默认案例失败: {e}")


def _seed_p5_graph_data(db):
    """将four-graph-data.json中的四图谱数据导入P5项目"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "four-graph-data.json")
    if not os.path.exists(data_path):
        print("[Startup] 四图谱数据文件不存在，跳过导入")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p5 = db.query(CourseProject).filter(CourseProject.project_id == "P5").first()
    if not p5:
        return

    fields = {
        "knowledge_graph": data.get("knowledge_graph"),
        "capability_graph": data.get("capability_graph"),
        "problem_graph": data.get("problem_graph"),
        "ideological_graph": data.get("ideological_graph"),
    }
    updated = False
    for field, value in fields.items():
        if value and not getattr(p5, field, None):
            setattr(p5, field, json.dumps(value, ensure_ascii=False))
            updated = True
            print(f"  [Startup] 导入 P5 {field}")

    if updated:
        db.commit()
        print("[Startup] P5四图谱数据导入完成")


def _init_default_projects():
    """初始化默认课程项目数据（P5）"""
    from app.core.database import SessionLocal
    from app.models.course_graph import CourseProject
    import json

    try:
        db = SessionLocal()
        existing = db.query(CourseProject).filter(CourseProject.project_id == "P5").first()
        if existing:
            # P5已存在，检查是否缺少四图谱数据，缺少则自动补全
            if not existing.knowledge_graph:
                _seed_p5_graph_data(db)
            db.close()
            return

        p5_sub_projects = [
            {
                "id": 1, "name": "飞行任务规划", "hours": 6,
                "tasks": [
                    {"id": 1, "name": "任务1：需求分析与飞行计划制定", "type": "basic",
                     "points": [
                         {"id": "1-1", "name": "应急物资分类与特性", "type": "knowledge", "standard": "1+X（货物分类）、京东标准", "desc": "医疗用品、食品、设备等分类，冷链/危险品识别"},
                         {"id": "1-2", "name": "运输需求快速评估", "type": "skill", "standard": "1+X（物流专项）", "desc": "紧急程度、数量、时效窗口评估"},
                         {"id": "1-3", "name": "飞行计划编制要素", "type": "skill", "standard": "民航局审定指南§3.5、航线规范§4.1", "desc": "航线、高度、时间、备降点、通信频点"},
                         {"id": "1-4", "name": "物流无人机选型原则", "type": "knowledge", "standard": "京东标准（机型选择）", "desc": "根据载重、航程、环境选型"},
                         {"id": "1-5", "name": "运行风险评估基础", "type": "knowledge", "standard": "审定指南§5.1、航线规范§5.2", "desc": "识别危险源、风险缓控措施概述"},
                         {"id": "1-6", "name": "飞行前协调沟通流程", "type": "skill", "standard": "审定指南§4.3(a)", "desc": "与空管、公安、外部服务商协调"}
                     ]},
                    {"id": 2, "name": "任务2：单点航线规划与空域申请", "type": "basic",
                     "points": [
                         {"id": "2-1", "name": "禁飞区与空域等级识别", "type": "knowledge", "standard": "1+X（空域管理）、航线规范§5.2", "desc": "管制空域、适飞空域、人口密集区/稀少区"},
                         {"id": "2-2", "name": "单点航线规划算法", "type": "skill", "standard": "1+X（路线规划）、京东中级", "desc": "点对点最短路径、障碍物避让"},
                         {"id": "2-3", "name": "航线保护区设置", "type": "skill", "standard": "航线规范附录A", "desc": "水平偏航容差、垂直偏航容差，99.7%概率"},
                         {"id": "2-4", "name": "空域申请流程与文书", "type": "skill", "standard": "1+X（飞行报备）、审定指南§2.3", "desc": "申请材料、空域批准"},
                         {"id": "2-5", "name": "起降点与备降点选址", "type": "skill", "standard": "航线规范§4.1", "desc": "受控区域、等效起降点、障碍物超障余度"},
                         {"id": "2-6", "name": "基准高度与真高限制", "type": "knowledge", "standard": "航线规范§4.2", "desc": "高度零位面、高度基准面，40m~120m真高"}
                     ]},
                    {"id": 3, "name": "任务3：网络航线规划与协同调度", "type": "advanced",
                     "points": [
                         {"id": "3-1", "name": "网络航线拓扑结构", "type": "knowledge", "standard": "1+X（高级）、航线规范§5.1", "desc": "多节点、多航线组成的网络，交叉点管理"},
                         {"id": "3-2", "name": "多机协同调度原则", "type": "skill", "standard": "京东高级（调度）、审定指南§6.1", "desc": "分布式操作、进离场顺序、等待点设置"},
                         {"id": "3-3", "name": "应急通信与实时路径优化", "type": "skill", "standard": "1+X（高级）、审定指南§7.2", "desc": "C2链路故障切换、动态重规划"},
                         {"id": "3-4", "name": "空中风险缓冲区划设", "type": "skill", "standard": "审定指南§4.3(b)、附件3", "desc": "与有人机碰撞风险降至可接受水平"},
                         {"id": "3-5", "name": "航线置信度计算", "type": "skill", "standard": "航线规范附录B", "desc": "安全性+可靠性+可接受性"},
                         {"id": "3-6", "name": "栅格化空域评估方法", "type": "knowledge", "standard": "航线规范§5.1.6", "desc": "100m×100m栅格评估"}
                     ]}
                ]
            },
            {
                "id": 2, "name": "飞行设备准备", "hours": 4,
                "tasks": [
                    {"id": 4, "name": "任务4：物资包装装载与行前准备", "type": "basic",
                     "points": [
                         {"id": "4-1", "name": "物资包装规范与载重计算", "type": "skill", "standard": "1+X（货物包装）、京东初级", "desc": "易碎品、冷链、危险品包装；重心配平"},
                         {"id": "4-2", "name": "无人机飞行前检查单", "type": "skill", "standard": "京东初级§1.3、审定指南附件4", "desc": "机身完整性、电池电量、定位系统校准"},
                         {"id": "4-3", "name": "货物固定与投放机构适配", "type": "skill", "standard": "京东中级§1.1.2", "desc": "抛投设备安装、货箱绑扎检查"},
                         {"id": "4-4", "name": "动力电池安全使用与充放电", "type": "knowledge", "standard": "京东初级§3.3、1+X（设备）", "desc": "电池安装、电压检测、存放电操作"},
                         {"id": "4-5", "name": "地面站与遥控器对频", "type": "skill", "standard": "京东初级§1.2.3", "desc": "链路检查、控制权交接"},
                         {"id": "4-6", "name": "环境安全确认（物理/电磁）", "type": "skill", "standard": "审定指南§4.2(a)、航线规范§6.1", "desc": "现场踏勘、通信信号强度测试"}
                     ]},
                    {"id": 5, "name": "任务5：多机协同装调与系统调试", "type": "advanced",
                     "points": [
                         {"id": "5-1", "name": "多旋翼无人机装调工具使用", "type": "skill", "standard": "京东中级§1.1.1", "desc": "机体装配、螺旋桨更换、紧固件检查"},
                         {"id": "5-2", "name": "多机协同编队参数设置", "type": "skill", "standard": "京东高级§1.1.3", "desc": "飞控参数调整（间距、速度、优先级）"},
                         {"id": "5-3", "name": "地面站系统联调", "type": "skill", "standard": "1+X（地面站）、京东中级", "desc": "航线上传、状态监控、手动/自动切换"},
                         {"id": "5-4", "name": "定位系统（GPS/北斗）校准", "type": "skill", "standard": "京东初级§1.3.4", "desc": "磁罗盘校准、IMU初始化"},
                         {"id": "5-5", "name": "避障传感器调试", "type": "skill", "standard": "1+X（设备知识）", "desc": "激光/视觉避障参数、失效模式处理"},
                         {"id": "5-6", "name": "油动无人机燃油加注与管理", "type": "knowledge", "standard": "京东中级§1.1.3（可选）", "desc": "燃油配比、安全加注"}
                     ]}
                ]
            },
            {
                "id": 3, "name": "飞行运输实操", "hours": 6,
                "tasks": [
                    {"id": 6, "name": "任务6：飞行模拟与虚拟仿真演练", "type": "basic",
                     "points": [
                         {"id": "6-1", "name": "飞行模拟器基本操作", "type": "skill", "standard": "1+X（虚拟仿真）、审定指南§2.3", "desc": "遥控器映射、视景系统、飞行参数设置"},
                         {"id": "6-2", "name": "应急投放虚拟仿真场景", "type": "skill", "standard": "京东高级§2.3.5", "desc": "模拟突发气象、通信中断下的精准投放"},
                         {"id": "6-3", "name": "非正常运行程序演练", "type": "skill", "standard": "审定指南附件4（非正常程序）", "desc": "GPS丢星、避障失效、动力下降处置"},
                         {"id": "6-4", "name": "航线飞行与避障训练", "type": "skill", "standard": "1+X（视距内航线飞行）", "desc": "定高匀速矩形/圆形航线、障碍物绕飞"},
                         {"id": "6-5", "name": "仿真数据记录与分析", "type": "skill", "standard": "京东高级§3.3", "desc": "飞行日志导出、偏差分析、效能评估"}
                     ]},
                    {"id": 7, "name": "任务7：飞行实操与物资精准投放", "type": "advanced",
                     "points": [
                         {"id": "7-1", "name": "超视距（BVLOS）飞行操作", "type": "skill", "standard": "1+X（中级/高级）、审定指南§3.1", "desc": "地面站监控、自动飞行、人工干预条件"},
                         {"id": "7-2", "name": "精准投放控制参数", "type": "skill", "standard": "1+X（投放）、京东中级", "desc": "投放高度（≤5m）、落点误差（≤1m）"},
                         {"id": "7-3", "name": "实际飞行实操流程", "type": "skill", "standard": "京东中级§2.2", "desc": "起降、悬停、航线飞行、投放、返航"},
                         {"id": "7-4", "name": "应急异常处置（丢星、低电量）", "type": "skill", "standard": "1+X（应急）、审定指南§4.1", "desc": "进入应急区、执行返航或迫降程序"},
                         {"id": "7-5", "name": "货物状态核查与数据回传", "type": "skill", "standard": "京东中级§2.3.7", "desc": "投放后货物完整性确认、回执上传"},
                         {"id": "7-6", "name": "运行空间与风险缓冲区管理", "type": "knowledge", "standard": "审定指南附件3", "desc": "飞行区、应急区、地面缓冲区的实时监控"}
                     ]},
                    {"id": 8, "name": "任务8：方案汇报与应急模拟演练", "type": "advanced",
                     "points": [
                         {"id": "8-1", "name": "运输方案优化与汇报", "type": "skill", "standard": "通用职业素养", "desc": "基于AI评分、企业反馈进行方案复盘"},
                         {"id": "8-2", "name": "应急响应预案制定", "type": "skill", "standard": "审定指南§5.2、附件4", "desc": "坠机、碰撞、泄漏等突发事件处置流程"},
                         {"id": "8-3", "name": "飞行前准备应急综合演练", "type": "skill", "standard": "1+X（高级）、审定指南§4.2(f)", "desc": "包含规划调整、飞行前突发故障等场景"},
                         {"id": "8-4", "name": "应急任务工单填写", "type": "skill", "standard": "京东高级§3.1.3", "desc": "记录任务批次、异常处置、决策依据"},
                         {"id": "8-5", "name": "团队协作", "type": "素养", "standard": "审定指南§6.1、京东高级", "desc": "飞手、调度、安全员等角色协同"},
                         {"id": "8-6", "name": "安全文化与责任担当", "type": "思政", "standard": "课程思政", "desc": "人民至上、生命至上；工匠精神"},
                         {"id": "8-7", "name": "物资投送应急综合演练", "type": "skill", "standard": "1+X（高级）、审定指南§4.2(f)", "desc": "包含物资装载、航线规划、精准投放等场景"}
                     ]}
                ]
            }
        ]

        p5_project = CourseProject(
            project_id="P5",
            name="应急物资低空智慧运输",
            hours=16,
            task_count=8,
            description="本项目聚焦无人机应急物资运输全流程，涵盖飞行任务规划、飞行设备准备、飞行运输实操三大子项目，培养学生的航线规划、设备操作和应急处置能力。",
            certifications=json.dumps(["无人机物流运输1+X（初/中/高级）", "无人系统空地协同赛"], ensure_ascii=False),
            sub_projects=json.dumps(p5_sub_projects, ensure_ascii=False),
        )
        db.add(p5_project)
        db.commit()
        print("[Startup] 默认项目P5初始化成功")

        # 自动导入P5四图谱数据
        _seed_p5_graph_data(db)

        db.close()
    except Exception as e:
        print(f"初始化默认项目失败: {e}")


@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    _init_default_case()
    _init_default_projects()
    yield


app = FastAPI(
    title="低空应急智慧运输智能体 API",
    description="模块1:配送点设置 | 模块2:物资需求 | 模块3:无人机选择 | 模块4:路径规划 | 模块5:方案诊断 | 模块6:方案优出 | 模块7:案例管理 | 模块8:系统设置",
    version="1.5.0",
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(points_router)
app.include_router(materials_router)
app.include_router(config_router)
app.include_router(uavs_router)
app.include_router(optimizer_router)
app.include_router(diagnosis_router)
app.include_router(workspace_router)
app.include_router(report_router)
app.include_router(llm_config_router)
app.include_router(case_study_router)
app.include_router(course_graph_router)
app.include_router(score_session_router)
app.include_router(ai_chat_router)


@app.get("/health", tags=["系统"])
def health_check():
    return {"status": "ok", "module": "配送点设置模块"}