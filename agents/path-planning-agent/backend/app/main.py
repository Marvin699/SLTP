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

# 确保所有模型在 create_all 之前被导入（注册到 Base.metadata）
from app.models.assignment import MaterialAssignment  # noqa: F401
from app.models.uav_param import UavParam  # noqa: F401
from app.models.ai_result import AiSelectionResult  # noqa: F401
from app.models.diagnosis import DiagnosisRecord  # noqa: F401
from app.models.optimizer import OptimizationRecord  # noqa: F401
from app.models.report import ReportRecord  # noqa: F401
from app.models.llm_config import LLMConfig  # noqa: F401
from app.models.case_study import CaseStudy  # noqa: F401

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

_migrate()

app = FastAPI(
    title="低空应急智慧运输智能体 API",
    description="模块1:配送点设置 | 模块2:物资需求 | 模块3:无人机选择 | 模块4:路径规划 | 模块5:方案诊断 | 模块6:方案优出 | 模块7:案例管理 | 模块8:系统设置",
    version="1.5.0",
)


@app.on_event("startup")
def init_default_case():
    """启动时初始化默认案例"""
    from app.core.database import SessionLocal
    from app.models.case_study import CaseStudy
    import json
    import time
    
    time.sleep(0.5)  # 等待数据库初始化完成
    
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
    except Exception as e:
        print(f"初始化默认案例失败: {e}")

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


@app.get("/api/health", tags=["系统"])
def health_check():
    return {"status": "ok", "module": "配送点设置模块"}