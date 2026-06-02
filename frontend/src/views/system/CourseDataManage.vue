<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/system')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          系统管理
        </el-button>
        <el-divider direction="vertical" />
        <h1>课程数据管理</h1>
      </div>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加项目
      </el-button>
    </div>

    <!-- 项目列表表格 -->
    <el-table
      :data="projects"
      v-loading="loading"
      style="width: 100%"
      row-key="id"
    >
      <el-table-column prop="project_id" label="项目编号" width="120" />
      <el-table-column prop="name" label="项目名称" min-width="200" />
      <el-table-column prop="hours" label="学时" width="80" align="center" />
      <el-table-column prop="task_count" label="任务数" width="80" align="center" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" align="center">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" type="warning" @click="handleImport(row)">导入</el-button>
          <el-button size="small" type="success" @click="handleExport(row)">导出</el-button>
          <el-popconfirm title="确定删除此项目？" @confirm="handleDelete(row)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑项目弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '添加项目'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="formData" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="项目编号" prop="project_id">
          <el-input v-model="formData.project_id" :disabled="isEdit" placeholder="如 P1, P2" />
        </el-form-item>
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="学时" prop="hours">
          <el-input-number v-model="formData.hours" :min="0" />
        </el-form-item>
        <el-form-item label="任务数" prop="task_count">
          <el-input-number v-model="formData.task_count" :min="0" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="关联认证">
          <el-select v-model="formData.certifications" multiple placeholder="选择认证类型" style="width: 100%">
            <el-option label="1+X证书" value="1+X证书" />
            <el-option label="技能大赛" value="技能大赛" />
            <el-option label="课程标准" value="课程标准" />
            <el-option label="行业认证" value="行业认证" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入JSON弹窗 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入项目数据"
      width="600px"
      destroy-on-close
    >
      <div class="import-area">
        <p class="import-tip">
          上传JSON文件，将覆盖项目 <strong>{{ importingProject?.project_id }}</strong> 的数据。
        </p>
        <p class="import-tip">支持的JSON格式：</p>
        <ul class="import-format-list">
          <li>直接是子项目数组</li>
          <li>包含 <code>sub_projects</code> 字段的对象</li>
          <li>包含 <code>sub_projects</code> + 四个图谱字段（<code>knowledge_graph</code>、<code>capability_graph</code>、<code>problem_graph</code>、<code>ideological_graph</code>）</li>
        </ul>
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".json"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .json 格式文件</div>
          </template>
        </el-upload>
        <div v-if="importPreview" class="import-preview">
          <p class="import-preview-title">数据预览</p>
          <div v-if="importPreview.subProjects.length" class="import-section">
            <el-tag type="primary" size="small" effect="dark">子项目数据</el-tag>
            <span class="import-count">{{ importPreview.subProjects.length }} 个子项目</span>
            <el-collapse class="import-collapse">
              <el-collapse-item v-for="(sp, idx) in importPreview.subProjects" :key="idx" :title="sp.name || `子项目 ${idx + 1}`">
                <div>学时: {{ sp.hours || 0 }}，任务数: {{ sp.tasks?.length || 0 }}</div>
              </el-collapse-item>
            </el-collapse>
          </div>
          <div v-if="importPreview.hasGraphs" class="import-section">
            <el-tag type="success" size="small" effect="dark">四图谱数据</el-tag>
            <span class="import-count">
              <span v-if="importPreview.knowledge_graph">知识图谱 </span>
              <span v-if="importPreview.capability_graph">能力图谱 </span>
              <span v-if="importPreview.problem_graph">问题图谱 </span>
              <span v-if="importPreview.ideological_graph">思政图谱</span>
            </span>
          </div>
          <el-empty v-if="!importPreview.subProjects.length && !importPreview.hasGraphs" description="未识别到有效数据" :image-size="60" />
        </div>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importing">确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 查看数据弹窗 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="项目数据预览"
      width="800px"
      destroy-on-close
    >
      <div class="view-area" v-loading="viewLoading">
        <div v-if="viewData" class="view-content">
          <div class="view-header">
            <h3>{{ viewData.name }} ({{ viewData.project_id }})</h3>
            <p>学时: {{ viewData.hours }} | 任务数: {{ viewData.task_count }}</p>
          </div>
          <div v-if="viewData.sub_projects && viewData.sub_projects.length" class="view-tree">
            <el-tree
              :data="buildTreeData(viewData.sub_projects)"
              :props="{ label: 'label', children: 'children' }"
              default-expand-all
            />
          </div>
          <el-empty v-else description="暂无子项目数据" />
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, UploadFilled, ArrowLeft } from '@element-plus/icons-vue'
import { fetchProjects, fetchProject, createProject, updateProject, deleteProject, uploadProjectFile } from '@/api/courseGraph'

const projects = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const importDialogVisible = ref(false)
const importingProject = ref(null)
const importPreview = ref(null)
const importFile = ref(null)
const importing = ref(false)
const uploadRef = ref(null)

