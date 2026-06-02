<script setup>
import { ref, onMounted } from 'vue'
import { useLLMStore } from '@/stores/pathPlanning/llm'

const llmStore = useLLMStore()

// 弹窗控制
const showModal = ref(false)
const modalTitle = ref('')
const editingId = ref(null)

// 表单数据
const form = ref({
  name: '',
  model_id: '',
  base_url: '',
  api_key: '',
  description: '',
  is_default: false,
})

// 测试状态
const testResult = ref(null)

onMounted(() => {
  llmStore.loadConfigs()
})

function openAddModal() {
  modalTitle.value = '添加大模型'
  editingId.value = null
  form.value = {
    name: '',
    model_id: '',
    base_url: 'https://api.deepseek.com',
    api_key: '',
    description: '',
    is_default: false,
  }
  testResult.value = null
  showModal.value = true
}

function openEditModal(config) {
  modalTitle.value = '编辑大模型'
  editingId.value = config.id
  form.value = {
    name: config.name,
    model_id: config.model_id,
    base_url: config.base_url,
    api_key: config.api_key,
    description: config.description || '',
    is_default: config.is_default,
  }
  testResult.value = null
  showModal.value = true
}

async function handleSave() {
  if (!form.value.name || !form.value.model_id || !form.value.base_url || !form.value.api_key) {
    alert('请填写完整信息')
    return
  }

  let result
  if (editingId.value) {
    result = await llmStore.updateConfig(editingId.value, form.value)
  } else {
    result = await llmStore.addConfig(form.value)
  }

  if (result) {
    showModal.value = false
  }
}

async function handleDelete(id) {
  if (confirm('确定删除此模型配置？')) {
    await llmStore.removeConfig(id)
  }
}

async function handleActivate(id) {
  await llmStore.activateConfig(id)
}

async function handleTest(id) {
  testResult.value = null
  const result = await llmStore.testConnection(id)
  testResult.value = result
}

function closeModal() {
  showModal.value = false
  testResult.value = null
}

function maskKey(key) {
  if (!key || key.length < 8) return key
  return key.substring(0, 6) + '****' + key.substring(key.length - 4)
}
</script>

