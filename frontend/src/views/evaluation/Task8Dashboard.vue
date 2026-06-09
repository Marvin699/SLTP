<template>
  <div class="task8-dashboard">
    <header class="t8-header">
      <div class="header-left">
        <div class="logo-icon">翼</div>
        <div>
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
        <el-button size="small" @click="$router.push('/evaluation')" class="back-teach-btn">← 返回</el-button>
        <router-link class="heatmap-btn" to="/evaluation/task8/heatmap">🔥 班级热力图</router-link>
        <template v-if="phase === 1">
          <button v-if="!demo1Running && !demo1Done" class="demo-btn" @click="runDemo(1)">▶ 展览</button>
          <button v-if="demo1Running" class="demo-btn demo-running" disabled>⏳ 展览中...</button>
          <button v-if="!demo1Running && demo1Done" class="demo-btn demo-reset" @click="resetDemo(1)">↺ 重置</button>
        </template>
        <template v-if="phase === 2">
          <button v-if="!demo2Running && !demo2Done" class="demo-btn" @click="runDemo(2)">▶ 展览</button>
          <button v-if="demo2Running" class="demo-btn demo-running" disabled>⏳ 展览中...</button>
          <button v-if="!demo2Running && demo2Done" class="demo-btn demo-reset" @click="resetDemo(2)">↺ 重置</button>
        </template>
        <template v-if="phase === 3">
          <button v-if="!demo3Running && !demo3Done" class="demo-btn" @click="runDemo(3)">▶ 展览</button>
          <button v-if="demo3Running" class="demo-btn demo-running" disabled>⏳ 展览中...</button>
          <button v-if="!demo3Running && demo3Done" class="demo-btn demo-reset" @click="resetDemo(3)">↺ 重置</button>
        </template>
        <template v-if="phase === 4">
        </template>
      </div>
    </header>

    <div class="main-container">
      <aside class="sidebar">
        <div class="sidebar-head">📚 任务8 · 课程图谱</div>

        <div class="section-title">🧠 技能点 · 核心能力</div>
        <div class="capability-list">
          <div v-for="cap in capabilities" :key="cap.key" class="glass capability-card" :class="{ weak: cap.score>0 && cap.score < 70 }">
            <div class="cap-header">
              <span class="cap-name">{{ cap.name }}</span>
              <span class="cap-score" :class="{ low: cap.score>0 && cap.score < 70 }">{{ cap.score>0 ? cap.score+'%' : '—' }}</span>
            </div>
            <div class="cap-progress">
              <div class="cap-progress-bar" :class="cap.score>=70 ? 'cap-bar-green' : (cap.score>0?'cap-bar-red':'')" :style="{ width: cap.score+'%' }"></div>
            </div>
            <div class="cap-footer">
              <span>权重 {{ cap.weight }}%</span>
              <span v-if="cap.score===0">等待达成度</span>
              <span v-else>{{ cap.score < 70 ? '⚠ 需提升' : '✓ 已达成' }}</span>
            </div>
          </div>
        </div>

        <div class="section-title" style="margin-top:6px;">🎯 素养点 · 核心价值</div>
        <div class="capability-list">
          <div v-for="lit in literacyPoints" :key="lit.key" class="glass capability-card" :class="{ weak: lit.score>0 && lit.score < 70 }">
            <div class="cap-header">
              <span class="cap-name">{{ lit.name }}</span>
              <span class="cap-score" :class="{ low: lit.score>0 && lit.score < 70 }">{{ lit.score>0 ? lit.score+'%' : '—' }}</span>
            </div>
            <div class="cap-progress">
              <div class="cap-progress-bar" :class="lit.score>=70 ? 'cap-bar-green' : (lit.score>0?'cap-bar-red':'')" :style="{ width: lit.score+'%' }"></div>
            </div>
            <div class="cap-footer">
              <span v-if="lit.score===0">环节结束后生成</span>
              <span v-else>{{ lit.score < 70 ? '⚠ 需提升' : '✓ 已达成' }}</span>
            </div>
          </div>
        </div>

        <div class="section-title" style="margin-top:6px;">环节进度</div>
        <div class="phase-track">
          <div class="phase-track-fill" :style="{width: phaseProgress + '%'}"></div>
          <div class="phase-track-text">环节{{ phase }}/4 · {{ phaseNameMap[phase] }}</div>
        </div>
      </aside>

      <main class="content">
        <div v-if="phase===1" class="content-grid">
          <div class="glass chart-panel">
            <div class="panel-title"><span class="icon">📊</span>企业导师分项评分</div>
            <div class="score-group-blocks">
              <div class="score-group-block" v-for="g in phase1Groups" :key="g.name">
                <div class="sg-label-row">
                  <span class="sg-label-dot" :style="{background:g.name==='揽星组'?'#00dc82':'#00a8ff'}"></span>
                  <span class="sg-label">{{ g.name }}</span>
                  <span class="sg-label-score">{{ g.total }}<em>/100</em></span>
                </div>
                <div class="sg-sub-blocks">
                  <div class="sg-sub">
                    <div class="sg-sub-row"><div class="sg-sub-label">方案设计</div><div class="sg-sub-value">{{ g.design }}</div><div class="sg-sub-unit">/50</div></div>
                    <div class="sg-sub-bar"><div class="sg-sub-bar-fill" :style="{width: (g.design*2)+'%', background:'linear-gradient(90deg,#00dc82,#00a8ff)'}"></div></div>
                    <div class="sg-sub-reason" v-if="g.reason_design">{{ g.reason_design }}</div>
                  </div>
                  <div class="sg-sub">
                    <div class="sg-sub-row"><div class="sg-sub-label">汇报展示</div><div class="sg-sub-value">{{ g.pres }}</div><div class="sg-sub-unit">/40</div></div>
                    <div class="sg-sub-bar"><div class="sg-sub-bar-fill" :style="{width: (g.pres*2.5)+'%', background:'linear-gradient(90deg,#00dc82,#00a8ff)'}"></div></div>
                    <div class="sg-sub-reason" v-if="g.reason_pres">{{ g.reason_pres }}</div>
                  </div>
                  <div class="sg-sub">
                    <div class="sg-sub-row"><div class="sg-sub-label">应对质疑</div><div class="sg-sub-value">{{ g.chal }}</div><div class="sg-sub-unit">/10</div></div>
                    <div class="sg-sub-bar"><div class="sg-sub-bar-fill" :style="{width: (g.chal*10)+'%', background:'linear-gradient(90deg,#00dc82,#00a8ff)'}"></div></div>
                    <div class="sg-sub-reason" v-if="g.reason_chal">{{ g.reason_chal }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="glass chart-panel p1-radar-panel"><div class="panel-title"><span class="icon">🎯</span>五维能力对比雷达图</div><div id="p1Radar" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">💬</span>互评加分记录</div><div id="p1PeerBar" class="chart-box" style="flex:1;"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🤖</span>AI 数据采集日志</div><div class="ai-log"><div v-for="(line,i) in aiLogs" :key="i" class="ai-log-line"><span class="ai-log-time">{{ line.time }}</span><span class="ai-log-text">{{ line.text }}</span></div></div></div>
        </div>

        <div v-if="phase===2" class="phase2-wrap">
          <div class="phase2-topbar">
            <div class="phase2-topbar-left">
              <div class="phase2-topbar-logo">🤖</div>
              <div>
                <div class="phase2-topbar-title">AI助教 · 应急工单评价大屏</div>
                <div class="phase2-topbar-sub">任务8 · 工单完整性检查与风险识别 · 六组数据实时分析</div>
              </div>
            </div>
            <div class="phase2-topbar-right">
              <span class="phase2-engine-chip"><span class="dot-pulse ok"></span>AI分析引擎运行中</span>
              <span class="phase2-return">← 返回数据大屏</span>
            </div>
          </div>

          <div class="phase2-cards">
            <div class="phase2-group-card"
                 v-for="(g,i) in phase2Groups"
                 :key="g.name"
                 :style="{boxShadow:'0 0 20px '+phase2RankShadow(i)+', inset 0 0 20px rgba(0,168,255,0.03)'}">
              <div class="phase2-group-head">
                <span class="phase2-group-name">{{ g.name }}</span>
                <span class="phase2-group-rank" :style="{background:phase2RankColor(i)}">#{{ i+1 }}</span>
              </div>
              <div class="phase2-group-checks">
                <div class="phase2-group-check" :class="{ok:g.cordOk}">
                  <span class="phase2-cick">{{ g.cordOk?'✅':'⬜' }}</span>决策坐标
                </div>
                <div class="phase2-group-check" :class="{ok:g.basisOk}">
                  <span class="phase2-cick">{{ g.basisOk?'✅':'⬜' }}</span>决策依据
                </div>
                <div class="phase2-group-check" :class="{ok:g.riskOk}">
                  <span class="phase2-cick">{{ g.riskOk?'✅':'⬜' }}</span>风险对冲
                </div>
              </div>
              <div class="phase2-group-bars">
                <div class="phase2-bar-row">
                  <span class="phase2-bar-label">决策依据</span>
                  <div class="phase2-bar-track"><div class="phase2-bar-fill basis-bar" :style="{width:g.basisPct+'%'}"></div></div>
                  <span class="phase2-bar-num">{{ g.basisCount }}</span>
                </div>
                <div class="phase2-bar-row">
                  <span class="phase2-bar-label">风险对冲</span>
                  <div class="phase2-bar-track"><div class="phase2-bar-fill risk-bar" :style="{width:g.riskPct+'%'}"></div></div>
                  <span class="phase2-bar-num">{{ g.riskCount }}</span>
                </div>
              </div>
              <div class="phase2-group-footer">
                <span class="phase2-group-score" :style="{color:phase2ScoreColor(g.score)}">{{ g.score }}</span>
                <span class="phase2-group-score-label">综合质量分</span>
              </div>
            </div>
          </div>

          <div class="phase2-body">
            <div class="phase2-col">
              <div class="glass chart-panel phase2-panel">
                <div class="panel-title"><span class="icon">📊</span>各组决策依据 &amp; 风险对冲对比</div>
                <div class="phase2-legend">
                  <span class="phase2-legend-item"><span class="phase2-legend-dot" style="background:#00a8ff"></span>决策依据</span>
                  <span class="phase2-legend-item"><span class="phase2-legend-dot" style="background:#ffaa3a"></span>风险对冲</span>
                </div>
                <div id="p2CompareBar" class="chart-box" style="min-height:260px"></div>
              </div>
              <div class="glass chart-panel phase2-panel">
                <div class="panel-title"><span class="icon">🎯</span>工单质量综合雷达图（TOP3）</div>
                <div id="p2Radar" class="chart-box" style="min-height:260px"></div>
              </div>
            </div>
            <div class="phase2-col">
              <div class="glass chart-panel phase2-panel">
                <div class="panel-title"><span class="icon">📝</span>AI助教工单分析日志</div>
                <div class="phase2-triad">
                  <div class="phase2-triad-item">
                    <div class="phase2-triad-icon">📍</div>
                    <div class="phase2-triad-label">决策坐标</div>
                    <div class="phase2-triad-status ok">✔ 6/6 完整</div>
                    <div class="phase2-triad-hint">全部小组均提供</div>
                  </div>
                  <div class="phase2-triad-item">
                    <div class="phase2-triad-icon">📋</div>
                    <div class="phase2-triad-label">决策依据</div>
                    <div class="phase2-triad-status ok">✔ 6/6 完整</div>
                    <div class="phase2-triad-hint">依据条数 2~4 条</div>
                  </div>
                  <div class="phase2-triad-item">
                    <div class="phase2-triad-icon">🛡️</div>
                    <div class="phase2-triad-label">风险对冲</div>
                    <div class="phase2-triad-status warn">⚠ 4/6 需加强</div>
                    <div class="phase2-triad-hint">策略条数 2~4 条</div>
                  </div>
                </div>
                <div class="phase2-log">
                  <div v-for="(l,i) in phase2Logs" :key="i" class="phase2-log-line">
                    <span class="phase2-log-time">{{ l.time }}</span>
                    <span class="phase2-log-text">{{ l.text }}</span>
                  </div>
                </div>
              </div>
              <div class="glass chart-panel phase2-panel">
                <div class="panel-title"><span class="icon">🏆</span>工单质量综合排行榜</div>
                <div class="phase2-rank-list">
                  <div v-for="(g,i) in phase2Sorted" :key="g.name" class="phase2-rank-row">
                    <div class="phase2-rank-name">{{ g.name }}</div>
                    <div class="phase2-rank-bar-track">
                      <div class="phase2-rank-bar-fill"
                           :style="{width:g.score+'%', background:phase2RankBarColor(i)}"></div>
                    </div>
                    <div class="phase2-rank-score">
                      {{ g.score }}分
                      <span v-if="i===0" class="phase2-rank-crown">👑</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="phase===3" class="content-grid">
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🔍</span>能力观测表得分</div><div id="p3DimChart" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📊</span>各组总分对比</div><div id="p3TotalChart" class="chart-box"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📱</span>裁判组实时评分</div><div class="judge-list"><div class="judge-item" v-for="j in judges" :key="j.name"><div><div class="judge-name">{{ j.name }}（裁判）</div><div class="judge-obj">评分对象：{{ j.group }}</div></div><div style="display:flex;gap:4px;flex-wrap:wrap;"><span class="ts-tag" v-for="d in j.dims" :key="d.label">{{ d.label }} {{ d.val }}</span></div></div></div></div>
          <div class="glass chart-panel center-panel"><div class="panel-title"><span class="icon">📲</span>电子评量表 · 飞行演练</div>
            <div class="rate-qr-wrap">
              <div class="qr-box" @click="rateQrEnlarged=true">
                <img :src="rateQrUrl||''" style="width:100%;height:100%;" alt="扫码" />
              </div>
              <div class="qr-hint">扫码进入 · 可在手机端切换三组评分（安全·规划·团队·改进）</div>
              <div class="rq-link" @click="copyRateLink()" :title="'点击复制'">{{ rateLink }}</div>
              <div class="rq-btn-row">
                <button class="rate-meta-btn" @click="refreshRateQr">🔄 更新二维码</button>
                <button class="rate-meta-btn rate-clear-btn" @click="resetAllRatings">🗑️ 清零所有评分</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="phase===4" class="content-grid phase4-grid">
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🗺️</span>最终班级能力达成度热力图</div><div id="p4Heatmap" class="chart-box" style="min-height:220px;"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📝</span>改进承诺墙</div><div class="promise-input-row"><select class="promise-select" v-model="promiseGroup"><option v-for="g in groups" :key="g" :value="g">{{ g }}</option></select><input class="promise-input" v-model="promiseText" placeholder="输入改进承诺..." @keyup.enter="addPromise" /><button class="promise-btn" @click="addPromise">添加承诺</button></div><div class="promise-list"><div class="promise-item" v-for="(p,i) in promises" :key="i"><span class="pi-group" :style="{color:groupColor(p.group)}">{{ p.group }}</span><span class="pi-text">{{ p.text }}</span></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🎯</span>能力成长轨迹</div><div class="trajectory-wrap"><div><div class="traj-label">课前</div><div id="p4RadarBefore" class="traj-radar"></div></div><div class="traj-arrow"><div class="arrow-line"></div><div class="arrow-badge">+{{ avgGrowth }}分</div></div><div><div class="traj-label">课后</div><div id="p4RadarAfter" class="traj-radar"></div></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">👤</span>个人能力画像</div><div class="personal-radar-grid" id="personalRadarGrid"></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">🏅</span>本堂课荣誉榜单</div><div class="awards-row"><div class="award-card" v-for="aw in awards" :key="aw.key" @click="showPersonalRadarModal(aw.group)"><div class="award-shine"></div><div class="award-icon">{{ aw.icon }}</div><div class="award-title" :style="{color:aw.color}">{{ aw.title }}</div><div class="award-group">{{ aw.group }}</div><div class="award-reason">{{ aw.reason }}</div></div></div></div>
          <div class="glass chart-panel"><div class="panel-title"><span class="icon">📊</span>课堂数据一览</div><div class="class-summary-grid"><div class="cs-item"><div class="cs-num">{{ classAvg }}</div><div class="cs-label">班级均分</div></div><div class="cs-item"><div class="cs-num">{{ topGroup }}</div><div class="cs-label">最佳小组</div></div><div class="cs-item"><div class="cs-num">{{ maxImprove }}%</div><div class="cs-label">最大进步</div></div><div class="cs-item"><div class="cs-num">{{ promiseCount }}</div><div class="cs-label">改进承诺</div></div></div></div>
        </div>
      </main>
    </div>

    <div class="ai-bar"><div class="ai-marquee-wrap"><div class="ai-marquee"><span v-for="(l,i) in marqueeLines" :key="i"><span class="dot">●</span>{{ l }}</span></div></div></div>
    <div class="status-bar"><div class="status-left"><span id="clock">{{ clock }}</span><span>环节 {{ phase }}/4</span><span>{{ phaseNameMap[phase] }}</span></div><div>智慧低空应急运输教学平台 v2.0 · 数据实时同步</div></div>

    <div class="modal-overlay" :class="{show: showModal}" @click.self="showModal=false"><div class="modal-content"><div class="modal-header"><div class="modal-title">{{ modalTitle }}</div><button class="modal-close" @click="showModal=false">&times;</button></div><div class="modal-body"><div class="modal-layout"><div class="modal-chart"><div id="modalRadar" style="width:100%;height:260px;"></div><div class="modal-compare"><div class="compare-label">班级均值 · {{ classAvgScore }}</div><div class="progress-track" style="height:10px;"><div class="progress-fill cap-bar-blue" :style="{width:classAvgScore+'%'}"></div></div><div class="compare-label">本次得分 · {{ modalWeightedScore }}</div><div class="progress-track" style="height:12px;"><div class="progress-fill cap-bar-green" :style="{width:modalWeightedScore+'%'}"></div></div></div></div><div class="modal-info"><div class="modal-score-card"><div class="modal-score-sub">加权综合得分</div><div class="modal-score">{{ modalWeightedScore }}</div><div class="modal-badge" :class="modalWeightedScore>=85?'excellent':modalWeightedScore>=75?'good':modalWeightedScore>=60?'mid':'low'">{{ modalWeightedScore>=85?'优秀':modalWeightedScore>=75?'良好':modalWeightedScore>=60?'合格':'待提升' }}</div></div><div style="font-size:12px;color:#7a9ab8;margin:8px 0 4px;">五维得分明细</div><div v-for="(d,i) in modalDims" :key="d.name" class="modal-dim-row"><span><em>{{ d.weight }}%</em>{{ d.name }}</span><span :class="modalData[i]>=70?'ok':'warn'">{{ modalData[i] }}</span></div><div class="modal-tip">💡 权重：综合25% · 汇报20% · 演练25% · 沟通15% · 改进15%</div></div></div></div></div></div>

    <div v-if="rateQrEnlarged" class="rate-enlarge-mask" @click.self="rateQrEnlarged = false">
      <div class="rate-qr-box"><img :src="rateQrUrl||''" alt="扫码" /></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import QRCode from 'qrcode'

const GROUP_KEYS = { 1:'揽星组', 2:'御风组', 3:'巡天组', 4:'逐日组', 5:'凌云组', 6:'长空组' }
const RATE_GIDS = [1, 3, 6]
const JUDGE_MOCK_TOTAL = { 1: 87, 3: 93, 6: 86 }
const JUDGE_MOCK_COUNT = { 1: 5, 3: 6, 6: 4 }
const RATE_BASE = (location.hostname || 'localhost') + ':8000'
const rateVersion = ref(Date.now())
const rateLatest = reactive({
  1:{group_id:1,group_name:'揽星组',total:0,dims:[],count:0,updated_at:0},
  2:{group_id:2,group_name:'御风组',total:0,dims:[],count:0,updated_at:0},
  3:{group_id:3,group_name:'巡天组',total:0,dims:[],count:0,updated_at:0},
  4:{group_id:4,group_name:'逐日组',total:0,dims:[],count:0,updated_at:0},
  5:{group_id:5,group_name:'凌云组',total:0,dims:[],count:0,updated_at:0},
  6:{group_id:6,group_name:'长空组',total:0,dims:[],count:0,updated_at:0},
})
const rateQrUrl = ref('')
const rateLink = ref('')
const rateQrEnlarged = ref(false)

async function _refreshQr() {
  const url = `${location.protocol}//${location.host}/evaluation/task8/rate?v=${rateVersion.value}`
  rateLink.value = url
  try {
    rateQrUrl.value = await QRCode.toDataURL(url, { width: 280, margin: 1, color:{ dark:'#0a1628', light:'#ffffff' } })
  } catch(e) { rateQrUrl.value = '' }
}
function refreshRateQr() { rateVersion.value = Date.now(); _refreshQr() }
function copyRateLink() {
  if (navigator.clipboard) navigator.clipboard.writeText(rateLink.value||'').catch(()=>{})
  else { const ta = document.createElement('textarea'); ta.value = rateLink.value||''; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta) }
}
async function resetAllRatings() {
  try { await fetch(`${location.protocol}//${RATE_BASE}/api/ratings/reset_all`, { method:'POST' }) } catch(e){}
  for (const k in rateLatest) {
    Object.assign(rateLatest[k], { total:0, dims:[], count:0, updated_at:0 })
  }
  refreshRateQr()
}
async function _pollRatings() {
  try {
    const base = `${location.protocol}//${RATE_BASE}/api/ratings/latest_all`
    const r = await fetch(base)
    const j = await r.json()
    for (const gid in j) {
      if (rateLatest[gid]) Object.assign(rateLatest[gid], j[gid])
    }
  } catch(e) {}
}
let _rateTimer = null
let _rateTimer2 = null
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
const modalDims = [{ name:'运输方案优化与汇报', weight:20 },{ name:'应急响应预案制定', weight:20 },{ name:'飞行前准备应急综合演练', weight:20 },{ name:'应急任务工单填写', weight:20 },{ name:'物资投送应急综合演练', weight:20 }]
const groups = ['揽星组','御风组','巡天组','逐日组','凌云组','长空组']
const groups2 = [{ name:'揽星组', design:45, pres:36, chal:8, total:89 },{ name:'御风组', design:42, pres:37, chal:7, total:86 },{ name:'巡天组', design:44, pres:35, chal:9, total:88 },{ name:'逐日组', design:38, pres:32, chal:6, total:76 }]
const phase1Groups = ref([
  { name:'揽星组', design:0, pres:0, chal:0, total:0, reason_design:'', reason_pres:'', reason_chal:'' },
  { name:'御风组', design:0, pres:0, chal:0, total:0, reason_design:'', reason_pres:'', reason_chal:'' }
])
const phase1GroupsTarget = [
  { name:'揽星组', design:46, pres:36, chal:8, total:90, reason_design:'逻辑完整、安全冗余量化到位、动态航程约束有创新', reason_pres:'数据扎实、表达清晰，但时间控制稍紧', reason_chal:'面对地形爬升问题，能快速回应并承诺改进' },
  { name:'御风组', design:42, pres:35, chal:9, total:86, reason_design:'极端天气备份航线考虑周全，但冗余偏重', reason_pres:'团队配合默契、演示流畅', reason_chal:'应对自如，补充两个改进点' }
]
const phase1PeerData = ref([
  { group:'揽星组', val:0 },
  { group:'御风组', val:0 }
])
const phase1PeerDataTarget = [
  { group:'揽星组', val:5 },
  { group:'御风组', val:5 }
]
const demo1Running = ref(false)
const demo1Done = ref(false)
const demo2Running = ref(false)
const demo2Done = ref(false)
const demo3Running = ref(false)
const demo3Done = ref(false)
const aiLogs = ref([])
const aiLogsFull = [
  { time:'14:32:05', text:'揽星组企业导师评分录入成功：方案设计46分' },
  { time:'14:32:08', text:'揽星组企业导师评分录入成功：汇报展示36分' },
  { time:'14:32:11', text:'揽星组企业导师评分录入成功：应对质疑8分' },
  { time:'14:32:12', text:'AI雷达图更新：揽星组综合方案设计能力+46分' },
  { time:'14:35:22', text:'御风组企业导师评分录入成功：方案设计42分' },
  { time:'14:35:25', text:'御风组企业导师评分录入成功：汇报展示37分' },
  { time:'14:35:28', text:'御风组企业导师评分录入成功：应对质疑7分' },
  { time:'14:35:30', text:'AI雷达对比雷达图生成完毕' },
  { time:'14:38:15', text:'互评环节：揽星组点评御风组+5分' },
  { time:'14:38:18', text:'互评环节：御风组点评揽星组+5分' },
  { time:'14:38:20', text:'环节一数据采集完成，热力图刷新中...' }
]

