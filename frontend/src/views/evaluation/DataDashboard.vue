<template>
  <div class="dash-page">
    <!-- 1920×1080 舞台，按窗口等比缩放（高度扣除顶栏） -->
    <div class="stage" :style="{ transform: 'scale(' + scale + ')' }">

      <!-- ===== 左侧学员名单面板（借鉴智慧评价系统，可收起） ===== -->
      <aside class="roster" :class="{ closed: !rosterOpen }">
        <div class="roster-head">
          <span class="roster-title">学员名单 <b>{{ students.length }}</b> 人</span>
          <button class="roster-fold" title="收起面板" @click="rosterOpen = false">⟨</button>
        </div>
        <div class="roster-body">
          <div v-for="(g, gi) in groupNames" :key="g" class="roster-group">
            <div class="rg-head" :class="{ on: curGroup === gi + 1 }" @click="setGroup(gi + 1)">
              <span class="rg-dot"></span>{{ g }}
              <span class="rg-cnt">{{ groupStudents(gi + 1).length }}人</span>
            </div>
            <div
              v-for="s in groupStudents(gi + 1)" :key="s.id"
              class="roster-stu" :class="{ sel: selected.has(s.id) }"
              :title="s.id + ' · ' + g + ' · 领航' + s.level + ' · 任务 ' + s.tasksDone + '/' + s.tasksTotal + ' · 增值+' + s.delta"
              @click="toggleStudent(s.id)"
            >
              <span class="rs-av" :style="{ background: s.avatarColor }">{{ s.name.charAt(0) }}</span>
              <span class="rs-nm">{{ s.name }}</span>
              <span v-if="s.nation" class="rs-nat">{{ s.nation }}</span>
              <span class="rs-lv" :class="'lv-' + s.level">{{ s.level }}</span>
              <span class="rs-score">{{ Math.round(avgOf(s.now)) }}</span>
            </div>
          </div>
        </div>
      </aside>
      <!-- 收起后的贴边把手 -->
      <button v-show="!rosterOpen" class="roster-handle" title="展开学员名单" @click="openRoster">
        学员名单 ⟨
      </button>

      <!-- ===== 右侧主舞台 ===== -->
      <div class="stage-main">

        <!-- 顶部标题条 -->
        <header>
          <div class="h-left">
            课程性质：<b>现代物流管理专业核心课</b><br>
            第四学期 · 32学时 / 2学分 · 30人 / 6组 · 国际学生5人
          </div>
          <div class="h-title">
            <h1>低空配送与应急处置</h1>
            <div class="sub">教 学 效 果 数 据 大 屏 · 诊 断 → 形 成 → 总 结</div>
          </div>
          <div class="h-right">
            <div class="clock">{{ clockText }}</div>
            <div class="date">评价主体：教师 · 企业导师 · 学生 · AI</div>
          </div>
        </header>

        <!-- 组别联动 Tab -->
        <div class="tabs">
          <span class="t-label">评价视角 <b>▍</b></span>
          <div class="tab" :class="{ on: curGroup === 0 }" @click="setGroup(0)">全班</div>
          <div v-for="(g, gi) in groupNames" :key="g" class="tab" :class="{ on: curGroup === gi + 1 }" @click="setGroup(gi + 1)">{{ g }}</div>
          <span class="t-note">成长阶梯：领航学徒 → 领航工匠 → 领航能手　｜　增值评分 = 当前得分 − 起点得分</span>
        </div>

        <main>
          <!-- 模块1 项目评价 -->
          <section class="card" id="c-project">
            <div class="card-head"><h2>项目评价 · 项目达成度</h2><span class="tag">总结性</span>
              <span class="hd-num">均值 <b>{{ projAvgText }}</b>%</span></div>
            <div class="chart" ref="chProjectEl"></div>
          </section>

          <!-- 模块5 过程评价·课堂实时 -->
          <section class="card" id="c-stage">
            <div class="card-head"><h2>过程评价 · 课堂实时</h2><span class="tag">三阶递进</span>
              <span class="hd-num">课前推送 · 课中采集 · 课后回炉</span></div>
            <div class="chart" ref="chStageEl"></div>
          </section>

          <!-- 模块3 个人画像 -->
          <section class="card" id="c-student">
            <div class="card-head"><h2>个人画像 · 五维能力雷达</h2><span class="tag">形成性</span>
              <span class="hd-num">{{ stuScopeText }}</span></div>
            <div class="stu-wrap">
              <div class="chart" ref="chStuEl"></div>
              <div class="stu-hint">在左侧学员名单中点击学生可单选/多选，多选显示平均画像；不选默认当前视角均值</div>
            </div>
          </section>

          <!-- 模块2 任务评价 -->
          <section class="card" id="c-task">
            <div class="card-head"><h2>任务评价 · 13项典型任务</h2><span class="tag">AI评分</span>
              <span class="hd-num">颜色=难度系数</span></div>
            <div class="chart" ref="chTaskEl"></div>
          </section>

          <!-- 桑基图 -->
          <section class="card" id="c-sankey">
            <div class="card-head"><h2>项目 → 任务 → 能力 流量分布</h2><span class="tag">桑基图</span></div>
            <div class="chart" ref="chSankeyEl"></div>
          </section>

          <!-- 模块4 行为轨迹热力图 -->
          <section class="card" id="c-proc">
            <div class="card-head"><h2>项目过程评价 · 行为轨迹</h2>
              <button v-for="(m, i) in procMetrics" :key="m" class="m-btn" :class="{ on: curMetric === i }" @click="curMetric = i">{{ mBtnNames[i] }}</button></div>
            <div class="chart" ref="chProcEl"></div>
          </section>

          <!-- 证书通过率 -->
          <section class="card" id="c-cert">
            <div class="card-head"><h2>证书通过率</h2><span class="tag">CAAC</span></div>
            <div class="mini-wrap">
              <div class="chart" ref="chCertEl"></div>
              <div class="mini-side">
                <div class="big-num green">90%</div>
                <div class="mini-label">无人机物流运输中级证</div>
                <div class="up-chip">较期初 <b>+26%</b></div>
              </div>
            </div>
          </section>

          <!-- AI智能体服务量 -->
          <section class="card" id="c-ai">
            <div class="card-head"><h2>AI智能体服务量</h2><span class="tag warn">四元主体</span></div>
            <div class="mini-wrap">
              <div class="chart" ref="chAiEl"></div>
              <div class="mini-side">
                <div class="big-num">2341</div>
                <div class="mini-label">累计服务人次</div>
                <div class="big-num orange">120</div>
                <div class="mini-label">节省教师工时(小时)</div>
              </div>
            </div>
          </section>

          <!-- 模块6 增值评价 -->
          <section class="card" id="c-delta">
            <div class="card-head"><h2>增值评价 · 进步增量</h2><span class="tag warn">纵向对比</span>
              <span class="hd-num">不横向排名 · 只看个人纵向进步</span></div>
            <div class="delta-wrap">
              <div class="chart" ref="chDeltaEl"></div>
              <div class="delta-side">
                <div class="slogan">以起点为基线，以增量论成长</div>
                <div class="delta-rows">
                  <div v-for="(d, i) in dimNames" :key="d" class="d-row">
                    <span class="dn">{{ d }}</span>
                    <span class="bar"><i :style="{ width: Math.min(100, deltaRows[i] / 40 * 100) + '%' }"></i></span>
                    <span class="dv">+{{ deltaRows[i] }}</span>
                  </div>
                </div>
                <div class="d-avg">平均增值量 <b>{{ deltaAvg }}</b> 分</div>
                <div class="d-note">虚线灰 = 起点画像　实线青 = 当前画像</div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