<template>
  <div class="module8-container">
    <!-- 头部 -->
    <div class="module-header">
      <h2>系统管理</h2>
      <p class="module-desc">管理大模型配置和系统设置</p>
    </div>

    <!-- 当前激活模型 -->
    <div class="active-section">
      <div class="active-label">当前使用模型</div>
      <div class="active-model" v-if="llmStore.activeConfig">
        <span class="model-name">{{ llmStore.activeConfig.name }}</span>
        <span class="model-id">{{ llmStore.activeConfig.model_id }}</span>
        <span class="model-badge active">运行中</span>
      </div>
      <div class="active-model empty" v-else>
        <span>未配置大模型</span>
      </div>
    </div>

    <!-- 大模型列表 -->
    <div class="llm-section">
      <div class="section-header">
        <h3>大模型配置</h3>
        <button class="btn btn-primary" @click="openAddModal">
          + 添加模型
        </button>
      </div>

      <div v-if="llmStore.loading" class="loading-text">加载中...</div>
      <div v-else-if="!llmStore.hasConfigs" class="empty-text">
        暂无模型配置，请点击"添加模型"
      </div>
      <div v-else class="llm-list">
        <div
          v-for="config in llmStore.configs"
          :key="config.id"
          class="llm-card"
          :class="{ active: config.is_active }"
        >
          <div class="llm-card-header">
            <div class="llm-name">
              {{ config.name }}
              <span v-if="config.is_default" class="default-badge">默认</span>
              <span v-if="config.is_active" class="active-badge">当前使用</span>
            </div>
            <div class="llm-actions">
              <button
                v-if="!config.is_active"
                class="btn btn-sm btn-success"
                @click="handleActivate(config.id)"
              >
                启用
              </button>
              <button
                class="btn btn-sm btn-secondary"
                @click="openEditModal(config)"
              >
                编辑
              </button>
              <button
                class="btn btn-sm btn-info"
                :disabled="llmStore.testingId === config.id"
                @click="handleTest(config.id)"
              >
                {{ llmStore.testingId === config.id ? '测试中...' : '测试' }}
              </button>
              <button
                class="btn btn-sm btn-danger"
                @click="handleDelete(config.id)"
              >
                删除
              </button>
            </div>
          </div>
          <div class="llm-info">
            <div class="info-row">
              <span class="info-label">模型ID:</span>
              <span class="info-value">{{ config.model_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">API地址:</span>
              <span class="info-value">{{ config.base_url }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">API Key:</span>
              <span class="info-value">{{ maskKey(config.api_key) }}</span>
            </div>
            <div class="info-row" v-if="config.description">
              <span class="info-label">描述:</span>
              <span class="info-value">{{ config.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ modalTitle }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>模型名称 <span class="required">*</span></label>
              <input v-model="form.name" placeholder="如：DeepSeek-V3" />
            </div>
            <div class="form-group">
              <label>模型ID <span class="required">*</span></label>
              <input v-model="form.model_id" placeholder="如：deepseek-chat" />
            </div>
            <div class="form-group">
              <label>API地址 <span class="required">*</span></label>
              <input v-model="form.base_url" placeholder="如：https://api.deepseek.com" />
            </div>
            <div class="form-group">
              <label>API Key <span class="required">*</span></label>
              <input v-model="form.api_key" type="password" placeholder="输入API密钥" />
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="form.description" rows="2" placeholder="可选：模型描述"></textarea>
            </div>
            <div class="form-group checkbox">
              <label>
                <input v-model="form.is_default" type="checkbox" />
                设为默认模型
              </label>
            </div>

            <!-- 测试结果 -->
            <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
              <div class="test-title">{{ testResult.success ? '✅ 连接成功' : '❌ 连接失败' }}</div>
              <div class="test-message">{{ testResult.message }}</div>
              <div v-if="testResult.response" class="test-response">响应: {{ testResult.response }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button v-if="editingId" class="btn btn-info" @click="handleTest(editingId)">测试连接</button>
            <button class="btn btn-primary" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.module8-container {
  padding: 16px;
}

.module-header {
  margin-bottom: 20px;
}

.module-header h2 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.module-desc {
  margin: 0;
  font-size: 12px;
  color: var(--text3);
}

/* 当前激活模型 */
.active-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.active-label {
  font-size: 11px;
  color: var(--text3);
  margin-bottom: 8px;
}

.active-model {
  display: flex;
  align-items: center;
  gap: 12px;
}

.active-model.empty {
  color: var(--text3);
  font-size: 13px;
}

.model-name {
  font-size: 14px;
  font-weight: bold;
}

.model-id {
  font-size: 12px;
  color: var(--text3);
  font-family: var(--mono);
}

.model-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--teal);
  color: var(--navy);
}

/* 大模型列表 */
.llm-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 14px;
}

.llm-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.llm-card {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  background: var(--navy2);
}

.llm-card.active {
  border-color: var(--teal);
  background: rgba(0, 255, 200, 0.05);
}

.llm-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.llm-name {
  font-size: 13px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.default-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--orange);
  color: white;
}

.active-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--teal);
  color: var(--navy);
}

.llm-actions {
  display: flex;
  gap: 6px;
}

.llm-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.info-label {
  color: var(--text3);
  width: 70px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text2);
  word-break: break-all;
}

/* 按钮 */
.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.85;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--teal);
  color: var(--navy);
}

.btn-secondary {
  background: var(--border);
  color: var(--text);
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-info {
  background: #1890ff;
  color: white;
}

.btn-danger {
  background: #f5222d;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 480px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 14px;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text3);
  cursor: pointer;
  font-size: 16px;
}

.modal-body {
  padding: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
}

/* 表单 */
.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  color: var(--text2);
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--navy2);
  color: var(--text);
  font-size: 12px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--teal);
}

.required {
  color: #f5222d;
}

/* 测试结果 */
.test-result {
  margin-top: 12px;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
}

.test-result.success {
  background: rgba(82, 196, 26, 0.1);
  border: 1px solid #52c41a;
}

.test-result.error {
  background: rgba(245, 34, 45, 0.1);
  border: 1px solid #f5222d;
}

.test-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.test-message {
  color: var(--text2);
}

.test-response {
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid var(--border);
  color: var(--text3);
  font-size: 11px;
}

/* 空状态 */
.loading-text,
.empty-text {
  text-align: center;
  padding: 24px;
  color: var(--text3);
  font-size: 12px;
}
</style>