function resetDemo(p) {
  _clearAnim()
  if (p === 1 || p === undefined) {
    phase1Groups.value = phase1Groups.value.map(g => ({ ...g, design:0, pres:0, chal:0, total:0, reason_design:'', reason_pres:'', reason_chal:'' }))
    phase1PeerData.value = phase1PeerData.value.map(p => ({ ...p, val:0 }))
    aiLogs.value = []
    demo1Done.value = false
    demo1Running.value = false
    capabilities.forEach(c => { c.score = 0 })
    knowledgePoints.forEach(k => { k.mastered = null })
    literacyPoints.forEach(l => { l.score = 0 })
  }
  if (p === 2 || p === undefined) {
    phase2Groups.forEach(g=>{ g.score = 0; g.basisPct = 0; g.riskPct = 0; g.basisCount = 0; g.riskCount = 0 })
    phase2Logs.value = []
    _disposePhase2Charts()
    const barEl = document.getElementById('p2CompareBar'); if (barEl) barEl.innerHTML = ''
    const radarEl = document.getElementById('p2Radar'); if (radarEl) radarEl.innerHTML = ''
    demo2Done.value = false
    demo2Running.value = false
    // 重置环节2的技能点，保留环节1的
    capabilities.forEach(c => { if (c.phase === 2) c.score = 0 })
  }
  if (p === 3 || p === undefined) {
    demo3Done.value = false
    demo3Running.value = false
    judges.forEach(j => { j.dims.forEach(d => { d.val = 0 }) })
    RATE_GIDS.forEach(gid => { rateLatest[gid].total = 0; rateLatest[gid].count = 0 })
    // 重置环节3的技能点，保留环节1和2的
    capabilities.forEach(c => { if (c.phase === 3) c.score = 0 })
  }
  if (p !== 2) renderPhaseCharts()
}

