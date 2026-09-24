#!/bin/bash
# 生产启动脚本（nginx 反代场景，无 docker）
# 用法：
#   ./scripts/start_server.sh start     # 启动（后台，日志按天写入 logs/app_YYYYMMDD.log）
#   ./scripts/start_server.sh stop      # 停止
#   ./scripts/start_server.sh restart   # 重启
#   ./scripts/start_server.sh status    # 查看状态
#
# 开机自启（systemd 示例）可改为直接 ExecStart=.venv/bin/python -m uvicorn ...
set -e

cd "$(dirname "$0")/.."

PORT=8000
PID_FILE="uvicorn.pid"
LOG_DIR="logs"
PYTHON=".venv/bin/python"
UVICORN="$PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port $PORT --workers 1"

mkdir -p "$LOG_DIR"

start() {
  if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
    echo "已在运行 (PID $(cat $PID_FILE))"
    exit 0
  fi
  LOG_FILE="$LOG_DIR/app_$(date +%Y%m%d).log"
  echo "启动中... 日志: $LOG_FILE"
  nohup $UVICORN >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 2
  if kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
    echo "已启动 (PID $(cat $PID_FILE), 端口 $PORT)"
  else
    echo "启动失败，最近日志："
    tail -20 "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
}

stop() {
  if [ ! -f "$PID_FILE" ]; then
    echo "未在运行"
    exit 0
  fi
  PID=$(cat "$PID_FILE")
  kill "$PID" 2>/dev/null || true
  for i in $(seq 1 10); do
    kill -0 "$PID" 2>/dev/null || break
    sleep 1
  done
  kill -9 "$PID" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "已停止"
}

case "${1:-start}" in
  start)   start ;;
  stop)    stop ;;
  restart) stop; start ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "运行中 (PID $(cat $PID_FILE))"
    else
      echo "未在运行"
    fi
    ;;
  *) echo "用法: $0 {start|stop|restart|status}"; exit 1 ;;
esac
