# 低空应急智能体 - 前端

Vue 3 + Vite + Element Plus + Tailwind CSS 项目。

## 启动

```bash
npm install
```

### 本地开发（HTTP）

开发环境如果本机没有 HTTPS 证书，使用 HTTP 模式：

```bash
npm run dev:http
# 浏览器访问 http://localhost:5175
```

### 服务器 / 生产（HTTPS）

服务器配置了证书后，使用默认 HTTPS 模式：

```bash
npm run dev        # 开发调试 HTTPS
npm run build      # 打包生产文件
npm run preview    # 预览打包结果
```

### 原理

`vite.config.js` 通过环境变量自动切换：

```js
https: process.env.VITE_HTTP === 'true' ? false : {
  cert: fs.readFileSync(...),
  key: fs.readFileSync(...),
},
```

- `npm run dev:http` → 注入 `VITE_HTTP=true` → Vite 以 HTTP 启动（本地友好）
- `npm run dev` 等其他脚本 → 未设置该环境变量 → Vite 以 HTTPS + 证书启动（服务器友好）

**推送到 GitHub 时 `vite.config.js` 原样保留，不会因为开发环境改动而影响服务器。**

## 目录结构

```
src/
├── assets/          # 静态资源
├── components/      # 公共组件（含路径规划 TopBar、ControlPanel 等）
├── router/          # 路由
├── stores/          # Pinia 状态
├── views/           # 页面视图
│   ├── agents/      # 路径规划智能体页面
│   └── evaluation/  # 教学智评页面（Section4Live 大屏 / Section4Student 学生端）
├── App.vue
└── main.js
```

## 关键页面

| 路由 | 文件 | 说明 |
|---|---|---|
| `/agents/pathPlanning` | views/agents/PathPlanningAgentView.vue | 路径规划智能体大屏（顶部 Tab + 左侧控制面板 + 背景地图） |
| `/evaluation/task4` | views/evaluation/Section4Live.vue | 教学智评任务4大屏（6组实时视频流 + AI检查） |
| `/evaluation/task4/student?group=N` | views/evaluation/Section4Student.vue | 学生端单组页面（扫码进入，开启摄像头，画面实时推流到大屏） |
