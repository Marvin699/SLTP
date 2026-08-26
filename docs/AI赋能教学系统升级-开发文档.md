# AI 赋能教学系统功能升级 — 开发文档

> 版本：v1.0（规划稿）
> 日期：2026-06-12
> 依据：甲方《AI赋能教学系统功能升级方案》（"人机双向奔赴"教学理念）
> 状态：规划阶段，尚未开始编码

---

## 一、项目现状盘点（截至 2026-08-07，commit `4321f74`）

### 1.1 前端路径规划智能体（`frontend/src/views/agents/pathPlanning/`）

| 模块 | 功能 | 与升级方案的关系 |
|------|------|----------------|
| Module1 | 需求点管理、案例加载、坐标表、距离矩阵 | 灾情参数输入的基础（部分可复用） |
| Module2 | 物资配置、配送点匹配 | 消耗系数推算物资量的基础 |
| Module3 | 无人机选型 + AI 智能选型（含展览模式） | 约束条件（载重/续航）已有载体 |
| Module4 | **ACO 蚁群算法路径规划**，参数面板已开放（蚂蚁数、迭代次数、α、β、ρ 挥发率、精英蚂蚁数） | "参数调整重新生成方案"**已具备** |
| Module5 | 方案诊断（规则诊断 + AI 诊断，四维评分：安全/时效/经济/可行，含展览模式） | "合理性评分系统"**已具备**，可作核验引擎复用 |
| Module6 | 方案报告库、**2 方案对比**（核心指标 + 四维分数）、报告预览 | "多方案管理"有基础，需扩展 |
| Module7 | 案例管理（CSV 导入导出、模板） | — |
| Module11 | 应急调度智能体图片管理 | — |

### 1.2 后端（`backend/app/`）

| 能力 | 现状 | 位置 |
|------|------|------|
| ACO 优化 | `/api/optimizer/run`，`OptimizeRequest` 支持 `aco_params`，同步计算 | `api/routes/optimizer.py` |
| 方案持久化 | `OptimizationRecord`（任务配置、方案数据、ACO 参数、结果摘要、总距离/能耗/趟次） | `models/optimizer.py` |
| 报告 | `Report` 模型 + `/api/report` | `models/report.py` |
| 诊断 | `Diagnosis` 模型 + `/api/diagnosis`，四维评分 | `models/diagnosis.py` |
| AI 对话 | `/api/ai-chat/chat`（DeepSeek，OpenAI 兼容），`ChatHistory` 仅存 user_id/role/content | `api/routes/ai_chat.py` |
| 用户系统 | JWT 登录/注册/改密、教师端学生管理（08-07 新增） | `api/routes/auth.py`、`views/system/StudentManage.vue` |
| LLM 基础服务 | 通用 LLM 调用封装（支持 reasoning 回退） | `services/llm_service.py` |

### 1.3 教学智评（课中，`frontend/src/views/evaluation/`）

- 环节一：运输方案汇报与知识深化（小组汇报、AI 词云与风险分析）
- 环节二：应急推演与工单处置（工单三要素、AI 综合质量分）
- 环节三：飞行演练与裁判评分（`ScoreSession` 模型）
- `AiAnalysisView.vue`：AI 助教方案点评（词云 + 静态评语）

### 1.4 现状结论

**已具备（约 40%）**：ACO 动态方案生成、参数可调重生成、四维评分诊断、方案库与 2 方案对比、AI 问答、用户体系。

**完全缺失（约 60%）**：反向质询/辩论交互、评判逻辑记录、合规性核验工具、深度学习闭环（假设-验证-反驳-重构）、课前→课中数据贯通、教师端监控/干预/思辨评估、全流程交互日志。

---

## 二、差距分析（升级方案 → 开发任务映射）

| # | 升级方案条目 | 现状 | 差距等级 | 对应开发任务 |
|---|------------|------|---------|------------|
| 1 | 课前·动态方案生成（灾情参数 + 6 类约束） | ACO 已有；载重/续航/禁飞区部分覆盖 | 🟡 增强 | T1 |
| 2 | 课前·多方案管理（保存/对比/重生成方案库） | 报告库 + 2 方案对比 | 🟡 增强 | T2 |
| 3 | 课中·反向质询（AI 辩论伙伴、追问、评判记录） | 无，仅单向问答 | 🔴 全新 | T3 |
| 4 | 课中·参数调整重生成 | Module4 参数面板已有 | 🟢 打通 | T2 |
| 5 | 课中·多方案对比 + 择优决策 | 2 方案对比，无择优 | 🟡 增强 | T2 |
| 6 | 新增·合规性核验工具（模板+指标+检查流程） | 无 | 🔴 全新 | T4 |
| 7 | 新增·深度学习闭环（假设-验证-反驳-重构） | 无 | 🔴 全新 | T3 |
| 8 | 整合·课前课中贯通 | 课中环节未引用课前方案 | 🔴 全新 | T5 |
| 9 | 教师·核验监控面板 | 无 | 🔴 全新 | T6 |
| 10 | 教师·质询干预机制 | 无 | 🔴 全新 | T6 |
| 11 | 教师·思辨能力评估 dashboard | 无（有 ScoreSession 可复用） | 🔴 全新 | T6 |
| 12 | 架构·实时计算/并发 | 同步计算，此前因慢加过展览模式 | 🟡 优化 | T7 |
| 13 | 架构·交互日志系统 | ChatHistory 仅对话内容 | 🔴 全新 | T8 |

