import time
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/calls", tags=["任务4·录像"])

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "media" / "calls"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

GROUP_VILLAGES = {
    1: "怀渠村", 2: "塘麻村", 3: "坡乐村", 4: "东风村", 5: "古桥村", 6: "新和村",
}

UPLOAD_COUNTER = {}


@router.post("/upload")
async def upload_chunk(
    group_id: int = Query(..., ge=1, le=6),
    group_name: str = Query("", description="组名，例 逐日组"),
    student_id: str = Query("", description="学生端随机会话ID"),
    seq: int = Query(0, ge=0, description="分片序号"),
    total: int = Query(9999, ge=1, description="总分片数(占位)"),
    chunk: UploadFile = File(...),
):
    key = f"g{group_id}"
    UPLOAD_COUNTER[key] = UPLOAD_COUNTER.get(key, 0) + 1
    n = UPLOAD_COUNTER[key]
    suffix = Path(chunk.filename or "chunk").suffix.lower() or ".webm"
    fname = f"g{group_id}_p{n:05d}_{int(time.time()*1000)}{suffix}"
    fpath = MEDIA_DIR / fname
    with fpath.open("wb") as f:
        shutil.copyfileobj(chunk.file, f)
    return {"ok": True, "name": fname, "url": f"/media/calls/{fname}", "size": fpath.stat().st_size, "seq": n}


@router.get("/list")
def list_calls(
    group_id: Optional[int] = Query(None, ge=1, le=6),
    limit: int = Query(50, ge=1, le=200),
):
    items = []
    for f in sorted(MEDIA_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not f.is_file():
            continue
        name = f.name
        if not name.startswith("g"):
            continue
        gid = int(name.split("_")[0].lstrip("g"))
        if group_id is not None and gid != group_id:
            continue
        st = f.stat()
        items.append({
            "name": name,
            "url": f"/media/calls/{name}",
            "size": st.st_size,
            "mtime": int(st.st_mtime),
            "group_id": gid,
        })
        if len(items) >= limit:
            break
    return {"items": items, "total": len(items)}


@router.get("/latest")
def latest_for_group(group_id: int = Query(..., ge=1, le=6)):
    best = None
    best_time = 0
    for f in MEDIA_DIR.iterdir():
        if not f.is_file():
            continue
        if not f.name.startswith(f"g{group_id}_"):
            continue
        st = f.stat()
        if st.st_mtime > best_time:
            best = f
            best_time = st.st_mtime
    if best is None:
        return {"ok": True, "item": None}
    return {
        "ok": True,
        "item": {
            "name": best.name,
            "url": f"/media/calls/{best.name}",
            "size": best.stat().st_size,
            "mtime": int(best.stat().st_mtime),
        },
    }