/* ================= 数据层：内联示例数据（固定种子，可复现；后续可替换为平台真实导出） ================= */
let _seed = 20240501
function rnd() { _seed = (_seed * 9301 + 49297) % 233280; return _seed / 233280 }
function ri(a, b) { return a + Math.floor(rnd() * (b - a + 1)) }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)) }

const DIMS = ['rule', 'air', 'ctrl', 'emg', 'coord']
const dimNames = ['法规认知', '空域规划', '设备操控', '应急决策', '协同指挥']

// 6 组真实组名与学员名单（长空组含 5 名国际学生，标注国籍）
const groupNames = ['长空组', '巡天组', '御风组', '揽星组', '逐日组', '凌云组']
const ROSTER = [
  { group: 1, members: [
    { name: '英星空', nation: '柬埔寨' }, { name: '佳琳', nation: '柬埔寨' }, { name: '南龙', nation: '老挝' },
    { name: '英俊', nation: '越南' }, { name: '盛美银', nation: '泰国' }] },
  { group: 2, members: [{ name: '韦财林' }, { name: '谢坤兰' }, { name: '王柳瑛' }, { name: '许宝连' }, { name: '钟阳' }] },
  { group: 3, members: [{ name: '劳丽敏' }, { name: '李俊铖' }, { name: '黄远扬' }, { name: '谢秋燕' }, { name: '赵婕' }] },
  { group: 4, members: [{ name: '冉啟玉' }, { name: '梁秀欣' }, { name: '梁晨霞' }, { name: '林明霞' }, { name: '吴芳娜' }] },
  { group: 5, members: [{ name: '方文萍' }, { name: '李晓颖' }, { name: '郭诗奕' }, { name: '黄金生' }, { name: '赵荣州' }] },
  { group: 6, members: [{ name: '梁心语' }, { name: '韦家霖' }, { name: '邓新祥' }, { name: '檀世长' }, { name: '梁珍' }] }
]

function avgOf(o) { return DIMS.reduce((t, d) => t + o[d], 0) / DIMS.length }

const students = []
ROSTER.forEach(function (rg) {
  rg.members.forEach(function (m) {
    const start = {}, now = {}
    DIMS.forEach(function (d) {
      const s = ri(40, 60)
      start[d] = s
      now[d] = clamp(s + ri(10, 40), 60, 95)
    })
    const proc = []
    for (let p = 0; p < 4; p++) proc.push([ri(2, 8), ri(3, 15), ri(2, 12), ri(0, 4)])
    students.push({
      id: 'S' + String(students.length + 1).padStart(2, '0'),
      name: m.name, nation: m.nation || '', group: rg.group,
      start: start, now: now,
      delta: +(avgOf(now) - avgOf(start)).toFixed(1),
      tasksDone: ri(9, 13), tasksTotal: 13, certPass: true, proc: proc,
      avatarColor: 'hsl(' + ((rg.group * 47 + students.length * 7) % 360) + ',72%,48%)'
    })
  })
})
// 成长阶梯：按当前均分排名赋级（30人 → 6能手 / 18工匠 / 6学徒）
;(function () {
  const order = students.slice().sort(function (a, b) { return avgOf(b.now) - avgOf(a.now) })
  order.forEach(function (s, idx) { s.level = idx < 6 ? '能手' : (idx < 24 ? '工匠' : '学徒') })
  // 证书通过率 90% ≈ 27/30：固定 3 人未通过
  ;[3, 11, 17].forEach(function (i) { students[i].certPass = false })
})()

