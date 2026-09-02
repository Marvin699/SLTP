"""小翼智能体：基于 pydantic-ai 的工具调用 Agent

设计原则（安全边界）：
- 所有工具只读，不提供任何增删改
- 数据归属强制取自 deps 中解析好的当前登录用户（JWT），模型无法伪造身份
- 跨学生/班级查询工具内部校验教师角色
- request_limit 限制单次问答的模型往返轮数，防止循环烧 token
"""
import json
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import llm_service
from app.models.user import User
from app.models.optimizer import OptimizationRecord
from app.models.report import ReportRecord
from app.models.verification import VerificationRecord
from app.models.activity_log import ActivityLog
from app.models.debate import DebateSession


@dataclass
class WingDeps:
    """每请求注入的运行时上下文：身份与数据库会话"""
    db: Session
    user: User


# ─── 内置手册知识库（search_manual 数据源，T11 手册页共用一份内容） ───
MANUAL_ENTRIES = [
    {"title": "学生流程 · 四步向导", "content": "①案例与配送点：加载灾害案例、编辑需求点、用「灾情参数推算」按人口×人均日消耗×保障时长推算物资总需求并校准分配。②物资与选型：给需求点勾选物资类别与数量、设置冷链时限、选无人机机型。③规划与诊断：选择计算档位（快速/标准/精细）运行蚁群算法路径规划，查看四维评分与合规核验。④辩论与优出：反向质询四阶段（假设→验证→反驳→重构），生成最终方案报告。"},
    {"title": "学生流程 · 灾情参数与物资校准", "content": "在步骤①展开「灾情参数推算」，填写受灾人口、人均日消耗、保障时长，系统自动算出物资总需求并实时显示分配差距（缺口红色/超配橙色/满足绿色）。点「校准」先预览各需求点数量变化（按比例缩放，不改物资种类），确认后生效。"},
    {"title": "学生流程 · 合规核验", "content": "步骤③生成方案后进入合规核验：先对学生自判 14 项指标（空域、气象、载重、航程、冷链、时效、经济），提交引擎复核；系统高亮学生判断与引擎结论的差异并计算一致率，帮助建立规范意识。"},
    {"title": "学生流程 · 反向质询辩论", "content": "步骤④创建辩论会话后，AI 导师按四阶段追问：假设提出→验证分析→反驳交锋→重构优化。可勾选评判维度（安全性/时效性/经济性等）和置信度。教师可介入留言（刷新页面可见）。完成后生成最终结论。"},
    {"title": "学生流程 · 多方案对比择优", "content": "生成多个方案报告后，在报告库中勾选 2-3 个方案对比四维评分（安全/时效/经济/可行）、总距离、趟次、耗时，选定最终方案并填写择优理由，标记为「已择优」。"},
    {"title": "学生流程 · 计算档位", "content": "步骤③规划区可选三档：快速⚡（30蚂蚁/50迭代，几秒出结果，课堂演示推荐）、标准（30蚂蚁/100迭代）、精细🎯（80蚂蚁/200迭代，约1-2分钟，追求方案质量时用）。档位选择会自动记住。"},
    {"title": "教师流程 · 信息管理", "content": "智能体页面右上角「🗂 信息管理」可进入管理页：案例管理（新建/编辑灾害案例、配送中心与需求点、物资模板、Excel 导入导出）和机型库管理（新建/编辑/删除无人机机型，学生选型列表实时更新）。"},
    {"title": "教师流程 · 教学监控台", "content": "教学智评的监控台包含：班级总览、学生核验记录（合规得分与差异）、反向质询回放（可查看辩论全程并以教师身份留言介入）、学习时间线（每个学生的方案生成/报告生成/核验/择优/质询全流程动作记录）。"},
    {"title": "教师流程 · 学情画像", "content": "学情画像整合学生的方案数据、核验差异、辩论表现和学习动作，生成个人薄弱点评语与班级共性薄弱项报告，辅助教师调整课堂讲解重点（航线约束识别/装载合规/突发处置）。"},
    {"title": "教师流程 · AI方案点评", "content": "课中环节一「智能体评分」选两组后进入 AI 分析页，右上角可切换「演示数据 / 真实方案」。真实方案模式会读取学生课前方案的四维评分与辩论数据，由大模型生成词云、风险提示和综合点评；模型限流时自动降级为规则化点评。"},
    {"title": "常见问题 · 账号密码", "content": "学生账号为姓名、初始密码 123456，首次登录建议修改。忘记密码请联系教师重置。教师账号由管理员维护。"},
    {"title": "常见问题 · 数据保存", "content": "案例、方案、报告、辩论记录、核验记录均保存在服务器数据库；页面上填写的部分参数（如灾情参数、计算档位）保存在浏览器 localStorage，清空浏览器数据会丢失。切换案例会重置上一案例的分配与规划结果。"},
]

