<template>
  <div class="task8-dashboard">
    <header class="t8-header">
      <div class="header-left">
        <div class="logo-icon">翼</div>
        <div>
          <h1>智慧低空应急运输教学平台</h1>
          <span class="header-sub">任务8 · 方案优化与应急模拟演练 · 实时数据大屏</span>
        </div>
      </div>
      <div class="phase-tabs">
        <div class="phase-tab" :class="{ active: phase===1 }" @click="phase=1"><span class="tab-dot"></span>环节一 · 方案汇报<em>5%</em></div>
        <div class="phase-tab" :class="{ active: phase===2 }" @click="phase=2"><span class="tab-dot"></span>环节二 · 应急推演<em>25%</em></div>
        <div class="phase-tab" :class="{ active: phase===3 }" @click="phase=3"><span class="tab-dot"></span>环节三 · 飞行演练<em>30%</em></div>
        <div class="phase-tab" :class="{ active: phase===4 }" @click="phase=4"><span class="tab-dot"></span>课堂小结<em>10%</em></div>
      </div>
      <div class="header-right">
        <div class="header-status-chip"><span class="dot-pulse ok"></span>数据实时同步中</div>
        <router-link class="heatmap-btn" to="/evaluation/task8/heatmap">🔥 班级热力图</router-link>
        <el-button size="small" @click="$router.push('/evaluation')" style="color:#7ab8e0;background:rgba(0,168,255,0.08);border-color:rgba(0,168,255,0.2);">返回教学智评</el-button>
      </div>
    </header>

    <div class="main-container">
      <aside class="sidebar">
        <div class="section-title">核心能力达成度</div>
        <div class="capability-list">
          <div v-for="cap in capabilities" :key="cap.key" class="glass capability-card" :class="{ weak: cap.score < 70 }">
            <div class="cap-header">
              <span class="cap-name">{{ cap.name }}</span>
              <span class="cap-score" :class="{ low: cap.score < 70 }">{{ cap.score }}%</span>
            </div>
            <div class="cap-progress">
              <div class="cap-progress-bar" :class="cap.score < 70 ? 'cap-bar-red' : 'cap-bar-green'" :style="{ width: cap.score + '%' }"></div>
            </div>
            <div class="cap-footer">
              <span>权重 {{ cap.weight }}%</span>
              <span>{{ cap.score < 70 ? '⚠ 需提升' : '✓ 正常' }}</span>
            </div>
          </div>
        </div>
        <div class="section-title" style="margin-top:8px;">环节进度</div>
        <div class="phase-track">
          <div class="phase-track-fill" :style="{width: phaseProgress + '%'}"></div>
          <div class="phase-track-text">环节{{ phase }}/4 · {{ phaseNameMap[phase] }}</div>
        </div>
      </aside>

      <main class="content">
        <div v-if="phase===1" class="content-grid">
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🎯</span>五维能力对比雷达图</div><div id="p1Radar" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📊</span>教师/企业导师分项评分</div>
            <div class="score-cards">
              <div class="score-card" v-for="g in groups2" :key="g.name"><div class="sc-label">{{ g.name }} · 总分</div><div class="sc-value">{{ g.total }}</div><div class="sc-sub">方案{{ g.design }} / 汇报{{ g.pres }} / 质疑{{ g.chal }}</div></div>
            </div>
            <div class="teacher-score-list">
              <div class="ts-item" v-for="g in groups2" :key="g.name"><span class="ts-group">{{ g.name }}</span><div class="ts-tags"><span class="ts-tag">方案设计 {{ g.design }}/50</span><span class="ts-tag">汇报展示 {{ g.pres }}/40</span><span class="ts-tag">应对质疑 {{ g.chal }}/10</span></div></div>
            </div>
          </div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">💬</span>互评加分记录</div><div class="peer-list"><div class="peer-item" v-for="p in peerLogs" :key="p.time"><span class="peer-time">{{ p.time }}</span><span class="peer-text">{{ p.text }}</span></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🤖</span>AI 数据采集日志</div><div class="ai-log"><div v-for="(line,i) in aiLogs" :key="i" class="ai-log-line"><span class="ai-log-time">{{ line.time }}</span><span class="ai-log-text">{{ line.text }}</span></div></div></div>
        </div>

        <div v-if="phase===2" class="content-grid phase2-grid">
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📈</span>各环节能力趋势</div><div id="p2Trend" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">⚖️</span>各组权重得分对比</div><div id="p2Bar" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🎮</span>应急推演·各组工单三要素</div><div class="progress-list"><div class="progress-item" v-for="p in drillProgress" :key="p.label"><span class="progress-label">{{ p.label }}</span><div class="progress-track"><div class="progress-fill cap-bar-green" :style="{width:p.v+'%'}"></div></div><span class="progress-value">{{ p.v }}%</span></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🔧</span>环节三·裁判组实时评分</div><div class="judge-list"><div class="judge-item" v-for="j in judges" :key="j.name"><div><div class="judge-name">{{ j.name }}（裁判）</div><div class="judge-obj">评分对象：{{ j.group }}</div></div><div style="display:flex;gap:4px;flex-wrap:wrap;"><span class="ts-tag" v-for="d in j.dims" :key="d.label">{{ d.label }} {{ d.val }}</span></div></div></div></div>
          <div class="glass chart-panel row-full"><div class="panel-title"><span class="icon">🎤</span>教师/企业导师点评 · 实时采集</div><div class="teacher-comment-grid">
              <div class="teacher-comment" v-for="(c,i) in teacherComments" :key="i">
                <div class="tc-header"><span class="tc-name" :style="{color:c.color}">{{ c.name }}</span><span class="tc-tag">{{ c.role }}</span><span class="tc-time">{{ c.time }}</span></div>
                <div class="tc-group">@{{ c.group }}</div>
                <div class="tc-text">{{ c.text }}</div>
                <div class="tc-tags"><span class="ts-tag" v-for="t in c.tags" :key="t">{{ t }}</span></div>
              </div>
            </div></div>
        </div>

        <div v-if="phase===3" class="content-grid">
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🔍</span>能力观测表得分</div><div id="p3DimChart" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📊</span>各组总分对比</div><div id="p3TotalChart" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📱</span>裁判组实时评分</div><div class="judge-list"><div class="judge-item" v-for="j in judges" :key="j.name"><div><div class="judge-name">{{ j.name }}（裁判）</div><div class="judge-obj">评分对象：{{ j.group }}</div></div><div style="display:flex;gap:4px;flex-wrap:wrap;"><span class="ts-tag" v-for="d in j.dims" :key="d.label">{{ d.label }} {{ d.val }}</span></div></div></div></div>
          <div class="glass chart-panel center-panel"><div class="panel-title"><span class="icon">📲</span>电子自评量表</div><div class="qr-wrap"><div class="qr-box"><div class="qr-inner"><div v-for="row in 25" :key="row" class="qr-row"><div v-for="c in 25" :key="c" class="qr-cell" :class="{on:qrSeed[row*25+c]}"></div></div></div><div class="qr-finder tl"></div><div class="qr-finder tr"></div><div class="qr-finder bl"></div></div><div class="qr-hint">扫码填写电子自评量表<br><span>自我能力打分 · 最大收获 · 改进承诺</span></div></div></div>
        </div>

        <div v-if="phase===4" class="content-grid phase4-grid">
          <div class="glass chart-panel big-qr-panel">
            <div class="panel-title"><span class="icon">📱</span>扫码获取个人能力报告</div>
            <div class="big-qr-wrap">
              <div class="big-qr-box">
                <div class="qr-inner" style="grid-template-columns:repeat(30,3.33px);grid-template-rows:repeat(30,3.33px);" v-for="(row,y) in 30" :key="'r'+y"><template v-for="(on,x) in 30" :key="'c'+x"><div class="qr-cell" :class="{on:qrSeed[y*30+x] || (x<3&&y<3)||(x>26&&y<3)||(x<3&&y>26)||(x>26&&y>26)}"></div></template></div>
                <div class="qr-finder tl"></div><div class="qr-finder tr"></div><div class="qr-finder bl"></div>
              </div>
              <div class="big-qr-info">
                <div class="bqr-title">扫码查看您的个人报告</div>
                <div class="bqr-sub">包含六维能力评分、雷达图、AI改进建议、教师点评</div>
                <div class="bqr-stats"><div><div class="bqr-num">24</div><div>学生</div></div><div><div class="bqr-num">6</div><div>小组</div></div><div><div class="bqr-num">8</div><div>环节</div></div><div><div class="bqr-num">76.4</div><div>班级均分</div></div></div>
              </div>
            </div>
          </div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🗺️</span>最终班级能力达成度热力图</div><div id="p4Heatmap" class="chart-box" style="min-height:220px;"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📝</span>改进承诺墙</div><div class="promise-input-row"><input class="promise-input" v-model="promiseText" placeholder="输入改进承诺..." @keyup.enter="addPromise" /><button class="promise-btn" @click="addPromise">添加承诺</button></div><div class="promise-list"><div class="promise-item" v-for="(p,i) in promises" :key="i"><span class="pi-group">{{ p.group }}</span><span class="pi-text">{{ p.text }}</span></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🎯</span>能力成长轨迹</div><div class="trajectory-wrap"><div><div class="traj-label">课前</div><div id="p4RadarBefore" class="traj-radar"></div></div><div class="arrow">→</div><div><div class="traj-label">课后</div><div id="p4RadarAfter" class="traj-radar"></div></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">👤</span>个人能力画像</div><div class="personal-radar-grid" id="personalRadarGrid"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🏅</span>本堂课荣誉榜单</div><div class="awards-row"><div class="award-card" v-for="aw in awards" :key="aw.key" @click="showPersonalRadarModal(aw.group)"><div class="award-shine"></div><div class="award-icon">{{ aw.icon }}</div><div class="award-title" :style="{color:aw.color}">{{ aw.title }}</div><div class="award-group">{{ aw.group }}</div><div class="award-reason">{{ aw.reason }}</div></div></div></div>
        </div>
      </main>
    </div>

    <div class="ai-bar"><div class="ai-marquee-wrap"><div class="ai-marquee"><span v-for="(l,i) in marqueeLines" :key="i"><span class="dot">●</span>{{ l }}</span></div></div></div>
    <div class="status-bar"><div class="status-left"><span id="clock">{{ clock }}</span><span>环节 {{ phase }}/4</span><span>{{ phaseNameMap[phase] }}</span></div><div>智慧低空应急运输教学平台 v2.0 · 数据实时同步</div></div>

    <div class="modal-overlay" :class="{show: showModal}" @click.self="showModal=false"><div class="modal-content"><div class="modal-header"><div class="modal-title">{{ modalTitle }}</div><button class="modal-close" @click="showModal=false">&times;</button></div><div class="modal-body"><div class="modal-layout"><div class="modal-chart"><div id="modalRadar" style="width:100%;height:260px;"></div><div class="modal-compare"><div class="compare-label">班级均值 · {{ classAvgScore }}</div><div class="progress-track" style="height:10px;"><div class="progress-fill cap-bar-blue" :style="{width:classAvgScore+'%'}"></div></div><div class="compare-label">本次得分 · {{ modalWeightedScore }}</div><div class="progress-track" style="height:12px;"><div class="progress-fill cap-bar-green" :style="{width:modalWeightedScore+'%'}"></div></div></div></div><div class="modal-info"><div class="modal-score-card"><div class="modal-score-sub">加权综合得分</div><div class="modal-score">{{ modalWeightedScore }}</div><div class="modal-badge" :class="modalWeightedScore>=85?'excellent':modalWeightedScore>=75?'good':modalWeightedScore>=60?'mid':'low'">{{ modalWeightedScore>=85?'优秀':modalWeightedScore>=75?'良好':modalWeightedScore>=60?'合格':'待提升' }}</div></div><div style="font-size:12px;color:#7a9ab8;margin:8px 0 4px;">五维得分明细</div><div v-for="(d,i) in modalDims" :key="d.name" class="modal-dim-row"><span><em>{{ d.weight }}%</em>{{ d.name }}</span><span :class="modalData[i]>=70?'ok':'warn'">{{ modalData[i] }}</span></div><div class="modal-tip">💡 权重：综合25% · 汇报20% · 演练25% · 沟通15% · 改进15%</div></div></div></div></div></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, onUnmounted } from 'vue'
