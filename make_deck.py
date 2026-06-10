from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

DARK_BG = RGBColor(0x06, 0x11, 0x1f)
ACCENT_BLUE = RGBColor(0x1a, 0x90, 0xff)
ACCENT_CYAN = RGBColor(0x00, 0xe5, 0xff)
ACCENT_GOLD = RGBColor(0xff, 0xb3, 0x00)
WHITE = RGBColor(0xff, 0xff, 0xff)
LIGHT_GRAY = RGBColor(0xcc, 0xd6, 0xe0)
SOFT_GRAY = RGBColor(0x9f, 0xac, 0xb8)

FONT_TITLE = "PingFang SC"
FONT_BODY = "PingFang SC"
FONT_MONO = "Menlo"

OUT = os.path.join(os.path.dirname(__file__), "低空应急智能运输_路演PPT_5分钟.pptx")


def blank_slide(prs):
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_top_bar(slide):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.08))
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT_BLUE


def add_bottom_bar(slide):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Inches(0.4), SLIDE_W, Inches(0.4)
    )
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0x0b, 0x1d, 0x32)

    left = slide.shapes.add_textbox(
        Inches(0.5), SLIDE_H - Inches(0.38), Inches(12), Inches(0.38)
    )
    tf = left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "智慧低空应急运输教学平台 · 5 分钟路演"
    run.font.size = Pt(10)
    run.font.color.rgb = SOFT_GRAY
    run.font.name = FONT_BODY
    p.alignment = PP_ALIGN.LEFT


def add_page_num(slide, n, total):
    tb = slide.shapes.add_textbox(
        SLIDE_W - Inches(1.2), SLIDE_H - Inches(0.38), Inches(1), Inches(0.38)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = f"{n} / {total}"
    run.font.size = Pt(10)
    run.font.color.rgb = SOFT_GRAY
    run.font.name = FONT_MONO
    p.alignment = PP_ALIGN.RIGHT


def add_heading(slide, title, subtitle=None, top=Inches(0.45)):
    tb = slide.shapes.add_textbox(Inches(0.65), top, Inches(12), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.size = Pt(32)
    run.font.bold = True
    run.font.color.rgb = WHITE
    run.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.LEFT

    if subtitle:
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size = Pt(13)
        r2.font.color.rgb = ACCENT_CYAN
        r2.font.name = FONT_BODY
        p2.alignment = PP_ALIGN.LEFT

    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.65), top + Inches(0.92), Inches(12), Inches(0.03)
    )
    line.line.fill.background()
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_BLUE


def add_card(slide, left, top, width, height, title, body_lines=None, accent=ACCENT_CYAN, bg=RGBColor(0x0c, 0x1f, 0x35)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.line.color.rgb = accent
    shape.line.width = Pt(1.2)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg

    accent_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height
    )
    accent_bar.line.fill.background()
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = accent

    tb = slide.shapes.add_textbox(left + Inches(0.28), top + Inches(0.12), width - Inches(0.34), height - Inches(0.18))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.space_before = Pt(0)
    r = p.add_run()
    r.text = title
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT_TITLE

    if body_lines:
        for line in body_lines:
            pp = tf.add_paragraph()
            pp.space_before = Pt(4)
            rr = pp.add_run()
            rr.text = line
            rr.font.size = Pt(11)
            rr.font.color.rgb = LIGHT_GRAY
            rr.font.name = FONT_BODY
            pp.level = 0


def add_bullet(text_frame, text, color=LIGHT_GRAY, indent=False):
    p = text_frame.add_paragraph()
    r = p.add_run()
    r.text = text
    r.font.size = Pt(14)
    r.font.color.rgb = color
    r.font.name = FONT_BODY
    if indent:
        p.level = 1
    return p