TOOL_LABELS = {
    "get_my_plan": "查询我的方案",
    "get_my_verification": "查询合规核验",
    "get_my_stats": "查询学习统计",
    "search_manual": "检索使用手册",
    "get_student_overview": "查询学生画像",
    "get_class_report": "生成班级报告",
}

# Agent 实例缓存（key: (base_url, model, api_key前8位)），避免每请求重复构建
_AGENT_CACHE = {}

SYSTEM_PROMPT = (
    "你是智慧低空应急运输教学平台的 AI 助教「小翼」，一名无人机应急物流领域的教学辅导专家。"
    "你的学生正在学习：灾害案例配置→灾情参数推算→物资分配→无人机选型→蚁群算法路径规划→合规核验→反向质询辩论→方案择优的完整流程。"
    "回答规则："
    "1. 涉及『我的方案/我的成绩/我的核验/平台怎么用』等个人数据或平台操作问题时，必须先调用工具查询真实数据，再基于数据回答，禁止编造数字；"
    "2. 涉及概念原理的问题（如什么是载重匹配、蚁群算法原理）直接讲解，不用调工具；"
    "3. 回答用简洁专业的中文，多用条目和数字，必要时给出改进建议；"
    "4. 你的角色是引导思考的助教，不直接替学生写结论，可以反问引导。"
)

TEACHER_PROMPT = (
    " 当前提问者是教师，你可以使用 get_student_overview 和 get_class_report 查询任意学生的画像与班级共性报告，"
    "回答侧重教学诊断与教学建议。"
)


def _get_latest_plan(db: Session, user_id: int) -> dict:
    """最新方案 + 四维评分（供学生自查与教师画像复用）"""
    plan: Optional[OptimizationRecord] = (
        db.query(OptimizationRecord)
        .filter(OptimizationRecord.user_id == user_id)
        .order_by(OptimizationRecord.id.desc())
        .first()
    )
    if not plan:
        return {"has_plan": False, "hint": "该学生还没有生成过路径规划方案"}

    report: Optional[ReportRecord] = (
        db.query(ReportRecord)
        .filter(ReportRecord.user_id == user_id)
        .order_by(ReportRecord.id.desc())
        .first()
    )
    scores = {}
    if report and report.report_data:
        try:
            scores = json.loads(report.report_data).get("scores", {})
        except Exception:
            scores = {}

    return {
        "has_plan": True,
        "created_at": plan.created_at.strftime("%m-%d %H:%M") if plan.created_at else None,
        "total_distance_km": round(plan.total_distance or 0, 1),
        "total_trips": plan.total_trips,
        "drone_count": plan.drone_count,
        "village_count": plan.village_count,
        "total_energy": round(plan.total_energy or 0, 1),
        "four_dim_scores": scores,
        "is_chosen": bool(report.is_chosen) if report else False,
    }


def _get_verification_summary(db: Session, user_id: int) -> dict:
    """最近一次合规核验摘要 + 未通过项"""
    v: Optional[VerificationRecord] = (
        db.query(VerificationRecord)
        .filter(VerificationRecord.user_id == user_id)
        .order_by(VerificationRecord.id.desc())
        .first()
    )
    if not v:
        return {"has_verification": False, "hint": "还没有提交过合规核验"}

    weak_items = []
    try:
        items = json.loads(v.checklist or "[]")
        for it in items:
            eng = it.get("engine_judgment")
            if eng in ("fail", "warn"):
                weak_items.append({"metric": it.get("metric"), "engine": eng})
    except Exception:
        pass

    return {
        "has_verification": True,
        "created_at": v.created_at.strftime("%m-%d %H:%M") if v.created_at else None,
        "verdict": v.verdict,
        "score": round(v.score or 0, 1),
        "consistency_pct": round(v.consistency or 0, 1),
        "mismatch_count": v.mismatch_count,
        "engine_failed_items": weak_items[:6],
    }