// 4个项目：全班达成率与目标值
const projects = [
  { name: '项目一 低空认知', short: '低空认知', done: 95, target: 90 },
  { name: '项目二 法规合规', short: '法规合规', done: 98, target: 90 },
  { name: '项目三 智能调度', short: '智能调度', done: 88, target: 85 },
  { name: '项目四 应急处置', short: '应急处置', done: 92, target: 85 }
]
const groupProject = {}
for (let g = 1; g <= 6; g++) groupProject[g] = projects.map(p => clamp(p.done + ri(-7, 3), 70, 100))

// 13个典型任务
const taskNames = ['空域准入', '航线规划', '机型匹配', '载荷校验', '法规测试', '应急申报', '工单派发',
  '动态避障', '路径重构', '安全降级', '现场协同', '事故复盘', '归档交接']
const tasks = taskNames.map(n => ({ name: n, doneRate: ri(70, 98), diff: ri(1, 4), aiScore: ri(75, 95) }))
const groupTasks = {}
for (let g = 1; g <= 6; g++) {
  groupTasks[g] = tasks.map(t => ({ doneRate: clamp(t.doneRate + ri(-8, 6), 60, 99), aiScore: clamp(t.aiScore + ri(-6, 5), 60, 99) }))
}
const taskProj = [0, 2, 0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 3]
const taskAbility = [[0, 1], [1], [2], [2], [0], [0, 3], [4], [2, 3], [1, 3], [3], [4], [3, 0], [4]]

// 课前/课中/课后 三阶段过程数据
const stageX = ['课前诊断', '课中·项目一', '课中·项目二', '课中·项目三', '课中·项目四', '课后回炉']
const stageBase = [
  { name: '学情画像推送覆盖率', data: [100, 96, 94, 92, 90, 88] },
  { name: '过程行为采集活跃率', data: [45, 72, 80, 86, 91, 65] },
  { name: '课后回炉任务完成率', data: [null, null, 38, 52, 68, 93] }
]
const groupStage = {}
for (let g = 1; g <= 6; g++) {
  groupStage[g] = stageBase.map(s => s.data.map(v => v === null ? null : clamp(v + ri(-6, 5), 20, 100)))
}

/* ================= 交互状态 ================= */
const curGroup = ref(0)                       // 0=全班，1~6=组
const selected = ref(new Set())               // 选中学生 id 集合
const curMetric = ref(0)
const procMetrics = ['提交次数', 'AI询问次数', '协作发言', '风险预警触发']
const procBtnNames = ['提交', 'AI询问', '协作发言', '风险预警']
const procMax = [8, 15, 12, 4]
const rosterOpen = ref(true)
const scale = ref(1)
const clockText = ref('--:--:--')

const mBtnNames = procBtnNames
function scopeStudents() { return curGroup.value === 0 ? students : students.filter(s => s.group === curGroup.value) }
function activeStudents() {
  if (selected.value.size > 0) return students.filter(s => selected.value.has(s.id))
  return scopeStudents()
}
function avgDims(list, key) {
  const r = {}
  DIMS.forEach(d => { r[d] = +(list.reduce((t, s) => t + s[key][d], 0) / list.length).toFixed(1) })
  return r
}
function dimsArr(o) { return DIMS.map(d => o[d]) }
function groupStudents(g) { return students.filter(s => s.group === g) }

function setGroup(g) { curGroup.value = g; selected.value = new Set() }
function toggleStudent(id) {
  const next = new Set(selected.value)
  if (next.has(id)) next.delete(id); else next.add(id)
  selected.value = next
}
function openRoster() {
  rosterOpen.value = true
  setTimeout(resizeAll, 350)
}

/* ================= 视图状态文本 ================= */
const projAvgText = computed(() => {
  const arr = curGroup.value === 0 ? projects.map(p => p.done) : groupProject[curGroup.value]
  return (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)
})
const stuScopeText = computed(() => {
  const act = activeStudents()
  if (selected.value.size > 0) return selected.value.size === 1 ? act[0].name : '已选' + selected.value.size + '人平均'
  return curGroup.value === 0 ? '全班平均' : groupNames[curGroup.value - 1] + '平均'
})
const deltaRows = ref([0, 0, 0, 0, 0])
const deltaAvg = ref('0')

/* ================= ECharts 通用样式（HUD 风） ================= */
const AX = {
  axisLine: { lineStyle: { color: 'rgba(0,212,255,.30)' } },
  axisTick: { show: false },
  axisLabel: { color: '#9FB3D9', fontSize: 10 },
  splitLine: { lineStyle: { color: 'rgba(0,212,255,.08)' } }
}
const TIP = {
  backgroundColor: 'rgba(8,24,54,.92)', borderColor: 'rgba(0,212,255,.5)',
  textStyle: { color: '#EAF4FF', fontSize: 11 }
}
const C_CYAN = '#00D4FF', C_ORANGE = '#FFB627', C_GREEN = '#4ADE80', C_GRAY = '#8A97B1'
const RADAR_IND = dimNames.map(n => ({ name: n, max: 100 }))
const RADAR_BASE = {
  radar: { indicator: RADAR_IND, radius: '68%', center: ['50%', '52%'], splitNumber: 4,
    axisName: { color: '#9FB3D9', fontSize: 11 },
    splitLine: { lineStyle: { color: 'rgba(0,212,255,.18)' } },
    splitArea: { areaStyle: { color: ['rgba(0,212,255,.02)', 'rgba(0,212,255,.05)'] } },
    axisLine: { lineStyle: { color: 'rgba(0,212,255,.25)' } } },
  tooltip: TIP
}

