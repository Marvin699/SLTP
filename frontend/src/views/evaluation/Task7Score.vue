<template>
  <div class="task7-score-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/evaluation')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回教学智评
        </el-button>
        <el-divider direction="vertical" />
        <h1>{{ config.task_name }}</h1>
      </div>
      <div class="header-right">
        <el-tag type="primary" effect="dark">{{ config.max_score }}分制</el-tag>
      </div>
    </div>

    <!-- 角色与小组选择 -->
    <div class="selection-bar">
      <div class="select-item">
        <label>评分角色</label>
        <el-select v-model="selectedRole" placeholder="请选择评分角色" size="default">
          <el-option v-for="role in config.scorer_roles" :key="role.id" :label="role.name" :value="role.id" />
        </el-select>
      </div>
      <div class="select-item">
        <label>评分小组</label>
        <el-select v-model="selectedGroup" placeholder="请选择小组" size="default">
          <el-option v-for="group in config.groups" :key="group" :label="group" :value="group" />
        </el-select>
      </div>
      <div class="select-item">
        <label>飞行时间（分钟）</label>
        <el-input v-model.number="flightTime" type="number" placeholder="输入飞行时间" size="default" style="width: 120px;" />
      </div>
    </div>

    <!-- 评分区域 -->
    <div class="score-content">
      <div v-for="dim in config.dimensions" :key="dim.id" class="dimension-card">
        <div class="dim-header">
          <div class="dim-title">
            <span class="dim-name">{{ dim.name }}</span>
            <span class="dim-score">（{{ dim.max_score }}分）</span>
          </div>
          <div class="dim-weight">权重 {{ (dim.weight * 100).toFixed(0) }}%</div>
        </div>
        <div class="dim-items">
          <div v-for="item in dim.items" :key="item.id" class="score-item">
            <div class="item-info">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-max">（{{ item.score }}分）</span>
            </div>
            <div class="item-criteria">{{ item.criteria }}</div>
            <div class="item-score-input">
              <template v-if="item.type === 'range'">
                <el-select v-model="scores[item.id]" placeholder="选择等级" size="small" class="score-select">
                  <el-option v-for="r in item.ranges" :key="r.score" :label="r.label" :value="r.score" />
                </el-select>
              </template>
              <template v-else>
                <el-input-number v-model="scores[item.id]" :min="0" :max="item.score" size="small" class="score-input" />
              </template>
            </div>
          </div>
        </div>
        <div class="dim-summary">
          <span class="summary-label">{{ dim.name }}得分：</span>
          <span class="summary-value">{{ getDimensionScore(dim) }} / {{ dim.max_score }}</span>
        </div>
      </div>
    </div>

    <!-- 时间系数 -->
    <div class="time-coefficient-card">
      <div class="tc-header">
        <span class="tc-title">{{ config.time_coefficient.name }}</span>
        <span class="tc-desc">{{ config.time_coefficient.description }}</span>
      </div>
      <div class="tc-rules">
        <div v-for="rule in config.time_coefficient.rules" :key="rule.condition" 
             class="tc-rule" :class="{ active: getTimeCoefficient() === rule.coefficient }">
          <span class="rule-label">{{ rule.label }}</span>
          <span class="rule-value">系数 {{ rule.coefficient }}</span>
        </div>
      </div>
      <div class="tc-current">
        当前时间系数：<span class="tc-value">{{ getTimeCoefficient() }}</span>
      </div>
    </div>

    <!-- 最终得分 -->
    <div class="final-score-card">
      <div class="fs-header">
        <span class="fs-title">🏆 最终得分</span>
      </div>
      <div class="fs-calculation">
        <div class="calc-item">
          <span class="calc-label">各项得分之和</span>
          <span class="calc-value">{{ totalScore }}</span>
        </div>
        <div class="calc-operator">×</div>
        <div class="calc-item">
          <span class="calc-label">时间系数</span>
          <span class="calc-value">{{ getTimeCoefficient() }}</span>
        </div>
        <div class="calc-operator">=</div>
        <div class="calc-item fs-result">
          <span class="calc-label">最终得分</span>
          <span class="calc-value">{{ finalScore }}</span>
        </div>
      </div>
      <div class="fs-grade">等级：{{ getGrade(finalScore) }}</div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" size="large" @click="submitScore" :disabled="!canSubmit">
        <el-icon><Paperclip /></el-icon> 提交评分
      </el-button>
      <el-button size="large" @click="resetScores">
        <el-icon><Refresh /></el-icon> 重置评分
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Paperclip, Refresh } from '@element-plus/icons-vue'
import config from '@/data/task7-evaluation-config.json'