def _get_stats(db: Session, user_id: int) -> dict:
    """学习动作统计 + 辩论进度"""
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).all()
    by_action = {}
    for lg in logs:
        by_action[lg.action] = by_action.get(lg.action, 0) + 1

    sessions = (
        db.query(DebateSession)
        .filter(DebateSession.user_id == user_id)
        .order_by(DebateSession.id.desc())
        .limit(3)
        .all()
    )
    debates = [
        {"stage": s.stage, "status": s.status, "group": s.group_name or f"会话#{s.id}"}
        for s in sessions
    ]
    return {"total_actions": len(logs), "actions": by_action, "debate_sessions": debates}


def _require_teacher(deps: "WingDeps") -> Optional[dict]:
    if deps.user.role != "teacher":
        return {"error": "该工具仅教师可用"}
    return None


def build_agent(cfg: dict):
    """构建小翼 Agent（按模型配置缓存；cfg 来自 llm_service.get_model_chain）"""
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    if not cfg.get("api_key"):
        return None

    cache_key = (cfg["base_url"], cfg["model"], cfg["api_key"][:8])
    if cache_key in _AGENT_CACHE:
        return _AGENT_CACHE[cache_key]

    agent = Agent(
        OpenAIChatModel(
            cfg["model"],
            provider=OpenAIProvider(base_url=cfg["base_url"], api_key=cfg["api_key"]),
        ),
        deps_type=WingDeps,
        system_prompt=SYSTEM_PROMPT,
        retries=1,
    )

    @agent.system_prompt
    def role_prompt(ctx: RunContext[WingDeps]) -> str:
        """按角色动态追加提示词：教师开放跨学生查询的引导"""
        return TEACHER_PROMPT if ctx.deps.user.role == "teacher" else ""

    # ── 学生工具（全员可用，数据强制取当前登录人） ──

    @agent.tool
    def get_my_plan(ctx: RunContext[WingDeps]) -> dict:
        """查询当前登录学生最新的路径规划方案：距离/趟次/机数/需求点/四维评分/是否择优"""
        return _get_latest_plan(ctx.deps.db, ctx.deps.user.id)

    @agent.tool
    def get_my_verification(ctx: RunContext[WingDeps]) -> dict:
        """查询当前登录学生最近一次合规核验：得分/一致率/未通过项"""
        return _get_verification_summary(ctx.deps.db, ctx.deps.user.id)

    @agent.tool
    def get_my_stats(ctx: RunContext[WingDeps]) -> dict:
        """查询当前登录学生的学习动作统计与辩论进度"""
        return _get_stats(ctx.deps.db, ctx.deps.user.id)

    @agent.tool
    def search_manual(ctx: RunContext[WingDeps], keyword: str) -> dict:
        """检索平台使用手册。keyword：中文关键词，如 校准、核验、档位、监控、密码"""
        kw = (keyword or "").strip()
        hits = [
            e for e in MANUAL_ENTRIES
            if kw in e["title"] or kw in e["content"]
        ] if kw else []
        if not hits:  # 兜底：模糊匹配任一字
            hits = [e for e in MANUAL_ENTRIES if kw and any(ch in e["content"] for ch in kw)]
        return {"results": [{"title": e["title"], "content": e["content"][:300]} for e in hits[:3]]}

    # ── 教师专属工具（内部校验角色） ──

    @agent.tool
    def get_student_overview(ctx: RunContext[WingDeps], student_name: str) -> dict:
        """（仅教师）查询指定学生的学情画像：方案/评分/核验/动作统计。student_name 为学生姓名"""
        denied = _require_teacher(ctx.deps)
        if denied:
            return denied
        db = ctx.deps.db
        stu: Optional[User] = (
            db.query(User)
            .filter(User.role == "student", User.is_active == True)  # noqa: E712
            .filter((User.username.contains(student_name)) | (User.student_no.contains(student_name)))
            .first()
        )
        if not stu:
            return {"error": f"未找到学生「{student_name}」"}
        return {
            "student": stu.username,
            "class_name": stu.class_name,
            "group_no": stu.group_no,
            "plan": _get_latest_plan(db, stu.id),
            "verification": _get_verification_summary(db, stu.id),
            "stats": _get_stats(db, stu.id),
        }

    @agent.tool
    def get_class_report(ctx: RunContext[WingDeps]) -> dict:
        """（仅教师）生成班级共性报告：各学生方案/核验概览与高频薄弱项"""
        denied = _require_teacher(ctx.deps)
        if denied:
            return denied
        db = ctx.deps.db
        students = db.query(User).filter(User.role == "student", User.is_active == True).all()  # noqa: E712
        rows, weak_counter = [], {}
        for s in students[:50]:
            plan = db.query(OptimizationRecord).filter(OptimizationRecord.user_id == s.id).count()
            v: Optional[VerificationRecord] = (
                db.query(VerificationRecord)
                .filter(VerificationRecord.user_id == s.id)
                .order_by(VerificationRecord.id.desc())
                .first()
            )
            row = {"name": s.username, "plans": plan, "verify_score": None, "verdict": None}
            if v:
                row["verify_score"] = round(v.score or 0, 1)
                row["verdict"] = v.verdict
                try:
                    for it in json.loads(v.checklist or "[]"):
                        if it.get("engine_judgment") == "fail":
                            key = it.get("metric", "")
                            weak_counter[key] = weak_counter.get(key, 0) + 1
                except Exception:
                    pass
            rows.append(row)
        weak_top = sorted(weak_counter.items(), key=lambda kv: -kv[1])[:5]
        return {
            "student_count": len(students),
            "per_student": rows,
            "common_weak_items": [{"metric": k, "fail_count": n} for k, n in weak_top],
        }

    _AGENT_CACHE[cache_key] = agent
    return agent


