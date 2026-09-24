"""任务8·电子评量表 API

v2：评分数据持久化到 SQLite（rating_records 表），替代原 JSON 文件存储。
原因：JSON 文件读-改-写无事务，课堂多人同时提交会互相覆盖丢分；
数据库 + WAL（core/database.py 已开启）下并发提交安全，且服务重启不丢数据。
首次启动自动把旧 JSON 数据一次性导入数据库（幂等，导入后文件改名 .imported）。
API 响应结构与 v1 完全一致，前端零改动。
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.deps import get_current_user, require_teacher
from app.core.database import SessionLocal
from app.models.rating import RatingRecord

router = APIRouter(prefix="/api/ratings", tags=["任务8·电子评量表"])

# 旧 JSON 数据目录（仅用于一次性迁移）
RATING_DIR = Path(__file__).resolve().parent.parent.parent.parent / "media" / "ratings"
RATING_DIR.mkdir(parents=True, exist_ok=True)

GROUP_KEYS = {
    1: "揽星组", 2: "御风组", 3: "巡天组", 4: "逐日组", 5: "凌云组", 6: "长空组",
}


# ── 旧 JSON 数据一次性迁移（幂等：导入成功/空文件后改名，不再重复处理） ──
def _migrate_json_files():
    for gid in GROUP_KEYS:
        src = RATING_DIR / f"g{gid}_list.json"
        if not src.exists():
            continue
        try:
            items = json.loads(src.read_text(encoding="utf-8") or "[]")
        except Exception:
            continue  # 文件损坏则保留，下次启动再试
        if isinstance(items, list) and items:
            db = SessionLocal()
            try:
                for it in items:
                    ts = it.get("ts") or int(time.time() * 1000)
                    try:
                        created = datetime.fromtimestamp(ts / 1000)
                    except Exception:
                        created = datetime.now()
                    db.add(RatingRecord(
                        group_id=gid,
                        name=(it.get("name") or "匿名")[:100],
                        role=(it.get("role") or "student")[:50],
                        dims=json.dumps(it.get("dims") or [], ensure_ascii=False),
                        total=it.get("total"),
                        created_at=created,
                    ))
                db.commit()
                print(f"[Ratings] 已迁移 g{gid} 的 {len(items)} 条 JSON 评分记录到数据库")
            except Exception as e:
                print(f"[Ratings] JSON 迁移失败 g{gid}: {e}")
                db.rollback()
                db.close()
                continue  # 保留原文件，下次启动重试
            finally:
                db.close()
        # 导入成功（或文件本就为空）→ 改名避免重复导入；latest 可由记录重算，直接废弃
        try:
            src.rename(src.with_suffix(".json.imported"))
        except Exception:
            pass
        latest = RATING_DIR / f"g{gid}_latest.json"
        if latest.exists():
            try:
                latest.rename(latest.with_suffix(".json.imported"))
            except Exception:
                pass


_migrate_json_files()


# ── 聚合工具 ──

def _item_from(r: RatingRecord) -> dict:
    try:
        dims = json.loads(r.dims) if r.dims else []
    except Exception:
        dims = []
    return {
        "name": r.name or "匿名",
        "role": r.role or "student",
        "dims": dims,
        "total": r.total,
        "ts": int(r.created_at.timestamp() * 1000) if r.created_at else 0,
    }


def _empty(group_id: int) -> dict:
    return {
        "group_id": group_id,
        "group_name": GROUP_KEYS.get(group_id, ""),
        "total": 0, "dims": [], "count": 0, "updated_at": 0,
    }


def _latest(db, group_id: int) -> dict:
    """从数据库聚合某组的最新评分看板（维度平均 / 总分平均 / 最近10条）"""
    rows = (
        db.query(RatingRecord)
        .filter(RatingRecord.group_id == group_id)
        .order_by(RatingRecord.created_at.asc(), RatingRecord.id.asc())
        .all()
    )
    if not rows:
        return _empty(group_id)

    items = [_item_from(r) for r in rows]

    # 维度平均：按 label 聚合全部记录（与 v1 的 key 对齐逻辑一致）
    agg: Dict[str, list] = {}
    for it in items:
        for d in it.get("dims", []):
            label = d.get("label")
            if label is None:
                continue
            agg.setdefault(label, []).append(int(d.get("val", 0)))
    dims = [{"label": k, "val": round(sum(v) / len(v))} for k, v in agg.items()]

    totals = [it["total"] for it in items if it.get("total") is not None]
    total_avg = round(sum(totals) / len(totals)) if totals else 0

    return {
        "group_id": group_id,
        "group_name": GROUP_KEYS.get(group_id, ""),
        "total": total_avg,
        "dims": dims,
        "count": len(items),
        "updated_at": items[-1]["ts"],
        "ratings": items[-10:],
    }


class RatingSubmit(BaseModel):
    group_id: int
    dims: List[Dict]
    total: Optional[int] = None
    name: Optional[str] = ""
    role: Optional[str] = "student"


@router.post("/submit")
def submit_rating(r: RatingSubmit, _: object = Depends(get_current_user)):
    group_id = r.group_id
    if group_id not in GROUP_KEYS:
        raise HTTPException(400, "未知 group_id")

    db = SessionLocal()
    try:
        db.add(RatingRecord(
            group_id=group_id,
            name=(r.name or "匿名")[:100],
            role=(r.role or "student")[:50],
            dims=json.dumps(r.dims or [], ensure_ascii=False),
            total=r.total,
        ))
        db.commit()

        count = db.query(RatingRecord).filter(RatingRecord.group_id == group_id).count()
        if not r.dims:
            return JSONResponse({"ok": True, "count": count})

        data = _latest(db, group_id)
        return JSONResponse({
            "ok": True,
            "group_id": group_id,
            "count": count,
            "total": data["total"],
            "dims": data["dims"],
        })
    finally:
        db.close()


@router.get("/latest")
def get_latest(group_id: int = Query(...), _: object = Depends(get_current_user)):
    db = SessionLocal()
    try:
        return JSONResponse(_latest(db, group_id))
    finally:
        db.close()


@router.get("/latest_all")
def get_latest_all(_: object = Depends(get_current_user)):
    db = SessionLocal()
    try:
        result = {}
        for gid in GROUP_KEYS:
            result[gid] = _latest(db, gid)
        return JSONResponse(result)
    finally:
        db.close()


@router.post("/reset")
def reset_group(group_id: Optional[int] = Query(None), _: object = Depends(require_teacher)):
    db = SessionLocal()
    try:
        q = db.query(RatingRecord)
        if group_id is not None:
            if group_id not in GROUP_KEYS:
                raise HTTPException(400, "未知 group_id")
            q = q.filter(RatingRecord.group_id == group_id)
            q.delete(synchronize_session=False)
            db.commit()
            return JSONResponse({"ok": True, "reset": group_id})
        q.delete(synchronize_session=False)
        db.commit()
        return JSONResponse({"ok": True, "reset": "all"})
    finally:
        db.close()


@router.post("/reset_all")
def reset_all(_: object = Depends(require_teacher)):
    db = SessionLocal()
    try:
        db.query(RatingRecord).delete(synchronize_session=False)
        db.commit()
        return JSONResponse({"ok": True})
    finally:
        db.close()