function runDemo(p) {
  if (p === 1) {
    if (demo1Running.value) return
    _clearAnim()
    demo1Running.value = true
    phase1Groups.value = phase1Groups.value.map(g => ({ ...g, design:0, pres:0, chal:0, total:0, reason_design:'', reason_pres:'', reason_chal:'' }))
    phase1PeerData.value = phase1PeerData.value.map(p => ({ ...p, val:0 }))
    aiLogs.value = []
    capabilities.forEach(c => { c.score = 0 })
    knowledgePoints.forEach(k => { k.mastered = null })
    literacyPoints.forEach(l => { l.score = 0 })
    renderPhaseCharts()
    setTimeout(() => {
      animateGroups()
      animatePeer()
      animateLogs()
    }, 2000)
  } else if (p === 2) {
    if (demo2Running.value) return
    _clearAnim()
    demo2Running.value = true
    demo2Done.value = false
    // 保留环节1的技能点分数，只重置环节2和3的
    capabilities.forEach(c => { if (c.phase !== 1) c.score = 0 })
    renderPhaseCharts()
    animateDemo2()
  } else if (p === 3) {
    if (demo3Running.value) return
    _clearAnim()
    demo3Running.value = true
    demo3Done.value = false
    // 保留环节1和2的技能点分数，只重置环节3的
    capabilities.forEach(c => { if (c.phase === 3) c.score = 0 })
    judges.forEach(j => { j.dims.forEach(d => { d.val = 0 }) })
    renderPhaseCharts()
    RATE_GIDS.forEach(gid => { rateLatest[gid].total = 0; rateLatest[gid].count = 0 })
    const dimChart = chartInstances.find(c => c._phase3Type === 'dim')
    const totalChart = chartInstances.find(c => c._phase3Type === 'total')
    const colors3 = ['#00a8ff','#00dc82','#ffaa3a']
    const easeInOutCubic = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
    // 每个维度独立配置：起评时间不同、评分速度不同
    const dimConfs = []
    JUDGE_TARGETS.forEach((tgt, gi) => {
      tgt.dims.forEach((td, di) => {
        dimConfs.push({
          gi, di, target: td.val,
          delay: Math.floor(Math.random() * 45) + 3,
          duration: Math.floor(Math.random() * 80) + 45,
        })
      })
    })
    // 三小组总分/人数独立配置
    const rateConfs = [[87,5],[93,6],[86,4]].map(([t,c]) => ({
      totalTarget: t, countTarget: c,
      delay: Math.floor(Math.random() * 30) + 5,
      duration: Math.floor(Math.random() * 60) + 50,
    }))
    // judge 索引 → gid 映射（揽星组=1, 巡天组=3, 长空组=6）
    const judgeGidMap = [6, 1, 3]
    let step = 0
    const tick = () => {
      step++
      let allDone = true
      dimConfs.forEach(cfg => {
        const local = step - cfg.delay
        if (local <= 0) { judges[cfg.gi].dims[cfg.di].val = 0; allDone = false; return }
        const t = Math.min(1, local / cfg.duration)
        judges[cfg.gi].dims[cfg.di].val = Math.round(cfg.target * easeInOutCubic(t))
        if (t < 1) allDone = false
      })
      // 电子评量表分数 = 对应裁判维度和
      rateConfs.forEach((rc, i) => {
        const local = step - rc.delay
        if (local <= 0) { allDone = false; return }
        const t = Math.min(1, local / rc.duration)
        const gid = judgeGidMap[i]
        rateLatest[gid].total = Math.round(rc.totalTarget * easeInOutCubic(t))
        rateLatest[gid].count = Math.round(rc.countTarget * easeInOutCubic(t))
        if (t < 1) allDone = false
      })
      // 刷新能力观测表（每个柱子直接读 judges 的当前值）
      if (dimChart) {
        dimChart.setOption({ series: JUDGE_TARGETS.map((tgt, idx) => ({
          name: tgt.group, type: 'bar',
          data: judges[idx].dims.map(d => d.val)
        })) }, false)
      }
      // 各组总分对比 = 各 judge dims 求和
      if (totalChart) {
        totalChart.setOption({ series:[{
          type: 'bar',
          data: JUDGE_TARGETS.map((tgt, idx) => {
            const total = judges[idx].dims.reduce((s, d) => s + d.val, 0)
            return {
              value: total,
              itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: colors3[idx] }, { offset: 1, color: colors3[idx] }] } }
            }
          }),
          barWidth: 40,
          label: { show: true, position: 'top', formatter: '{c}分', color: '#c8d4e0', fontSize: 14, fontWeight: 'bold' },
          markLine: { silent: true, data: [{ type: 'average', name: '平均' }], lineStyle: { color: 'rgba(0,168,255,0.3)', type: 'dashed' }, label: { color: '#5a7a9a', fontSize: 10, formatter: '平均 {c}' } }
        }] }, false)
      }
      if (allDone) {
        JUDGE_TARGETS.forEach((tgt, gi) => {
          tgt.dims.forEach((td, di) => { judges[gi].dims[di].val = td.val })
        })
        judgeGidMap.forEach((gid, i) => {
          rateLatest[gid].total = [[87,5],[93,6],[86,4]][i][0]
          rateLatest[gid].count = [[87,5],[93,6],[86,4]][i][1]
        })
        if (dimChart) dimChart.setOption({ series: JUDGE_TARGETS.map(tgt => ({ name: tgt.group, type:'bar', data: tgt.dims.map(d => d.val) })) }, false)
        if (totalChart) totalChart.setOption({ series:[{
          type:'bar',
          data: JUDGE_TARGETS.map((tgt, idx) => ({
            value: tgt.dims.reduce((s,d)=>s+d.val,0),
            itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:colors3[idx]},{offset:1,color:colors3[idx]}]}}
          })),
          barWidth:40,
          label:{show:true, position:'top', formatter:'{c}分', color:'#c8d4e0', fontSize:14, fontWeight:'bold'},
          markLine:{silent:true, data:[{type:'average',name:'平均'}], lineStyle:{color:'rgba(0,168,255,0.3)',type:'dashed'},label:{color:'#5a7a9a',fontSize:10,formatter:'平均 {c}'}}
        }] }, false)
        // 环节3显示应急任务工单填写（只更新环节3的技能点）
        const capTargets3 = [0, 0, 0, 88, 0]
        capabilities.forEach((c, i) => {
          if (capTargets3[i] === 0) return
          c.score = capTargets3[i]
        })
        demo3Running.value = false
        demo3Done.value = true
      }
    }
    _animInterval(tick, 80)
  }
}

function animateGroups() {
  const steps = 28
  const targets = phase1GroupsTarget
  const groupAnim = (gi, field) => {
    const target = targets[gi][field]
    let step = 0
    _animInterval(() => {
      step++
      phase1Groups.value[gi][field] = Math.round(target * step / steps)
      if (step >= steps) {
        phase1Groups.value[gi][field] = target
      }
    }, 30)
  }
  groupAnim(0, 'design')
  groupAnim(0, 'pres')
  groupAnim(0, 'chal')
  setTimeout(() => groupAnim(0, 'total'), 400)
  groupAnim(1, 'design')
  groupAnim(1, 'pres')
  groupAnim(1, 'chal')
  setTimeout(() => groupAnim(1, 'total'), 400)
  setTimeout(() => {
    phase1Groups.value.forEach((g, i) => {
      g.reason_design = targets[i].reason_design
      g.reason_pres = targets[i].reason_pres
      g.reason_chal = targets[i].reason_chal
    })
    renderPhaseCharts()
  }, 900)
}

function animateDemo2() {
  phase2Logs.value = []
  phase2Groups.forEach((g,i)=>{ g.score = 0; g.basisPct = 0; g.riskPct = 0; g.basisCount = 0; g.riskCount = 0; })
  _renderPhase2Charts(true)
  _animTimeout(()=>{
    const steps = 22
    let step = 0
    _animInterval(()=>{
      step++
      phase2Groups.forEach(g=>{
        g.basisCount = Math.round(g._basis * step / steps)
        g.riskCount = Math.round(g._risk * step / steps)
        g.basisPct = Math.round(100 * g.basisCount / Math.max(1, g._basis))
        g.riskPct = Math.round(100 * g.riskCount / Math.max(1, g._risk))
        g.score = Math.round(g._score * step / steps)
      })
      if (step >= steps) {
        phase2Groups.forEach(g=>{
          g.basisCount = g._basis; g.riskCount = g._risk
          g.basisPct = Math.round(100 * g._basis / 4)
          g.riskPct = Math.round(100 * g._risk / 4)
          g.score = g._score
        })
        _renderPhase2Charts(false)
        // 环节2显示应急响应预案制定、飞行前准备应急综合演练、物资投送应急综合演练
        const capTargets2 = [0, 82, 78, 0, 85]
        capabilities.forEach((c, i) => {
          if (capTargets2[i] === 0) return
          c.score = capTargets2[i]
        })
        phase2LogsFull.forEach((l, idx)=>{
          _animTimeout(()=>{
            phase2Logs.value.push({ time:l.time, text:l.text })
            if (idx === phase2LogsFull.length - 1) {
              demo2Running.value = false; demo2Done.value = true
            }
          }, 260 * idx)
        })
      }
    }, 42)
  }, 300)
}

