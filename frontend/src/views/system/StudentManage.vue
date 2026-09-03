<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/system')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回系统管理
        </el-button>
        <el-divider direction="vertical" />
        <h1>学生管理</h1>
      </div>
      <div class="header-right">
        <el-tooltip content="学生注册时填写此邀请码即归入您名下，点击复制" placement="bottom">
          <el-button class="invite-btn" @click="copyInviteCode">
            <el-icon><Key /></el-icon>
            邀请码&nbsp;<b class="invite-code">{{ inviteCode || '······' }}</b>
          </el-button>
        </el-tooltip>
        <el-tooltip content="重置邀请码（旧码失效）" placement="bottom">
          <el-button @click="resetInviteCode"><el-icon><RefreshRight /></el-icon></el-button>
        </el-tooltip>
        <el-button type="primary" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon> 批量导入学生
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon> 下载导入模板
        </el-button>
        <el-button @click="refreshList" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">总学生数</div>
        <div class="stat-value">{{ students.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">今日新增</div>
        <div class="stat-value">{{ todayNew }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">需改密码</div>
        <div class="stat-value warn">{{ needChangeCount }}</div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索姓名 / 学号 / 小组"
        style="width: 280px"
        clearable
        @keyup.enter="searchStudents"
        @clear="searchStudents"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button @click="searchStudents">搜索</el-button>
    </div>

    <!-- 学生列表 -->
    <el-table
      :data="students"
      v-loading="loading"
      style="width: 100%"
      :header-cell-style="{ background: 'rgba(64, 158, 255, 0.1)', color: '#c0c8d4' }"
      :row-style="{ background: 'transparent' }"
    >
      <el-table-column prop="username" label="姓名" width="120" />
      <el-table-column prop="student_no" label="学号" width="140" />
      <el-table-column prop="class_name" label="班级" width="160">
        <template #default="{ row }">{{ row.class_name || '未分班' }}</template>
      </el-table-column>
      <el-table-column prop="group_no" label="小组" width="120">
        <template #default="{ row }">{{ row.group_no || '未分组' }}</template>
      </el-table-column>
      <el-table-column label="归属" width="110">
        <template #default="{ row }">
          <el-tag v-if="row.assigned" type="success" size="small" effect="plain">我的学生</el-tag>
          <el-button v-else size="small" type="warning" link @click="claimStudent(row)">认领</el-button>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.must_change_password" type="warning" size="small">需改密</el-tag>
          <el-tag v-else type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" class="action-btn reset-btn" @click="handleReset(row)">
            <el-icon><RefreshRight /></el-icon> 重置密码
          </el-button>
          <el-button size="small" class="action-btn delete-btn" @click="handleDelete(row)">
            <el-icon><Delete /></el-icon> 删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImportDialog" title="批量导入学生" width="640px">
      <div class="import-tips">
        <p><strong>导入说明：</strong></p>
        <ol>
          <li>请先点击「下载导入模板」获取 Excel 模板</li>
          <li>按模板填写学生信息（姓名、学号、班级、小组）</li>
          <li>班级和小组可留空</li>
          <li>导入后初始密码统一为 <code>123456</code>，学生首次登录后强制修改</li>
          <li>重复的姓名或学号会自动跳过</li>
        </ol>
      </div>

      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将 Excel 文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 .xlsx / .xls 格式</div>
        </template>
      </el-upload>

      <div v-if="parsedStudents.length > 0" class="preview-area">
        <div class="preview-title">
          预览：共解析到 {{ parsedStudents.length }} 名学生
          <el-button text type="primary" size="small" @click="parsedStudents = []">清空</el-button>
        </div>
        <el-table :data="parsedStudents.slice(0, 5)" max-height="200" size="small">
          <el-table-column prop="username" label="姓名" />
          <el-table-column prop="student_no" label="学号" />
          <el-table-column prop="class_name" label="班级" />
          <el-table-column prop="group_no" label="小组" />
        </el-table>
        <p v-if="parsedStudents.length > 5" class="more-hint">仅显示前 5 行，共 {{ parsedStudents.length }} 行</p>
      </div>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button @click="handleParseExcel" :disabled="!selectedFile">解析 Excel</el-button>
        <el-button type="primary" @click="handleBatchImport" :loading="importing" :disabled="parsedStudents.length === 0">
          确认导入 ({{ parsedStudents.length }} 人)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Upload, Download, Refresh, Search, UploadFilled, RefreshRight, Delete, Key } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const token = localStorage.getItem('sltp_token')

const api = axios.create({
  baseURL: API_BASE,
  headers: { Authorization: `Bearer ${token}` }
})

const loading = ref(false)
const importing = ref(false)
const students = ref([])
const keyword = ref('')
const inviteCode = ref('')
const showImportDialog = ref(false)
const selectedFile = ref(null)
const parsedStudents = ref([])
const uploadRef = ref(null)

const todayNew = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return students.value.filter(s => s.created_at?.startsWith(today)).length
})

