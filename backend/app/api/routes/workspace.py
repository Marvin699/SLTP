import json
import sqlite3
import time
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/api/path-planning/workspace", tags=["工作区持久化"])

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "path_planning_data.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    conn = _get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workspace_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


_ensure_table()


@router.post("/save/{module_id}")
async def save_module(module_id: str, req: Request):
    if module_id not in ("module1", "module2", "module3", "module4"):
        raise HTTPException(400, "module_id 必须是 module1~module4")
    payload = await req.json()
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO workspace_snapshots(module,data,updated_at) VALUES(?,?,?)
               ON CONFLICT(module) DO UPDATE SET
                 data=excluded.data,
                 updated_at=excluded.updated_at""",
            (module_id, json.dumps(payload, ensure_ascii=False), int(time.time())),
        )
        conn.commit()
        return {"success": True, "module": module_id, "saved_at": int(time.time())}
    finally:
        conn.close()


@router.get("/load/{module_id}")
async def load_module(module_id: str):
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT data, updated_at FROM workspace_snapshots WHERE module=?", (module_id,)
        ).fetchone()
        if not row:
            return {"success": True, "module": module_id, "data": None, "note": "尚无保存数据"}
        return {
            "success": True,
            "module": module_id,
            "data": json.loads(row["data"]),
            "updated_at": row["updated_at"],
        }
    finally:
        conn.close()


@router.get("/list")
async def list_modules():
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT module, updated_at FROM workspace_snapshots ORDER BY module"
        ).fetchall()
        return {
            "success": True,
            "items": [{"module": r["module"], "updated_at": r["updated_at"]} for r in rows],
        }
    finally:
        conn.close()