import * as echarts from 'echarts'
const phase = ref(1)
const phaseProgress = computed(() => phase.value * 25)
const clock = ref('')
const showModal = ref(false)
const phaseNameMap = { 1:'方案汇报与知识深化', 2:'应急推演与工单处置', 3:'飞行演练与裁判评分', 4:'课堂小结与能力复盘' }
const phaseShortMap = { 1:'方案', 2:'推演', 3:'飞行', 4:'小结' }
const phaseTipMap = { 1:'正在采集企业导师评分...', 2:'应急推演进行中 · 各组工单三要素实时更新', 3:'裁判组正在打分 · 六维能力维度更新中', 4:'课堂小结 · 正在生成个人能力画像与班级报告' }

const modalTitle = ref('')
const modalData = ref([])
const modalWeightedScore = ref(0)
const modalDims = [{ name:'综合方案设计', weight:25 },{ name:'成果汇报展示', weight:20 },{ name:'演练组织指挥', weight:25 },{ name:'跨部门协调沟通', weight:15 },{ name:'持续改进优化', weight:15 }]
const groups = ['揽星组','御风组','巡天组','逐日组','凌云组','长空组']
const groups2 = [{ name:'揽星组', design:45, pres:36, chal:8, total:89 },{ name:'御风组', design:42, pres:37, chal:7, total:86 },{ name:'巡天组', design:44, pres:35, chal:9, total:88 },{ name:'逐日组', design:38, pres:32, chal:6, total:76 }]
const capabilities = reactive([
  { key:'design', name:'综合方案设计', score:77, weight:25, indicators:['方案逻辑完整性','安全冗余量化','航线规划科学性','载重配合理性'], trend:[60,65,70,75,77] },
  { key:'present', name:'成果汇报展示', score:75, weight:20, indicators:['表达清晰度','数据准确','PPT设计','时间控制'], trend:[55,60,68,72,75] },
  { key:'drillCmd', name:'演练组织指挥', score:82, weight:25, indicators:['决策速度','工单三要素完整','应急流程规范','资源调配合理'], trend:[65,70,74,79,82] },
  { key:'comm', name:'跨部门协调沟通', score:79, weight:15, indicators:['信息传递准确性','角色分工合理性','冲突解决效率','团队协作默契'], trend:[62,66,70,75,79] },
  { key:'improve', name:'持续改进优化', score:68, weight:15, indicators:['改进清单具体性','优化措施可执行','反思深度','迭代意识'], trend:[45,48,52,58,68], weak:true }
])
const personalRadar = { '揽星组':[45,36,55,48,52], '御风组':[42,37,58,55,50], '巡天组':[40,34,60,50,54], '逐日组':[38,32,50,45,48], '凌云组':[41,35,52,47,50], '长空组':[39,33,54,49,51] }
const awards = [
  { key:'pilot', icon:'🏆', title:'领航能手', group:'揽星组', reason:'综合方案设计77分领先，安全冗余量化获企业导师认可', color:'#ffd24d' },
  { key:'craftsman', icon:'⚙️', title:'领航工匠', group:'巡天组', reason:'演练组织指挥82分全班最高，应急决策工单质量最佳', color:'#00dc82' },
  { key:'apprentice', icon:'🌱', title:'领航学徒', group:'逐日组', reason:'跨部门协调沟通进步显著，课后改进承诺具体可执行', color:'#00a8ff' },
  { key:'progress', icon:'🚀', title:'进步之星', group:'御风组', reason:'成果汇报展示从课前55分提升至75分，进步达36%', color:'#c870ff' }
]
const marqueeLines = ['揽星组得分已录入，班级能力雷达图更新中……','当前最弱能力点：持续改进优化（68分）','御风组"成果汇报展示"得分37分','工单分析完毕，巡天组应急决策能力88分领先','AI助教小翼在线 · 数据采集正常','五维雷达图实时刷新中……']
const peerLogs = [{ time:'14:38:15', text:'揽星组点评御风组 +5分' },{ time:'14:38:18', text:'御风组点评揽星组 +5分' },{ time:'14:38:20', text:'环节一数据采集完成，热力图刷新中...' }]
const aiLogs = [{ time:'14:32:05', text:'揽星组企业导师评分录入成功：方案设计45分' },{ time:'14:32:08', text:'揽星组企业导师评分录入成功：汇报展示36分' },{ time:'14:32:11', text:'揽星组企业导师评分录入成功：应对质疑8分' },{ time:'14:32:12', text:'AI雷达图更新：揽星组综合方案设计能力+45分' },{ time:'14:35:22', text:'御风组企业导师评分录入成功：方案设计42分' },{ time:'14:35:28', text:'御风组企业导师评分录入成功：应对质疑7分' }]
const drillProgress = [{ label:'逐日组工单', v:75 },{ label:'揽星组工单', v:88 },{ label:'御风组工单', v:82 },{ label:'巡天组工单', v:92 }]
const judges = [
  { name:'黄雅诗', group:'长空组', dims:[{label:'安全',val:31},{label:'规范',val:30},{label:'团队',val:13},{label:'改进',val:12}] },
  { name:'黄怀理', group:'揽星组', dims:[{label:'安全',val:33},{label:'规范',val:32},{label:'团队',val:12},{label:'改进',val:10}] },
  { name:'张静怡', group:'巡天组', dims:[{label:'安全',val:34},{label:'规范',val:28},{label:'团队',val:14},{label:'改进',val:11}] }
]
const teacherComments = reactive([
  { name:'王 · 应急救援', role:'企业导师', color:'#00dc82', time:'14:42', group:'揽星组', text:'方案设计能考虑地形损耗，很专业！建议加入极端天气的备份航线预案。', tags:['方案设计+8','应对质疑+6','综合能力'] },
  { name:'李 · 无人机系统', role:'主讲教师', color:'#00a8ff', time:'14:45', group:'巡天组', text:'应急推演的工单三要素写得清晰，尤其是RFID标识的漏项提醒，值得全组推广。', tags:['演练组织+7','规范意识+5','亮点'] },
  { name:'陈 · 飞行演练', role:'飞行教练', color:'#c870ff', time:'14:48', group:'逐日组', text:'跨部门沟通环节，逐日组主动承担了地面引导任务，团队协作加分！', tags:['协调沟通+9','团队协作','加分'] },
  { name:'刘 · 安全保障', role:'安全员', color:'#ffaa3a', time:'14:52', group:'御风组', text:'飞行演练的电量双控策略不错，但要注意低温环境下锂电池的放电倍率限制。', tags:['安全规范+6','风险提示','改进建议'] }
])
const classAvgScore = ref(76)
const promiseText = ref('')
const promises = reactive([
  { group:'揽星组', text:'我们会把地形爬升损耗公式纳入动态航程约束模型。' },
  { group:'御风组', text:'我们会把电量优先规则写进协同策略，并增加温控检查清单。' },
  { group:'巡天组', text:'建立单电切换三步确认口诀：一改参数、二按卡扣、三听自检。' },
  { group:'逐日组', text:'把安全约束数字化模板写进智能体预设规则，下次推演一键调用。' },
  { group:'凌云组', text:'应急推演中补充极端天气备份航线预案，加入风阻补偿系数。' },
  { group:'长空组', text:'完善工单三要素的RFID校验步骤，避免标识漏项。' }
])
function addPromise() { const t = promiseText.value.trim(); if (!t) { promiseText.value=''; return } promises.unshift({ group:'揽星组', text:t }); promiseText.value='' }