const needChangeCount = computed(() => students.value.filter(s => s.must_change_password).length)

async function refreshList() {
  loading.value = true
  try {
    const res = await api.get('/api/auth/students', { params: { keyword: keyword.value } })
    if (res.data.success) {
      students.value = res.data.students
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '获取学生列表失败')
  } finally {
    loading.value = false
  }
}

function searchStudents() {
  refreshList()
}

async function fetchInviteCode() {
  try {
    const res = await api.get('/api/auth/invite-code')
    if (res.data.success) inviteCode.value = res.data.invite_code
  } catch (err) {
    console.error('获取邀请码失败', err)
  }
}

async function copyInviteCode() {
  if (!inviteCode.value) return
  try {
    await navigator.clipboard.writeText(inviteCode.value)
    ElMessage.success(`邀请码 ${inviteCode.value} 已复制，发给学生注册时填写`)
  } catch {
    ElMessage.info(`邀请码：${inviteCode.value}`)
  }
}

async function resetInviteCode() {
  await ElMessageBox.confirm(
    '重置后旧邀请码立即失效，已注册学生不受影响。确定重置？',
    '重置邀请码',
    { type: 'warning', confirmButtonText: '重置', cancelButtonText: '取消' }
  )
  try {
    const res = await api.post('/api/auth/invite-code')
    if (res.data.success) {
      inviteCode.value = res.data.invite_code
      ElMessage.success(`新邀请码：${res.data.invite_code}`)
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '重置失败')
  }
}

async function claimStudent(row) {
  try {
    const res = await api.post(`/api/auth/students/${row.id}/claim`)
    if (res.data.success) {
      ElMessage.success(res.data.message)
      refreshList()
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '认领失败')
  }
}

function downloadTemplate() {
  // 生成 Excel 模板
  const template = [
    { 姓名: '张三', 学号: '202401001', 班级: '物流2024-1班', 小组: '逐日组' },
    { 姓名: '李四', 学号: '202401002', 班级: '物流2024-1班', 小组: '逐日组' },
    { 姓名: '王五', 学号: '202401003', 班级: '物流2024-1班', 小组: '长空组' },
  ]
  const ws = XLSX.utils.json_to_sheet(template)
  ws['!cols'] = [{ wch: 12 }, { wch: 16 }, { wch: 20 }, { wch: 12 }]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生名单')
  XLSX.writeFile(wb, '学生导入模板.xlsx')
  ElMessage.success('模板已下载')
}

function handleFileChange(file) {
  selectedFile.value = file.raw
  parsedStudents.value = []
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件，请先移除当前文件')
}

async function handleParseExcel() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择 Excel 文件')
    return
  }

  try {
    const data = await selectedFile.value.arrayBuffer()
    const wb = XLSX.read(data)
    const ws = wb.Sheets[wb.SheetNames[0]]
    const rows = XLSX.utils.sheet_to_json(ws, { defval: '' })

    const parsed = rows.map(row => ({
      username: String(row['姓名'] || row['name'] || '').trim(),
      student_no: String(row['学号'] || row['student_no'] || '').trim(),
      class_name: String(row['班级'] || row['class'] || '').trim() || null,
      group_no: String(row['小组'] || row['group'] || '').trim() || null,
    })).filter(item => item.username && item.student_no)

    if (parsed.length === 0) {
      ElMessage.warning('未解析到有效数据，请检查表头是否为「姓名/学号/班级/小组」')
      return
    }

    parsedStudents.value = parsed
    ElMessage.success(`解析成功：共 ${parsed.length} 名学生`)
  } catch (err) {
    ElMessage.error('解析 Excel 失败：' + err.message)
  }
}