/* ================= 图表实例与渲染 ================= */
const chProjectEl = ref(), chStageEl = ref(), chStuEl = ref(), chTaskEl = ref()
const chSankeyEl = ref(), chProcEl = ref(), chCertEl = ref(), chAiEl = ref(), chDeltaEl = ref()
let chProject, chStage, chStu, chTask, chSankey, chProc, chCert, chAi, chDelta
const DIFF_COLOR = { 1: C_GREEN, 2: C_CYAN, 3: '#2E7CF6', 4: C_ORANGE }
const STAGE_COLORS = [C_CYAN, C_GREEN, C_ORANGE]

function renderProject() {
  const g = curGroup.value
  const series = [
    { name: '全班达成率', type: 'bar', barWidth: 14,
      data: projects.map(p => p.done),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: '#00D4FF' }, { offset: 1, color: 'rgba(0,212,255,.15)' }] },
        borderRadius: [2, 2, 0, 0] },
      label: { show: true, position: 'top', color: C_CYAN, fontSize: 10, formatter: '{c}%' } },
    { name: '目标值', type: 'bar', barWidth: 6, barGap: '40%',
      data: projects.map(p => p.target),
      itemStyle: { color: 'rgba(255,182,39,.75)', borderRadius: [2, 2, 0, 0] } }
  ]
  if (g !== 0) {
    series.push({ name: groupNames[g - 1] + '达成率', type: 'bar', barWidth: 14, barGap: '40%',
      data: groupProject[g],
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: C_GREEN }, { offset: 1, color: 'rgba(74,222,128,.15)' }] },
        borderRadius: [2, 2, 0, 0] },
      label: { show: true, position: 'top', color: C_GREEN, fontSize: 10, formatter: '{c}%' } })
  }
  chProject.setOption({
    grid: { left: 38, right: 12, top: 34, bottom: 22 },
    legend: { top: 0, right: 0, textStyle: { color: '#9FB3D9', fontSize: 10 }, itemWidth: 12, itemHeight: 8 },
    tooltip: Object.assign({ trigger: 'axis', valueFormatter: v => v + '%' }, TIP),
    xAxis: Object.assign({ type: 'category', data: projects.map(p => p.short) }, AX),
    yAxis: Object.assign({ type: 'value', min: 60, max: 105 }, AX),
    series
  }, true)
}

function renderTask() {
  const g = curGroup.value
  const data = g === 0
    ? tasks.map(t => ({ d: t.doneRate, a: t.aiScore }))
    : groupTasks[g].map(t => ({ d: t.doneRate, a: t.aiScore }))
  chTask.setOption({
    grid: { left: 36, right: 12, top: 30, bottom: 40 },
    legend: { top: 0, right: 0, textStyle: { color: '#9FB3D9', fontSize: 10 }, itemWidth: 12, itemHeight: 8 },
    tooltip: Object.assign({ trigger: 'axis',
      formatter: ps => {
        const i = ps[0].dataIndex, t = tasks[i]
        return '<b>' + t.name + '</b><br>任务完成率：' + data[i].d + '%<br>AI智能体评分：' + data[i].a
          + '<br>难度系数：' + '★'.repeat(t.diff) + '（' + t.diff + '）'
      } }, TIP),
    xAxis: Object.assign({ type: 'category', data: taskNames }, AX,
      { axisLabel: { color: '#9FB3D9', fontSize: 9, interval: 0, rotate: 42 } }),
    yAxis: Object.assign({ type: 'value', min: 50, max: 100 }, AX),
    series: [
      { name: '任务完成率', type: 'bar', barWidth: 9,
        data: data.map((v, i) => ({ value: v.d, itemStyle: { color: DIFF_COLOR[tasks[i].diff], borderRadius: [2, 2, 0, 0] } })) },
      { name: 'AI智能体评分', type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
        data: data.map(v => v.a),
        lineStyle: { color: C_ORANGE, width: 1.5 }, itemStyle: { color: C_ORANGE } }
    ]
  }, true)
}

function renderStuRadar() {
  const act = activeStudents()
  const nowAvg = avgDims(act, 'now')
  const label = stuScopeText.value
  const classAvg = avgDims(students, 'now')
  chStu.setOption(Object.assign({}, RADAR_BASE, {
    legend: { top: 0, right: 0, textStyle: { color: '#9FB3D9', fontSize: 10 }, itemWidth: 12, itemHeight: 8 },
    series: [{ type: 'radar', symbolSize: 4,
      data: [
        { value: dimsArr(nowAvg), name: label,
          lineStyle: { color: C_CYAN, width: 2 }, itemStyle: { color: C_CYAN },
          areaStyle: { color: 'rgba(0,212,255,.25)' } },
        { value: dimsArr(classAvg), name: '全班均值',
          lineStyle: { color: C_GRAY, width: 1, type: 'dashed' }, itemStyle: { color: C_GRAY },
          areaStyle: { color: 'rgba(138,151,177,.06)' } }
      ] }]
  }), true)
}