let _p2BarChart = null
let _p2RadarChart = null
function _renderPhase2Charts(isInit) {
  const bar = document.getElementById('p2CompareBar')
  const radar = document.getElementById('p2Radar')
  const names = phase2Groups.map(g=>g.name)
  const basisVals = phase2Groups.map(g=>g.basisCount)
  const riskVals = phase2Groups.map(g=>g.riskCount)
  if (bar) {
    if (isInit || !_p2BarChart) {
      if (_p2BarChart) try { _p2BarChart.dispose() } catch(e){}
      _p2BarChart = echarts.init(bar)
    }
    _p2BarChart.setOption({
      animation: false, animationDuration: 0,
      tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
      legend:{data:['决策依据','风险对冲'], textStyle:{color:'#6b8cae', fontSize:12}, top:0, right:10, itemWidth:22, itemHeight:14},
      grid:{left:40,right:30,top:44,bottom:24},
      xAxis:{type:'category', data:names, axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:11}},
      yAxis:{type:'value', max:6, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#4a6a8a', fontSize:10}},
      series:[
        { name:'决策依据', type:'bar', data:basisVals, barWidth:18, barGap:'12%',
          itemStyle:{color:'#00a8ff', borderRadius:[4,4,0,0]},
          label:{show:true, position:'top', formatter:'{c}条', color:'#00a8ff', fontSize:11, fontWeight:'bold'} },
        { name:'风险对冲', type:'bar', data:riskVals, barWidth:18,
          itemStyle:{color:'#ffaa3a', borderRadius:[4,4,0,0]},
          label:{show:true, position:'top', formatter:'{c}条', color:'#ffaa3a', fontSize:11, fontWeight:'bold'} }
      ]
    }, true)
    _p2BarChart.resize()
  }
  if (radar) {
    if (isInit || !_p2RadarChart) {
      if (_p2RadarChart) try { _p2RadarChart.dispose() } catch(e){}
      _p2RadarChart = echarts.init(radar)
    }
    const top3 = phase2Sorted.value.slice(0,3)
    _p2RadarChart.setOption({
      animation: false, animationDuration: 0,
      legend:{data:top3.map(g=>g.name), textStyle:{color:'#c8e4ff', fontSize:12}, bottom:2, left:'center', itemWidth:18, itemHeight:10},
      radar:{
        indicator:[
          {name:'决策坐标完整度', max:100},
          {name:'决策依据充分性', max:100},
          {name:'风险对冲强度', max:100},
          {name:'三要素均衡度', max:100},
          {name:'综合质量分', max:100}
        ],
        shape:'polygon', radius:'68%', center:['50%','42%'],
        axisName:{color:'#e0f5ff', fontSize:11, fontWeight:'bold'},
        splitArea:{areaStyle:{color:['rgba(0,168,255,0.04)','rgba(0,220,180,0.08)']}},
        axisLine:{lineStyle:{color:'rgba(0,168,255,0.25)'}},
        splitLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}
      },
      series:[{ type:'radar', animation: false, animationDuration: 0, data: top3.map((g)=>({
        value:[
          g.cordOk?100:60,
          Math.round(g.basisPct),
          Math.round(g.riskPct),
          Math.round((g.basisPct+g.riskPct+(g.cordOk?100:0))/3),
          g.score
        ],
        name:g.name,
        lineStyle:{width:3},
        areaStyle:{opacity:0.22},
        itemStyle:{symbol:'circle', symbolSize:7}
      })) }],
      color:['#00dc82','#00a8ff','#ffaa3a']
    }, true)
    _p2RadarChart.resize()
  }
}

function _disposePhase2Charts() {
  if (_p2BarChart) { try { _p2BarChart.dispose() } catch(e){} _p2BarChart = null }
  if (_p2RadarChart) { try { _p2RadarChart.dispose() } catch(e){} _p2RadarChart = null }
}

function animatePeer() {
  setTimeout(() => {
    phase1PeerData.value[0].val = phase1PeerDataTarget[0].val
    renderPhaseCharts()
  }, 800)
  setTimeout(() => {
    phase1PeerData.value[1].val = phase1PeerDataTarget[1].val
    renderPhaseCharts()
  }, 1600)
  setTimeout(() => {
    // 环节1只显示运输方案优化与汇报
    const capTargets = [77, 0, 0, 0, 0]
    capabilities.forEach((c, i) => {
      if (capTargets[i] === 0) return
      let step = 0, steps = 20, t = capTargets[i]
      _animInterval(() => {
        step++
        c.score = Math.round(t * step / steps)
        if (step >= steps) { c.score = t }
      }, 120)
    })
    knowledgePoints[0].mastered = true
    knowledgePoints[1].mastered = true
    knowledgePoints[2].mastered = true
    const litTargets = [82, 80]
    literacyPoints.forEach((l, i) => {
      let step = 0, steps = 20, t = litTargets[i]
      _animInterval(() => {
        step++
        l.score = Math.round(t * step / steps)
        if (step >= steps) { l.score = t }
      }, 30)
    })
    setTimeout(() => {
      demo1Running.value = false
      demo1Done.value = true
    }, 700)
  }, 1900)
}

function animateLogs() {
  aiLogs.value = []
  aiLogsFull.forEach((l, i) => {
    setTimeout(() => {
      aiLogs.value.push({ time:l.time, text:l.text })
    }, 500 + i * 500)
  })
}
const capabilities = reactive([
  { key:'design', name:'运输方案优化与汇报', score:0, weight:20, indicators:['方案逻辑完整性','AI评分复盘','企业反馈整合','汇报表达清晰度'], phase: 1 },
  { key:'present', name:'应急响应预案制定', score:0, weight:20, indicators:['突发事件识别','处置流程规范','预案可执行性','风险缓控措施'], phase: 2 },
  { key:'drillCmd', name:'飞行前准备应急综合演练', score:0, weight:20, indicators:['规划调整能力','突发故障应对','飞行前检查完整','决策速度'], phase: 2 },
  { key:'comm', name:'应急任务工单填写', score:0, weight:20, indicators:['工单三要素完整','异常处置记录','决策依据清晰','信息传递准确'], phase: 3 },
  { key:'improve', name:'物资投送应急综合演练', score:0, weight:20, indicators:['物资装载规范','航线规划合理','精准投放控制','安全裕度保障'], phase: 2 }
])

const knowledgePoints = reactive([
  { key:'ticket', name:'工单三要素', mastered:null },
  { key:'team', name:'团队协作', mastered:null },
  { key:'safety', name:'安全文化与责任担当', mastered:null }
])

