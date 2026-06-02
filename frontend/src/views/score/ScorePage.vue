<template>
  <div class="score-page">
    <!-- 加载中 -->
    <div v-if="loading" class="state-box">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 链接无效 -->
    <div v-else-if="error" class="state-box">
      <el-icon :size="48" color="#e74c3c"><CircleCloseFilled /></el-icon>
      <h2>{{ error }}</h2>
      <p>请联系教师获取有效链接</p>
    </div>

    <!-- 选择评分身份 -->
    <div v-else-if="!scorerRole" class="role-select-box">
      <div class="role-card-wrapper">
        <div class="role-icon-big">📋</div>
        <div class="role-section-tag" v-if="sessionInfo.section_name">{{ sessionInfo.section_name }}</div>
        <h2>{{ sessionInfo.title }}</h2>

        <!-- 第一步：选择角色类别 -->
        <div v-if="!selectedCategory">
          <p class="role-hint">请选择您的评分身份</p>
          <div class="role-grid">
            <div v-for="cat in categoryOptions" :key="cat.value"
                 class="role-item" @click="selectedCategory = cat.value">
              <span class="role-emoji">{{ cat.icon }}</span>
              <span class="role-label">{{ cat.label }}</span>
            </div>
          </div>
        </div>

        <!-- 第二步：输入姓名 -->
        <div v-else class="name-input-step">
          <p class="role-hint">
            身份：<strong>{{ currentCategoryLabel }}</strong>
            <el-button text type="info" size="small" @click="selectedCategory = ''; scorerName = ''" style="margin-left: 8px;">返回</el-button>
          </p>
          <div class="name-input-box">
            <el-input
              v-model="scorerName"
              placeholder="请输入您的姓名"
              size="large"
              clearable
              maxlength="20"
              @keyup.enter="confirmRole"
            />
          </div>
          <el-button type="primary" size="large" @click="confirmRole" :disabled="!scorerName.trim()"
            style="margin-top: 16px; width: 200px;">进入评分</el-button>
        </div>
      </div>
    </div>

    <!-- 已提交 -->
    <div v-else-if="submitted" class="state-box">
      <el-icon :size="48" color="#67c23a"><CircleCheckFilled /></el-icon>
      <h2>评分提交成功</h2>
      <p>感谢 {{ scorerRole }} 的评分！</p>
    </div>

    <!-- 评分界面 -->
    <div v-else class="score-content">
      <div class="score-header">
        <div class="score-header-left">
          <div class="score-section" v-if="sessionInfo.section_name">{{ sessionInfo.section_name }}</div>
          <div class="score-title">{{ sessionInfo.title }}</div>
        </div>
        <div class="scorer-info">
          评分身份: <strong>{{ scorerRole }}</strong>
          <el-button text type="danger" size="small" @click="resetRole">切换</el-button>
        </div>
      </div>

      <div class="group-list">
        <div v-for="(group, gi) in sessionInfo.groups" :key="group" class="group-score-card">
          <div class="group-header">
            <span class="group-dot" :style="{ background: GROUP_COLORS[gi % GROUP_COLORS.length] }"></span>
            <span class="group-name">{{ group }}</span>
          </div>
          <div class="dim-list">
            <div v-for="dim in sessionInfo.dimensions" :key="dim" class="dim-row">
              <span class="dim-label">{{ dim }}</span>
              <span class="dim-weight">{{ getWeightPercent(dim) }}%</span>
              <el-slider v-model="scores[`${group}-${dim}`]" :min="0" :max="100" :step="1" show-input input-size="small" />
            </div>
          </div>
        </div>
      </div>

      <div class="submit-bar">
        <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting" :disabled="submitted">
          提交评分
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, CircleCloseFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import { fetchSessionByToken, submitScores } from '@/api/scoreSession'

const route = useRoute()
const token = route.params.token

const loading = ref(true)
const error = ref('')
const sessionInfo = ref(null)
const selectedCategory = ref('')
const scorerName = ref('')
const scorerRole = ref('')
const submitted = ref(false)
const submitting = ref(false)
const scores = reactive({})

const GROUP_COLORS = ['#e74c3c', '#3b82f6', '#2ecc71', '#9b59b6', '#f39c16', '#1abc9c']

const categoryOptions = [
  { value: '裁判组', label: '裁判组', icon: '⚖️' },
  { value: '观察员', label: '观察员', icon: '👁️' },
  { value: '老师', label: '老师', icon: '👨‍🏫' },
  { value: '企业导师', label: '企业导师', icon: '👔' },
]

const currentCategoryLabel = computed(() => {
  const found = categoryOptions.find(c => c.value === selectedCategory.value)
  return found ? found.label : ''
})

function getWeightPercent(dim) {
  const weights = sessionInfo.value?.weights || {}
  return weights[dim] ? (weights[dim] * 100).toFixed(0) : 0
}