function renderProc() {
  const list = scopeStudents()
  const data = []
  list.forEach((s, y) => s.proc.forEach((pv, x) => data.push([x, y, pv[curMetric.value]])))
  const warnMode = curMetric.value === 3
  chProc.setOption({
    grid: { left: 46, right: 10, top: 8, bottom: 40 },
    tooltip: Object.assign({ position: 'top',
      formatter: p => list[p.value[1]].name + ' · ' + projects[p.value[0]].short
        + '<br>' + procMetrics[curMetric.value] + '：<b>' + p.value[2] + '</b> 次' }, TIP),
    xAxis: Object.assign({ type: 'category', data: projects.map(p => p.short),
      axisLabel: { color: '#9FB3D9', fontSize: 10 },
      splitArea: { show: true, areaStyle: { color: ['rgba(0,212,255,.02)'] } } }, AX),
    yAxis: Object.assign({ type: 'category', data: list.map(s => s.name),
      axisLabel: { color: '#9FB3D9', fontSize: 9, interval: list.length > 12 ? 1 : 0 } }, AX),
    visualMap: { min: 0, max: procMax[curMetric.value], calculable: true, orient: 'horizontal',
      left: 'center', bottom: 0, itemWidth: 10, itemHeight: 80,
      textStyle: { color: '#7FA8E0', fontSize: 9 },
      inRange: { color: warnMode
        ? ['#0A1F44', 'rgba(255,182,39,.45)', C_ORANGE]
        : ['#0A1F44', '#0E5A8A', C_CYAN] } },
    series: [{ type: 'heatmap', data,
      label: { show: list.length <= 8, color: '#EAF4FF', fontSize: 9 },
      itemStyle: { borderColor: 'rgba(10,31,68,.9)', borderWidth: 1 },
      emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,212,255,.8)' } } }]
  }, true)
}

function renderStage() {
  const g = curGroup.value
  const series = stageBase.map((s, i) => {
    const d = g === 0 ? s.data : groupStage[g][i]
    return { name: s.name, type: 'line', smooth: true, data: d, connectNulls: true,
      symbol: 'circle', symbolSize: 6,
      lineStyle: { color: STAGE_COLORS[i], width: 2 }, itemStyle: { color: STAGE_COLORS[i] },
      areaStyle: i === 1 ? { color: 'rgba(74,222,128,.08)' } : undefined }
  })
  series[0].markArea = {
    silent: true, itemStyle: { color: 'rgba(0,212,255,.05)' },
    label: { color: '#5E7BA8', fontSize: 10, position: 'top' },
    data: [
      [{ name: '诊断性评价', xAxis: '课前诊断' }, { xAxis: '课前诊断' }],
      [{ name: '形成性评价', xAxis: '课中·项目一', itemStyle: { color: 'rgba(74,222,128,.05)' } }, { xAxis: '课中·项目四' }],
      [{ name: '总结性评价', xAxis: '课后回炉', itemStyle: { color: 'rgba(255,182,39,.06)' } }, { xAxis: '课后回炉' }]
    ]
  }
  chStage.setOption({
    grid: { left: 38, right: 14, top: 34, bottom: 22 },
    legend: { top: 0, right: 0, textStyle: { color: '#9FB3D9', fontSize: 10 }, itemWidth: 12, itemHeight: 8 },
    tooltip: Object.assign({ trigger: 'axis', valueFormatter: v => v === null ? '—' : v + '%' }, TIP),
    xAxis: Object.assign({ type: 'category', boundaryGap: false, data: stageX,
      axisLabel: { color: '#9FB3D9', fontSize: 9.5 } }, AX),
    yAxis: Object.assign({ type: 'value', min: 0, max: 100 }, AX),
    series
  }, true)
}

function renderDelta() {
  const act = activeStudents()
  const sAvg = avgDims(act, 'start'), nAvg = avgDims(act, 'now')
  chDelta.setOption(Object.assign({}, RADAR_BASE, {
    radar: Object.assign({}, RADAR_BASE.radar, { radius: '70%', center: ['50%', '54%'],
      axisName: { color: '#9FB3D9', fontSize: 10 } }),
    legend: { top: 0, left: 0, textStyle: { color: '#9FB3D9', fontSize: 10 }, itemWidth: 12, itemHeight: 8 },
    series: [{ type: 'radar', symbolSize: 3,
      data: [
        { value: dimsArr(sAvg), name: '起点画像',
          lineStyle: { color: C_GRAY, width: 1.5, type: 'dashed' }, itemStyle: { color: C_GRAY },
          areaStyle: { color: 'rgba(138,151,177,.10)' } },
        { value: dimsArr(nAvg), name: '当前画像',
          lineStyle: { color: C_CYAN, width: 2 }, itemStyle: { color: C_CYAN },
          areaStyle: { color: 'rgba(0,212,255,.30)' } }
      ] }]
  }), true)
  let total = 0
  deltaRows.value = DIMS.map(d => {
    const dv = +(nAvg[d] - sAvg[d]).toFixed(1)
    total += dv
    return Math.max(0, dv)
  })
  deltaAvg.value = (total / 5).toFixed(1)
}

function renderSankey() {
  const nodes = []
  projects.forEach(p => nodes.push({ name: p.short }))
  taskNames.forEach(n => nodes.push({ name: n }))
  dimNames.forEach(n => nodes.push({ name: '能力·' + n }))
  const links = []
  taskNames.forEach((tn, i) => {
    const w = Math.round(tasks[i].doneRate / 12)
    links.push({ source: projects[taskProj[i]].short, target: tn, value: w })
    taskAbility[i].forEach(a => {
      links.push({ source: tn, target: '能力·' + dimNames[a], value: Math.max(2, Math.round(w / taskAbility[i].length)) })
    })
  })
  chSankey.setOption({
    tooltip: Object.assign({ trigger: 'item',
      formatter: p => p.dataType === 'edge'
        ? p.data.source + ' → ' + p.data.target + '：<b>' + p.data.value + '</b>'
        : '<b>' + p.name + '</b>' }, TIP),
    series: [{ type: 'sankey', left: 8, right: 66, top: 8, bottom: 8,
      nodeWidth: 10, nodeGap: 5, draggable: false,
      emphasis: { focus: 'adjacency' },
      label: { color: '#C9D6F2', fontSize: 9.5 },
      lineStyle: { color: 'gradient', opacity: .30, curveness: .5 },
      levels: [
        { depth: 0, itemStyle: { color: C_CYAN } },
        { depth: 1, itemStyle: { color: '#2E7CF6' } },
        { depth: 2, itemStyle: { color: C_GREEN } }
      ],
      data: nodes, links }]
  })
}

function renderCert() {
  chCert.setOption({
    series: [{ type: 'gauge', startAngle: 210, endAngle: -30, min: 0, max: 100, radius: '96%',
      progress: { show: true, width: 9,
        itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: C_CYAN }, { offset: 1, color: C_GREEN }] } } },
      axisLine: { lineStyle: { width: 9, color: [[1, 'rgba(255,255,255,.08)']] } },
      axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
      pointer: { show: false }, anchor: { show: false },
      title: { show: true, offsetCenter: [0, '34%'], color: '#7FA8E0', fontSize: 10 },
      detail: { valueAnimation: true, formatter: '{value}%', color: C_GREEN,
        fontSize: 26, fontFamily: 'Consolas', offsetCenter: [0, '-2%'] },
      data: [{ value: 90, name: '27/30 人通过' }] }]
  })
}

