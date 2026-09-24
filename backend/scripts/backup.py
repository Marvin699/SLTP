#!/usr/bin/env python3
"""数据库 + 静态资源备份脚本（正式投产"救命稻草"）

备份内容：
  1. SQLite 数据库（用 sqlite3 backup API，WAL 模式下也能拿到一致性快照，无需停服）
  2. uploads/   课件与资料
  3. media/     任务4视频分片、评分附件
  4. .env       环境配置（含密钥，备份包请妥善保管）

输出：backend/backups/backup_YYYYMMDD_HHMMSS.zip
保留策略：默认保留最近 10 份，可用 --keep N 调整

用法：
  .venv/bin/python scripts/backup.py            # 手动备份
  crontab -e 里加（每天凌晨 2 点自动备份 + 按天记日志）：
    0 2 * * * cd /path/to/backend && .venv/bin/python scripts/backup.py >> backups/cron.log 2>&1
"""
import argparse
import shutil
import sqlite3
import sys
import zipfile
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
BACKUPS_DIR = BACKEND_DIR / "backups"
DEFAULT_KEEP = 10

# (名称, 路径, 是否必须存在) —— 缺失的目录跳过并提示，不算失败
STATIC_TARGETS = [
    ("uploads", BACKEND_DIR / "uploads", False),
    ("media", BACKEND_DIR / "media", False),
    ("reports", BACKEND_DIR / "reports", False),
    ("env", BACKEND_DIR / ".env", False),
]


def find_database() -> Path:
    """从 .env / 默认位置解析数据库路径"""
    env = BACKEND_DIR / ".env"
    url = ""
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DATABASE_URL"):
                url = line.split("=", 1)[1].strip()
                break
    if not url:
        url = "sqlite:///./path_planning_data.db"
    # sqlite:///./xxx.db → backend/xxx.db
    return BACKEND_DIR / url.split("///")[-1].lstrip("./")


def backup_database(db_path: Path, out_dir: Path) -> Path:
    """sqlite3 backup API：在线一致性快照（WAL 三文件问题不存在，无需拷 -wal/-shm）"""
    snap = out_dir / db_path.name
    src = sqlite3.connect(str(db_path))
    dst = sqlite3.connect(str(snap))
    try:
        src.backup(dst)  # 事务级快照，运行中备份也一致
    finally:
        src.close()
        dst.close()
    return snap


def main():
    parser = argparse.ArgumentParser(description="平台数据备份")
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP, help=f"保留最近 N 份备份（默认 {DEFAULT_KEEP}）")
    parser.add_argument("--out", type=str, default=str(BACKUPS_DIR), help="备份输出目录")
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out)
    work_dir = out_dir / f"tmp_{stamp}"
    work_dir.mkdir(parents=True, exist_ok=True)

    db_path = find_database()
    if not db_path.exists():
        print(f"[备份失败] 未找到数据库文件: {db_path}")
        sys.exit(1)

    # 1) 数据库快照
    snap = backup_database(db_path, work_dir)
    print(f"[1/3] 数据库快照完成: {snap.name} ({snap.stat().st_size // 1024} KB)")

    # 2) 静态资源复制
    copied = []
    for name, path, _ in STATIC_TARGETS:
        if not path.exists():
            print(f"[2/3] 跳过 {name}（不存在）")
            continue
        target = work_dir / name
        if path.is_dir():
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)
        copied.append(name)
    print(f"[2/3] 静态资源复制完成: {', '.join(copied) if copied else '（无）'}")

    # 3) 打包
    zip_path = out_dir / f"backup_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(work_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(work_dir))
    shutil.rmtree(work_dir)
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"[3/3] 备份完成: {zip_path} ({size_mb:.1f} MB)")

    # 4) 清理旧备份
    backups = sorted(out_dir.glob("backup_*.zip"))
    for old in backups[:-args.keep] if len(backups) > args.keep else []:
        old.unlink()
        print(f"      清理旧备份: {old.name}")
    print(f"      当前保留 {min(len(backups), args.keep)} 份")


if __name__ == "__main__":
    main()