---

## 三、开发任务拆解（按四期推进）

### 第一期 · 课中核心：反向质询 + 深度学习闭环（T3、T7 部分）

> 甲方核心理念"人机双向奔赴"的载体，优先级最高。

#### T3.1 数据层：辩论会话与评判逻辑记录（新表）

```
backend/app/models/debate.py
├─ DebateSession（辩论会话）
│   id / user_id / case_id / plan_record_id(关联 OptimizationRecord)
│   stage: hypothesis|verify|rebut|rebuild（四阶段）
│   status: active|completed
│   final_choice_plan_id（最终择优方案）
│   created_at / updated_at
└─ DebateMessage（辩论消息，比 ChatHistory 多结构化字段）
    id / session_id / role: student|ai|teacher
    content（原文）
    judgment_logic（学生评判依据，结构化 JSON：维度、理由、置信度）
    challenge_type（AI 追问类型：assumption|risk|alternative|standard）
    created_at
```

#### T3.2 后端：辩论引擎路由（新路由，复用 llm_service）

```
backend/app/api/routes/debate.py
├─ POST /api/debate/session          创建辩论会话（绑定方案）
├─ POST /api/debate/challenge        AI 追问：输入学生评判逻辑 →
│                                     LLM 以"辩论伙伴"角色生成针对性追问
│                                     system_prompt 定位：不给答案、只质询依据
├─ POST /api/debate/rebut            学生反驳/重构提交
├─ GET  /api/debate/session/{id}     会话回放（四阶段时间线）
└─ POST /api/debate/teacher-note     教师介入留言（三期用，先留接口）
```

追问策略（system_prompt 工程，无新算法）：
- 假设质询："你假设风速不变，依据是什么？"
- 风险质询："若 #D03 延迟 10min，你的方案哪个环节最先失效？"
- 替代质询："β 从 3 调到 5 就能改善时效吗？有没有副作用？"
- 标准质询："该结论对照哪条合规指标？"

#### T3.3 前端：辩论交互界面（新页面）

```
frontend/src/views/agents/pathPlanning/DebateRoom.vue（或 evaluation 下）
├─ 左：方案卡片（从方案库选择，展示四维分数）
├─ 中：对话流（学生陈述 → AI 追问 → 学生反驳），带阶段进度条
│       假设 → 验证 → 反驳 → 重构（四节点可视化）
└─ 右：评判逻辑记录面板（学生勾选评判维度 + 填写依据，自动入 DebateMessage.judgment_logic）
```

路由 + 路径规划智能体侧边导航新增"反向质询"入口。

### 第二期 · 课前迭代闭环：核验 + 对比 + 重生成（T1、T2、T4）

#### T4.1 合规性核验工具

```
数据层：backend/app/models/verification.py
└─ VerificationRecord（核验记录）
    id / user_id / plan_record_id
    checklist: JSON（每项：指标名/标准值/学生判定 pass|fail|na/备注）
    score（合规得分）/ verdict
    created_at

后端：backend/app/api/routes/verification.py
├─ GET  /api/verification/template    下发核验模板（标准模板：空域/气象/载重/
│                                     续航/冷链/时效/经济 7 组指标）
├─ POST /api/verification/check       提交学生核验结果（服务端复用 Diagnosis
│                                     引擎交叉校验，标记"学生判定 vs 引擎判定"差异）
└─ GET  /api/verification/records     核验历史（供教师端三期用）

前端：Module5 旁新增"合规核验"Tab 或新 Module
├─ 核验清单（勾选 + 备注 + 差异高亮）
└─ 核验得分 + "基于核验结果重新生成"按钮 → 跳 Module4 并回填建议参数
```

#### T2.1 多方案对比增强（改 Module6）

- 对比数量：2 → 最多 4（前端 compareData 结构从 report1/2 改数组）
- 新增"择优决策"：对比面板加"选定此方案"按钮 → 写入 `OptimizationRecord.is_chosen` 或新字段，并记录决策理由
- 新增"从此方案派生重生成"：对比项一键 → Module4 回填该方案 ACO 参数