def slide1_cover(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)

    add_top_bar(s)
    add_bottom_bar(s)
    add_page_num(s, 1, total)

    big = s.shapes.add_textbox(Inches(0.9), Inches(1.5), Inches(12), Inches(2))
    tf = big.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "智慧低空应急运输\n教学平台"
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT_TITLE
    r.font.shadow = True
    p.alignment = PP_ALIGN.LEFT

    tag = s.shapes.add_textbox(Inches(0.9), Inches(3.6), Inches(12), Inches(0.7))
    tf2 = tag.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    r2 = p2.add_run()
    r2.text = "AI × 无人机 · 路径规划 · 装箱优化 · 岗课赛证"
    r2.font.size = Pt(22)
    r2.font.color.rgb = ACCENT_CYAN
    r2.font.name = FONT_BODY

    sub = s.shapes.add_textbox(Inches(0.9), Inches(4.4), Inches(12), Inches(2))
    tf3 = sub.text_frame
    tf3.word_wrap = True

    for line in [
        "面向高职/本科 · 无人机物流 / 应急物流 / 智慧物流 专业",
        "把「低空经济 + AI + 应急」搬进课堂，做可落地的工程化实训",
    ]:
        p = tf3.add_paragraph()
        p.space_before = Pt(6)
        rr = p.add_run()
        rr.text = line
        rr.font.size = Pt(15)
        rr.font.color.rgb = LIGHT_GRAY
        rr.font.name = FONT_BODY

    foot = s.shapes.add_textbox(Inches(0.9), Inches(6.4), Inches(12), Inches(0.6))
    tf4 = foot.text_frame
    tf4.word_wrap = True
    labels = ["教学平台", "AI 智能体", "岗课赛证", "案例：渠洋村应急物资配送"]
    for i, lb in enumerate(labels):
        p = tf4.paragraphs[0] if i == 0 else tf4.add_paragraph()
        rr = p.add_run()
        rr.text = ("· " if i > 0 else "") + lb
        rr.font.size = Pt(12)
        rr.font.color.rgb = ACCENT_GOLD
        rr.font.name = FONT_MONO
        rr.font.bold = (i == 3)
        if i < 3:
            p.space_before = Pt(0)

    return s


def slide2_problem(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)
    add_heading(s, "痛点 · 为什么要做", "从真实应急救灾场景出发")

    card_x = Inches(0.55)
    card_top = Inches(1.7)
    card_w = Inches(4.0)
    card_h = Inches(3.6)
    gap = Inches(0.4)

    cards = [
        (
            "应急物流不只是「送过去」",
            [
                "灾区路毁、桥梁断，地面运输卡死。",
                "传统课堂只教理论，没有真实约束。",
                "学生不知道一架无人机飞几趟、带多少。",
            ],
            ACCENT_GOLD,
        ),
        (
            "低空经济的人才缺口",
            [
                "2025 年低空经济规模破 2 万亿。",
                "无人机物流 / 应急岗位爆发。",
                "但学校没有可实操的路径规划平台。",
            ],
            ACCENT_CYAN,
        ),
        (
            "AI 只是噱头？",
            [
                "不是！让 AI 当「实训助理 + 诊断老师」。",
                "蚁群算法 CVRP + 动态能耗模型。",
                "学生先做题，AI 再点评和打分。",
            ],
            ACCENT_BLUE,
        ),
    ]

    for i, (t, body, ac) in enumerate(cards):
        add_card(s, card_x + i * (card_w + gap), card_top, card_w, card_h, t, body, ac)

    add_bottom_bar(s)
    add_page_num(s, 2, total)
    return s


def slide3_what(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)
    add_heading(s, "平台是什么", "一个教学平台 + 三个独立 AI 智能体")

    left = s.shapes.add_textbox(Inches(0.65), Inches(1.7), Inches(4.7), Inches(5.2))
    tf = left.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "智慧低空应急运输教学平台"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = ACCENT_CYAN
    r.font.name = FONT_TITLE

    add_bullet(tf, "· 首页驾驶舱（ECharts 数据大屏）")
    add_bullet(tf, "· 课程中心 + 实训任务发布/提交")
    add_bullet(tf, "· 四主体教学智评（学生互评 / 教师 / 企业专家 / AI）")
    add_bullet(tf, "· 学习资源库（无人机规范 / 应急案例）")
    add_bullet(tf, "· 系统管理 + 统一登录鉴权")
    add_bullet(tf, "· AI 助教（浮窗）")

    agents_top = Inches(1.7)
    agents_left = Inches(5.6)
    agents_w = Inches(2.3)
    agents_h = Inches(2.2)
    gap_h = Inches(0.3)
    gap_v = Inches(0.4)

    agents = [
        ("路径规划", "CVRP 蚁群算法\n动态能耗 · 载重-航程\n渠洋村案例", ACCENT_CYAN),
        ("装箱评价", "空间利用率\n重量平衡\n安全评分", ACCENT_GOLD),
        ("课程图谱", "知识 / 能力 / 问题 / 思政 四图谱\n学习路径推荐", RGBColor(0x80, 0xcb, 0xff)),
    ]

    for i, (t, b, ac) in enumerate(agents):
        col = i % 3
        row = i // 3
        add_card(
            s,
            agents_left + col * (agents_w + gap_h),
            agents_top + row * (agents_h + gap_v),
            agents_w,
            agents_h,
            t,
            b.split("\n"),
            ac,
        )

    tag = s.shapes.add_textbox(Inches(5.6), agents_top + agents_h + gap_v, Inches(7), Inches(0.5))
    tf2 = tag.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    r2 = p2.add_run()
    r2.text = "每个智能体：独立前端 + 独立后端 + API 接入平台主系统"
    r2.font.size = Pt(11)
    r2.font.color.rgb = SOFT_GRAY
    r2.font.name = FONT_MONO
    r2.font.italic = True

    add_bottom_bar(s)
    add_page_num(s, 3, total)
    return s


