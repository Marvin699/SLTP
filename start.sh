#!/bin/bash
# 智慧低空应急运输教学平台 - 一键启动脚本（macOS）
# 用法: ./start.sh  （前后端一起启动）
#       ./start.sh backend|frontend  （只启动其中一端）

cd "$(dirname "$0")"
ROOT_DIR="$(pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

BLUE='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'

# ---------- 工具函数 ----------
port_pid() { lsof -ti :"$1" -sTCP:LISTEN 2>/dev/null; }

check_port_free() {
  local port="$1" name="$2"
  local pid; pid=$(port_pid "$port")
  if [ -n "$pid" ]; then
    echo -e "${YELLOW}⚠ 端口 $port 已被占用（PID $pid）:${NC}"
    ps -p "$pid" -o command= | head -1
    read -r "答复?端口被占用，是否杀掉该进程? (y/n) " ans
    if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
      kill -9 "$pid" 2>/dev/null
      sleep 1
      [ -z "$(port_pid "$port")" ] && echo -e "${GREEN}✓ 端口 $port 已释放${NC}" || { echo -e "${RED}✗ 释放失败，请手动处理${NC}"; exit 1; }
    else
      echo -e "${YELLOW}跳过，端口 $port 沿用现有进程${NC}"
      return 1
    fi
  fi
  return 0
}

start_backend() {
  echo -e "\n${BLUE}══════════ 启动后端 (FastAPI :8000) ══════════${NC}"
  if ! check_port_free 8000; then return; fi
  cd "$BACKEND_DIR"
  # 优先使用项目实际使用的 .venv（uvicorn 装在里面）；没有则回退创建 venv
  if [ ! -f .venv/bin/uvicorn ] && [ ! -x .venv/bin/python ]; then
    if [ ! -d venv ]; then
      echo -e "${YELLOW}未发现 .venv / venv，创建虚拟环境...${NC}"
      python3 -m venv venv
      ./venv/bin/pip install -q -r requirements.txt
    fi
  fi
  PY_BIN=".venv/bin/python"
  [ -x "$PY_BIN" ] || PY_BIN="venv/bin/python"
  nohup "$PY_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
    > "$LOG_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!
  echo "后端 PID: $BACKEND_PID（日志: logs/backend.log）"
  echo -n "等待后端就绪"
  for i in $(seq 1 30); do
    curl -s -o /dev/null -m 1 http://localhost:8000/docs && { echo -e "\n${GREEN}✓ 后端已就绪: http://localhost:8000/docs${NC}"; return; }
    echo -n "."; sleep 1
  done
  echo -e "${RED}✗ 后端 30 秒内未就绪，查看日志: logs/backend.log${NC}"
}

start_frontend() {
  echo -e "\n${BLUE}══════════ 启动前端 (Vite :5175) ══════════${NC}"
  if ! check_port_free 5175; then return; fi
  cd "$FRONTEND_DIR"
  if [ ! -d node_modules ]; then
    echo -e "${YELLOW}未发现 node_modules，安装依赖...${NC}"
    npm install --silent
  fi
  nohup npx vite --port 5175 --host \
    > "$LOG_DIR/frontend.log" 2>&1 &
  FRONTEND_PID=$!
  echo "前端 PID: $FRONTEND_PID（日志: logs/frontend.log）"
  echo -n "等待前端就绪"
  for i in $(seq 1 30); do
    # vite 配置了 https（自签证书），http/https 都探测
    code_http=$(curl -s -o /dev/null -m 1 -w "%{http_code}" http://localhost:5175 2>/dev/null)
    code_https=$(curl -sk -o /dev/null -m 1 -w "%{http_code}" https://localhost:5175 2>/dev/null)
    if [ "$code_http" = "200" ] || [ "$code_https" = "200" ]; then
      echo -e "\n${GREEN}✓ 前端已就绪: https://localhost:5175${NC}"
      return
    fi
    echo -n "."; sleep 1
  done
  echo -e "\n${RED}✗ 前端 30 秒内未就绪，查看日志: logs/frontend.log${NC}"
}

show_result() {
  echo -e "\n${BLUE}══════════════════════════════════════${NC}"
  echo -e "${GREEN}  ✅ 启动完成${NC}"
  echo -e "  前端页面 : http://localhost:5175"
  echo -e "  后端接口 : http://localhost:8000/docs"
  echo -e "  停止服务 : ./stop.sh"
  echo -e "${BLUE}══════════════════════════════════════${NC}"
}

# ---------- 主流程 ----------
case "${1:-all}" in
  backend)  start_backend ;;
  frontend) start_frontend ;;
  all)      start_backend; start_frontend; show_result ;;
  *) echo "用法: $0 [all|backend|frontend]"; exit 1 ;;
esac