const router = useRouter()

// 选择状态
const selectedRole = ref('')
const selectedGroup = ref('')
const flightTime = ref(5)

// 评分数据
const scores = ref({})

// 初始化评分
function initScores() {
  scores.value = {}
  config.dimensions.forEach(dim => {
    dim.items.forEach(item => {
      scores.value[item.id] = item.score
    })
  })
}

// 计算维度得分
function getDimensionScore(dim) {
  return dim.items.reduce((sum, item) => sum + (scores.value[item.id] || 0), 0)
}

// 总得分（未乘时间系数）
const totalScore = computed(() => {
  return config.dimensions.reduce((sum, dim) => sum + getDimensionScore(dim), 0)
})

// 时间系数
function getTimeCoefficient() {
  const time = flightTime.value || 5
  const rules = config.time_coefficient.rules
  if (time <= 5) return rules[0].coefficient
  if (time <= 6) return rules[1].coefficient
  return rules[2].coefficient
}

// 最终得分
const finalScore = computed(() => {
  return Math.round(totalScore.value * getTimeCoefficient() * 100) / 100
})

// 等级评定
function getGrade(score) {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

// 是否可以提交
const canSubmit = computed(() => {
  return selectedRole.value && selectedGroup.value && flightTime.value >= 0
})

// 提交评分
function submitScore() {
  if (!canSubmit.value) {
    ElMessage.warning('请填写完整评分信息')
    return
  }
  
  const scoreData = {
    task_id: config.task_id,
    role: selectedRole.value,
    role_name: config.scorer_roles.find(r => r.id === selectedRole.value)?.name,
    group: selectedGroup.value,
    flight_time: flightTime.value,
    time_coefficient: getTimeCoefficient(),
    dimension_scores: config.dimensions.map(dim => ({
      dimension_id: dim.id,
      dimension_name: dim.name,
      score: getDimensionScore(dim),
      max_score: dim.max_score,
      items: dim.items.map(item => ({
        item_id: item.id,
        item_name: item.name,
        score: scores.value[item.id] || 0,
        max_score: item.score
      }))
    })),
    total_score: totalScore.value,
    final_score: finalScore.value,
    grade: getGrade(finalScore.value),
    submitted_at: new Date().toISOString()
  }
  
  // 保存到本地存储
  const savedScores = JSON.parse(localStorage.getItem('task7_scores') || '[]')
  savedScores.push(scoreData)
  localStorage.setItem('task7_scores', JSON.stringify(savedScores))
  
  ElMessage.success('评分提交成功！')
  resetScores()
}

// 重置评分
function resetScores() {
  initScores()
  flightTime.value = 5
}

onMounted(() => {
  initScores()
})
</script>

<style scoped>
.task7-score-page {
  padding: 28px;
  color: #fff;
  min-height: calc(100vh - 100px);
  font-size: 16px;
}

/* 顶部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.page-header h1 { margin: 0; font-size: 26px; font-weight: 700; }
.back-btn { color: #409eff; font-size: 16px; }

/* 选择栏 */
.selection-bar {
  display: flex;
  gap: 28px;
  padding: 24px 28px;
  background: rgba(13, 33, 55, 0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  margin-bottom: 28px;
}
.select-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.select-item label { font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 500; }
.select-item :deep(.el-select .el-input__wrapper) {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.12);
}
.select-item :deep(.el-input__inner) { color: #e2e8f0; font-size: 16px; }

/* 评分区域 */
.score-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.dimension-card {
  background: rgba(13, 33, 55, 0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 24px;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.dim-title { display: flex; align-items: center; gap: 10px; }
.dim-name { font-size: 20px; font-weight: 700; }
.dim-score { color: #409eff; font-size: 18px; font-weight: 600; }
.dim-weight { font-size: 14px; color: rgba(255,255,255,0.5); }

.dim-items { display: flex; flex-direction: column; gap: 18px; }

.score-item {
  padding: 18px;
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
}
.item-info { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.item-name { font-size: 17px; font-weight: 500; }
.item-max { color: rgba(255,255,255,0.5); font-size: 14px; }
.item-criteria { font-size: 15px; color: rgba(255,255,255,0.7); margin-bottom: 12px; line-height: 1.6; }
.item-score-input { display: flex; justify-content: flex-end; }
.score-select { width: 180px; }
.score-input { width: 110px; }

.dim-summary {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.summary-label { font-size: 15px; color: rgba(255,255,255,0.6); }
.summary-value { font-size: 24px; font-weight: 700; color: #67c23a; }

/* 时间系数卡片 */
.time-coefficient-card {
  background: rgba(13, 33, 55, 0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 24px;
}
.tc-header { margin-bottom: 18px; }
.tc-title { font-size: 20px; font-weight: 700; margin-right: 14px; }
.tc-desc { font-size: 15px; color: rgba(255,255,255,0.6); }
.tc-rules { display: flex; gap: 16px; margin-bottom: 18px; }
.tc-rule {
  flex: 1;
  padding: 16px;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  text-align: center;
  transition: all 0.2s;
}
.tc-rule.active {
  background: rgba(64,158,255,0.15);
  border-color: rgba(64,158,255,0.3);
}
.rule-label { display: block; font-size: 15px; margin-bottom: 6px; }
.rule-value { display: block; font-size: 18px; font-weight: 700; color: #409eff; }
.tc-current {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.tc-value { font-size: 24px; font-weight: 700; color: #f59c0b; }

/* 最终得分卡片 */
.final-score-card {
  background: linear-gradient(135deg, rgba(64,158,255,0.15) 0%, rgba(103,194,58,0.15) 100%);
  border: 1px solid rgba(64,158,255,0.3);
  border-radius: 14px;
  padding: 28px;
  margin-bottom: 28px;
}
.fs-header { margin-bottom: 24px; }
.fs-title { font-size: 22px; font-weight: 700; }
.fs-calculation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.calc-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.calc-label { font-size: 16px; color: rgba(255,255,255,0.6); }
.calc-value { font-size: 26px; font-weight: 700; color: #fff; }
.calc-operator { font-size: 30px; color: rgba(255,255,255,0.4); }
.fs-result .calc-value { font-size: 42px; color: #00d4ff; }
.fs-grade {
  text-align: center;
  margin-top: 20px;
  font-size: 19px;
}

/* 操作按钮 */
.action-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 暗色主题下拉框 */
:deep(.el-select .el-input__wrapper) {
  background: rgba(13,33,55,0.8);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  height: 48px;
}
:deep(.el-select .el-input__wrapper:hover) { border-color: rgba(64,158,255,0.4); }
:deep(.el-select .el-input__wrapper.is-focus) { border-color: #409eff; }
:deep(.el-select .el-input__inner) { color: #e2e8f0; font-size: 16px; }
:deep(.el-select .el-input__inner::placeholder) { color: rgba(255,255,255,0.35); }
:deep(.el-select .el-select__caret) { font-size: 18px; }

:deep(.el-input-number) {
  --el-input-number-input-bg-color: rgba(0,0,0,0.3);
  --el-input-number-input-color: #e2e8f0;
  --el-input-number-input-border-color: rgba(255,255,255,0.12);
  --el-input-number-input-font-size: 16px;
  height: 44px;
}
:deep(.el-input-number .el-input__inner) { font-size: 16px; }

:deep(.el-button) {
  font-size: 16px;
  padding: 12px 32px;
  border-radius: 10px;
}
:deep(.el-button:not(.el-button--primary):not(.el-button--danger):not(.el-button--success):not(.el-button--warning)) {
  --el-button-bg-color: rgba(64,158,255,0.15);
  --el-button-border-color: rgba(64,158,255,0.3);
  --el-button-text-color: #a0c4ff;
}

:deep(.el-tag) {
  font-size: 15px;
  padding: 6px 16px;
}

:deep(.el-divider) {
  height: 28px;
  margin: 0 16px;
}
</style>