#### T1.1 灾情参数与约束增强（改 Module1/Module4）

- Module1 增加"灾情参数卡"：受灾人口、人均消耗系数、保障时长 → 自动推算物资需求（现有物资配置前置推导）
- Module4 增加约束展示区：空域（禁飞区已有）、气象（风速/降水输入）、载重（选型联动）、续航、冷链时限（新增温控物资时效字段，超时预警）

### 第三期 · 教师端：监控 + 干预 + 评估（T6、T8）

#### T6.1 教师监控面板（新页面组）

```
frontend/src/views/teacher/（新目录）
├─ Dashboard.vue      总览：各学生/小组方案数、核验通过率、辩论参与度
├─ VerifyMonitor.vue  方案核验监控：实时核验过程（轮询/WebSocket）、
│                     教师干预（下发提示、标记优秀）
├─ DebateMonitor.vue  质询监控：辩论时间线回放、教师介入留言
│                     （调 T3.2 预留的 /teacher-note 接口）
└─ Assessment.vue     思辨能力评估：基于评判逻辑质量 + 核验差异率 +
                      反驳深度（LLM 打分）生成报告，教学效果分析图表
```

权限：复用 08-07 新增的 JWT 用户体系（role=teacher）。

#### T8.1 交互日志系统

```
backend/app/models/activity_log.py
└─ ActivityLog：id / user_id / action(方案生成|参数调整|核验|对比|辩论|择优)
    / payload JSON / plan_record_id / created_at
```
后端在 optimizer/verification/debate/report 路由统一埋点（FastAPI middleware + 显式调用）。

### 第四期 · 架构升级（T7、T5）

#### T7.1 计算性能与并发

- 现状：`/api/optimizer/run` 同步阻塞，迭代次数大时响应慢（此前因此做过展览模式）
- 方案：
  1. 参数预设档位（快速/标准/精细，前端默认"快速"：迭代 ≤ 50）
  2. `run_in_executor` 线程池化，避免阻塞事件循环（FastAPI `def` 路由自动线程池，成本最低）
  3. 如仍慢：任务表 + 前端轮询（`OptimizationRecord` 加 status 字段）
- 并发：SQLite → 如多教师同时用，评估切 PostgreSQL（`config.py` 已有 DATABASE_URL 可切换）

#### T5.1 课前课中贯通

- 环节一"方案汇报"页面接入方案库（`OptimizationRecord` 列表），学生汇报时直接引用课前方案四维分数与航线图
- `AiAnalysisView` 的静态评语 → 改为读取真实方案的 Diagnosis + Debate 数据生成
- 数据连续性：case_id + user_id 贯穿（方案 → 核验 → 辩论 → 择优 → 课中汇报 → 课后报告）

---

## 四、接口与数据流总览

```
课前（路径规划智能体）
  灾情参数 ──► ACO 生成方案 ──► OptimizationRecord（方案库）
       ▲                              │
       └── 参数回填（α/β/ρ）◄── T4 核验 / T2 对比择优（迭代闭环）
                                      │
课中（教学智评）                        ▼
  环节一：方案汇报 ←── 方案库引用（T5）
  反向质询辩论室 ←── DebateSession/Messages（T3：假设→验证→反驳→重构）
  环节二/三：应急推演 / 飞行演练（已有）
                                      │
教师端（T6）                            ▼
  核验监控 / 质询干预 / 思辨评估 dashboard ←── ActivityLog（T8）+ 各业务表
```

---

## 五、里程碑建议

| 阶段 | 内容 | 交付物 |
|------|------|--------|
| M1 | T3 反向质询 + 闭环四阶段 UI + DebateRoom | 可演示的"AI 辩论伙伴"课中流程 |
| M2 | T4 合规核验 + T2 对比择优 + T1 约束增强 | 课前迭代闭环完整 |
| M3 | T6 教师端三面板 + T8 日志 | 教学监控能力 |
| M4 | T7 性能/并发 + T5 课前课中贯通 | 全流程贯通 + 稳定性 |

依赖关系：T3/T4 无相互依赖可并行；T6 依赖 T3/T4/T8 的数据；T5 依赖方案库字段稳定。

---

## 六、风险与决策点（需与甲方/团队确认）

1. **LLM 追问质量**：DeepSeek 辩论式 system_prompt 需调优，建议先做 prompt 实验（1 天）再定交互细节
2. **SQLite 并发**：课堂几十人同时辩论/核验，写压力可控，但 optimizer 并发需实测
3. **课中环节一现有评分维度是否要纳入辩论数据**（方案完整性 0.35 权重是否调整）
4. **旧方案数据兼容**：OptimizationRecord 新增字段需允许 NULL，不影响存量
5. **工期**：M1+M2 为核心可演示范围，M3/M4 可视排期压缩
