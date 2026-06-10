<template>
  <div class="heatmap-wrap">
  <div class="task8-heatmap" :style="{ transform: 'scale('+heatScale+')' }">
    <header class="header">
      <div class="header-left">
        <div class="logo-icon">翼</div>
        <h1>任务8 · 班级能力达成度热力图</h1>
        <span class="header-sub">全组六维能力扫描 · 24位学生</span>
      </div>
      <div class="header-right">
        <router-link class="nav-back" to="/evaluation/task8">← 返回任务8大屏</router-link>
        <router-link class="nav-back" to="/evaluation">← 返回教学智评</router-link>
      </div>
    </header>

    <div class="main-container">
      <aside class="sidebar">
        <div class="section-title">筛选小组</div>
        <div class="filter-pills">
          <span v-for="g in groupList" :key="g" class="filter-pill" :class="{active:selectedGroup===g}" @click="selectedGroup = g">{{ g }}</span>
        </div>

        <div class="section-title">班级雷达速览</div>
        <div class="glass radar-card">
          <div id="classRadarMini" style="width:100%;height:160px;"></div>
          <div class="class-radar-sub">六维能力班级均值</div>
        </div>

        <div class="section-title">班级概况</div>
        <div class="glass info-card">
          <div class="info-row"><span class="info-label">学生总数</span><span class="info-value">24 人</span></div>
          <div class="info-row"><span class="info-label">平均综合得分</span><span class="info-value">76.4</span></div>
          <div class="info-row"><span class="info-label">达标率 (≥70)</span><span class="info-value" style="color:#00dc82">87.5%</span></div>
          <div class="info-row"><span class="info-label">薄弱率 (<70)</span><span class="info-value" style="color:#ff6b50">12.5%</span></div>
        </div>

        <div class="section-title">维度权重</div>
        <div class="glass info-card">
          <div class="dim-weight-row" v-for="d in dims" :key="d.name">
            <span class="dim-name">{{ d.name }}</span>
            <div class="dim-bar-wrap"><div class="dim-bar" :style="{width:d.weight+'%'}"></div></div>
            <span class="dim-w">{{ d.weight }}%</span>
          </div>
        </div>

        <div class="section-title">数据说明</div>
        <div class="glass info-card" style="line-height:1.8;">
          热力矩阵颜色：深蓝→浅绿→金黄→橙红 代表能力分数 0→50→80→100。点击成员卡片可查看个人能力雷达图。
        </div>
      </aside>

      <main class="content">
        <div class="glass chart-panel">
          <div class="panel-title"><span class="icon">🔥</span>班级能力热力矩阵 <span class="tooltip-hint">横轴：六维能力 · 纵轴：学生</span></div>
          <div id="heatmapChart" class="heatmap-container"></div>
        </div>

        <div class="glass chart-panel">
          <div class="panel-title"><span class="icon">🧑‍🎓</span>成员能力扫描 <span class="tooltip-hint">共 {{ filteredMembers.length }} 人</span></div>
          <div class="member-grid">
            <div class="member-card" v-for="m in filteredMembers" :key="m.name" @click="openMember(m)">
              <div class="m-header">
                <span class="m-name">{{ m.name }}</span>
                <span class="m-badge" :class="{leader:m.role==='组长',safe:m.role==='安全员',deputy:m.role==='副组长'}">{{ m.role || '组员' }}</span>
                <span class="m-role">{{ m.group }}</span>
              </div>
              <div class="m-score-row">
                <span class="m-tag" v-for="(s,i) in m.scores" :key="i" :style="{color:getScoreColor(s),borderColor:getScoreColor(s,0.3),background:getScoreColor(s,0.1)}">
                  {{ dims[i].name.slice(0,4) }} {{ s }}
                </span>
              </div>
              <div class="m-bar"><div class="m-bar-fill" :style="{width:getAvg(m.scores)+'%'}"></div></div>
            </div>
          </div>
        </div>

        <div class="glass chart-panel">
          <div class="panel-title"><span class="icon">🎖️</span>获奖名单</div>
          <div class="awards-row">
            <div v-for="a in awards" :key="a.key" class="award-card">
              <div class="award-shine"></div>
              <div class="award-icon">{{ a.icon }}</div>
              <div class="award-title">{{ a.title }}</div>
              <div class="award-group">{{ a.group }} · {{ a.person }}</div>
              <div class="award-reason">{{ a.reason }}</div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <div class="modal-overlay" :class="{show:showModal}" @click.self="showModal=false">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title">{{ modalName }} · 个人能力画像</div>
          <button class="modal-close" @click="showModal=false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-layout">
            <div class="modal-chart">
              <div id="memberRadar" style="width:100%;height:280px;"></div>
              <div class="heatmap-compare">
                <div class="compare-label">班级加权均值 · {{ classAvgWeighted }}</div>
                <div class="heatmap-compare-track"><div class="heatmap-compare-fill blue" :style="{width:classAvgWeighted+'%'}"></div></div>
                <div class="compare-label">本次加权得分 · {{ modalWeighted }}</div>
                <div class="heatmap-compare-track"><div class="heatmap-compare-fill green" :style="{width:modalWeighted+'%'}"></div></div>
              </div>
            </div>
            <div class="modal-info">
              <div class="modal-score-card">
                <div class="modal-score-sub">加权综合得分</div>
                <div class="modal-score">{{ modalWeighted }}</div>
                <div class="heatmap-badge" :class="modalWeighted>=82?'excellent':modalWeighted>=75?'good':modalWeighted>=60?'mid':'low'">{{ modalWeighted>=82?'优秀':modalWeighted>=75?'良好':modalWeighted>=60?'合格':'待提升' }}</div>
              </div>
              <div style="font-size:12px;color:#7a9ab8;margin:8px 0 4px;">六维得分明细</div>
              <div v-for="(s,i) in modalScores" :key="i" class="modal-dim-row">
                <span><em>{{ dims[i].weight }}%</em>{{ dims[i].name }}</span>
                <span :class="s>=70?'ok':'warn'">{{ s }}</span>
              </div>
              <div class="modal-compare-grid">
                <div v-for="(s,i) in modalScores" :key="'c'+i" class="mc-row">
                  <span class="mc-dim">{{ dims[i].name }}</span>
                  <div class="mc-bar-wrap">
                    <div class="mc-bar class-bar" :style="{width:classAvgScores[i]+'%'}"></div>
                    <div class="mc-bar person-bar" :style="{width:s+'%'}"></div>
                  </div>
                  <span class="mc-val">{{ s }}</span>
                </div>
              </div>
              <div style="font-size:11px;color:#4a6a8a;margin-top:6px;line-height:1.6;">
                所属小组：<b style="color:#8ab4d0">{{ modalGroup }}</b><br>
                加权规则：{{ dims.map(d=>d.name+d.weight+'%').join(' · ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="heatmap-status-bar">
      <span style="font-family:monospace;color:#00dc82;">{{ new Date().toLocaleTimeString('zh-CN',{hour12:false}) }}</span>
      <span>小组数 6 · 成员 24 · 热力图实时同步</span>
      <span>加权班级均值 {{ classAvgWeighted }} · 达标率 87.5%</span>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const heatScale = ref(1)
function calcHeatScale() {
  const baseW = 1920, baseH = 1080
  const wScale = window.innerWidth / baseW
  const hScale = window.innerHeight / baseH
  heatScale.value = Math.min(wScale, hScale, 1.5)
}

const dims = [
  { name:'综合方案设计', weight:20 },
  { name:'成果汇报展示', weight:15 },
  { name:'演练组织指挥', weight:25 },
  { name:'跨部门协调沟通', weight:15 },
  { name:'持续改进优化', weight:10 },
  { name:'安全规范意识', weight:15 }
]

const groupList = ['揽星组','御风组','巡天组','逐日组','凌云组','长空组']

function seed(scores){ return { scores:scores } }
const members = [
  { name:'谭玉曼', group:'揽星组', role:'调度工程师', ...seed([88,82,90,80,78,86]) },
  { name:'梁庆蝉', group:'揽星组', role:'运维工程师', ...seed([82,76,86,74,70,84]) },
  { name:'黄雅诗', group:'揽星组', role:'运维工程师', ...seed([85,80,88,78,74,86]) },
  { name:'蔡林宏', group:'揽星组', role:'无人机操作员', ...seed([80,78,84,76,68,82]) },
  { name:'刘华妮', group:'揽星组', role:'无人机操作员', ...seed([78,74,82,72,66,80]) },
  { name:'陈熙然', group:'揽星组', role:'地勤保障', ...seed([76,72,80,70,64,78]) },

  { name:'莫经玉', group:'御风组', role:'调度工程师', ...seed([80,84,86,88,78,86]) },
  { name:'刘子尧', group:'御风组', role:'运维工程师', ...seed([78,82,84,86,74,84]) },
  { name:'陈庆业', group:'御风组', role:'运维工程师', ...seed([76,78,82,84,72,82]) },
  { name:'王艳', group:'御风组', role:'无人机操作员', ...seed([82,80,88,80,76,84]) },
  { name:'邹丽丽', group:'御风组', role:'无人机操作员', ...seed([74,76,80,82,70,80]) },
  { name:'卜天泽', group:'御风组', role:'地勤保障', ...seed([78,80,82,84,72,82]) },

  { name:'邓新祥', group:'巡天组', role:'调度工程师', ...seed([78,74,92,80,82,86]) },
  { name:'韦怡伶', group:'巡天组', role:'运维工程师', ...seed([76,72,90,78,80,84]) },
  { name:'施金晓', group:'巡天组', role:'无人机操作员', ...seed([74,70,88,76,78,82]) },
  { name:'黄怀理', group:'巡天组', role:'无人机操作员', ...seed([72,74,86,78,76,80]) },
  { name:'张静怡', group:'巡天组', role:'地勤保障', ...seed([76,72,88,74,74,82]) },
  { name:'陆荣旭', group:'巡天组', role:'地勤保障', ...seed([74,76,86,80,72,82]) },

  { name:'张心怡', group:'逐日组', role:'调度工程师', ...seed([72,66,74,68,60,72]) },
  { name:'熊丽雪', group:'逐日组', role:'运维工程师', ...seed([70,68,72,70,62,70]) },
  { name:'黄瑞典', group:'逐日组', role:'无人机操作员', ...seed([68,66,70,68,58,68]) },
  { name:'李思远', group:'逐日组', role:'无人机操作员', ...seed([70,70,74,72,64,72]) },
  { name:'王浩宇', group:'逐日组', role:'地勤保障', ...seed([68,68,70,70,60,68]) },
  { name:'陈雨萱', group:'逐日组', role:'地勤保障', ...seed([72,70,72,72,66,72]) },

  { name:'赵宇航', group:'凌云组', role:'调度工程师', ...seed([76,74,80,76,70,80]) },
  { name:'孙佳怡', group:'凌云组', role:'运维工程师', ...seed([74,72,78,74,68,78]) },
  { name:'周子涵', group:'凌云组', role:'无人机操作员', ...seed([72,70,76,72,66,76]) },
  { name:'吴佳琪', group:'凌云组', role:'无人机操作员', ...seed([74,74,80,76,68,78]) },
  { name:'郑昊然', group:'凌云组', role:'地勤保障', ...seed([70,68,76,72,66,74]) },
  { name:'林思颖', group:'凌云组', role:'地勤保障', ...seed([74,72,78,74,70,78]) },

  { name:'何俊杰', group:'长空组', role:'调度工程师', ...seed([74,72,82,78,68,78]) },
  { name:'谢雨欣', group:'长空组', role:'运维工程师', ...seed([72,68,80,76,66,76]) },
  { name:'罗志强', group:'长空组', role:'无人机操作员', ...seed([70,70,82,74,64,76]) },
  { name:'韩雪婷', group:'长空组', role:'无人机操作员', ...seed([72,72,80,78,66,78]) },
  { name:'冯子轩', group:'长空组', role:'地勤保障', ...seed([68,68,78,74,64,74]) },
  { name:'董佳慧', group:'长空组', role:'地勤保障', ...seed([70,70,80,76,68,76]) }
]

const awards = [
  { key:'pilot', icon:'🏆', title:'领航能手', group:'揽星组', person:'蔡林宏', reason:'综合方案设计88分，安全冗余量化模型获企业导师高度认可' },
  { key:'craftsman', icon:'⚙️', title:'领航工匠', group:'巡天组', person:'邓新祥', reason:'演练组织指挥92分全班最高，应急决策工单质量最佳' },
  { key:'apprentice', icon:'🌱', title:'领航学徒', group:'逐日组', person:'熊丽雪', reason:'跨部门协调沟通进步显著，改进承诺具体可执行' },
  { key:'progress', icon:'🚀', title:'进步之星', group:'御风组', person:'卜天泽', reason:'持续改进优化52→74，全班进步最大' }
]

const selectedGroup = ref('揽星组')
const showModal = ref(false)
const modalName = ref('')
const modalGroup = ref('')
const modalScores = ref([])
const modalWeighted = ref(0)
const classAvgScores = computed(() => {
  if (!members.length) return dims.map(()=>75)
  return dims.map((_,i) => {
    const sum = members.reduce((s,m)=>s+m.scores[i], 0)
    return Math.round(sum/members.length)
  })
})
const classAvgWeighted = computed(() => {
  return Math.round(classAvgScores.value.reduce((s,v,i)=>s+v*dims[i].weight/100,0))
})

const filteredMembers = computed(() => {
  if (selectedGroup.value === '全部') return members
  return members.filter(m => m.group === selectedGroup.value)
})

function getAvg(arr){ return Math.round(arr.reduce((a,b)=>a+b,0)/arr.length) }

function getScoreColor(score, alpha=1){
  if (score >= 80) return `rgba(255,210,77,${alpha})`
  if (score >= 70) return `rgba(0,220,130,${alpha})`
  if (score >= 60) return `rgba(0,168,255,${alpha})`
  return `rgba(255,107,80,${alpha})`
}

let charts = []
function renderClassRadar() {
  const el = document.getElementById('classRadarMini')
  if (!el) return
  try { const c = charts.find(cc=>cc.__classRadar) || echarts.init(el); c.__classRadar = true; charts.push(c)
    c.setOption({
      radar:{ indicator:dims.map(d=>({name:d.name.length>4?d.name.slice(0,4):d.name,max:100})), shape:'polygon', radius:'60%', axisName:{color:'#8ab4d0', fontSize:10}, splitArea:{areaStyle:{color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.06)']}}, axisLine:{lineStyle:{color:'rgba(0,168,255,0.2)'}}, splitLine:{lineStyle:{color:'rgba(0,168,255,0.12)'}} },
      series:[{type:'radar',data:[{value:classAvgScores.value,name:'班级均值',lineStyle:{color:'#00a8ff',width:2},areaStyle:{color:'rgba(0,168,255,0.15)'},itemStyle:{color:'#00a8ff'},symbol:'circle',symbolSize:4}]}] })
  } catch(e){}
}
function renderHeatmap(){
  charts.forEach(c=>{if(!c.__classRadar){try{c.dispose()}catch(e){}}})
  charts = charts.filter(c=>c.__classRadar)
  const el = document.getElementById('heatmapChart')
  if (!el) return
  const c = echarts.init(el)
  charts.push(c)
  const dimLabels = dims.map(d=>d.name)
  const names = filteredMembers.value.map(m=>m.name+'\n'+m.group)
  const data = []
  filteredMembers.value.forEach((m, yi) => {
    m.scores.forEach((s, xi) => {
      data.push([xi, yi, s])
    })
  })
  c.setOption({
    tooltip:{ formatter:p=>`${filteredMembers.value[p.data[1]].name} · ${dimLabels[p.data[0]]}<br/>分数：<b>${p.data[2]}</b>` },
    grid:{ left:90, right:20, top:10, bottom:30 },
    xAxis:{ type:'category', data:dimLabels, axisLabel:{ color:'#8ab4d0', fontSize:11, rotate:0, interval:0 }, axisLine:{ lineStyle:{ color:'rgba(0,168,255,0.2)' } } },
    yAxis:{ type:'category', data:names.reverse(), axisLabel:{ color:'#c8d4e0', fontSize:10 }, axisLine:{ lineStyle:{ color:'rgba(0,168,255,0.2)' } } },
    visualMap:{ show:false, min:40, max:95, calculable:false,
      inRange:{ color:['#0a2860','#0052cc','#00a8ff','#00dc82','#ffd24d','#ff8c5a','#ff4444'] } },
    series:[{ type:'heatmap', data:data.map(d=>[d[0], filteredMembers.value.length-1-d[1], d[2]]), label:{ show:true, color:'#0a1628', fontSize:10, fontWeight:'bold' },
      emphasis:{ itemStyle:{ shadowBlur:10, shadowColor:'rgba(0,0,0,0.5)' } },
      itemStyle:{ borderColor:'rgba(0,168,255,0.08)', borderWidth:1, borderRadius:2 } }]
  })

  renderClassRadar()
}
function openMember(m){
  modalName.value = m.name
  modalGroup.value = m.group
  modalScores.value = [...m.scores]
  modalWeighted.value = Math.round(m.scores.reduce((s,si,i)=>s+si*dims[i].weight/100,0))
  showModal.value = true
  setTimeout(()=>{
    const el = document.getElementById('memberRadar')
    if (!el) return
    const rc = echarts.init(el); charts.push(rc)
    rc.setOption({
      radar:{
        indicator:dims.map(d=>({ name:d.name, max:100 })),
        shape:'polygon', radius:'65%',
        axisName:{ color:'#8ab4d0', fontSize:11 },
        splitArea:{ areaStyle:{ color:['rgba(0,168,255,0.02)','rgba(0,168,255,0.05)'] } },
        axisLine:{ lineStyle:{ color:'rgba(0,168,255,0.15)' } },
        splitLine:{ lineStyle:{ color:'rgba(0,168,255,0.12)' } }
      },
      series:[{ type:'radar', data:[
        {
          value:classAvgScores.value, name:'班级均值',
          lineStyle:{ color:'#00a8ff', width:1.5, type:'dashed' },
          areaStyle:{ color:'transparent' },
          symbol:'none'
        },
        {
          value:m.scores, name:m.name,
          lineStyle:{ color:'#00dc82', width:2.5 },
          areaStyle:{ color:'rgba(0,220,130,0.2)' },
          itemStyle:{ color:'#00dc82' },
          symbol:'circle', symbolSize:6
        }
      ] }]
    })
  }, 80)
}
onMounted(()=>{
  calcHeatScale()
  renderHeatmap()
  window.addEventListener('resize', ()=>{ calcHeatScale(); renderHeatmap() })
  document.body.style.overflow = 'hidden'
})
onBeforeUnmount(()=>{
  document.body.style.overflow = ''
})
watch(selectedGroup, () => renderHeatmap())
</script>

<style scoped>
.heatmap-wrap{position:fixed;top:0;left:0;width:100vw;height:100vh;background:#060d1f;overflow:hidden;z-index:9999;}
.task8-heatmap{margin:0;padding:0;width:1920px;height:1080px;background:#060d1f;color:#c8d4e0;display:flex;flex-direction:column;font-family:'Microsoft YaHei','PingFang SC',sans-serif;box-sizing:border-box;transform-origin:top left;}
.header{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:linear-gradient(180deg,rgba(0,20,40,0.95),rgba(6,13,31,0.98));border-bottom:1px solid rgba(0,168,255,0.2);position:relative;z-index:100;}
.header-left{display:flex;align-items:center;gap:12px;}
.logo-icon{width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#00a8ff,#00dc82);display:flex;align-items:center;justify-content:center;font-size:18px;color:#fff;font-weight:bold;}
.header h1{font-size:20px;color:#e0f0ff;font-weight:600;letter-spacing:2px;animation:glow 3s ease-in-out infinite;margin:0;}
.header-sub{color:#6b8cae;font-size:12px;margin-left:12px;letter-spacing:1px;}
.header-right{display:flex;gap:8px;}
.nav-back{padding:8px 14px;border-radius:6px;font-size:12px;background:rgba(0,168,255,0.08);color:#7a9ab8;border:1px solid rgba(0,168,255,0.15);text-decoration:none;transition:all 0.3s;}
.nav-back:hover{background:rgba(0,168,255,0.18);color:#a0c8e8;border-color:rgba(0,168,255,0.3);}
.main-container{display:flex;flex:1;overflow:hidden;padding:12px;gap:12px;}
.sidebar{width:260px;min-width:260px;display:flex;flex-direction:column;gap:10px;overflow-y:auto;}
.content{flex:1;display:flex;flex-direction:column;gap:10px;overflow-y:auto;padding-right:4px;}
.section-title{font-size:13px;color:#00a8ff;font-weight:600;padding:0 4px 6px;border-bottom:1px solid rgba(0,168,255,0.15);margin-bottom:4px;display:flex;align-items:center;gap:6px;}
.section-title::before{content:'';width:3px;height:14px;background:linear-gradient(180deg,#00a8ff,#00dc82);border-radius:2px;}
.glass{background:linear-gradient(135deg,rgba(0,168,255,0.06),rgba(0,220,180,0.03));border:1px solid rgba(0,168,255,0.15);border-radius:12px;backdrop-filter:blur(10px);position:relative;overflow:hidden;}
.glass::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,168,255,0.4),transparent);}
.glass::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,220,180,0.2),transparent);}
.filter-pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:2px;}
.filter-pill{padding:5px 12px;border-radius:14px;font-size:12px;cursor:pointer;background:rgba(0,168,255,0.06);color:#6b8cae;border:1px solid rgba(0,168,255,0.1);transition:all 0.3s;}
.filter-pill:hover{background:rgba(0,168,255,0.12);color:#8ab4d0;}
.filter-pill.active{background:linear-gradient(135deg,rgba(0,168,255,0.2),rgba(0,220,180,0.15));color:#00dc82;border-color:rgba(0,220,180,0.3);}
.info-card{padding:12px 14px;font-size:12px;color:#7a9ab8;}
.info-row{display:flex;justify-content:space-between;padding:3px 0;}
.info-label{color:#5a7a9a;}
.info-value{color:#8ab4d0;font-weight:500;}
.chart-panel{padding:14px;display:flex;flex-direction:column;}
.panel-title{font-size:15px;color:#e0f0ff;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.panel-title .icon{width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,rgba(0,168,255,0.15),rgba(0,220,180,0.1));display:flex;align-items:center;justify-content:center;font-size:14px;border:1px solid rgba(0,168,255,0.2);}
.heatmap-container{flex:1;min-height:320px;}
.tooltip-hint{font-size:11px;color:#4a6a8a;margin-left:auto;font-weight:normal;}
.member-grid{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;}
.member-card{flex:0 0 210px;padding:10px 12px;border-radius:10px;background:rgba(0,168,255,0.04);border:1px solid rgba(0,168,255,0.1);cursor:pointer;transition:all 0.3s;}
.member-card:hover{border-color:rgba(0,168,255,0.3);background:rgba(0,168,255,0.08);transform:translateY(-1px);}
.m-name{font-size:13px;color:#c8d4e0;font-weight:500;}
.m-role{font-size:10px;color:#5a7a9a;background:rgba(0,168,255,0.1);padding:2px 6px;border-radius:4px;}
.m-score-row{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px;}
.m-tag{font-size:10px;padding:2px 5px;border-radius:3px;border:1px solid rgba(0,168,255,0.12);}
.m-bar{height:4px;background:rgba(255,255,255,0.06);border-radius:2px;margin-top:8px;overflow:hidden;}
.m-bar-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#00a8ff,#00dc82);transition:width 0.8s ease;}
.awards-row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;}
.award-card{flex:1;min-width:160px;padding:14px;border-radius:12px;text-align:center;position:relative;overflow:hidden;animation:fadeInScale 0.5s ease both;cursor:pointer;transition:all 0.3s;}
.award-card:nth-child(1){border:1px solid rgba(255,200,50,0.3);background:linear-gradient(135deg,rgba(255,200,50,0.1),rgba(255,160,30,0.04));}
.award-card:nth-child(2){border:1px solid rgba(0,220,180,0.3);background:linear-gradient(135deg,rgba(0,220,180,0.1),rgba(0,168,255,0.04));}
.award-card:nth-child(3){border:1px solid rgba(0,168,255,0.3);background:linear-gradient(135deg,rgba(0,168,255,0.1),rgba(0,100,200,0.04));}
.award-card:nth-child(4){border:1px solid rgba(200,100,255,0.3);background:linear-gradient(135deg,rgba(200,100,255,0.1),rgba(150,50,220,0.04));}
.award-card:hover{transform:translateY(-3px);}
.award-icon{font-size:28px;margin-bottom:6px;}
.award-title{font-size:13px;font-weight:700;margin-bottom:3px;}
.award-card:nth-child(1) .award-title{color:#ffd24d;}
.award-card:nth-child(2) .award-title{color:#00dc82;}
.award-card:nth-child(3) .award-title{color:#00a8ff;}
.award-card:nth-child(4) .award-title{color:#c870ff;}
.award-group{font-size:15px;color:#e0f0ff;font-weight:600;margin-bottom:3px;}
.award-reason{font-size:11px;color:#6b8cae;line-height:1.4;}
.award-shine{position:absolute;top:0;left:-100%;width:50%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);animation:shimmer 3s infinite;}
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px);display:none;align-items:center;justify-content:center;z-index:1000;}
.modal-overlay.show{display:flex;}
.modal-content{width:680px;max-height:88vh;background:#0a1628;border:1px solid rgba(0,168,255,0.25);border-radius:16px;padding:24px;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.5);animation:fadeIn 0.3s;}
.modal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
.modal-title{font-size:17px;color:#e0f0ff;font-weight:600;}
.modal-close{width:32px;height:32px;border-radius:8px;border:1px solid rgba(0,168,255,0.2);background:rgba(0,168,255,0.08);color:#7a9ab8;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.3s;}
.modal-close:hover{background:rgba(255,60,60,0.15);color:#ff6b50;border-color:rgba(255,60,60,0.3);}
.modal-body{flex:1;overflow-y:auto;}
.modal-layout{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;}
.modal-chart{background:rgba(0,168,255,0.04);border-radius:10px;padding:10px;border:1px solid rgba(0,168,255,0.1);}
.modal-score-card{padding:12px;border-radius:10px;background:linear-gradient(135deg,rgba(0,168,255,0.15),rgba(0,220,180,0.08));border:1px solid rgba(0,168,255,0.25);text-align:center;}
.modal-score-sub{font-size:12px;color:#8ab4d0;}
.modal-score{font-size:36px;color:#00dc82;font-weight:700;letter-spacing:2px;text-shadow:0 0 12px rgba(0,220,130,0.5);}
.modal-dim-row{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed rgba(0,168,255,0.1);font-size:12px;}
.modal-dim-row span:last-child{font-weight:700;}
.modal-dim-row .ok{color:#00dc82;}
.modal-dim-row .warn{color:#ff6b50;}

.heatmap-status-bar{height:30px;background:rgba(0,10,30,0.95);border-top:1px solid rgba(0,168,255,0.15);display:flex;align-items:center;justify-content:space-between;padding:0 20px;font-size:11px;color:#5a7a9a;}
.radar-card{padding:12px 14px;}
.class-radar-sub{font-size:10px;color:#4a6a8a;margin-top:6px;text-align:center;}
.dim-weight-row{display:flex;align-items:center;gap:8px;padding:4px 0;}
.dim-name{font-size:11px;color:#8ab4d0;min-width:60px;}
.dim-bar-wrap{flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;}
.dim-bar{height:100%;border-radius:3px;background:linear-gradient(90deg,#00a8ff,#00dc82);}
.dim-w{font-size:10px;color:#00dc82;font-weight:600;min-width:28px;text-align:right;}
.m-badge{font-size:9px;padding:1px 6px;border-radius:8px;margin-right:6px;}
.m-badge.leader{background:rgba(255,210,77,0.15);color:#ffd24d;border:1px solid rgba(255,210,77,0.3);}
.m-badge.safe{background:rgba(0,220,130,0.15);color:#00dc82;border:1px solid rgba(0,220,130,0.3);}
.m-badge.deputy{background:rgba(0,168,255,0.15);color:#00a8ff;border:1px solid rgba(0,168,255,0.3);}
.heatmap-badge{display:inline-block;font-size:10px;padding:2px 8px;border-radius:10px;margin-top:6px;font-weight:600;}
.heatmap-badge.excellent{background:rgba(255,210,77,0.15);color:#ffd24d;border:1px solid rgba(255,210,77,0.3);}
.heatmap-badge.good{background:rgba(0,220,130,0.15);color:#00dc82;border:1px solid rgba(0,220,130,0.3);}
.heatmap-badge.mid{background:rgba(0,168,255,0.15);color:#00a8ff;border:1px solid rgba(0,168,255,0.3);}
.heatmap-badge.low{background:rgba(255,107,80,0.15);color:#ff6b50;border:1px solid rgba(255,107,80,0.3);}
.modal-dim-row em{font-style:normal;color:#5a7a9a;font-size:9px;margin-right:4px;}
.heatmap-compare{margin-top:12px;padding:10px;border-radius:6px;background:rgba(0,168,255,0.04);border:1px solid rgba(0,168,255,0.1);}
.compare-label{font-size:11px;color:#8ab4d0;margin-bottom:4px;}
.heatmap-compare-track{height:10px;background:rgba(255,255,255,0.06);border-radius:5px;overflow:hidden;margin-bottom:8px;}
.heatmap-compare-fill{height:100%;border-radius:5px;position:relative;overflow:hidden;}
.heatmap-compare-fill.blue{background:linear-gradient(90deg,#0a2860,#00a8ff);}
.heatmap-compare-fill.green{background:linear-gradient(90deg,#00a8ff,#00dc82);}
.modal-compare-grid{margin-top:10px;padding:10px;border-radius:6px;background:rgba(0,168,255,0.04);border:1px solid rgba(0,168,255,0.1);}
.mc-row{display:flex;align-items:center;gap:8px;padding:4px 0;}
.mc-dim{font-size:10px;color:#8ab4d0;min-width:60px;flex-shrink:0;}
.mc-bar-wrap{flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;position:relative;overflow:hidden;}
.mc-bar{position:absolute;top:0;left:0;height:100%;border-radius:3px;transition:width 0.3s;}
.class-bar{background:rgba(0,168,255,0.4);z-index:1;}
.person-bar{background:rgba(0,220,130,0.9);z-index:2;}
.mc-val{font-size:10px;color:#00dc82;font-weight:600;min-width:24px;text-align:right;}
@keyframes glow{0%,100%{text-shadow:0 0 10px rgba(0,168,255,0.5);}50%{text-shadow:0 0 20px rgba(0,168,255,0.9);}}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeInScale{from{opacity:0;transform:scale(0.92);}to{opacity:1;transform:scale(1);}}
@keyframes shimmer{0%{background-position:-200% 0;}100%{background-position:200% 0;}}
</style>