function renderAi() {
  chAi.setOption({
    tooltip: Object.assign({ trigger: 'item', formatter: '{b}：{c}%（{d}%）' }, TIP),
    legend: { bottom: 0, left: 'center', textStyle: { color: '#9FB3D9', fontSize: 9 }, itemWidth: 10, itemHeight: 7 },
    series: [{ type: 'pie', radius: ['42%', '66%'], center: ['50%', '42%'],
      label: { show: false }, itemStyle: { borderColor: '#0A1F44', borderWidth: 2 },
      data: [
        { value: 30, name: '教师评价', itemStyle: { color: C_CYAN } },
        { value: 20, name: '企业导师评价', itemStyle: { color: '#2E7CF6' } },
        { value: 25, name: '学生互评', itemStyle: { color: C_GREEN } },
        { value: 25, name: 'AI智能评价', itemStyle: { color: C_ORANGE } }
      ] }]
  })
}

function renderAll() {
  renderProject(); renderTask(); renderStuRadar(); renderProc(); renderStage(); renderDelta()
}
function resizeAll() {
  [chProject, chTask, chStu, chProc, chStage, chDelta, chSankey, chCert, chAi]
    .forEach(c => c && c.resize())
}

/* ================= 舞台缩放 + 时钟 ================= */
function fit() {
  scale.value = Math.min(window.innerWidth / 1920, (window.innerHeight - 66) / 1080)
}
let clockTimer = null
function tick() {
  const d = new Date(), p = n => String(n).padStart(2, '0')
  clockText.value = p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds())
    + '  周' + '日一二三四五六'[d.getDay()]
}

watch(curGroup, renderAll)
watch(selected, () => { renderStuRadar(); renderDelta() })
watch(curMetric, renderProc)
function onResize() { fit(); resizeAll() }

onMounted(() => {
  fit()
  tick()
  clockTimer = setInterval(tick, 1000)
  chProject = echarts.init(chProjectEl.value)
  chStage = echarts.init(chStageEl.value)
  chStu = echarts.init(chStuEl.value)
  chTask = echarts.init(chTaskEl.value)
  chSankey = echarts.init(chSankeyEl.value)
  chProc = echarts.init(chProcEl.value)
  chCert = echarts.init(chCertEl.value)
  chAi = echarts.init(chAiEl.value)
  chDelta = echarts.init(chDeltaEl.value)
  renderAll()
  renderSankey(); renderCert(); renderAi()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  clearInterval(clockTimer)
  window.removeEventListener('resize', onResize)
  ;[chProject, chTask, chStu, chProc, chStage, chDelta, chSankey, chCert, chAi]
    .forEach(c => c && c.dispose())
})
</script>

<style scoped>
/* ===== 全局：深蓝底 + 科技 HUD 风 ===== */
.dash-page {
  width: 100%;
  height: calc(100vh - 66px);
  overflow: hidden;
  background: #050D21;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stage {
  width: 1920px;
  height: 1080px;
  flex: none;
  transform-origin: center center;
  padding: 12px 16px;
  display: flex;
  gap: 10px;
  position: relative;
  background:
    radial-gradient(ellipse at 50% -10%, rgba(0,212,255,.14), transparent 55%),
    radial-gradient(ellipse at 50% 112%, rgba(46,124,246,.12), transparent 55%),
    #0A1F44;
}
.stage::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: radial-gradient(circle, rgba(0,212,255,.07) 1px, transparent 1.3px);
  background-size: 26px 26px;
}