onMounted(async () => {
  try {
    const res = await fetchSessionByToken(token)
    sessionInfo.value = res.data
    for (const group of sessionInfo.value.groups) {
      for (const dim of sessionInfo.value.dimensions) {
        scores[`${group}-${dim}`] = 0
      }
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '链接无效或已过期'
  } finally {
    loading.value = false
  }
})

function confirmRole() {
  const name = scorerName.value.trim()
  if (!selectedCategory.value || !name) return
  scorerRole.value = `${selectedCategory.value}-${name}`
}

function resetRole() {
  scorerRole.value = ''
  selectedCategory.value = ''
  scorerName.value = ''
}

async function handleSubmit() {
  if (!scorerRole.value) return
  submitting.value = true
  try {
    const scoreList = []
    for (const group of sessionInfo.value.groups) {
      for (const dim of sessionInfo.value.dimensions) {
        scoreList.push({
          group_id: group,
          dimension: dim,
          score: scores[`${group}-${dim}`],
        })
      }
    }
    await submitScores({
      session_token: token,
      scorer_role: scorerRole.value,
      scores: scoreList,
    })
    submitted.value = true
    ElMessage.success('评分提交成功！')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.score-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
  color: #fff;
  padding: 24px;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
}
.state-box h2 { margin: 16px 0 8px; font-size: 22px; }
.state-box p { color: #c0c8d4; margin: 0; }

/* 角色选择 */
.role-select-box {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}
.role-card-wrapper {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 48px 40px;
  text-align: center;
  max-width: 520px;
  width: 100%;
}
.role-icon-big { font-size: 48px; margin-bottom: 12px; }
.role-section-tag {
  display: inline-block;
  background: rgba(64,158,255,0.15);
  border: 1px solid rgba(64,158,255,0.3);
  color: #409eff;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 12px;
}
.role-card-wrapper h2 { margin: 0 0 8px; font-size: 20px; }
.role-hint { margin: 0 0 24px; color: #c0c8d4; font-size: 14px; }
.role-hint strong { color: #409eff; }

.role-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 8px;
}
.role-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 2px solid rgba(255,255,255,0.08);
  cursor: pointer;
  transition: all 0.2s;
}
.role-item:hover {
  border-color: rgba(64,158,255,0.4);
  background: rgba(64,158,255,0.08);
}
.role-item.active {
  border-color: #409eff;
  background: rgba(64,158,255,0.15);
}
.role-emoji { font-size: 24px; }
.role-label { font-size: 13px; color: #e2e8f0; font-weight: 500; }

/* 姓名输入步骤 */
.name-input-step {
  margin-top: 8px;
}
.name-input-box {
  max-width: 320px;
  margin: 0 auto;
}
.name-input-box :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: none;
  border-radius: 8px;
}
.name-input-box :deep(.el-input__wrapper:hover) {
  border-color: rgba(64,158,255,0.4);
}
.name-input-box :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
}
.name-input-box :deep(.el-input__inner) {
  color: #fff;
  text-align: center;
  font-size: 16px;
}
.name-input-box :deep(.el-input__inner::placeholder) {
  color: rgba(255,255,255,0.3);
}

/* 评分界面 */
.score-content { max-width: 900px; margin: 0 auto; }
.score-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.score-header-left { flex: 1; }
.score-section {
  display: inline-block;
  background: rgba(64,158,255,0.15);
  border: 1px solid rgba(64,158,255,0.3);
  color: #409eff;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 16px;
  margin-bottom: 8px;
}
.score-title { font-size: 18px; font-weight: 600; }
.scorer-info { font-size: 14px; color: #c0c8d4; white-space: nowrap; }
.scorer-info strong { color: #fff; margin: 0 4px; }

.group-score-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 16px;
}
.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.group-dot { width: 12px; height: 12px; border-radius: 50%; }
.group-name { font-size: 16px; font-weight: 600; }
.dim-list { display: flex; flex-direction: column; gap: 10px; }
.dim-row { display: flex; align-items: center; gap: 12px; }
.dim-label { width: 80px; font-size: 13px; color: #c0c8d4; flex-shrink: 0; }
.dim-weight {
  width: 40px;
  font-size: 12px;
  color: #f59c0b;
  font-weight: 600;
  text-align: right;
  flex-shrink: 0;
}
.dim-row :deep(.el-slider) { flex: 1; }

.submit-bar {
  position: sticky;
  bottom: 0;
  background: rgba(10, 22, 40, 0.95);
  border-top: 1px solid rgba(255,255,255,0.1);
  padding: 16px 0;
  text-align: center;
  margin-top: 24px;
}

:deep(.el-slider__runway) { background: rgba(255,255,255,0.1); }
:deep(.el-slider__bar) { background: #409eff; }
</style>