async function handleBatchImport() {
  if (parsedStudents.value.length === 0) return
  importing.value = true
  try {
    const res = await api.post('/api/auth/batch-register', {
      students: parsedStudents.value,
      default_password: '123456'
    })
    if (res.data.success) {
      ElMessage.success(res.data.message)
      if (res.data.fail_list.length > 0) {
        const failText = res.data.fail_list.map(f => `第${f.row}行：${f.reason}`).join('\n')
        ElMessageBox.alert(failText, '失败详情', { type: 'warning' })
      }
      showImportDialog.value = false
      parsedStudents.value = []
      selectedFile.value = null
      refreshList()
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '批量导入失败')
  } finally {
    importing.value = false
  }
}

async function handleReset(row) {
  try {
    await ElMessageBox.confirm(
      `确认重置「${row.username}」的密码为 123456？学生下次登录后需要修改密码。`,
      '重置密码',
      { type: 'warning' }
    )
    const res = await api.post(`/api/auth/reset-password/${row.id}`, { new_password: '123456' })
    if (res.data.success) {
      ElMessage.success(res.data.message)
      refreshList()
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '重置失败')
    }
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除学生「${row.username}」（${row.student_no}）？此操作不可恢复。`,
      '删除学生',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
    const res = await api.delete(`/api/auth/students/${row.id}`)
    if (res.data.success) {
      ElMessage.success(res.data.message)
      refreshList()
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  refreshList()
  fetchInviteCode()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
  color: #fff;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}
.header-right {
  display: flex;
  gap: 8px;
}
.back-btn {
  color: #c0c8d4 !important;
  font-size: 14px;
}
.back-btn:hover {
  color: #409eff !important;
}
.page-container h1 {
  margin: 0;
  font-size: 22px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 18px 20px;
}
.stat-label {
  font-size: 13px;
  color: #c0c8d4;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}
.stat-value.warn {
  color: #e6a23c;
}

.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

/* 操作按钮样式：深色背景下清晰可见，不用白加蓝 text 设计 */
.action-btn {
  border: 1px solid transparent !important;
  font-weight: 500 !important;
}
.action-btn .el-icon {
  margin-right: 2px;
}
.reset-btn {
  background: rgba(230, 162, 60, 0.15) !important;
  border-color: rgba(230, 162, 60, 0.4) !important;
  color: #e6a23c !important;
}
.reset-btn:hover {
  background: rgba(230, 162, 60, 0.3) !important;
  border-color: #e6a23c !important;
  color: #fff !important;
}
.delete-btn {
  background: rgba(245, 108, 108, 0.15) !important;
  border-color: rgba(245, 108, 108, 0.4) !important;
  color: #f56c6c !important;
}
.delete-btn:hover {
  background: rgba(245, 108, 108, 0.3) !important;
  border-color: #f56c6c !important;
  color: #fff !important;
}

/* 深色主题适配 Element Plus 表格 */
:deep(.el-table) {
  background: transparent;
  color: #e2e8f0;
}
:deep(.el-table tr),
:deep(.el-table td),
:deep(.el-table th.el-table__cell) {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.08);
}
:deep(.el-table tbody tr:hover > td) {
  background: rgba(64, 158, 255, 0.08) !important;
}
:deep(.el-table__inner-wrapper::before) {
  background-color: rgba(255, 255, 255, 0.08);
}
:deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(64, 158, 255, 0.2);
}

.import-tips {
  background: rgba(64, 158, 255, 0.06);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}
.import-tips p {
  margin: 0 0 8px;
  color: #c0c8d4;
}
.import-tips ol {
  margin: 0;
  padding-left: 20px;
  color: #c0c8d4;
  font-size: 13px;
  line-height: 1.8;
}
.import-tips code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 3px;
  color: #67c23a;
}

.preview-area {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
}
.preview-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  color: #67c23a;
  font-weight: 600;
}
.more-hint {
  text-align: center;
  color: #c0c8d4;
  font-size: 12px;
  margin: 8px 0 0;
}
</style>