function dimsLabels() { return ['综合方案设计','成果汇报展示','演练组织指挥','跨部门协调沟通','持续改进优化'] }

let chartInstances = []
function renderPhaseCharts() {
  chartInstances.forEach(c=>{try{c.dispose()}catch(e){}}); chartInstances=[]
  const dims5 = dimsLabels()
  if (phase.value === 1) {
    const el = document.getElementById('p1Radar'); if (el) {
      const c = echarts.init(el); chartInstances.push(c)
      c.setOption({
        tooltip:{}, legend:{data:groups2.map(g=>g.name), textStyle:{color:'#6b8cae', fontSize:11}, top:0},
        radar:{indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#8ab4d0', fontSize:9}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.15)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} },
        series:[{ type:'radar', data: groups2.map(g=>({ value:personalRadar[g.name]||[70,65,80,75,70], name:g.name, lineStyle:{width:2}, areaStyle:{opacity:0.2}, itemStyle:{symbol:'circle', symbolSize:6} })) }]
      })
    }
  } else if (phase.value === 2) {
    const tr = document.getElementById('p2Trend'); if (tr) {
      const c = echarts.init(tr); chartInstances.push(c)
      c.setOption({ tooltip:{trigger:'axis'}, legend:{data:capabilities.map(cp=>cp.name), textStyle:{color:'#6b8cae', fontSize:10}, top:0},
        grid:{left:40,right:20,top:40,bottom:24},
        xAxis:{type:'category', data:['课前','任务1-3','任务4-5','任务6-7','任务8'], axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#5a7a9a', fontSize:10}},
        yAxis:{type:'value', max:100, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#4a6a8a', fontSize:10}},
        series: capabilities.map(cp=>({ name:cp.name, type:'line', smooth:true, data:cp.trend, lineStyle:{width:2}, itemStyle:{symbol:'circle', symbolSize:4}, areaStyle:{opacity:0.08} })) })
    }
    const br = document.getElementById('p2Bar'); if (br) {
      const c = echarts.init(br); chartInstances.push(c)
      c.setOption({ tooltip:{trigger:'axis'}, grid:{left:50,right:20,top:20,bottom:30},
        xAxis:{type:'category', data:groups, axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:11}},
        yAxis:{type:'value', max:100, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#4a6a8a', fontSize:10}},
        series:[{ type:'bar', data: groups.map(g=>({ value:Math.round(personalRadar[g].reduce((s,v,j)=>s+v+[25,20,25,15,15][j]/100,0)), itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#00a8ff'},{offset:1,color:'#00dc82'}]}, borderRadius:[4,4,0,0]} })), barWidth:28, label:{show:true, position:'top', formatter:'{c}', color:'#c8d4e0', fontSize:13, fontWeight:'bold'}, markLine:{silent:true, data:[{yAxis:70, lineStyle:{color:'rgba(255,100,60,0.5)',type:'dashed'}, label:{color:'#ff6b50', fontSize:10, formatter:'达标70'}}]} }] })
    }
  } else if (phase.value === 3) {
    const d3 = document.getElementById('p3DimChart'); if (d3) {
      const c = echarts.init(d3); chartInstances.push(c)
      c.setOption({ tooltip:{trigger:'axis',axisPointer:{type:'shadow'}}, legend:{data:['长空组','揽星组','巡天组'],textStyle:{color:'#6b8cae',fontSize:11},top:0},
        grid:{left:55,right:20,top:30,bottom:20},
        xAxis:{type:'category',data:['安全性(35%)','规范性(35%)','团队配合(15%)','持续改进(15%)'],axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#5a7a9a',fontSize:10}},
        yAxis:{type:'value',axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
        series:[ {name:'长空组',type:'bar',data:[31,30,13,12],barWidth:16,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#00a8ff'},{offset:1,color:'#0066aa'}]}}}, {name:'揽星组',type:'bar',data:[33,32,12,10],barWidth:16,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#00dc82'},{offset:1,color:'#00a060'}]}}}, {name:'巡天组',type:'bar',data:[34,28,14,11],barWidth:16,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#ffaa3a'},{offset:1,color:'#cc7700'}]}}} ] })
    }
    const t3 = document.getElementById('p3TotalChart'); if (t3) {
      const c = echarts.init(t3); chartInstances.push(c)
      c.setOption({ tooltip:{trigger:'axis'}, grid:{left:50,right:30,top:20,bottom:30},
        xAxis:{type:'category',data:['长空组','揽星组','巡天组'],axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:12}},
        yAxis:{type:'value',max:100,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
        series:[{ type:'bar',data:[{value:86,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#00a8ff'},{offset:1,color:'#0066aa'}]}}},{value:87,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#00dc82'},{offset:1,color:'#00a060'}]}}},{value:87,itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#ffaa3a'},{offset:1,color:'#cc7700'}]}}}],barWidth:40, label:{show:true,position:'top',formatter:'{c}分',color:'#c8d4e0',fontSize:14,fontWeight:'bold'}, markLine:{silent:true,data:[{type:'average',name:'平均'}],lineStyle:{color:'rgba(0,168,255,0.3)',type:'dashed'},label:{color:'#5a7a9a',fontSize:10,formatter:'平均 {c}'}} }] })
    }
  } else if (phase.value === 4) {
    const hm = document.getElementById('p4Heatmap')
    if (hm) {
      const c = echarts.init(hm); chartInstances.push(c)
      const heatData = capabilities.map(cp => {
        const isLow = cp.score < 70
        const cs = isLow
          ? {type:'linear',x:0,y:0,x2:1,y2:0,colorStops:[{offset:0,color:'#ff4444'},{offset:1,color:'#ff8c5a'}]}
          : {type:'linear',x:0,y:0,x2:1,y2:0,colorStops:[{offset:0,color:'#00a8ff'},{offset:1,color:'#00dc82'}]}
        return { value:cp.score, itemStyle:{ color:cs, borderRadius:[0,4,4,0] } }
      })
      c.setOption({
        tooltip:{trigger:'axis'},
        grid:{left:130,right:100,top:10,bottom:10},
        xAxis:{type:'value',max:100,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:11,formatter:'{value}%'}},
        yAxis:{type:'category',data:capabilities.map(c=>c.name),axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:12},inverse:true},
        series:[{ type:'bar', data:heatData, barHeight:26,
          markLine:{silent:true,data:[{xAxis:70,lineStyle:{color:'rgba(255,100,60,0.5)',type:'dashed'},label:{color:'#ff6b50',fontSize:10,formatter:'达标线70%'}}]} }]
      })
    }
    const before = document.getElementById('p4RadarBefore'); if (before) {
      const c = echarts.init(before); chartInstances.push(c)
      c.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#4a6a8a',fontSize:9}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.02)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}} }, series:[{type:'radar',data:[{value:[0,0,0,0,0],name:'课前',lineStyle:{color:'rgba(0,168,255,0.2)',width:1,type:'dashed'},areaStyle:{color:'transparent'},symbol:'none'}]}] })
    }
    const after = document.getElementById('p4RadarAfter'); if (after) {
      const c = echarts.init(after); chartInstances.push(c)
      c.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#8ab4d0',fontSize:9}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.15)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} }, series:[{type:'radar',data:[{value:capabilities.map(c=>c.score),name:'课后',lineStyle:{color:'#00dc82',width:2},areaStyle:{color:'rgba(0,220,130,0.2)'},itemStyle:{color:'#00dc82'},symbol:'circle',symbolSize:5}]}] })
    }
    const grid = document.getElementById('personalRadarGrid'); if (grid) {
      grid.innerHTML = groups.map((g,i)=>`<div class="personal-card" data-g="${g}"><div class="pr-name">${g}</div><div id="miniRadar_${i}" style="width:100%;height:90px;"></div><div class="pr-sub">点击查看画像</div></div>`).join('')
      setTimeout(()=>{
        groups.forEach((g,i)=>{ const el=document.getElementById(`miniRadar_${i}`); if(!el)return; const mc=echarts.init(el); chartInstances.push(mc); mc.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'55%', axisName:{show:false}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.03)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.06)'}} }, series:[{type:'radar',data:[{value:personalRadar[g],name:g,lineStyle:{color:'#00dc82',width:1.5},areaStyle:{color:'rgba(0,220,130,0.15)'},itemStyle:{color:'#00dc82'},symbol:'circle',symbolSize:3}]}] }) })
        document.querySelectorAll('.personal-card').forEach(card=>{ card.addEventListener('click', e=>showPersonalRadarModal(card.getAttribute('data-g'))) })
      }, 80)
    }
  }
}

function showPersonalRadarModal(group) {
  const data = personalRadar[group], weights=[25,20,25,15,15]
  modalData.value = data; modalWeightedScore.value = Math.round(data.reduce((s,v,i)=>s+v*weights[i]/100,0)); modalTitle.value = group + ' - 个人能力画像'; showModal.value = true
  setTimeout(()=>{
    const d=document.getElementById('modalRadar'); if(!d)return; const mc=echarts.init(d); chartInstances.push(mc)
    mc.setOption({ radar:{ indicator:dimsLabels().map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#8ab4d0',fontSize:11}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.15)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} }, series:[{type:'radar',data:[{value:data,name:group,lineStyle:{color:'#00a8ff',width:2.5},areaStyle:{color:'rgba(0,168,255,0.2)'},itemStyle:{color:'#00a8ff'},symbol:'circle',symbolSize:6}]}] })
  }, 100)
}

function genQrSeed(size=25) {
  const o = {}
  for (let i=0;i<size*size;i++) o[i] = Math.random() > 0.5
  const finder = Math.min(size, 7)
  for (let y=0;y<finder;y++) for (let x=0;x<finder;x++) {
    const solid = (x===0||x===finder-1||y===0||y===finder-1) || (x>=2&&x<=finder-3&&y>=2&&y<=finder-3)
    o[y*size+x]=solid; o[y*size+(size-x-1)]=solid; o[(size-y-1)*size+x]=solid
  }
  return o
}
const qrSeed = genQrSeed(25)
const bigQrSeed = genQrSeed(30)

const rootScale = ref(1)
function calcScale() {
  const baseW = 1920, baseH = 1080
  const wScale = window.innerWidth / baseW
  const hScale = window.innerHeight / baseH
  rootScale.value = Math.min(wScale, hScale)
  document.documentElement.style.setProperty('--root-scale', rootScale.value.toFixed(3))
}
let qrTimer = null
onMounted(()=>{
  const tick = () => { const n = new Date(); clock.value = String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')+':'+String(n.getSeconds()).padStart(2,'0') }
  tick(); setInterval(tick, 1000); renderPhaseCharts()
  calcScale(); window.addEventListener('resize', calcScale)
  setInterval(()=>{ capabilities.forEach(cap=>{ cap.score=Math.min(100,Math.max(0,Math.round(cap.score+(Math.random()*4-2)))) }) }, 30000)
  qrTimer = setInterval(()=>{ Object.assign(qrSeed, genQrSeed(25)); Object.assign(bigQrSeed, genQrSeed(30)) }, 4000)
  window.addEventListener('resize', ()=>chartInstances.forEach(c=>{try{c.resize()}catch(e){}}))
})
onUnmounted(()=>{
  window.removeEventListener('resize', calcScale)
  if (qrTimer) clearInterval(qrTimer)
})
watch(phase, ()=>setTimeout(renderPhaseCharts, 60))
</script>

<style scoped>
.task8-dashboard { margin:0; padding:0; width:1920px; min-width:1920px; height:1080px; min-height:1080px; background:#060d1f; color:#c8d4e0; display:flex; flex-direction:column; font-family:'Microsoft YaHei','PingFang SC',sans-serif; box-sizing:border-box; transform-origin:top left; transform:scale(var(--root-scale,1)); font-size:18px; }
@media (max-width: 1920px) {
  .task8-dashboard { transform-origin:top left; }
}
.flex{display:flex}.gap8{gap:8px}.items-center{align-items:center}
.glass { background:linear-gradient(135deg,rgba(0,168,255,0.06),rgba(0,220,180,0.03)); border:1px solid rgba(0,168,255,0.15); border-radius:12px; backdrop-filter:blur(10px); position:relative; overflow:hidden; }
.glass::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(0,168,255,0.4),transparent); }
.glass::after { content:''; position:absolute; bottom:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(0,220,180,0.2),transparent); }

.t8-header { height:90px; display:flex; align-items:center; justify-content:space-between; padding:0 32px; background:linear-gradient(180deg,rgba(0,20,40,0.95),rgba(6,13,31,0.98)); border-bottom:1px solid rgba(0,168,255,0.2); }
.header-left { display:flex; align-items:center; gap:18px; }
.logo-icon { width:56px; height:56px; border-radius:14px; background:linear-gradient(135deg,#00a8ff,#00dc82); display:flex; align-items:center; justify-content:center; font-size:28px; color:#fff; font-weight:bold; }
.t8-header h1 { font-size:32px; color:#e0f0ff; font-weight:600; letter-spacing:2px; animation:glow 3s ease-in-out infinite; margin:0; }
.header-sub { color:#6b8cae; font-size:17px; margin-left:16px; letter-spacing:1px; }
@keyframes glow { 0%,100%{text-shadow:0 0 10px rgba(0,168,255,0.5);} 50%{text-shadow:0 0 20px rgba(0,168,255,0.9),0 0 30px rgba(0,168,255,0.5);} }

.phase-tabs { display:flex; gap:4px; }
.header-meta { font-size:11px; color:#5a7a9a; margin-left:14px; padding-left:14px; border-left:1px solid rgba(0,168,255,0.2); letter-spacing:0.5px; }
.phase-tab { padding:14px 26px; border-radius:10px; font-size:18px; cursor:pointer; background:rgba(0,168,255,0.08); color:#7a9ab8; border:1px solid rgba(0,168,255,0.12); transition:all 0.3s; display:flex; align-items:center; gap:10px; }
.phase-tab:hover { background:rgba(0,168,255,0.15); color:#a0c8e8; }
.phase-tab.active { background:linear-gradient(135deg,rgba(0,168,255,0.22),rgba(0,220,180,0.18)); color:#00dc82; border-color:rgba(0,220,180,0.4); box-shadow:0 0 16px rgba(0,220,130,0.2),0 0 30px rgba(0,168,255,0.1); text-shadow:0 0 8px rgba(0,220,130,0.5); }
.phase-tab em { font-style:normal; color:#4a6a8a; font-size:13px; padding:3px 10px; border-radius:10px; background:rgba(0,168,255,0.1); }
.phase-tab.active em { background:rgba(0,220,180,0.2); color:#00dc82; }
.tab-dot { display:inline-block; width:9px; height:9px; border-radius:50%; background:#3a5a7a; margin-right:2px; vertical-align:middle; transition:all 0.3s; }
.phase-tab.active .tab-dot { background:#00dc82; box-shadow:0 0 8px #00dc82; }
.header-right { display:flex; align-items:center; gap:10px; }
.header-status-chip { display:flex; align-items:center; gap:8px; padding:8px 14px; border-radius:16px; font-size:13px; color:#b8d4e8; background:rgba(0,220,130,0.08); border:1px solid rgba(0,220,130,0.2); }
.dot-pulse { width:8px; height:8px; border-radius:50%; display:inline-block; }
.dot-pulse.ok { background:#00dc82; box-shadow:0 0 8px #00dc82; animation:pulseDot 1.6s ease-in-out infinite; }
.dot-pulse.blue { background:#00a8ff; box-shadow:0 0 8px #00a8ff; animation:pulseDot 2.2s ease-in-out infinite; }
.dot-pulse.warn { background:#ffaa3a; box-shadow:0 0 8px #ffaa3a; animation:pulseDot 2.8s ease-in-out infinite; }
.dot-pulse.purple { background:#c870ff; box-shadow:0 0 8px #c870ff; animation:pulseDot 2s ease-in-out infinite; }
@keyframes pulseDot { 0%,100%{ transform:scale(1); } 50%{ transform:scale(1.4); opacity:0.6; } }

.header-right { display:flex; align-items:center; gap:10px; }
.heatmap-btn { padding:10px 16px; border-radius:8px; font-size:14px; text-decoration:none; background:rgba(0,168,255,0.1); color:#00dc82; border:1px solid rgba(0,220,180,0.25); transition:all 0.3s; }
.heatmap-btn:hover { background:rgba(0,220,180,0.15); box-shadow:0 0 12px rgba(0,220,130,0.3); }

.main-container { display:flex; flex:1; overflow:hidden; padding:12px; gap:12px; }
.sidebar { width:280px; min-width:280px; display:flex; flex-direction:column; gap:12px; overflow-y:auto; }
.section-title { font-size:17px; color:#8ab4d0; font-weight:600; padding:2px 0 6px 10px; margin-bottom:6px; letter-spacing:1px; position:relative; }
.section-title::before { content:''; position:absolute; left:0; top:4px; width:3px; height:14px; background:linear-gradient(180deg,#00a8ff,#00dc82); border-radius:2px; }

.t8-info { padding:12px 14px; }
.t8-status { padding:10px 14px; display:flex; flex-direction:column; gap:8px; font-size:11px; color:#7a9ab8; }
.phase-progress-bar { display:flex; justify-content:space-between; gap:6px; }
.phase-progress-item { flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 0; border-radius:6px; border:1px solid rgba(0,168,255,0.1); background:rgba(0,168,255,0.03); transition:all 0.3s; }
.phase-progress-item .pp-num { width:18px; height:18px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; background:rgba(10,40,96,0.6); color:#5a7a9a; border:1px solid rgba(0,168,255,0.2); }
.phase-progress-item .pp-label { font-size:9px; color:#5a7a9a; }
.phase-progress-item.done { background:rgba(0,220,130,0.08); border-color:rgba(0,220,130,0.25); }
.phase-progress-item.done .pp-num { background:rgba(0,220,130,0.2); color:#00dc82; border-color:rgba(0,220,130,0.5); }
.phase-progress-item.active { background:linear-gradient(135deg,rgba(0,168,255,0.15),rgba(0,220,130,0.12)); border-color:rgba(0,220,130,0.4); box-shadow:0 0 12px rgba(0,220,130,0.15); }
.phase-progress-item.active .pp-num { background:linear-gradient(135deg,#00a8ff,#00dc82); color:#061628; border:none; box-shadow:0 0 8px rgba(0,220,130,0.6); }
.phase-progress-item.active .pp-label { color:#00dc82; font-weight:600; }
.phase-progress-item.todo { opacity:0.55; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#00dc82; box-shadow:0 0 6px #00dc82; }
.status-dot.blue { background:#00a8ff; box-shadow:0 0 6px #00a8ff; }
.status-dot.warn { background:#ffaa3a; box-shadow:0 0 6px #ffaa3a; }

.capability-card { padding:18px 20px; margin-bottom:12px; border-radius:16px; position:relative; overflow:hidden; cursor:pointer; transition:all 0.3s; animation:fadeIn 0.5s ease both; }
.capability-card:hover { transform:translateX(3px); box-shadow:0 0 24px rgba(0,168,255,0.15), inset 0 0 20px rgba(0,168,255,0.05); }
.capability-card.weak:hover { box-shadow:0 0 24px rgba(255,80,60,0.2), inset 0 0 20px rgba(255,80,60,0.05); }
.capability-card.weak .cap-name { color:#ff8c70; }
.cap-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.cap-name { font-size:20px; color:#d0e4f0; font-weight:500; transition:color 0.3s; }
.cap-score { font-size:24px; font-weight:700; color:#00dc82; transition:all 0.3s; }
.cap-score.low { color:#ff6b50; animation:pulseScore 2s ease-in-out infinite; }
.cap-progress { height:8px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden; margin-bottom:10px; }
.cap-progress-bar { height:100%; border-radius:4px; position:relative; width:0; animation:progressGrow 1s ease forwards; }
.cap-progress-bar::after { content:''; position:absolute; right:0; top:0; bottom:0; width:14px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.4)); }
.cap-bar-green { background:linear-gradient(90deg,#00a8ff,#00dc82); }
.cap-bar-red { background:linear-gradient(90deg,#ff4444,#ff8c5a); }
.cap-footer { display:flex; justify-content:space-between; margin-top:10px; font-size:14px; color:#6a8aaa; }
@keyframes progressGrow { from{width:0} to{width:var(--target-width,100%)} }
@keyframes pulseScore { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
.phase-track { position:relative; height:32px; background:#0a1530; border:1px solid rgba(0,168,255,0.1); border-radius:6px; overflow:hidden; display:flex; align-items:center; }
.phase-track-fill { position:absolute; left:0; top:0; bottom:0; background:linear-gradient(90deg,rgba(0,168,255,0.15),rgba(0,220,130,0.2)); border-radius:6px; transition:width 0.8s ease; }
.phase-track-text { position:relative; z-index:1; font-size:12px; color:#8ab4d0; padding:0 12px; letter-spacing:0.5px; }
@keyframes fadeIn { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:translateY(0);} }

.content { flex:1; display:flex; flex-direction:column; gap:10px; overflow:hidden; }
.content-grid { flex:1; display:grid; gap:10px; overflow-y:auto; padding-right:4px; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; }
.content-grid.phase4-grid { grid-template-columns:1fr 1fr; grid-template-rows:auto auto auto auto; }
.row-full { grid-column:1 / -1; }
.chart-panel { padding:20px; display:flex; flex-direction:column; animation:fadeIn 0.5s; }
.panel-title { font-size:20px; color:#e0f0ff; font-weight:600; margin-bottom:16px; display:flex; align-items:center; gap:8px; flex-shrink:0; }
.panel-title .icon { width:36px; height:36px; border-radius:8px; background:linear-gradient(135deg,rgba(0,168,255,0.15),rgba(0,220,180,0.1)); display:flex; align-items:center; justify-content:center; font-size:18px; border:1px solid rgba(0,168,255,0.2); }
.center-panel { align-items:center; justify-content:center; }
.chart-box { flex:1; min-height:240px; width:100%; }

.score-cards { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
.score-card { flex:1; min-width:140px; padding:14px 16px; border-radius:10px; background:linear-gradient(135deg,rgba(0,168,255,0.06),rgba(0,100,200,0.03)); border:1px solid rgba(0,168,255,0.12); text-align:center; transition:all 0.3s; }
.score-card:hover { transform:translateY(-2px); border-color:rgba(0,168,255,0.3); }
.score-card .sc-label { font-size:17px; color:#6b8cae; margin-bottom:8px; }
.score-card .sc-value { font-size:36px; font-weight:700; color:#00dc82; }
.score-card .sc-sub { font-size:15px; color:#4a6a8a; margin-top:4px; }

.teacher-score-list, .judge-list { display:flex; flex-direction:column; gap:8px; }
.ts-item, .judge-item { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 12px; border-radius:8px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.08); transition:all 0.3s; }
.ts-item:hover, .judge-item:hover { background:rgba(0,168,255,0.08); border-color:rgba(0,168,255,0.18); }
.ts-group { width:60px; font-size:17px; color:#8ab4d0; font-weight:500; }
.ts-tags { display:flex; gap:6px; flex:1; flex-wrap:wrap; }
.ts-tag { padding:4px 12px; border-radius:12px; font-size:15px; background:rgba(0,168,255,0.1); color:#7ab8e0; border:1px solid rgba(0,168,255,0.15); }
.judge-name { font-size:17px; color:#00a8ff; font-weight:600; }
.judge-obj { font-size:15px; color:#5a7a9a; margin-top:2px; }

.peer-list, .ai-log { display:flex; flex-direction:column; gap:4px; }
.peer-item, .ai-log-line { padding:10px 14px; font-size:16px; border-radius:4px; background:rgba(0,168,255,0.04); border-left:2px solid rgba(0,220,130,0.4); }
.peer-time, .ai-log-time { color:#00dc82; margin-right:6px; font-family:monospace; font-size:15px; }
.peer-text, .ai-log-text { color:#7a9ab8; }

.progress-list { display:flex; flex-direction:column; gap:10px; }
.progress-item { display:flex; align-items:center; gap:10px; }
.progress-label { width:110px; font-size:17px; color:#8ab4d0; }
.progress-track { flex:1; height:16px; background:rgba(255,255,255,0.06); border-radius:8px; overflow:hidden; }
.progress-fill { height:100%; border-radius:8px; transition:width 1s ease; position:relative; }
.progress-fill::after { content:''; position:absolute; right:0; top:0; bottom:0; width:15px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.4)); }
.progress-value { width:40px; text-align:right; font-size:17px; color:#00dc82; font-weight:600; }

.qr-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; padding:16px; }
.qr-box { width:148px; height:148px; border-radius:10px; background:#fff; padding:10px; position:relative; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 16px rgba(0,0,0,0.4); }
.qr-inner { width:124px; height:124px; display:grid; grid-template-columns:repeat(25, 4.96px); grid-template-rows:repeat(25, 4.96px); gap:0; }
.qr-cell { background:#fff; }
.qr-cell.on { background:#0a1628; }
.qr-finder { position:absolute; width:26px; height:26px; border:3px solid #0a1628; background:#fff; box-sizing:border-box; }
.qr-finder.tl { top:10px; left:10px; border-right:none; border-bottom:none; }
.qr-finder.tr { top:10px; right:10px; border-left:none; border-bottom:none; }
.qr-finder.bl { bottom:10px; left:10px; border-right:none; border-top:none; }
.qr-hint { font-size:11px; color:#7a9ab8; text-align:center; line-height:1.6; }
.qr-hint span { color:#4a6a8a; }

.promise-input-row { display:flex; gap:8px; margin-bottom:10px; }
.promise-input { flex:1; padding:8px 12px; border-radius:6px; background:rgba(0,168,255,0.06); border:1px solid rgba(0,168,255,0.2); color:#c8d4e0; font-size:12px; outline:none; font-family:inherit; }
.promise-input:focus { border-color:rgba(0,168,255,0.5); }
.promise-btn { padding:0 16px; border-radius:6px; background:linear-gradient(135deg,#00a8ff,#00dc82); color:#061628; font-weight:600; font-size:12px; border:none; cursor:pointer; }
.promise-btn:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,220,130,0.4); }
.promise-list { display:flex; flex-direction:column; gap:5px; max-height:150px; overflow-y:auto; }
.promise-item { display:flex; gap:8px; padding:6px 10px; border-radius:6px; background:rgba(0,168,255,0.04); border-left:2px solid rgba(0,168,255,0.3); font-size:11px; line-height:1.7; }
.promise-item .pi-group { color:#00dc82; font-weight:600; white-space:nowrap; }
.promise-item .pi-text { color:#9ab9d6; flex:1; }

.trajectory-wrap { display:flex; align-items:center; justify-content:center; gap:12px; flex:1; }
.traj-label { text-align:center; font-size:11px; color:#5a7a9a; margin-bottom:4px; }
.traj-radar { width:180px; height:180px; }
.arrow { font-size:20px; color:#00dc82; font-weight:bold; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

.personal-radar-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.personal-card { padding:8px; border-radius:6px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); cursor:pointer; transition:all 0.3s; text-align:center; }
.personal-card:hover { background:rgba(0,168,255,0.1); border-color:rgba(0,168,255,0.3); transform:translateY(-2px); }
.pr-name { font-size:11px; color:#00a8ff; font-weight:600; margin-bottom:2px; }
.pr-sub { font-size:10px; color:#4a6a8a; margin-top:2px; }

.awards-row { display:flex; gap:10px; flex-wrap:wrap; }
.award-card { position:relative; flex:1; min-width:140px; padding:14px; border-radius:10px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.15); cursor:pointer; overflow:hidden; transition:all 0.3s; text-align:center; }
.award-card:hover { transform:translateY(-3px); border-color:rgba(0,220,180,0.4); box-shadow:0 0 20px rgba(0,220,130,0.3); }
.award-shine { position:absolute; top:-50%; left:-50%; width:50%; height:200%; background:linear-gradient(120deg,transparent,rgba(255,255,255,0.25),transparent); transform:skewX(-30deg) translateX(-200%); animation:shine 4s infinite; pointer-events:none; }
@keyframes shine { 0%{transform:translateX(-200%) skewX(-30deg);} 40%,100%{transform:translateX(200%) skewX(-30deg);} }
.award-icon { font-size:26px; margin-bottom:4px; }
.award-title { font-size:13px; font-weight:700; margin-bottom:2px; }
.award-group { font-size:11px; color:#8ab4d0; margin-bottom:6px; }
.award-reason { font-size:10px; color:#5a7a9a; line-height:1.5; text-align:left; }

.ai-bar { height:46px; background:rgba(0,20,40,0.8); border-top:1px solid rgba(0,168,255,0.2); overflow:hidden; }
.ai-marquee-wrap { height:100%; display:flex; align-items:center; white-space:nowrap; }
.ai-marquee { display:inline-block; padding-left:100%; animation:marquee 40s linear infinite; font-size:17px; color:#7a9ab8; }
.ai-marquee span { margin-right:60px; }
.ai-marquee .dot { color:#00dc82; margin-right:6px; animation:pulse 1s infinite; }
@keyframes marquee { 0%{transform:translateX(0);} 100%{transform:translateX(-100%);} }

.status-bar { height:40px; background:rgba(0,10,30,0.95); border-top:1px solid rgba(0,168,255,0.1); display:flex; align-items:center; justify-content:space-between; padding:0 20px; font-size:16px; color:#5a7a9a; }
.status-left { display:flex; gap:20px; color:#8ab4d0; }
.status-left span:first-child { font-family:monospace; color:#00dc82; font-size:17px; }

.modal-overlay { position:fixed; inset:0; background:rgba(0,10,30,0.85); backdrop-filter:blur(8px); display:flex; align-items:center; justify-content:center; opacity:0; pointer-events:none; transition:opacity 0.3s; z-index:2000; }
.modal-overlay.show { opacity:1; pointer-events:auto; }
.modal-content { width:600px; max-width:90vw; max-height:85vh; background:linear-gradient(135deg,#0a1f3a,#0d2a4e); border:1px solid rgba(0,168,255,0.3); border-radius:14px; overflow:hidden; box-shadow:0 20px 60px rgba(0,100,220,0.4); }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:14px 20px; border-bottom:1px solid rgba(0,168,255,0.2); background:linear-gradient(180deg,#0a2f55,#0a1f3a); }
.modal-title { font-size:16px; color:#e0f0ff; font-weight:600; letter-spacing:1px; }
.modal-close { width:28px; height:28px; border-radius:6px; background:rgba(255,100,60,0.1); border:1px solid rgba(255,100,60,0.3); color:#ff8c5a; font-size:18px; cursor:pointer; }
.modal-close:hover { background:rgba(255,100,60,0.3); }
.modal-body { padding:20px; }
.modal-layout { display:flex; gap:20px; }
.modal-chart { flex:1; }
.modal-info { width:200px; display:flex; flex-direction:column; }
.modal-score-card { padding:12px; border-radius:8px; background:linear-gradient(135deg,rgba(0,220,130,0.15),rgba(0,168,255,0.1)); border:1px solid rgba(0,220,130,0.3); text-align:center; margin-bottom:12px; }
.modal-score-sub { font-size:10px; color:#5a7a9a; }
.modal-score { font-size:36px; font-weight:700; color:#00dc82; text-shadow:0 0 20px rgba(0,220,130,0.6); }
.modal-badge { display:inline-block; font-size:10px; padding:2px 8px; border-radius:10px; margin-top:6px; font-weight:600; }
.modal-badge.excellent { background:rgba(255,210,77,0.15); color:#ffd24d; border:1px solid rgba(255,210,77,0.3); }
.modal-badge.good { background:rgba(0,220,130,0.15); color:#00dc82; border:1px solid rgba(0,220,130,0.3); }
.modal-badge.mid { background:rgba(0,168,255,0.15); color:#00a8ff; border:1px solid rgba(0,168,255,0.3); }
.modal-badge.low { background:rgba(255,107,80,0.15); color:#ff6b50; border:1px solid rgba(255,107,80,0.3); }
.modal-dim-row { display:flex; justify-content:space-between; align-items:center; padding:3px 0; font-size:11px; color:#8ab4d0; border-bottom:1px dashed rgba(0,168,255,0.08); }
.modal-dim-row em { font-style:normal; color:#5a7a9a; font-size:9px; margin-right:4px; }
.modal-dim-row .ok { color:#00dc82; font-weight:600; }
.modal-dim-row .warn { color:#ffaa3a; font-weight:600; }
.modal-tip { margin-top:8px; font-size:10px; color:#4a6a8a; padding:6px; border-radius:4px; background:rgba(0,168,255,0.05); border-left:2px solid rgba(0,168,255,0.2); line-height:1.6; }
.modal-compare { margin-top:12px; padding:10px; border-radius:6px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); }
.compare-label { font-size:11px; color:#8ab4d0; margin-bottom:4px; }
.cap-bar-blue { background:linear-gradient(90deg,#0a2860,#00a8ff); border-radius:3px; position:relative; overflow:hidden; }
.cap-bar-green { background:linear-gradient(90deg,#00a8ff,#00dc82); border-radius:3px; position:relative; overflow:hidden; }
.phase2-grid { grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr auto; }
.teacher-comment-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.teacher-comment { padding:10px 12px; border-radius:8px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); transition:all 0.3s; }
.teacher-comment:hover { background:rgba(0,168,255,0.08); border-color:rgba(0,168,255,0.25); transform:translateY(-2px); }
.tc-header { display:flex; align-items:center; gap:6px; margin-bottom:4px; }
.tc-name { font-size:12px; font-weight:600; }
.tc-tag { font-size:9px; padding:1px 6px; border-radius:8px; background:rgba(255,255,255,0.06); color:#5a7a9a; }
.tc-time { font-size:9px; color:#4a6a8a; margin-left:auto; font-family:monospace; }
.tc-group { font-size:11px; color:#00dc82; font-weight:500; margin-bottom:4px; }
.tc-text { font-size:11px; color:#b8d4e8; line-height:1.6; margin-bottom:6px; min-height:44px; }
.tc-tags { display:flex; gap:4px; flex-wrap:wrap; }
.tc-tags .ts-tag { font-size:9px; padding:1px 5px; }
.big-qr-panel { grid-column:1 / 2; grid-row:1 / 2; display:flex; flex-direction:column; }
.big-qr-wrap { display:flex; gap:16px; padding:10px; flex:1; }
.big-qr-box { width:220px; height:220px; border-radius:10px; background:#fff; padding:12px; position:relative; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 20px rgba(0,0,0,0.3); flex-shrink:0; }
.big-qr-box .qr-inner { width:196px; height:196px; display:grid; }
.big-qr-info { flex:1; display:flex; flex-direction:column; justify-content:center; padding:8px 0; }
.bqr-title { font-size:16px; color:#e0f0ff; font-weight:600; margin-bottom:4px; }
.bqr-sub { font-size:11px; color:#7a9ab8; margin-bottom:16px; line-height:1.6; }
.bqr-stats { display:flex; gap:18px; }
.bqr-stats > div { text-align:center; padding:8px 14px; border-radius:8px; background:rgba(0,168,255,0.06); border:1px solid rgba(0,168,255,0.12); }
.bqr-num { font-size:22px; color:#00dc82; font-weight:700; margin-bottom:2px; text-shadow:0 0 12px rgba(0,220,130,0.4); }
.bqr-stats > div div:last-child { font-size:10px; color:#5a7a9a; }
</style>