const literacyPoints = reactive([
  { key:'team', name:'团队协作', score:0, weight:50 },
  { key:'safety', name:'安全文化与责任担当', score:0, weight:50 }
])
const personalRadar = { '揽星组':[45,36,55,48,52], '御风组':[42,37,58,55,50], '巡天组':[40,34,60,50,54], '逐日组':[38,32,50,45,48], '凌云组':[41,35,52,47,50], '长空组':[39,33,54,49,51] }
const awards = [
  { key:'pilot', icon:'🏆', title:'领航能手', group:'揽星组', reason:'综合方案设计77分领先，安全冗余量化获企业导师认可', color:'#ffd24d' },
  { key:'craftsman', icon:'⚙️', title:'领航工匠', group:'巡天组', reason:'方案综合得分93分全班最高，应急决策工单质量最佳', color:'#00dc82' },
  { key:'apprentice', icon:'🌱', title:'领航学徒', group:'逐日组', reason:'跨部门协调沟通进步显著，课后改进承诺具体可执行', color:'#00a8ff' },
  { key:'progress', icon:'🚀', title:'进步之星', group:'御风组', reason:'成果汇报展示从课前55分提升至75分，进步达36%', color:'#c870ff' }
]
const marqueeLines = ['揽星组得分已录入，班级能力雷达图更新中……','当前最弱能力点：持续改进优化（68分）','御风组"成果汇报展示"得分37分','工单分析完毕，巡天组应急决策能力93分领先','AI助教小翼在线 · 数据采集正常','五维雷达图实时刷新中……']
const peerLogs = [{ time:'14:38:15', text:'揽星组点评御风组 +5分' },{ time:'14:38:18', text:'御风组点评揽星组 +5分' },{ time:'14:38:20', text:'环节一数据采集完成，热力图刷新中...' }]
const drillProgress = [{ label:'逐日组工单', v:75 },{ label:'揽星组工单', v:88 },{ label:'御风组工单', v:82 },{ label:'巡天组工单', v:92 }]
const JUDGE_TARGETS = [
  { name:'黄雅诗', group:'长空组', dims:[{label:'安全',val:31},{label:'规划',val:30},{label:'团队',val:13},{label:'改进',val:12}] },
  { name:'黄怀理', group:'揽星组', dims:[{label:'安全',val:33},{label:'规划',val:32},{label:'团队',val:12},{label:'改进',val:10}] },
  { name:'张静怡', group:'巡天组', dims:[{label:'安全',val:36},{label:'规划',val:30},{label:'团队',val:15},{label:'改进',val:12}] }
]
const judges = reactive(JUDGE_TARGETS.map(j => ({
  name: j.name, group: j.group,
  dims: j.dims.map(d => ({ label: d.label, val: 0 }))
})))
const teacherComments = reactive([
  { name:'王 · 应急救援', role:'企业导师', color:'#00dc82', time:'14:42', group:'揽星组', text:'方案设计能考虑地形损耗，很专业！建议加入极端天气的备份航线预案。', tags:['方案设计+8','应对质疑+6','综合能力'] },
  { name:'李 · 无人机系统', role:'主讲教师', color:'#00a8ff', time:'14:45', group:'巡天组', text:'应急推演的工单三要素写得清晰，尤其是RFID标识的漏项提醒，值得全组推广。', tags:['演练组织+7','规范意识+5','亮点'] },
  { name:'陈 · 飞行演练', role:'飞行教练', color:'#c870ff', time:'14:48', group:'逐日组', text:'跨部门沟通环节，逐日组主动承担了地面引导任务，团队协作加分！', tags:['协调沟通+9','团队协作','加分'] },
  { name:'刘 · 安全保障', role:'安全员', color:'#ffaa3a', time:'14:52', group:'御风组', text:'飞行演练的电量双控策略不错，但要注意低温环境下锂电池的放电倍率限制。', tags:['安全规范+6','风险提示','改进建议'] }
])
const phase2Groups = reactive([
  { name:'揽星组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:100, _basis:4, _risk:4 },
  { name:'长空组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:100, _basis:4, _risk:4 },
  { name:'凌云组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:100, _basis:4, _risk:4 },
  { name:'御风组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:88,  _basis:4, _risk:3 },
  { name:'逐日组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:75,  _basis:3, _risk:2 },
  { name:'巡天组', cordOk:true, basisOk:true, riskOk:true, basisPct:0, riskPct:0, basisCount:0, riskCount:0, score:0, _score:63,  _basis:3, _risk:2 },
])
const phase2Sorted = computed(() => {
  const copy = phase2Groups.slice().sort((a,b)=>b.score-a.score)
  return copy
})
const phase2Logs = ref([])
const phase2LogsFull = [
  { time:'14:36:02', text:'[揽星组] 决策坐标 · 配送中心+3需求点完整录入，经纬度校验通过' },
  { time:'14:36:18', text:'[长空组] 决策依据 · 提交航线规划依据 4 条（载重/航程/风速/地形）' },
  { time:'14:36:34', text:'[凌云组] 风险对冲 · 三备份策略填写：电量双控+气象+通信' },
  { time:'14:37:05', text:'[御风组] 风险对冲条数偏少（3/4），AI建议补充备份航线预案' },
  { time:'14:37:22', text:'[逐日组] 决策依据 3 条 · 缺少地形爬升损耗公式，建议加强' },
  { time:'14:37:48', text:'[巡天组] 风险对冲 2 条 · 建议增加低温锂电池放电特性相关预案' },
  { time:'14:38:10', text:'[AI引擎] 六组工单三要素完整性扫描完毕，正在生成综合质量分' },
  { time:'14:38:32', text:'[AI引擎] TOP3 · 揽星/长空/凌云 三组综合质量 100 分' },
]
function phase2RankColor(i) {
  return ['#00dc82','#00a8ff','#00a8ff','#ffaa3a','#ff8c5a','#ff6b50'][i] || '#00a8ff'
}
function phase2RankShadow(i) {
  return ['rgba(0,220,130,0.4)','rgba(0,168,255,0.35)','rgba(0,168,255,0.3)','rgba(255,170,58,0.25)','rgba(255,140,90,0.2)','rgba(255,107,80,0.2)'][i] || 'transparent'
}
function phase2RankBarColor(i) {
  return ['linear-gradient(90deg,#00dc82,#00a8ff)','linear-gradient(90deg,#00a8ff,#00dc82)','linear-gradient(90deg,#00a8ff,#00dc82)','linear-gradient(90deg,#00a8ff,#00a8ff)','linear-gradient(90deg,#00dc82,#00a8ff)','linear-gradient(90deg,#ffaa3a,#00a8ff)'][i] || 'linear-gradient(90deg,#00a8ff,#00dc82)'
}
function phase2ScoreColor(s) {
  if (s >= 95) return '#00dc82'
  if (s >= 85) return '#00a8ff'
  if (s >= 70) return '#ffaa3a'
  return '#ff6b50'
}

const classAvgScore = ref(76)
const classAvg = computed(()=>classAvgScore.value)
const topGroup = computed(()=>{
  let best='', max=0
  groups.forEach(g=>{ const s=personalRadar[g].reduce((a,b)=>a+b,0)/5; if(s>max){max=s;best=g} })
  return best
})
const maxImprove = computed(()=>{
  let max=0
  groups.forEach(g=>{ const before=personalRadar[g].map(v=>Math.round(v*0.72)); const after=personalRadar[g]; const bAvg=before.reduce((a,v)=>a+v,0)/5; const aAvg=after.reduce((a,v)=>a+v,0)/5; const imp=bAvg>0?Math.round((aAvg-bAvg)/bAvg*100):0; if(imp>max)max=imp })
  return max
})
const promiseCount = computed(()=>promises.length)
const promiseText = ref('')
const promiseGroup = ref('揽星组')
const promises = reactive([
  { group:'揽星组', text:'我们会把地形爬升损耗公式纳入动态航程约束模型。' },
  { group:'御风组', text:'我们会把电量优先规则写进协同策略，并增加温控检查清单。' },
  { group:'巡天组', text:'建立单电切换三步确认口诀：一改参数、二按卡扣、三听自检。' },
  { group:'逐日组', text:'把安全约束数字化模板写进智能体预设规则，下次推演一键调用。' },
  { group:'凌云组', text:'应急推演中补充极端天气备份航线预案，加入风阻补偿系数。' },
  { group:'长空组', text:'完善工单三要素的RFID校验步骤，避免标识漏项。' }
])
function addPromise() { const t = promiseText.value.trim(); if (!t) { promiseText.value=''; return } promises.unshift({ group:promiseGroup.value, text:t }); promiseText.value='' }

function groupColor(g) {
  const map = {'揽星组':'#00dc82','长空组':'#00a8ff','凌云组':'#ffaa3a','御风组':'#c870ff','逐日组':'#ff6b6b','巡天组':'#ffd24d'}
  return map[g] || '#8ab4d0'
}
const avgGrowth = computed(() => {
  const before = [45,36,55,48,52,42,37,58,55,50,40,34,60,50,54,38,32,50,45,48,41,35,52,47,50,39,33,54,49,51]
  const after = personalRadar
  let total = 0, count = 0
  for (const g of groups) { const b = after[g].map(v=>Math.round(v*0.72)); const a = after[g]; total += a.reduce((s,v,i)=>s+v-b[i],0); count += a.length }
  return Math.round(total/count)
})

function dimsLabels() { return ['运输方案优化与汇报','应急响应预案制定','飞行前准备应急综合演练','应急任务工单填写','物资投送应急综合演练'] }

let chartInstances = []
let _animTimers = []
function _clearAnim() { _animTimers.forEach(t=>{ try{clearInterval(t)}catch(e){} try{clearTimeout(t)}catch(e){} }); _animTimers=[] }
function _animInterval(fn, ms) { const t = setInterval(fn, ms); _animTimers.push(t); return t }
function _animTimeout(fn, ms) { const t = setTimeout(fn, ms); _animTimers.push(t); return t }

function renderPhaseCharts() {
  chartInstances.forEach(c=>{try{c.dispose()}catch(e){}}); chartInstances=[]
  const dims5 = dimsLabels()
  if (phase.value === 1) {
    const groups1 = phase1Groups.value
    const peer1 = phase1PeerData.value
    const hasData = phase.value === 1 ? (demo1Done.value || demo1Running.value) :
                    phase.value === 2 ? (demo2Done.value || demo2Running.value) :
                                        (demo3Done.value || demo3Running.value)
    const el = document.getElementById('p1Radar'); if (el) {
      if (!hasData) { el.innerHTML = ''; }
      else {
        const c = echarts.init(el); chartInstances.push(c)
        c.setOption({
          animation: false, animationDuration: 0,
          tooltip:{}, legend:{data:groups1.map(g=>g.name), textStyle:{color:'#c8e4ff', fontSize:14}, bottom:4, left:'center', itemWidth:18, itemHeight:10},
          radar:{indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'76%', center:['50%','42%'], axisName:{color:'#e0f5ff', fontSize:13, fontWeight:'bold'}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.05)','rgba(0,168,255,0.1)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.25)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}} },
          series:[{ type:'radar', animation: false, animationDuration: 0, data: groups1.map(g=>({
            value:[
              Math.min(100, Math.round(g.design * 1.4 + 10)),
              Math.min(100, Math.round(g.pres * 1.6 + 10)),
              Math.min(100, Math.round(g.chal * 5 + 35)),
              g.total,
              Math.min(100, Math.round((g.design + g.pres) * 0.7 + 25))
            ],
            name:g.name, lineStyle:{width:3}, areaStyle:{opacity:0.22}, itemStyle:{symbol:'circle', symbolSize:8}
          })) }],
          color:['#00a8ff','#00dc82']
        })
      }
    }
    const peer = document.getElementById('p1PeerBar'); if (peer) {
      if (!hasData) { peer.innerHTML = ''; }
      else {
        const c = echarts.init(peer); chartInstances.push(c)
        c.setOption({
          animation: false, animationDuration: 0,
          tooltip:{trigger:'axis'},
          grid:{left:40,right:20,top:40,bottom:24},
          xAxis:{type:'category', data:peer1.map(p=>p.group), axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:13}},
          yAxis:{type:'value', max:10, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#5a7a9a', fontSize:11}},
          series:[{ type:'bar', animation: false, animationDuration: 0, data: peer1.map(p=>({
            value:p.val,
            itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#ff9a3a'},{offset:1,color:'#c76400'}]},borderRadius:[6,6,0,0]},
            label:{show:p.val>0, position:'top', formatter:'+{c}分', color:'#ff9a3a', fontSize:13, fontWeight:'bold'}
          })), barWidth:42 }]
        })
      }
    }
  } else if (phase.value === 2) {
    const bar = document.getElementById('p2CompareBar')
    if (bar) {
      const c = echarts.init(bar); chartInstances.push(c)
      const names = phase2Groups.map(g=>g.name)
      const basisVals = phase2Groups.map(g=>g.basisCount)
      const riskVals = phase2Groups.map(g=>g.riskCount)
      c.setOption({
        tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
        legend:{data:['决策依据','风险对冲'], textStyle:{color:'#6b8cae', fontSize:13}, top:2, right:10, itemWidth:22, itemHeight:14},
        grid:{left:40,right:30,top:50,bottom:28},
        xAxis:{type:'category', data:names, axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:12}},
        yAxis:{type:'value', max:6, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#4a6a8a', fontSize:10}},
        series:[
          { name:'决策依据', type:'bar', data:basisVals, barWidth:20, barGap:'10%',
            itemStyle:{color:'#00a8ff', borderRadius:[4,4,0,0]},
            label:{show:true, position:'top', formatter:'{c}条', color:'#00a8ff', fontSize:12, fontWeight:'bold'} },
          { name:'风险对冲', type:'bar', data:riskVals, barWidth:20,
            itemStyle:{color:'#ffaa3a', borderRadius:[4,4,0,0]},
            label:{show:true, position:'top', formatter:'{c}条', color:'#ffaa3a', fontSize:12, fontWeight:'bold'} }
        ]
      })
    }
    const r = document.getElementById('p2Radar')
    if (r) {
      const top3 = phase2Sorted.value.slice(0,3)
      const c = echarts.init(r); chartInstances.push(c)
      c.setOption({
        animation: false, animationDuration: 0,
        legend:{data:top3.map(g=>g.name), textStyle:{color:'#c8e4ff', fontSize:13}, bottom:2, left:'center', itemWidth:18, itemHeight:10},
        radar:{
          indicator:[
            {name:'决策坐标完整度', max:100},
            {name:'决策依据充分性', max:100},
            {name:'风险对冲强度', max:100},
            {name:'三要素均衡度', max:100},
            {name:'综合质量分', max:100}
          ],
          shape:'polygon', radius:'70%', center:['50%','40%'],
          axisName:{color:'#e0f5ff', fontSize:12, fontWeight:'bold'},
          splitArea:{areaStyle:{color:['rgba(0,168,255,0.04)','rgba(0,220,180,0.08)']}},
          axisLine:{lineStyle:{color:'rgba(0,168,255,0.25)'}},
          splitLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}
        },
        series:[{ type:'radar', animation: false, animationDuration: 0, data: top3.map((g,i)=>({
          value:[
            g.cordOk?100:60,
            Math.round(g.basisPct),
            Math.round(g.riskPct),
            Math.round((g.basisPct+g.riskPct+(g.cordOk?100:0))/3),
            g.score
          ],
          name:g.name,
          lineStyle:{width:3},
          areaStyle:{opacity:0.22},
          itemStyle:{symbol:'circle', symbolSize:7}
        })) }],
        color:['#00dc82','#00a8ff','#ffaa3a']
      })
    }
  } else if (phase.value === 3) {
    const d3 = document.getElementById('p3DimChart'); if (d3) {
      const c = echarts.init(d3); c._phase3Type = 'dim'; chartInstances.push(c)
      const dimLabels = judges[0]?.dims.map(d => d.label) || ['安全','规划','团队','改进']
      const seriesNames = judges.map(j => j.group)
      const colors = ['#00a8ff','#00dc82','#ffaa3a']
      c.setOption({
        animation: false, animationDuration: 0,
        tooltip:{trigger:'axis',axisPointer:{type:'shadow'}}, legend:{data:seriesNames,textStyle:{color:'#6b8cae',fontSize:11},top:0},
        grid:{left:55,right:20,top:30,bottom:20},
        xAxis:{type:'category',data:dimLabels,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#5a7a9a',fontSize:10}},
        yAxis:{type:'value',max:50,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
        series: judges.map((j, idx) => ({
          name: j.group, type:'bar', data: j.dims.map(d => d.val), barWidth:16,
          itemStyle:{ color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:colors[idx]},{offset:1,color:colors[idx]}]} }
        }))
      })
    }
    const t3 = document.getElementById('p3TotalChart'); if (t3) {
      const c = echarts.init(t3); c._phase3Type = 'total'; chartInstances.push(c)
      const colors3 = ['#00a8ff', '#00dc82', '#ffaa3a']
      c.setOption({
        animation: false, animationDuration: 0,
        tooltip:{trigger:'axis'}, grid:{left:50,right:30,top:20,bottom:30},
        xAxis:{type:'category',data:judges.map(j=>j.group),axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:12}},
        yAxis:{type:'value',max:100,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
        series:[{ type:'bar',
          data: judges.map((j, idx) => ({
            value: j.dims.reduce((s,d)=>s+d.val,0),
            itemStyle:{ color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:colors3[idx]},{offset:1,color:colors3[idx]}]} }
          })),
          barWidth:40,
          label:{show:true, position:'top', formatter:'{c}分', color:'#c8d4e0', fontSize:14, fontWeight:'bold'},
          markLine:{silent:true, data:[{type:'average',name:'平均'}], lineStyle:{color:'rgba(0,168,255,0.3)',type:'dashed'}, label:{color:'#5a7a9a',fontSize:10,formatter:'平均 {c}'}}
        }]
      })
    }
  } else if (phase.value === 4) {
    const hm = document.getElementById('p4Heatmap')
    if (hm) {
      const c = echarts.init(hm); chartInstances.push(c)
      const dims = dimsLabels()
      const heatData = []
      groups.forEach((g, gi) => {
        const vals = personalRadar[g]
        vals.forEach((v, di) => {
          heatData.push([gi, di, v])
        })
      })
      c.setOption({
        tooltip:{position:'top', formatter:(p)=>`${groups[p.value[0]]}<br/>${dims[p.value[1]]}: <b>${p.value[2]}分</b>`},
        grid:{left:90,right:30,top:20,bottom:30},
        xAxis:{type:'category',data:groups,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:11},splitArea:{show:true,areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.04)']}}},
        yAxis:{type:'category',data:dims,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:10},splitArea:{show:true,areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.04)']}}},
        visualMap:{min:30,max:100,calculable:false,orient:'horizontal',left:'center',bottom:0,show:false,inRange:{color:['#0a1628','#0066cc','#00dc82','#ffd24d']}},
        series:[{ type:'heatmap', data:heatData, label:{show:true,formatter:'{c}',color:'#e0f0ff',fontSize:11,fontWeight:'bold'}, emphasis:{itemStyle:{shadowBlur:10,shadowColor:'rgba(0,220,130,0.5)'}} }]
      })
    }
    const before = document.getElementById('p4RadarBefore'); if (before) {
      const c = echarts.init(before); chartInstances.push(c)
      const beforeVals = personalRadar['揽星组'].map(v => Math.round(v * 0.72))
      c.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#4a6a8a',fontSize:9}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.02)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}} }, series:[{type:'radar',data:[{value:beforeVals,name:'课前',lineStyle:{color:'rgba(0,168,255,0.5)',width:1.5,type:'dashed'},areaStyle:{color:'rgba(0,168,255,0.08)'},itemStyle:{color:'rgba(0,168,255,0.5)'},symbol:'circle',symbolSize:4}]}] })
    }
    const after = document.getElementById('p4RadarAfter'); if (after) {
      const c = echarts.init(after); chartInstances.push(c)
      c.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#8ab4d0',fontSize:9}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.15)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} }, series:[{type:'radar',data:[{value:personalRadar['揽星组'],name:'课后',lineStyle:{color:'#00dc82',width:2.5},areaStyle:{color:'rgba(0,220,130,0.25)'},itemStyle:{color:'#00dc82'},symbol:'circle',symbolSize:6}]}] })
    }
    const grid = document.getElementById('personalRadarGrid'); if (grid) {
      const top3 = ['揽星组','御风组','巡天组']
      grid.innerHTML = top3.map((g,i)=>`<div class="personal-card" data-g="${g}"><div class="pr-name">${g}</div><div id="miniRadar_${i}" style="width:100%;height:120px;"></div><div class="pr-score">${personalRadar[g].reduce((s,v)=>s+v,0)/5|0}分</div><div class="pr-sub">点击查看画像</div></div>`).join('')
      setTimeout(()=>{
        top3.forEach((g,i)=>{ const el=document.getElementById(`miniRadar_${i}`); if(!el)return; const mc=echarts.init(el); chartInstances.push(mc); mc.setOption({ radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'75%', axisName:{show:false}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.03)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.06)'}} }, series:[{type:'radar',data:[{value:personalRadar[g],name:g,lineStyle:{color:groupColor(g),width:2.5},areaStyle:{color:groupColor(g)+'40'},itemStyle:{color:groupColor(g)},symbol:'circle',symbolSize:5}]}] }) })
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
onMounted(async () => {
  await _refreshQr()
  _rateTimer = setInterval(_pollRatings, 2000)
  const tick = () => { const n = new Date(); clock.value = String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')+':'+String(n.getSeconds()).padStart(2,'0') }
  tick(); renderPhaseCharts()
  calcScale(); window.addEventListener('resize', calcScale)
  _rateTimer2 = setInterval(tick, 1000)
  window.addEventListener('resize', ()=>chartInstances.forEach(c=>{try{c.resize()}catch(e){}}))
})
onUnmounted(() => {
  window.removeEventListener('resize', calcScale)
  if (_rateTimer) clearInterval(_rateTimer)
  if (_rateTimer2) clearInterval(_rateTimer2)
})
watch(phase, ()=>{
  // 切换环节时只重新渲染图表，不重置技能点分数
  setTimeout(() => {
    chartInstances.forEach(c=>{try{c.dispose()}catch(e){}}); chartInstances=[]
    const dims5 = dimsLabels()
    if (phase.value === 1) {
      const groups1 = phase1Groups.value
      const peer1 = phase1PeerData.value
      const hasData = demo1Done.value || demo1Running.value
      const el = document.getElementById('p1Radar'); if (el) {
        if (!hasData) { el.innerHTML = ''; }
        else {
          const c = echarts.init(el); chartInstances.push(c)
          c.setOption({
            animation: false, animationDuration: 0,
            tooltip:{}, legend:{data:groups1.map(g=>g.name), textStyle:{color:'#c8e4ff', fontSize:14}, bottom:4, left:'center', itemWidth:18, itemHeight:10},
            radar:{indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'76%', center:['50%','42%'], axisName:{color:'#e0f5ff', fontSize:13, fontWeight:'bold'}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.05)','rgba(0,168,255,0.1)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.25)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}} },
            series:[{ type:'radar', animation: false, animationDuration: 0, data: groups1.map(g=>({
              value:[
                Math.min(100, Math.round(g.design * 1.4 + 10)),
                Math.min(100, Math.round(g.pres * 1.6 + 10)),
                Math.min(100, Math.round(g.chal * 5 + 35)),
                g.total,
                Math.min(100, Math.round((g.design + g.pres) * 0.7 + 25))
              ],
              name:g.name, lineStyle:{width:3}, areaStyle:{opacity:0.22}, itemStyle:{symbol:'circle', symbolSize:8}
            })) }],
            color:['#00a8ff','#00dc82']
          })
        }
      }
      const peer = document.getElementById('p1PeerBar'); if (peer) {
        if (!hasData) { peer.innerHTML = ''; }
        else {
          const c = echarts.init(peer); chartInstances.push(c)
          c.setOption({
            animation: false, animationDuration: 0,
            tooltip:{trigger:'axis'},
            grid:{left:40,right:20,top:40,bottom:24},
            xAxis:{type:'category', data:peer1.map(p=>p.group), axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:13}},
            yAxis:{type:'value', max:10, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#5a7a9a', fontSize:11}},
            series:[{ type:'bar', animation: false, animationDuration: 0, data: peer1.map(p=>({
              value:p.val,
              itemStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:'#ff9a3a'},{offset:1,color:'#c76400'}]},borderRadius:[6,6,0,0]},
              label:{show:p.val>0, position:'top', formatter:'+{c}分', color:'#ff9a3a', fontSize:13, fontWeight:'bold'}
            })), barWidth:42 }]
          })
        }
      }
    } else if (phase.value === 2) {
      const bar = document.getElementById('p2CompareBar')
      if (bar) {
        const c = echarts.init(bar); chartInstances.push(c)
        const names = phase2Groups.map(g=>g.name)
        const basisVals = phase2Groups.map(g=>g.basisCount)
        const riskVals = phase2Groups.map(g=>g.riskCount)
        c.setOption({
          tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
          legend:{data:['决策依据','风险对冲'], textStyle:{color:'#6b8cae', fontSize:13}, top:2, right:10, itemWidth:22, itemHeight:14},
          grid:{left:40,right:30,top:50,bottom:28},
          xAxis:{type:'category', data:names, axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, axisLabel:{color:'#8ab4d0', fontSize:12}},
          yAxis:{type:'value', max:6, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}}, axisLabel:{color:'#4a6a8a', fontSize:10}},
          series:[
            { name:'决策依据', type:'bar', data:basisVals, barWidth:20, barGap:'10%',
              itemStyle:{color:'#00a8ff', borderRadius:[4,4,0,0]},
              label:{show:true, position:'top', formatter:'{c}条', color:'#00a8ff', fontSize:12, fontWeight:'bold'} },
            { name:'风险对冲', type:'bar', data:riskVals, barWidth:20,
              itemStyle:{color:'#ffaa3a', borderRadius:[4,4,0,0]},
              label:{show:true, position:'top', formatter:'{c}条', color:'#ffaa3a', fontSize:12, fontWeight:'bold'} }
          ]
        })
      }
      const r = document.getElementById('p2Radar')
      if (r) {
        const top3 = phase2Sorted.value.slice(0,3)
        const c = echarts.init(r); chartInstances.push(c)
        c.setOption({
          animation: false, animationDuration: 0,
          legend:{data:top3.map(g=>g.name), textStyle:{color:'#c8e4ff', fontSize:13}, bottom:2, left:'center', itemWidth:18, itemHeight:10},
          radar:{
            indicator:[
              {name:'决策坐标完整度', max:100},
              {name:'决策依据充分性', max:100},
              {name:'风险对冲强度', max:100},
              {name:'三要素均衡度', max:100},
              {name:'综合质量分', max:100}
            ],
            shape:'polygon', radius:'70%', center:['50%','40%'],
            axisName:{color:'#e0f5ff', fontSize:12, fontWeight:'bold'},
            splitArea:{areaStyle:{color:['rgba(0,168,255,0.04)','rgba(0,220,180,0.08)']}},
            axisLine:{lineStyle:{color:'rgba(0,168,255,0.25)'}},
            splitLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}
          },
          series:[{ type:'radar', animation: false, animationDuration: 0, data: top3.map((g,i)=>({
            value:[
              g.cordOk?100:60,
              Math.round(g.basisPct),
              Math.round(g.riskPct),
              Math.round((g.basisPct+g.riskPct+(g.cordOk?100:0))/3),
              g.score
            ],
            name:g.name,
            lineStyle:{width:3},
            areaStyle:{opacity:0.22},
            itemStyle:{symbol:'circle', symbolSize:7}
          })) }],
          color:['#00dc82','#00a8ff','#ffaa3a']
        })
      }
    } else if (phase.value === 3) {
      const d3 = document.getElementById('p3DimChart'); if (d3) {
        const c = echarts.init(d3); c._phase3Type = 'dim'; chartInstances.push(c)
        const dimLabels = judges[0]?.dims.map(d => d.label) || ['安全','规划','团队','改进']
        const seriesNames = judges.map(j => j.group)
        const colors = ['#00a8ff','#00dc82','#ffaa3a']
        c.setOption({
          animation: false, animationDuration: 0,
          tooltip:{trigger:'axis',axisPointer:{type:'shadow'}}, legend:{data:seriesNames,textStyle:{color:'#6b8cae',fontSize:11},top:0},
          grid:{left:55,right:20,top:30,bottom:20},
          xAxis:{type:'category',data:dimLabels,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#5a7a9a',fontSize:10}},
          yAxis:{type:'value',max:50,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
          series: judges.map((j, idx) => ({
            name: j.group, type:'bar', data: j.dims.map(d => d.val), barWidth:16,
            itemStyle:{ color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:colors[idx]},{offset:1,color:colors[idx]}]} }
          }))
        })
      }
      const t3 = document.getElementById('p3TotalChart'); if (t3) {
        const c = echarts.init(t3); c._phase3Type = 'total'; chartInstances.push(c)
        const colors3 = ['#00a8ff', '#00dc82', '#ffaa3a']
        c.setOption({
          animation: false, animationDuration: 0,
          tooltip:{trigger:'axis'}, grid:{left:50,right:30,top:20,bottom:30},
          xAxis:{type:'category',data:judges.map(j=>j.group),axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:12}},
          yAxis:{type:'value',max:100,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}},axisLabel:{color:'#4a6a8a',fontSize:10}},
          series:[{ type:'bar',
            data: judges.map((j, idx) => ({
              value: j.dims.reduce((s,d)=>s+d.val,0),
              itemStyle:{ color:{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:colors3[idx]},{offset:1,color:colors3[idx]}]} }
            })),
            barWidth:40,
            label:{show:true, position:'top', formatter:'{c}分', color:'#c8d4e0', fontSize:14, fontWeight:'bold'},
            markLine:{silent:true, data:[{type:'average',name:'平均'}], lineStyle:{color:'rgba(0,168,255,0.3)',type:'dashed'}, label:{color:'#5a7a9a',fontSize:10,formatter:'平均 {c}'}}
          }]
        })
      }
    } else if (phase.value === 4) {
      const hm = document.getElementById('p4Heatmap')
      if (hm) {
        const c = echarts.init(hm); chartInstances.push(c)
        const dims = dims5
        const heatData = []
        groups.forEach((g, gi) => {
          const vals = personalRadar[g]
          vals.forEach((v, di) => {
            heatData.push([gi, di, v])
          })
        })
        c.setOption({
          animation: false, animationDuration: 0,
          tooltip:{position:'top', formatter:(p)=>`${groups[p.value[0]]}<br/>${dims[p.value[1]]}: <b>${p.value[2]}分</b>`},
          grid:{left:90,right:30,top:20,bottom:30},
          xAxis:{type:'category',data:groups,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:11},splitArea:{show:true,areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.04)']}}},
          yAxis:{type:'category',data:dims,axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}},axisLabel:{color:'#8ab4d0',fontSize:10},splitArea:{show:true,areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.04)']}}},
          visualMap:{min:30,max:100,calculable:false,orient:'horizontal',left:'center',bottom:0,show:false,inRange:{color:['#0a1628','#0066cc','#00dc82','#ffd24d']}},
          series:[{ type:'heatmap', data:heatData, label:{show:true,formatter:'{c}',color:'#e0f0ff',fontSize:11,fontWeight:'bold'}, emphasis:{itemStyle:{shadowBlur:10,shadowColor:'rgba(0,220,130,0.5)'}} }]
        })
      }
      const before = document.getElementById('p4RadarBefore'); if (before) {
        const c = echarts.init(before); chartInstances.push(c)
        const beforeVals = personalRadar['揽星组'].map(v => Math.round(v * 0.72))
        c.setOption({ animation: false, animationDuration: 0, radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#4a6a8a',fontSize:9}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.02)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.08)'}} }, series:[{type:'radar', animation: false, animationDuration: 0, data:[{value:beforeVals,name:'课前',lineStyle:{color:'rgba(0,168,255,0.5)',width:1.5,type:'dashed'},areaStyle:{color:'rgba(0,168,255,0.08)'},itemStyle:{color:'rgba(0,168,255,0.5)'},symbol:'circle',symbolSize:4}]}] })
      }
      const after = document.getElementById('p4RadarAfter'); if (after) {
        const c = echarts.init(after); chartInstances.push(c)
        c.setOption({ animation: false, animationDuration: 0, radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'65%', axisName:{color:'#8ab4d0',fontSize:9}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.15)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} }, series:[{type:'radar', animation: false, animationDuration: 0, data:[{value:personalRadar['揽星组'],name:'课后',lineStyle:{color:'#00dc82',width:2.5},areaStyle:{color:'rgba(0,220,130,0.25)'},itemStyle:{color:'#00dc82'},symbol:'circle',symbolSize:6}]}] })
      }
      const grid = document.getElementById('personalRadarGrid'); if (grid) {
        const top3 = ['揽星组','御风组','巡天组']
        grid.innerHTML = top3.map((g,i)=>`<div class="personal-card" data-g="${g}"><div class="pr-name">${g}</div><div id="miniRadar_${i}" style="width:100%;height:120px;"></div><div class="pr-score">${personalRadar[g].reduce((s,v)=>s+v,0)/5|0}分</div><div class="pr-sub">点击查看画像</div></div>`).join('')
        setTimeout(()=>{
          top3.forEach((g,i)=>{ const el=document.getElementById(`miniRadar_${i}`); if(!el)return; const mc=echarts.init(el); chartInstances.push(mc); mc.setOption({ animation: false, animationDuration: 0, radar:{ indicator:dims5.map(d=>({name:d,max:100})), shape:'polygon', radius:'75%', axisName:{show:false}, splitArea:{areaStyle:{color:'rgba(0,168,255,0.03)'}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.1)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.06)'}} }, series:[{type:'radar', animation: false, animationDuration: 0, data:[{value:personalRadar[g],name:g,lineStyle:{color:groupColor(g),width:2.5},areaStyle:{color:groupColor(g)+'40'},itemStyle:{color:groupColor(g)},symbol:'circle',symbolSize:5}]}] }) })
          document.querySelectorAll('.personal-card').forEach(card=>{ card.addEventListener('click', e=>showPersonalRadarModal(card.getAttribute('data-g'))) })
        }, 80)
      }
    }
  }, 60)
})


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
.header-sub { color:#e0f0ff; font-size:22px; font-weight:600; letter-spacing:2px; animation:glow 3s ease-in-out infinite; white-space:nowrap; }
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
.demo-btn { padding:9px 18px; border-radius:8px; font-size:14px; font-weight:600; background:linear-gradient(135deg,rgba(0,220,180,0.2),rgba(0,168,255,0.2)); color:#00dc82; border:1px solid rgba(0,220,180,0.35); cursor:pointer; transition:all 0.3s; letter-spacing:1px; }
.demo-btn:hover:not(:disabled) { background:linear-gradient(135deg,rgba(0,220,180,0.35),rgba(0,168,255,0.35)); box-shadow:0 0 14px rgba(0,220,130,0.4); transform:translateY(-1px); }
.demo-btn:disabled { opacity:0.6; cursor:not-allowed; }
.demo-btn.demo-running { background:linear-gradient(135deg,rgba(255,184,77,0.25),rgba(255,107,107,0.2)); color:#ffd479; border-color:rgba(255,212,121,0.4); animation:demoPulse 1.2s ease-in-out infinite; }
.demo-btn.demo-reset { background:linear-gradient(135deg,rgba(106,90,205,0.2),rgba(0,168,255,0.2)); color:#a5c9ff; border-color:rgba(165,201,255,0.35); }
.demo-btn.demo-reset:hover:not(:disabled) { background:linear-gradient(135deg,rgba(106,90,205,0.35),rgba(0,168,255,0.35)); box-shadow:0 0 14px rgba(0,168,255,0.4); }

@keyframes demoPulse { 0%,100%{ box-shadow:0 0 0 rgba(255,212,121,0); } 50%{ box-shadow:0 0 18px rgba(255,212,121,0.55); } }

.back-teach-btn { padding:4px 10px; font-size:12px; color:#6fa8c8; background:rgba(0,168,255,0.06); border:1px solid rgba(0,168,255,0.15); border-radius:6px; }
.back-teach-btn:hover { color:#a6d5f0; background:rgba(0,168,255,0.12); border-color:rgba(0,168,255,0.25); }

.main-container { display:flex; flex:1; overflow:hidden; padding:12px; gap:12px; }
.sidebar { width:280px; min-width:280px; display:flex; flex-direction:column; gap:10px; overflow-y:auto; }
.sidebar-head { font-size:15px; font-weight:700; color:#9cd7ff; padding:4px 10px 8px; letter-spacing:1px; border-bottom:1px solid rgba(0,168,255,0.15); margin-bottom:2px; }
.section-title { font-size:14px; color:#8ab4d0; font-weight:600; padding:2px 0 6px 10px; margin-bottom:4px; letter-spacing:1px; position:relative; }
.section-title::before { content:''; position:absolute; left:0; top:4px; width:3px; height:12px; background:linear-gradient(180deg,#00a8ff,#00dc82); border-radius:2px; }

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

.capability-card { padding:18px 20px; margin-bottom:12px; border-radius:16px; position:relative; overflow:hidden; cursor:pointer; }
.capability-card:hover { transform:translateX(3px); box-shadow:0 0 24px rgba(0,168,255,0.15), inset 0 0 20px rgba(0,168,255,0.05); }
.capability-card.weak:hover { box-shadow:0 0 24px rgba(255,80,60,0.2), inset 0 0 20px rgba(255,80,60,0.05); }
.capability-card.weak .cap-name { color:#ff8c70; }
.cap-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.cap-name { font-size:20px; color:#d0e4f0; font-weight:500; }
.cap-score { font-size:24px; font-weight:700; color:#00dc82; }
.cap-score.low { color:#ff6b50; }
.cap-progress { height:8px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden; margin-bottom:10px; }
.cap-progress-bar { height:100%; border-radius:4px; position:relative; width:0; }
.cap-progress-bar::after { content:''; position:absolute; right:0; top:0; bottom:0; width:14px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.4)); }
.cap-bar-green { background:linear-gradient(90deg,#00a8ff,#00dc82); }
.cap-bar-red { background:linear-gradient(90deg,#ff4444,#ff8c5a); }
.cap-footer { display:flex; justify-content:space-between; margin-top:10px; font-size:14px; color:#6a8aaa; }

.kp-list { display:flex; flex-direction:column; gap:6px; }
.kp-item { display:flex; align-items:center; gap:8px; padding:9px 12px; border-radius:12px; font-size:14px; background:rgba(0,24,48,0.4); border:1px solid rgba(0,168,255,0.08); }
.kp-dot { display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; font-size:12px; font-weight:700; flex-shrink:0; }
.kp-item.done .kp-dot { background:rgba(0,220,130,0.15); color:#00dc82; }
.kp-item.learning .kp-dot { background:rgba(255,170,58,0.15); color:#ffaa3a; }
.kp-item:not(.done):not(.learning) .kp-dot { background:rgba(255,80,60,0.15); color:#ff6c48; }
.kp-name { flex:1; color:#cfe4f8; }
.kp-tag { font-size:12px; padding:2px 8px; border-radius:10px; background:rgba(0,220,130,0.15); color:#00dc82; }
.kp-tag-gray { background:rgba(108,168,220,0.15); color:#6ca8dc; }
.kp-tag-red { background:rgba(255,80,60,0.15); color:#ff8c70; }

@keyframes pulseScore { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
.phase-track { position:relative; height:32px; background:#0a1530; border:1px solid rgba(0,168,255,0.1); border-radius:6px; overflow:hidden; display:flex; align-items:center; }
.phase-track-fill { position:absolute; left:0; top:0; bottom:0; background:linear-gradient(90deg,rgba(0,168,255,0.15),rgba(0,220,130,0.2)); border-radius:6px; }
.phase-track-text { position:relative; z-index:1; font-size:12px; color:#8ab4d0; padding:0 12px; letter-spacing:0.5px; }
@keyframes fadeIn { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:translateY(0);} }

.content { flex:1; display:flex; flex-direction:column; gap:10px; overflow:hidden; }
.content-grid { flex:1; display:grid; gap:10px; overflow-y:auto; padding-right:4px; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; }
.content-grid.phase4-grid { grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr 1fr; }
.row-full { grid-column:1 / -1; }
.chart-panel { padding:20px; display:flex; flex-direction:column; animation:fadeIn 0.5s; }
.panel-title { font-size:20px; color:#e0f0ff; font-weight:600; margin-bottom:16px; display:flex; align-items:center; gap:8px; flex-shrink:0; }
.panel-title .icon { width:36px; height:36px; border-radius:8px; background:linear-gradient(135deg,rgba(0,168,255,0.15),rgba(0,220,180,0.1)); display:flex; align-items:center; justify-content:center; font-size:18px; border:1px solid rgba(0,168,255,0.2); }
.center-panel { align-items:center; justify-content:center; }
.chart-box { flex:1; min-height:240px; width:100%; }

.p1-radar-panel { padding: 8px 16px 4px !important; }
.p1-radar-panel .panel-title { margin-bottom: 4px; font-size:18px; }
.p1-radar-panel .chart-box { min-height:320px; }

.score-group-blocks { display:flex; flex-direction:column; gap:14px; }
.score-group-block { padding:14px 16px; border-radius:10px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); }
.sg-label { font-size:17px; color:#00dc82; font-weight:600; margin-bottom:10px; letter-spacing:1px; }
.sg-sub-blocks { display:flex; gap:10px; }
.sg-sub { flex:1; padding:12px 10px; border-radius:8px; background:rgba(0,0,0,0.3); border:1px solid rgba(0,168,255,0.08); text-align:center; }
.sg-sub.total { background:rgba(0,220,130,0.06); border-color:rgba(0,220,130,0.18); }
.sg-sub-label { font-size:13px; color:#5a7a9a; margin-bottom:6px; letter-spacing:0.5px; }
.sg-sub-value { font-size:30px; font-weight:700; color:#00dc82; line-height:1.1; }
.sg-sub-value.big { font-size:36px; }
.sg-sub-unit { font-size:12px; color:#4a6a8a; margin-top:2px; }

.sg-label-row { display:flex; align-items:center; gap:8px; margin-bottom:10px; }
.sg-label-dot { width:10px; height:10px; border-radius:50%; box-shadow: 0 0 10px currentColor; }
.sg-label-score { margin-left:auto; font-size:18px; color:#fff; font-weight:600; }
.sg-label-score em { font-size:11px; color:#7a9ab8; font-style:normal; font-weight:400; margin-left:2px; }
.sg-sub-row { display:flex; align-items:baseline; justify-content:space-between; }
.sg-sub-bar { height:6px; background:rgba(122,154,184,.15); border-radius:4px; margin:4px 0; overflow:hidden; }
.sg-sub-bar-fill { height:100%; border-radius:4px; transition:width 1.6s ease-out; }
.sg-sub-reason { font-size:11px; color:#7a9ab8; line-height:1.4; letter-spacing:.2px; padding-left:6px; border-left:2px solid rgba(0,220,130,.5); margin-top:4px; }

.sg-mini-bars { margin-top:12px; display:flex; flex-direction:column; gap:6px; padding-top:10px; border-top:1px dashed rgba(0,168,255,0.15); }
.sg-mini-bar-wrap { display:flex; align-items:center; gap:10px; }
.sg-mini-bar-label { font-size:14px; color:#6b8cae; width:54px; flex-shrink:0; }
.sg-mini-bar { flex:1; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; }
.sg-mini-bar-fill { height:100%; border-radius:4px; transition:width 1s ease; position:relative; }
.sg-mini-bar-fill::after { content:''; position:absolute; right:0; top:0; bottom:0; width:14px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.35)); }

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
.promise-list { display:flex; flex-direction:column; gap:5px; flex:1; overflow-y:auto; }
.promise-item { display:flex; gap:8px; padding:6px 10px; border-radius:6px; background:rgba(0,168,255,0.04); border-left:2px solid rgba(0,168,255,0.3); font-size:11px; line-height:1.7; }
.promise-item .pi-group { color:#00dc82; font-weight:600; white-space:nowrap; }
.promise-item .pi-text { color:#9ab9d6; flex:1; }

.trajectory-wrap { display:flex; align-items:center; justify-content:center; gap:12px; flex:1; }
.traj-label { text-align:center; font-size:11px; color:#5a7a9a; margin-bottom:4px; }
.traj-radar { width:180px; height:180px; }
.arrow { font-size:20px; color:#00dc82; font-weight:bold; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

.personal-radar-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; flex:1; min-height:0; }
.personal-card { padding:8px; border-radius:6px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); cursor:pointer; transition:all 0.3s; text-align:center; display:flex; flex-direction:column; }
.personal-card:hover { background:rgba(0,168,255,0.1); border-color:rgba(0,168,255,0.3); transform:translateY(-2px); }
.pr-name { font-size:12px; color:#00a8ff; font-weight:600; margin-bottom:2px; }
.pr-score { font-size:14px; font-weight:700; color:#00dc82; margin:4px 0 2px; }
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

.class-summary-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; flex:1; align-content:center; }
.cs-item { text-align:center; padding:12px 8px; border-radius:8px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); }
.cs-num { font-size:28px; font-weight:800; color:#00dc82; line-height:1; }
.cs-label { font-size:11px; color:#8ab4d0; margin-top:4px; }

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
.rate-qr-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; padding:14px 16px 16px; }
.rq-btn-row { display:flex; gap:8px; margin-top:2px; }
.rq-link { width:100%; font-size:10px; color:#4a6a8a; text-align:center; word-break:break-all; line-height:1.3; padding:4px 8px; border-radius:4px; background:rgba(0,168,255,0.04); border:1px dashed rgba(0,168,255,0.18); cursor:pointer; }
.rq-link:hover { color:#b8d4e8; background:rgba(0,168,255,0.1); }
.rq-stats { display:flex; gap:12px; margin-top:6px; }
.rq-stat { flex:1; padding:6px 10px; border-radius:6px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.12); text-align:center; }
.rq-stat-name { font-size:12px; color:#b8d4e8; font-weight:600; }
.rq-stat-num { font-size:22px; color:#00dc82; font-weight:700; line-height:1.2; }
.rq-stat-meta { font-size:9px; color:#5a7a9a; }
.rate-meta-btn { font-size:11px; padding:4px 10px; border-radius:6px; background:rgba(0,168,255,0.1); color:#b8d4e8; border:1px solid rgba(0,168,255,0.25); cursor:pointer; transition:all 0.25s; }
.rate-meta-btn:hover { background:rgba(0,168,255,0.22); color:#fff; border-color:rgba(0,220,180,0.6); }
.rate-clear-btn { background:rgba(255,100,100,0.08); border-color:rgba(255,100,100,0.3); color:#ffcaca; }
.rate-clear-btn:hover { background:rgba(255,80,80,0.22); color:#fff; border-color:rgba(255,100,100,0.7); }
.rate-enlarge-mask { position:fixed; inset:0; background:rgba(0,0,0,0.7); display:flex; align-items:center; justify-content:center; z-index:1000; }
.rate-enlarge-mask .rate-qr-box { width:360px; height:360px; background:#fff; padding:16px; border-radius:14px; box-shadow:0 10px 40px rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; }
.rate-enlarge-mask .rate-qr-box img { width:100%; height:100%; }

.phase2-wrap { display:flex; flex-direction:column; gap:10px; flex:1; min-height:0; padding:0; }
.phase2-topbar { display:flex; align-items:center; justify-content:space-between; padding:8px 16px; background:linear-gradient(90deg,rgba(0,168,255,0.12),rgba(0,220,180,0.04)); border:1px solid rgba(0,168,255,0.2); border-radius:8px; flex-shrink:0; }
.phase2-topbar-left { display:flex; align-items:center; gap:12px; }
.phase2-topbar-logo { width:40px; height:40px; border-radius:10px; background:linear-gradient(135deg,#00a8ff,#00dc82); display:flex; align-items:center; justify-content:center; font-size:22px; }
.phase2-topbar-title { font-size:20px; font-weight:700; color:#e0f0ff; letter-spacing:1px; }
.phase2-topbar-sub { font-size:12px; color:#6b8cae; letter-spacing:0.5px; margin-top:2px; }
.phase2-topbar-right { display:flex; align-items:center; gap:14px; }
.phase2-engine-chip { display:flex; align-items:center; gap:8px; padding:6px 14px; border-radius:16px; background:rgba(0,220,130,0.1); border:1px solid rgba(0,220,130,0.25); color:#00dc82; font-size:13px; }
.phase2-return { font-size:13px; color:#6b8cae; cursor:pointer; padding:6px 10px; border-radius:6px; background:rgba(0,168,255,0.08); border:1px solid rgba(0,168,255,0.15); }
.phase2-return:hover { color:#a0c8e8; background:rgba(0,168,255,0.18); }

.phase2-cards { display:grid; grid-template-columns:repeat(6, 1fr); gap:8px; flex-shrink:0; }
.phase2-group-card { padding:10px 10px 8px; border-radius:8px; background:linear-gradient(135deg,rgba(0,168,255,0.08),rgba(0,220,180,0.03)); border:1px solid rgba(0,168,255,0.18); transition:all 0.3s; display:flex; flex-direction:column; min-height:140px; }
.phase2-group-card:hover { transform:translateY(-2px); border-color:rgba(0,220,180,0.4); box-shadow:0 0 20px rgba(0,220,130,0.2); }
.phase2-group-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.phase2-group-name { font-size:15px; font-weight:700; color:#e0f0ff; }
.phase2-group-rank { font-size:10px; font-weight:700; color:#fff; padding:2px 8px; border-radius:10px; letter-spacing:1px; }
.phase2-group-checks { display:flex; flex-direction:column; gap:2px; margin-bottom:6px; }
.phase2-group-check { display:flex; align-items:center; gap:5px; font-size:11px; color:#6b8cae; }
.phase2-group-check .phase2-cick { font-size:10px; width:14px; display:inline-block; text-align:center; }
.phase2-group-check.ok { color:#00dc82; }
.phase2-group-bars { display:flex; flex-direction:column; gap:4px; margin-bottom:6px; }
.phase2-bar-row { display:flex; align-items:center; gap:6px; font-size:10px; }
.phase2-bar-label { color:#5a7a9a; width:56px; flex-shrink:0; }
.phase2-bar-track { flex:1; height:6px; background:rgba(122,154,184,0.15); border-radius:3px; overflow:hidden; }
.phase2-bar-fill { height:100%; border-radius:3px; transition:width 1.2s ease; position:relative; }
.phase2-bar-fill.basis-bar { background:linear-gradient(90deg,#00a8ff,#00dc82); }
.phase2-bar-fill.risk-bar { background:linear-gradient(90deg,#ffaa3a,#ff8c5a); }
.phase2-bar-num { color:#c8d4e0; font-size:11px; font-weight:600; width:18px; text-align:right; }
.phase2-group-footer { display:flex; align-items:baseline; gap:6px; padding-top:4px; border-top:1px dashed rgba(0,168,255,0.15); margin-top:auto; }
.phase2-group-score { font-size:22px; font-weight:700; color:#00dc82; text-shadow:0 0 10px currentColor; min-width:36px; }
.phase2-group-score-label { font-size:9px; color:#5a7a9a; letter-spacing:0.5px; }

.phase2-body { display:flex; gap:10px; flex:1; min-height:0; }
.phase2-col { flex:1; display:flex; flex-direction:column; gap:10px; min-height:0; min-width:0; }
.phase2-panel { flex:1; padding:8px 12px !important; min-height:0; min-width:0; display:flex; flex-direction:column; overflow:hidden; }
.phase2-panel .panel-title { margin-bottom:2px; font-size:15px; }

.phase2-legend { display:flex; align-items:center; gap:18px; margin-bottom:2px; padding-left:4px; }
.phase2-legend-item { display:flex; align-items:center; gap:6px; font-size:11px; color:#8ab4d0; }
.phase2-legend-dot { width:12px; height:12px; border-radius:3px; }

.phase2-triad { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-bottom:6px; }
.phase2-triad-item { padding:6px 6px; border-radius:6px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.1); text-align:center; }
.phase2-triad-icon { font-size:14px; margin-bottom:2px; }
.phase2-triad-label { font-size:12px; color:#e0f0ff; font-weight:600; }
.phase2-triad-status { font-size:11px; margin-top:2px; font-weight:600; }
.phase2-triad-status.ok { color:#00dc82; }
.phase2-triad-status.warn { color:#ffaa3a; }
.phase2-triad-hint { font-size:9px; color:#5a7a9a; margin-top:1px; }

.phase2-log { flex:1; min-height:0; overflow-y:auto; display:flex; flex-direction:column; gap:3px; padding-right:4px; }
.phase2-log-line { padding:4px 8px; border-radius:4px; background:rgba(0,168,255,0.04); border-left:2px solid rgba(0,220,130,0.4); font-size:11px; line-height:1.6; }
.phase2-log-time { color:#00dc82; margin-right:6px; font-family:monospace; font-size:10px; }
.phase2-log-text { color:#8ab4d0; }

.phase2-rank-list { display:flex; flex-direction:column; gap:4px; padding:2px 0; flex:1; min-height:0; overflow-y:auto; }
.phase2-rank-row { display:flex; align-items:center; gap:10px; padding:3px 8px; border-radius:5px; background:rgba(0,168,255,0.04); border:1px solid rgba(0,168,255,0.08); }
.phase2-rank-name { width:60px; font-size:12px; font-weight:600; color:#c8e4ff; flex-shrink:0; }
.phase2-rank-bar-track { flex:1; height:12px; background:rgba(122,154,184,0.1); border-radius:6px; overflow:hidden; }
.phase2-rank-bar-fill { height:100%; border-radius:6px; transition:width 1.4s ease; }
.phase2-rank-score { width:55px; text-align:right; font-size:11px; font-weight:700; color:#00dc82; }
.phase2-rank-crown { margin-left:4px; }
</style>
