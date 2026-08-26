#!/bin/bash
# 智慧低空应急运输教学平台 - 一键停止脚本（macOS）
# 用法: ./stop.sh            停止全部（前端+后端）
#       ./stop.sh backend    只停止后端 (8000)
#       ./stop.sh frontend   只停止前端 (5175)

cd "$(dirname "$0")"
GREEN='\033[0;32m'; YELLOW='\033[0;33m'; NC='\033[0m'

# 根据 $1 决定要停哪些端口
case "$1" in
  backend)  PORTS=(8000) ;;
  frontend) PORTS=(5175) ;;
  *)        PORTS=(8000 5175) ;;
esac

stopped=0

# 按端口杀（覆盖 uvicorn / vite / node）
for port in "${PORTS[@]}"; do
  pids=$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null)
  if [ -n "$pids" ]; then
    echo "停止端口 $port (PID: $(echo $pids | tr '\n' ' '))"
    kill $pids 2>/dev/null
    stopped=1
  fi
done

sleep 1

# 二次确认（对 kill 无响应的强杀）
for port in "${PORTS[@]}"; do
  pids=$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null)
  [ -n "$pids" ] && kill -9 $pids 2>/dev/null
done

if [ $stopped -eq 1 ]; then
  echo -e "${GREEN}✓ 已停止: ${PORTS[*]}${NC}"
else
  echo -e "${YELLOW}没有发现正在运行的服务（端口 ${PORTS[*]} 均空闲）${NC}"
fi
