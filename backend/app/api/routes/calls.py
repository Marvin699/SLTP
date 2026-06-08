import json
import time
import shutil
import os
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/calls", tags=["任务4·录像"])

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "media" / "calls"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

GROUP_VILLAGES = {
    1: "怀渠村", 2: "塘麻村", 3: "坡乐村", 4: "东风村", 5: "古桥村", 6: "新和村",
}

STREAM_ROOMS = {}


class StreamRoom:
    def __init__(self):
        self.student_ws = None
        self.live_ws_set = set()
        self.last_frame_b64 = None
        self.last_frame_time = 0
        self.lock = asyncio.Lock()


def _room(group_id: int) -> StreamRoom:
    if group_id not in STREAM_ROOMS:
        STREAM_ROOMS[group_id] = StreamRoom()
    return STREAM_ROOMS[group_id]


def _ext_from_mime(mime: str, filename: str) -> str:
    if filename:
        suf = Path(filename).suffix.lower()
        if suf in ('.webm', '.mp4', '.ogg'):
            return suf
    if mime:
        m = mime.lower()
        if 'mp4' in m:
            return '.mp4'
        if 'webm' in m:
            return '.webm'
    return '.webm'


UPLOAD_COUNTER = {}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        hello = json.loads(raw)
        group_id = int(hello.get("group_id") or 0)
        role = hello.get("role", "student")
        if not group_id:
            await websocket.close(code=4400)
            return
        room = _room(group_id)

        if role == "student":
            async with room.lock:
                if room.student_ws is not None:
                    try: await room.student_ws.close(code=4401)
                    except Exception: pass
                room.student_ws = websocket
            try:
                while True:
                    msg = await websocket.receive()
                    if msg["type"] == "websocket.disconnect":
                        break
                    if msg["type"] != "websocket.receive":
                        continue
                    payload = msg.get("text")
                    if payload:
                        try:
                            data = json.loads(payload)
                            if data.get("type") == "frame":
                                room.last_frame_b64 = data.get("data")
                                room.last_frame_time = time.time()
                                if room.live_ws_set:
                                    dead = []
                                    for lw in list(room.live_ws_set):
                                        try:
                                            await lw.send_text(payload)
                                        except Exception:
                                            dead.append(lw)
                                    for d in dead:
                                        room.live_ws_set.discard(d)
                        except Exception:
                            pass
                    else:
                        binary = msg.get("bytes")
                        if binary:
                            import base64
                            b64 = base64.b64encode(binary).decode("ascii")
                            room.last_frame_b64 = b64
                            room.last_frame_time = time.time()
                            j = json.dumps({"type": "frame", "group_id": group_id, "data": b64})
                            if room.live_ws_set:
                                dead = []
                                for lw in list(room.live_ws_set):
                                    try:
                                        await lw.send_text(j)
                                    except Exception:
                                        dead.append(lw)
                                for d in dead:
                                    room.live_ws_set.discard(d)
            except WebSocketDisconnect:
                pass
            except Exception:
                pass
            async with room.lock:
                if room.student_ws is websocket:
                    room.student_ws = None

        elif role == "live":
            async with room.lock:
                room.live_ws_set.add(websocket)
            try:
                if room.last_frame_b64:
                    await websocket.send_text(json.dumps({
                        "type": "frame",
                        "group_id": group_id,
                        "data": room.last_frame_b64,
                        "from_cache": True,
                    }))
                while True:
                    msg = await websocket.receive()
                    if msg["type"] == "websocket.disconnect":
                        break
            except WebSocketDisconnect:
                pass
            except Exception:
                pass
            finally:
                async with room.lock:
                    room.live_ws_set.discard(websocket)
        else:
            await websocket.close(code=4402)
            return
    except Exception:
        try: await websocket.close(code=4410)
        except Exception: pass


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
    mime = chunk.content_type or ''
    ext = _ext_from_mime(mime, chunk.filename or '')
    fname = f"g{group_id}_p{n:05d}_{int(time.time()*1000)}{ext}"
    fpath = MEDIA_DIR / fname
    with fpath.open("wb") as f:
        shutil.copyfileobj(chunk.file, f)

    _cleanup_old_for_group(group_id, keep_recent=30)

    return {
        "ok": True, "name": fname, "url": f"/media/calls/{fname}",
        "size": fpath.stat().st_size, "seq": n, "mime": mime,
    }


def _cleanup_old_for_group(group_id: int, keep_recent: int = 30):
    try:
        items = []
        for f in MEDIA_DIR.iterdir():
            if not f.is_file():
                continue
            if not f.name.startswith(f"g{group_id}_"):
                continue
            items.append(f)
        items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for old in items[keep_recent:]:
            try:
                os.remove(old)
            except OSError:
                pass
    except OSError:
        pass


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