async def run_wing_chat(messages: list, user: User, db: Session) -> dict:
    """主入口：带工具的小翼问答。

    messages: 前端历史 + 本轮消息（最后一条为 user 提问）
    返回 {success, reply, tools_used}；异常时抛出由调用方降级。
    """
    from pydantic_ai.messages import (
        ModelRequest,
        ModelResponse,
        ToolCallPart,
        UserPromptPart,
        TextPart,
    )
    from pydantic_ai.usage import UsageLimits

    # 模型调用链故障切换：主模型失败（429/超时/异常）自动尝试备用模型
    chain = [c for c in llm_service.get_model_chain()]
    if not chain:
        raise RuntimeError("LLM 未配置")

    history = []
    for m in messages[:-1][-10:]:  # 最多带 10 轮历史，防 token 膨胀
        if m["role"] == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=m["content"])]))
        elif m["role"] == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=m["content"])]))

    deps = WingDeps(db=db, user=user)
    last_err = None
    for i, cfg in enumerate(chain):
        agent = build_agent(cfg)
        if agent is None:
            continue
        tag = cfg["model"] if i == 0 else f"{cfg['model']}(备用#{i})"
        try:
            print(f"[小翼] 开始调用 {tag}...")
            result = await agent.run(
                messages[-1]["content"],
                deps=deps,
                message_history=history,
                usage_limits=UsageLimits(request_limit=8),
            )
        except Exception as e:
            last_err = e
            print(f"[小翼] {tag} 调用异常: {type(e).__name__}: {e}")
            if i < len(chain) - 1:
                print(f"[小翼] 自动切换到下一个备用模型...")
            continue

        # 提取本轮实际用过的工具（前端展示"小翼查询了什么"）
        tools_used = []
        for m in result.all_messages():
            if isinstance(m, ModelResponse):
                for p in m.parts:
                    if isinstance(p, ToolCallPart):
                        label = TOOL_LABELS.get(p.tool_name)
                        if label and label not in tools_used:
                            tools_used.append(label)

        return {"success": True, "reply": result.output, "tools_used": tools_used}

    raise RuntimeError(f"小翼调用失败（含备用模型共 {len(chain)} 个均不可用）: {str(last_err)}")
