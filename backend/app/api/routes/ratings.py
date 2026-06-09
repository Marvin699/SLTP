import json
import time
import threading
from pathlib import Path
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/ratings", tags=["任务8·电子评量表"])

RATING_DIR = Path(__file__).resolve().parent.parent.parent.parent / "media" / "ratings"
RATING_DIR.mkdir(parents=True, exist_ok=True)

GROUP_KEYS = {
    1: "揽星组", 2: "御风组", 3: "巡天组", 4: "逐日组", 5: "凌云组", 6: "长空组",
}

_lock = threading.Lock()


def _group_file(group_id: int) -> Path:
    return RATING_DIR / f"g{group_id}_latest.json"


def _group_list_file(group_id: int) -> Path:
    return RATING_DIR / f"g{group_id}_list.json"


def _ensure_list(group_id: int) -> list:
    p = _group_list_file(group_id)
    if not p.exists():
        p.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _reset_group(group_id: int):
    with _lock:
        _group_file(group_id).write_text(json.dumps({}), encoding="utf-8")
        _group_list_file(group_id).write_text("[]", encoding="utf-8")


def _reset_all():
    with _lock:
        for g in GROUP_KEYS:
            _group_file(g).write_text(json.dumps({}), encoding="utf-8")
            _group_list_file(g).write_text("[]", encoding="utf-8")


def _latest(group_id: int) -> dict:
    p = _group_file(group_id)
    if not p.exists():
        return {"group_id": group_id, "group_name": GROUP_KEYS.get(group_id, ""), "total": 0, "dims": [], "count": 0, "updated_at": 0}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not data or "total" not in data:
            return {"group_id": group_id, "group_name": GROUP_KEYS.get(group_id, ""), "total": 0, "dims": [], "count": 0, "updated_at": 0}
        return {
            "group_id": group_id,
            "group_name": GROUP_KEYS.get(group_id, ""),
            "total": data.get("total", 0),
            "dims": data.get("dims", []),
            "count": data.get("count", 0),
            "updated_at": data.get("updated_at", 0),
            "ratings": data.get("ratings", []),
        }
    except Exception:
        return {"group_id": group_id, "group_name": GROUP_KEYS.get(group_id, ""), "total": 0, "dims": [], "count": 0, "updated_at": 0}


class RatingSubmit(BaseModel):
    group_id: int
    dims: List[Dict]
    total: Optional[int] = None
    name: Optional[str] = ""
    role: Optional[str] = "student"


@router.post("/submit")
def submit_rating(r: RatingSubmit):
    group_id = r.group_id
    if group_id not in GROUP_KEYS:
        raise HTTPException(400, "未知 group_id")

    with _lock:
        lst = _ensure_list(group_id)
        item = {
            "name": r.name or "匿名",
            "role": r.role or "student",
            "dims": r.dims,
            "total": r.total,
            "ts": int(time.time() * 1000),
        }
        lst.append(item)
        _group_list_file(group_id).write_text(json.dumps(lst, ensure_ascii=False), encoding="utf-8")

        if not r.dims:
            return JSONResponse({"ok": True, "count": len(lst)})

        dim_labels = [d.get("label", f"d{i+1}") for i, d in enumerate(r.dims)]
        dim_vals = [int(d.get("val", 0)) for d in r.dims]
        total = r.total if r.total is not None else sum(dim_vals)

        agg = {}
        for prev in lst:
            for j, d in enumerate(prev.get("dims", [])):
                if j >= len(dim_labels):
                    break
                key = dim_labels[j]
                if key not in agg:
                    agg[key] = []
                agg[key].append(int(d.get("val", 0)))

        dim_avg = []
        for i, label in enumerate(dim_labels):
            vals = agg.get(label, dim_vals[i:i+1])
            if not vals:
                continue
            avg = round(sum(vals) / len(vals))
            dim_avg.append({"label": label, "val": avg})

        all_totals = [prev.get("total") for prev in lst if prev.get("total") is not None]
        all_totals.append(total)
        total_avg = round(sum(all_totals) / len(all_totals)) if all_totals else total

        latest_data = {
            "group_id": group_id,
            "group_name": GROUP_KEYS[group_id],
            "total": total_avg,
            "dims": dim_avg,
            "count": len(lst),
            "updated_at": int(time.time() * 1000),
            "ratings": lst[-10:],
        }
        _group_file(group_id).write_text(json.dumps(latest_data, ensure_ascii=False), encoding="utf-8")

    return JSONResponse({"ok": True, "group_id": group_id, "count": len(lst), "total": total_avg, "dims": dim_avg})


@router.get("/latest")
def get_latest(group_id: int = Query(...)):
    data = _latest(group_id)
    return JSONResponse(data)


@router.get("/latest_all")
def get_latest_all():
    result = {}
    for gid, gname in GROUP_KEYS.items():
        result[gid] = _latest(gid)
    return JSONResponse(result)


@router.post("/reset")
def reset_group(group_id: Optional[int] = Query(None)):
    if group_id is not None:
        _reset_group(group_id)
        return JSONResponse({"ok": True, "reset": group_id})
    _reset_all()
    return JSONResponse({"ok": True, "reset": "all"})


@router.post("/reset_all")
def reset_all():
    _reset_all()
    return JSONResponse({"ok": True})
