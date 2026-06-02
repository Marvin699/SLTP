# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智慧低空应急运输教学平台 (Smart Low-Altitude Emergency Transportation Teaching Platform) — a Vue 3 + Django teaching platform for drone logistics courses. The project is in early-stage development with a frontend framework built out and backend as empty scaffolding.

**Core principle**: "Teaching" is the core. AI is an enhancement tool, not the main focus. Follow `开发参考文件.md` for architectural decisions.

## Development Commands

```bash
# Frontend (Vue 3 + Vite)
cd frontend
npm install --registry https://registry.npmmirror.com  # install deps (use China mirror)
npm run dev    # dev server on port 5175 (5174 is primary)
npm run build  # production build

# Agents have separate frontend/backend directories (currently empty scaffolding)
```

## Architecture

```
├── frontend/          # Vue 3 + Element Plus + ECharts + Pinia + Vue Router
├── backend/           # Django (empty scaffold, apps/ directory structure ready)
├── agents/            # 3 independent agents, each with own frontend/backend
│   ├── packing-agent/              # 装箱评价 (has reference React app + data files)
│   ├── path-planning-agent/        # 路径规划
│   └── teaching-graph-agent/       # 课程教学图谱
└── 开发参考文件.md      # System architecture spec (READ THIS before major decisions)
```

### Frontend Key Points

- **Vite config**: `@` alias → `./src/`, port 5174 (may fallback to 5175)
- **Entry**: `src/main.js` registers Element Plus, Pinia, Router globally
- **Layout**: `src/layouts/MainLayout.vue` wraps all main pages (top nav + content area)
- **Routes**: Main pages nested under `/` with MainLayout; agents at `/agent/*` as standalone pages
- **Styling**: Deep blue tech theme (`#0a1628` background), Element Plus dark overrides via `:deep()`

### Implemented Pages

| Page | File | Status |
|------|------|--------|
| Home dashboard | `views/home/index.vue` | Complete — 3-column layout, ECharts charts, AI assistant button |
| Teaching evaluation | `views/evaluation/index.vue` | Substantial — multi-role (teacher/student/expert), 5 evaluation dimensions |
| Course center, Training, Resources, System | `views/*/index.vue` | Placeholder only |
| 3 Agent pages | `views/agents/*.vue` | Placeholder with back button |

### Agent Data Files

Reference data for the teaching-graph agent lives in `agents/packing-agent/`:
- `四图谱数据v3.json` — Four-graph dataset (knowledge, capability, problem, ideological graphs)
- `应急物资无人机智慧运输_四图谱v3.xlsx` — Same data in Excel format
- `应急物资无人机图谱开发参考/` — Reference React app + data files + documentation

## Key Conventions

- All npm installs must use `--registry https://registry.npmmirror.com` (China mirror)
- Agent pages are independent from MainLayout — they have their own full-screen dark background
- Image files in `src/assets/images/` must use ASCII filenames only (no Chinese characters — Vite import error)
- Evaluation page supports 3 roles via `currentRole` ref: `teacher`, `student`, `expert`
- Business logic details must be confirmed with the user before implementation (per 开发参考文件.md)