def slide4_core(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)
    add_heading(s, "核心亮点 · 路径规划智能体", "工程化可运行的 CVRP 求解器")

    top = Inches(1.7)
    left1 = Inches(0.55)
    w1 = Inches(3.9)
    h1 = Inches(2.5)
    gap = Inches(0.4)

    add_card(
        s,
        left1 + 0 * (w1 + gap),
        top,
        w1,
        h1,
        "蚁群算法 CVRP",
        [
            "多无人机 · 多趟次 · 带时间窗/优先级",
            "目标函数 = 0.4 距离 + 0.3 能耗 + 0.2 优先级 + 0.1 负载均衡",
        ],
        ACCENT_CYAN,
    )

    add_card(
        s,
        left1 + 1 * (w1 + gap),
        top,
        w1,
        h1,
        "动态能耗模型",
        [
            "能耗 = 距离 × (1 + 当前载重 / 最大载重)",
            "满载去程能耗是空载返航的 2 倍",
            "载重→航程分段线性插值（0 kg 26 km / 80 kg 6 km）",
        ],
        ACCENT_GOLD,
    )

    add_card(
        s,
        left1 + 2 * (w1 + gap),
        top,
        w1,
        h1,
        "无人机型号库 + 任务规划 Agent",
        [
            "内置多种无人机参数（FC100 等）",
            "大模型驱动的无人机选型：重量 / 航程 / 抗风 / 冷链",
            "输出完整配送计划 + 可行性评分 + 风险预警",
        ],
        RGBColor(0x80, 0xcb, 0xff),
    )

    # Case study box
    case_top = top + h1 + Inches(0.5)
    case_left = Inches(0.55)
    case_w = Inches(5.8)
    case_h = Inches(4.5)

    add_card(
        s,
        case_left,
        case_top,
        case_w,
        case_h,
        "真实案例：广西渠洋村应急物资配送",
        [
            "配送中心：渠洋村",
            "需求点：怀渠 / 塘麻 / 坡乐 / 东风 / 古桥 / 新和 / 怀书 / 雅力 共 8 个村",
            "距离矩阵：已真实测算（最远村 ~27 km）",
            "物资类别：抢修 / 生活保障 / 医疗 / 冷链 / 安置保障",
            "",
            "→ 学生先完成 8 个实训模块（从布点、选机、规划、诊断、报告）",
            "→ AI 自动批改 + 生成 Word 报告 + 导出 GeoJSON 可在地图查看航线",
        ],
        ACCENT_CYAN,
        bg=RGBColor(0x0a, 0x24, 0x40),
    )

    arch_left = case_left + case_w + Inches(0.35)
    arch_w = Inches(6.2)
    arch_h = Inches(4.5)

    add_card(
        s,
        arch_left,
        case_top,
        arch_w,
        arch_h,
        "架构 · 单人可开发 · 学校可部署",
        [
            "前端  Vue 3 + Vite + Element Plus + Pinia + ECharts + 地图",
            "后端  Django + REST（路径规划引擎原生 Python）",
            "算法  原生蚁群 / 约束检查器 / 成本评估器 / GeoJSON · Excel 导出",
            "AI    支持 OpenAI / DeepSeek / 通义千问 / 本地模型（可切换）",
            "智能体接入方式：API + 独立 iframe（零耦合）",
            "一键生成实训报告（docx / pdf）",
            "",
            "路线：先跑通，再逐步升级",
        ],
        ACCENT_GOLD,
        bg=RGBColor(0x0a, 0x24, 0x40),
    )

    add_bottom_bar(s)
    add_page_num(s, 4, total)
    return s