const viewDialogVisible = ref(false)
const viewLoading = ref(false)
const viewData = ref(null)

const formData = ref({
  project_id: '',
  name: '',
  hours: 0,
  task_count: 0,
  description: '',
  certifications: [],
})

const formRules = {
  project_id: [{ required: true, message: '请输入项目编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

async function loadProjects() {
  loading.value = true
  try {
    const res = await fetchProjects()
    projects.value = res.data || []
  } catch (e) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  isEdit.value = false
  formData.value = { project_id: '', name: '', hours: 0, task_count: 0, description: '', certifications: [] }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateProject(formData.value.project_id, formData.value)
      ElMessage.success('更新成功')
    } else {
      await createProject(formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProjects()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

function handleImport(row) {
  importingProject.value = row
  importPreview.value = null
  importFile.value = null
  importDialogVisible.value = true
}

function handleFileChange(file) {
  importFile.value = file.raw
  importPreview.value = null

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target.result)
      let subProjects = []
      if (Array.isArray(json)) {
        subProjects = json
      } else if (json.sub_projects) {
        subProjects = json.sub_projects
      }
      importPreview.value = {
        subProjects,
        knowledge_graph: json.knowledge_graph || null,
        capability_graph: json.capability_graph || null,
        problem_graph: json.problem_graph || null,
        ideological_graph: json.ideological_graph || null,
        hasGraphs: !!(json.knowledge_graph || json.capability_graph || json.problem_graph || json.ideological_graph),
      }
    } catch {
      ElMessage.error('JSON解析失败，请检查文件格式')
    }
  }
  reader.readAsText(file.raw)
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

async function handleImportSubmit() {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  importing.value = true
  try {
    await uploadProjectFile(importingProject.value.project_id, importFile.value)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    loadProjects()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

async function handleExport(row) {
  try {
    const res = await fetchProject(row.project_id)
    const data = res.data
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.project_id}_${row.name}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

async function handleView(row) {
  viewDialogVisible.value = true
  viewLoading.value = true
  viewData.value = null
  try {
    const res = await fetchProject(row.project_id)
    viewData.value = res.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    viewLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await deleteProject(row.project_id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

function buildTreeData(subProjects) {
  return subProjects.map((sp, spIdx) => ({
    label: sp.name || `子项目 ${spIdx + 1}`,
    children: (sp.tasks || []).map((task, tIdx) => ({
      label: task.name || `任务 ${tIdx + 1}`,
      children: (task.points || []).map((pt, pIdx) => ({
        label: pt.name || `知识点 ${pIdx + 1}`,
      }))
    }))
  }))
}

onMounted(() => {
  loadProjects()
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
  margin-bottom: 20px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}
.back-btn {
  color: #c0c8d4 !important;
  font-size: 14px;
}
.back-btn:hover {
  color: #409eff !important;
}
.page-header h1 {
  margin: 0;
  font-size: 22px;
}
.import-area {
  padding: 10px 0;
}
.import-tip {
  color: #c0c8d4;
  font-size: 13px;
  margin-bottom: 10px;
}
.import-tip code {
  background: rgba(100, 160, 255, 0.15);
  padding: 2px 6px;
  border-radius: 3px;
  color: #60a5fa;
}
.import-preview {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}
.import-preview-title {
  color: #60a5fa;
  margin-bottom: 10px;
  font-weight: 600;
}
.import-section {
  margin-bottom: 12px;
}
.import-section:last-child { margin-bottom: 0; }
.import-count {
  font-size: 12px;
  color: #c0c8d4;
  margin-left: 8px;
}
.import-collapse { margin-top: 8px; }
.import-format-list {
  color: #c0c8d4;
  font-size: 13px;
  padding-left: 20px;
  margin: 0 0 12px;
}
.import-format-list li { margin-bottom: 4px; }
.view-area {
  min-height: 200px;
}
.view-header {
  margin-bottom: 16px;
}
.view-header h3 {
  margin: 0 0 4px;
  color: #fff;
}
.view-header p {
  margin: 0;
  color: #c0c8d4;
  font-size: 13px;
}
.view-tree {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
}

:deep(.el-table) {
  background: transparent;
  color: #e2e8f0;
}
:deep(.el-table th) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #c0c8d4;
}
:deep(.el-table td) {
  border-bottom-color: rgba(255, 255, 255, 0.06);
}
:deep(.el-table tr:hover > td) {
  background: rgba(255, 255, 255, 0.04) !important;
}
:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: rgba(255, 255, 255, 0.04) !important;
}
:deep(.el-dialog) {
  background: #1a2332;
}
:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
:deep(.el-dialog__title) {
  color: #fff;
}
:deep(.el-form-item__label) {
  color: #c0c8d4;
}
:deep(.el-upload-dragger) {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.15);
}
:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
}
:deep(.el-upload__text) {
  color: #c0c8d4;
}
</style>
