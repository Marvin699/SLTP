"""工作空间API - 处理各模块数据的保存和加载"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime

router = APIRouter(prefix="/api/path-planning/workspace", tags=["workspace"])

WORK_DIR = Path(__file__).parent.parent.parent.parent.parent / "work"
WORK_DIR.mkdir(exist_ok=True)


class Module1Data(BaseModel):
    center: Optional[Dict[str, Any]] = None
    demands: List[Dict[str, Any]] = []
    distance_matrix: Optional[List[List[float]]] = None
    saved_at: str = ""


class Module2Data(BaseModel):
    assignments: List[Dict[str, Any]] = []
    saved_at: str = ""


class Module3Data(BaseModel):
    all_models: List[Dict[str, Any]] = []
    selected_uavs: List[Dict[str, Any]] = []
    saved_at: str = ""


@router.post("/save/module1")
async def save_module1(data: Module1Data):
    """保存模块一数据（配送中心、需求点、距离矩阵）"""
    try:
        file_path = WORK_DIR / "module01.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        return {"success": True, "message": "模块一数据保存成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/save/module2")
async def save_module2(data: Module2Data):
    """保存模块二数据（物资需求、优先级、配送模式）"""
    try:
        file_path = WORK_DIR / "module02.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        return {"success": True, "message": "模块二数据保存成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/save/module3")
async def save_module3(data: Module3Data):
    """保存模块三数据（无人机配置、选择的无人机）"""
    try:
        file_path = WORK_DIR / "module03.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        return {"success": True, "message": "模块三数据保存成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/load/module1")
async def load_module1():
    """加载模块一数据"""
    try:
        file_path = WORK_DIR / "module01.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"success": True, "data": data}
        return {"success": False, "message": "文件不存在"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/load/module2")
async def load_module2():
    """加载模块二数据"""
    try:
        file_path = WORK_DIR / "module02.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"success": True, "data": data}
        return {"success": False, "message": "文件不存在"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/load/module3")
async def load_module3():
    """加载模块三数据"""
    try:
        file_path = WORK_DIR / "module03.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"success": True, "data": data}
        return {"success": False, "message": "文件不存在"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/status")
async def get_workspace_status():
    """获取工作空间状态"""
    status = {
        "module1_exists": (WORK_DIR / "module01.json").exists(),
        "module2_exists": (WORK_DIR / "module02.json").exists(),
        "module3_exists": (WORK_DIR / "module03.json").exists(),
    }
    return {"success": True, "status": status}
