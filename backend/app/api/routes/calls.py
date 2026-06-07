import os
import time
import shutil
import uuid
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


@router.post("/upload")
async def upload_chunk(
    group_id: int = Query(..., ge=1, le=6),
    group_name: str = Query("", description="组名，例 逐日组"),
    student_id: str = Query("", description="学生端随机会话ID"),
    seq: int = Query(..., ge=0, description="分片序号"),
    total: int = Query(..., ge=1, description="总分片数"),
    chunk: UploadFile = File(...),
):
    sid = student_id or "anon"
    session_dir = MEDIA_DIR / f"g{group_id}_{sid}"
    session_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(chunk.filename or "chunk").suffix.lower() or ".webm"
    chunk_path = session_dir / f"part_{seq:05d}{suffix}"

    with chunk_path.open("wb") as f:
        shutil.copyfileobj(chunk.file, f)

    if seq >= total - 1:
        merged_path = session_dir / f"{group_name or GROUP_VILLAGES.get(group_id, 'group')}_{int(time.time())}.webm"
        merged = open(merged_path, "wb")
        for i in range(total):
            p = session_dir / f"part_{i:05d}{suffix}"
            if p.exists():
                with p.open("rb") as part:
                    shutil.copyfileobj(part, merged)
                try:
                    p.unlink()
                except Exception:
                    pass
        merged.close()
        try:
            session_dir.rmdir()
        except Exception:
            pass
        return {
            "ok": True,
            "merged": True,
            "url": f"/media/calls/{merged_path.name}",
            "name": merged_path.name,
            "size": merged_path.stat().st_size,
        }

    return {"ok": True, "seq": seq, "saved": str(chunk_path)}


@router.get("/list")
def list_calls(
    group_id: Optional[int] = Query(None, ge=1, le=6),
    limit: int = Query(30, ge=1, le=200),
):
    items = []
    for f in sorted(MEDIA_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not f.is_file():
            continue
        name = f.name
        if group_id is not None and not name.startswith(f"g{group_id}_") and not name.startswith(GROUP_VILLAGES.get(group_id, "")):
            continue
        st = f.stat()
        items.append({
            "name": name,
            "url": f"/media/calls/{name}",
            "size": st.st_size,
            "mtime": int(st.st_mtime),
            "group_id": int(name.split("_")[0].lstrip("g")) if name.startswith("g") else None,
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
        if f.name.startswith(f"g{group_id}_"):
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