def slide5_demo(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)
    add_heading(s, "5 分钟演示怎么跑", "讲者可以跟着这条故事线边操作边讲")

    steps = [
        ("① 首页驾驶舱", "登录 → 看学习/实训/AI 三大数据面板", ACCENT_CYAN),
        ("② 进路径规划 Agent", "模块一布点：渠洋村 + 8 个需求村", ACCENT_GOLD),
        ("③ 二-四模块", "录入物资需求（重量/优先级/冷链）→ 选无人机 → 跑蚁群算法", RGBColor(0x80, 0xcb, 0xff)),
        ("④ 方案看地图", "GeoJSON 航线 + 每架无人机 / 每趟距离载重能耗", ACCENT_CYAN),
        ("⑤ AI 诊断 + 报告", "AI 点评短板 → 一键导出配送计划报告（docx）", ACCENT_GOLD),
        ("⑥ 平台闭环", "实训提交 → 四主体评价 → 看自己的能力画像", WHITE),
    ]

    box_x = Inches(0.55)
    box_y = Inches(1.7)
    box_w = Inches(4.0)
    box_h = Inches(1.3)
    gap_x = Inches(0.4)
    gap_y = Inches(0.35)

    for i, (t, b, c) in enumerate(steps):
        col = i % 3
        row = i // 3
        add_card(
            s,
            box_x + col * (box_w + gap_x),
            box_y + row * (box_h + gap_y),
            box_w,
            box_h,
            t,
            [b],
            c,
        )

    add_bottom_bar(s)
    add_page_num(s, 5, total)
    return s


def slide6_values(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)
    add_heading(s, "价值主张", "对学生 · 对老师 · 对专业建设")

    col_w = Inches(3.9)
    gap = Inches(0.35)
    top = Inches(1.7)

    columns = [
        (
            "对学生",
            [
                "· 不是背公式，是亲手规划真实救灾航线",
                "· 从菜鸟「随便飞飞」到理解载重-航程非线性关系",
                "· 输出可就业的作品集（渠洋村案例）",
                "· 岗课赛证：准备 1+X 无人机物流证书",
            ],
            ACCENT_CYAN,
        ),
        (
            "对老师",
            [
                "· 备课素材 = 真实案例 + 真实数据",
                "· AI 助教 7×24 答疑 + 批改",
                "· 四主体评价形成教学闭环",
                "· 可作为比赛/创新创业项目的底座",
            ],
            ACCENT_GOLD,
        ),
        (
            "对专业",
            [
                "· 低空经济 / 应急物流 / 智慧物流 三方向通吃",
                "· 可扩展：新增集装箱装箱、多旋翼集群、禁飞区 …",
                "· 可申请教科研项目课题",
                "· 企业/行业专家可接入指导",
            ],
            RGBColor(0x80, 0xcb, 0xff),
        ),
    ]

    for i, (t, body, ac) in enumerate(columns):
        add_card(
            s,
            Inches(0.55) + i * (col_w + gap),
            top,
            col_w,
            Inches(4.5),
            t,
            body,
            ac,
            bg=RGBColor(0x0a, 0x24, 0x40),
        )

    # Bottom big quote
    qbox = s.shapes.add_textbox(
        Inches(0.65), Inches(6.3), Inches(12), Inches(0.9)
    )
    tf = qbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "一句话：让每一个想做无人机物流的学生，有一台「随时可练、随时可评」的教学飞行塔。"
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = ACCENT_CYAN
    r.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.LEFT

    add_bottom_bar(s)
    add_page_num(s, 6, total)
    return s


def slide7_end(prs, total):
    s = blank_slide(prs)
    set_slide_bg(s, DARK_BG)
    add_top_bar(s)

    big = s.shapes.add_textbox(Inches(1), Inches(2), Inches(11.3), Inches(1.5))
    tf = big.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "谢谢"
    r.font.size = Pt(72)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT_TITLE
    r.font.shadow = True
    p.alignment = PP_ALIGN.CENTER

    sub = s.shapes.add_textbox(Inches(1), Inches(3.7), Inches(11.3), Inches(2.4))
    tf2 = sub.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    rr = p2.add_run()
    rr.text = "提问 · 体验 · 合作开发"
    rr.font.size = Pt(24)
    rr.font.color.rgb = ACCENT_CYAN
    rr.font.name = FONT_BODY
    p2.alignment = PP_ALIGN.CENTER

    for line in [
        "案例：广西渠洋村 8 村应急物资配送",
        "技术栈：Vue 3 · Django · Python 蚁群算法 · LLM",
        "开源友好 · 单人可部署 · 欢迎共建",
    ]:
        pp = tf2.add_paragraph()
        pp.space_before = Pt(10)
        rrr = pp.add_run()
        rrr.text = line
        rrr.font.size = Pt(14)
        rrr.font.color.rgb = LIGHT_GRAY
        rrr.font.name = FONT_MONO
        pp.alignment = PP_ALIGN.CENTER

    add_bottom_bar(s)
    add_page_num(s, 7, total)
    return s


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    total = 7
    slide1_cover(prs, total)
    slide2_problem(prs, total)
    slide3_what(prs, total)
    slide4_core(prs, total)
    slide5_demo(prs, total)
    slide6_values(prs, total)
    slide7_end(prs, total)

    prs.save(OUT)
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