/* ===== 左侧学员名单面板 ===== */
.roster {
  width: 236px;
  flex: none;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0,212,255,.35);
  border-radius: 4px;
  background: rgba(8,24,54,.72);
  box-shadow: 0 0 12px rgba(0,212,255,.14), inset 0 0 22px rgba(0,212,255,.04);
  overflow: hidden;
  transition: width .32s ease, opacity .32s ease, padding .32s ease;
}
.roster.closed {
  width: 0;
  opacity: 0;
  padding: 0;
  border-width: 0;
}
.roster-head {
  flex: none;
  height: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border-bottom: 1px solid rgba(0,212,255,.22);
  background: linear-gradient(90deg, rgba(0,212,255,.10), rgba(0,212,255,.03));
}
.roster-title { flex: 1; font-size: 13px; color: #7FA8E0; letter-spacing: 1px; white-space: nowrap; }
.roster-title b { color: #00D4FF; font-size: 16px; font-family: Consolas, monospace; }
.roster-fold {
  width: 22px; height: 22px; flex: none;
  color: #7FA8E0; background: transparent;
  border: 1px solid rgba(0,212,255,.3); border-radius: 3px;
  cursor: pointer; font-size: 13px; line-height: 1;
  transition: all .18s;
}
.roster-fold:hover { color: #04122B; background: #00D4FF; }
.roster-body { flex: 1; min-height: 0; overflow-y: auto; padding: 6px 6px 10px; }
.roster-body::-webkit-scrollbar { width: 4px; }
.roster-body::-webkit-scrollbar-thumb { background: rgba(0,212,255,.25); border-radius: 2px; }

.roster-group { margin-bottom: 6px; }
.rg-head {
  display: flex; align-items: center; gap: 6px;
  height: 26px; padding: 0 8px;
  font-size: 12.5px; color: #9FB3D9;
  border: 1px solid rgba(0,212,255,.22);
  border-radius: 3px; background: rgba(0,212,255,.05);
  cursor: pointer; transition: all .18s; user-select: none;
  letter-spacing: 1px;
}
.rg-head:hover { color: #00D4FF; border-color: #00D4FF; box-shadow: 0 0 8px rgba(0,212,255,.3); }
.rg-head.on {
  color: #04122B; background: linear-gradient(180deg, #00D4FF, #0FA8D8);
  font-weight: 700; border-color: #00D4FF; box-shadow: 0 0 12px rgba(0,212,255,.5);
}
.rg-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; opacity: .8; }
.rg-cnt { margin-left: auto; font-size: 10px; opacity: .75; }

.roster-stu {
  display: flex; align-items: center; gap: 6px;
  height: 27px; margin-top: 2px; padding: 0 7px 0 12px;
  font-size: 12px; color: #B9CBE8;
  border: 1px solid transparent; border-radius: 3px;
  cursor: pointer; transition: all .15s; white-space: nowrap;
}
.roster-stu:hover { border-color: rgba(0,212,255,.5); background: rgba(0,212,255,.08); }
.roster-stu.sel {
  border-color: #00D4FF; background: rgba(0,212,255,.16); color: #EAF6FF;
  box-shadow: 0 0 8px rgba(0,212,255,.35);
}
.rs-av {
  width: 17px; height: 17px; flex: none;
  border-radius: 50%; color: #fff;
  font-size: 10px; line-height: 17px; text-align: center;
  text-shadow: 0 1px 2px rgba(0,0,0,.4);
}
.rs-nm { flex: none; width: 46px; overflow: hidden; }
.rs-nat {
  flex: none; font-size: 9px; color: #FFB627;
  border: 1px solid rgba(255,182,39,.45); border-radius: 2px;
  padding: 0 3px; line-height: 13px; letter-spacing: 1px;
}
.rs-lv { margin-left: auto; flex: none; font-size: 9px; padding: 0 4px; border-radius: 2px; line-height: 14px; }
.lv-学徒 { color: #9FB3D9; border: 1px solid rgba(159,179,217,.5); }
.lv-工匠 { color: #00D4FF; border: 1px solid rgba(0,212,255,.6); }
.lv-能手 { color: #FFB627; border: 1px solid rgba(255,182,39,.6); }
.rs-score { flex: none; width: 24px; text-align: right; font-size: 12px; color: #4ADE80; font-family: Consolas, monospace; font-weight: 700; }

/* 收起后贴边把手 */
.roster-handle {
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  z-index: 3;
  writing-mode: vertical-lr;
  padding: 14px 4px;
  font-size: 12px; letter-spacing: 4px;
  color: #7dd3fc;
  background: rgba(8,24,54,.8);
  border: 1px solid rgba(0,212,255,.35); border-left: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0,212,255,.2);
  transition: all .2s;
}
.roster-handle:hover { color: #04122B; background: #00D4FF; }

/* ===== 主舞台右侧 ===== */
.stage-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  z-index: 1;
}

header {
  height: 64px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  background: linear-gradient(90deg, rgba(0,212,255,.10), rgba(0,212,255,.03) 40%, rgba(0,212,255,.10));
  border: 1px solid rgba(0,212,255,.35);
  border-radius: 4px;
  box-shadow: 0 0 14px rgba(0,212,255,.15), inset 0 0 24px rgba(0,212,255,.05);
}
header .h-left { width: 430px; font-size: 12px; color: #7FA8E0; line-height: 1.6; }
header .h-left b { color: #00D4FF; }
header .h-title { text-align: center; }
header .h-title h1 {
  font-size: 26px; letter-spacing: 6px; color: #EAF6FF; font-weight: 700;
  text-shadow: 0 0 12px rgba(0,212,255,.7), 0 0 32px rgba(0,212,255,.35);
}
header .h-title .sub { font-size: 12px; color: #00D4FF; letter-spacing: 3px; margin-top: 3px; }
header .h-right { width: 430px; text-align: right; }
.clock {
  font-size: 24px; color: #FFB627;
  font-family: "Consolas", "Courier New", monospace;
  text-shadow: 0 0 10px rgba(255,182,39,.5); letter-spacing: 2px;
}
header .h-right .date { font-size: 11px; color: #7FA8E0; margin-top: 2px; }

.tabs { height: 40px; flex: none; display: flex; align-items: center; gap: 8px; }
.tabs .t-label { font-size: 13px; color: #7FA8E0; margin: 0 6px 0 2px; letter-spacing: 1px; }
.tabs .t-label b { color: #FFB627; }
.tab {
  height: 30px; padding: 0 16px; line-height: 28px; font-size: 13px;
  color: #9FB3D9; cursor: pointer;
  border: 1px solid rgba(0,212,255,.30); border-radius: 3px;
  background: rgba(0,212,255,.05);
  transition: all .18s; user-select: none;
}
.tab:hover { color: #00D4FF; border-color: #00D4FF; box-shadow: 0 0 8px rgba(0,212,255,.35); }
.tab.on {
  color: #04122B; background: linear-gradient(180deg, #00D4FF, #0FA8D8);
  font-weight: 700; box-shadow: 0 0 14px rgba(0,212,255,.6);
}
.tabs .t-note { margin-left: auto; font-size: 11px; color: #5E7BA8; letter-spacing: 1px; }

main {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: 1.02fr 1.08fr 0.94fr;
  gap: 10px;
}

.card {
  border: 1px solid rgba(0,212,255,.35); border-radius: 4px;
  background: rgba(8,24,54,.62);
  box-shadow: 0 0 12px rgba(0,212,255,.14), inset 0 0 22px rgba(0,212,255,.04);
  display: flex; flex-direction: column;
  padding: 8px 10px; min-height: 0; min-width: 0; position: relative;
}
.card-head { flex: none; height: 24px; display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.card-head::before {
  content: '';
  width: 4px; height: 14px;
  background: linear-gradient(180deg, #00D4FF, #0FA8D8);
  border-radius: 1px; box-shadow: 0 0 6px rgba(0,212,255,.8);
}
.card-head h2 { font-size: 14px; color: #EAF4FF; letter-spacing: 1px; font-weight: 600; white-space: nowrap; }
.card-head .tag {
  font-size: 10px; color: #0A1F44; background: #00D4FF;
  border-radius: 2px; padding: 1px 6px; letter-spacing: 1px; font-weight: 700;
}
.card-head .tag.warn { background: #FFB627; }
.card-head .hd-num { margin-left: auto; font-size: 12px; color: #7FA8E0; white-space: nowrap; }
.card-head .hd-num b { color: #00D4FF; font-size: 17px; font-family: Consolas, monospace; }
.chart { flex: 1; min-height: 0; width: 100%; }

#c-project { grid-column: 1/5; grid-row: 1; }
#c-stage   { grid-column: 5/9; grid-row: 1; }
#c-student { grid-column: 9/13; grid-row: 1/3; }
#c-task    { grid-column: 1/5; grid-row: 2; }
#c-sankey  { grid-column: 5/9; grid-row: 2; }
#c-proc    { grid-column: 1/5; grid-row: 3; }
#c-cert    { grid-column: 5/7; grid-row: 3; }
#c-ai      { grid-column: 7/9; grid-row: 3; }
#c-delta   { grid-column: 9/13; grid-row: 3; }

.stu-wrap { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.stu-hint { flex: none; font-size: 10px; color: #5E7BA8; margin-top: 3px; }

.m-btn {
  height: 18px; padding: 0 7px; font-size: 10px; line-height: 16px;
  color: #9FB3D9; cursor: pointer;
  border: 1px solid rgba(0,212,255,.3); border-radius: 2px;
  background: transparent; transition: all .15s;
}
.m-btn:hover { color: #00D4FF; }
.m-btn.on { color: #04122B; background: #00D4FF; font-weight: 700; }

.delta-wrap { flex: 1; min-height: 0; display: flex; }
.delta-wrap .chart { width: 56%; min-height: 0; }
.delta-side { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding-left: 8px; }
.slogan {
  font-size: 15px; color: #FFB627; letter-spacing: 2px; font-weight: 700;
  text-shadow: 0 0 10px rgba(255,182,39,.45); margin-bottom: 8px;
}
.slogan::before { content: '「'; color: #00D4FF; }
.slogan::after { content: '」'; color: #00D4FF; }
.d-row { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: #B9CBE8; margin: 3px 0; }
.d-row .dn { width: 56px; flex: none; }
.d-row .bar { flex: 1; height: 6px; background: rgba(255,255,255,.06); border-radius: 3px; overflow: hidden; }
.d-row .bar i { display: block; height: 100%; background: linear-gradient(90deg, #0FA8D8, #4ADE80); border-radius: 3px; }
.d-row .dv { width: 34px; flex: none; text-align: right; color: #4ADE80; font-family: Consolas, monospace; font-weight: 700; }
.d-avg { margin-top: 8px; font-size: 12px; color: #7FA8E0; }
.d-avg b { color: #4ADE80; font-size: 24px; font-family: Consolas, monospace; text-shadow: 0 0 10px rgba(74,222,128,.5); }
.d-note { font-size: 10px; color: #5E7BA8; margin-top: 4px; }

.mini-wrap { flex: 1; min-height: 0; display: flex; }
.mini-wrap .chart { flex: 1; }
.mini-side { width: 44%; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 6px; }
.big-num {
  font-size: 34px; font-weight: 800; font-family: Consolas, monospace; color: #00D4FF;
  text-shadow: 0 0 14px rgba(0,212,255,.6); line-height: 1;
}
.big-num.green { color: #4ADE80; text-shadow: 0 0 14px rgba(74,222,128,.6); }
.big-num.orange { color: #FFB627; text-shadow: 0 0 14px rgba(255,182,39,.6); }
.mini-label { font-size: 11px; color: #7FA8E0; letter-spacing: 1px; }
.up-chip { font-size: 11px; color: #4ADE80; border: 1px solid rgba(74,222,128,.5); border-radius: 2px; padding: 1px 8px; }
.up-chip b { font-family: Consolas, monospace; font-size: 14px; }
</style>
