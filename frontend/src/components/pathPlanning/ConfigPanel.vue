<script setup>
import { ref, onMounted } from 'vue'
import { useConfigStore } from '@/stores/pathPlanning/config'
import { saveConfig } from '@/api/pathPlanning/config'

const props = defineProps({
  moduleKey: { type: String, required: true }, // 'module1' | 'module2' | 'module3'
})

const emit = defineEmits(['close'])

const configStore = useConfigStore()
const content = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('info')

onMounted(async () => {
  await refreshContent()
})

async function refreshContent() {
  loading.value = true
  try {
    content.value = await configStore.loadCombinedConfig()
    if (!content.value) {
      content.value = '# 低空应急智慧运输 — 任务配置信息\n\n> 尚未保存任何配置\n'
    }
  } catch (e) {
    content.value = '# 低空应急智慧运输 — 任务配置信息\n\n> 读取失败\n'
  } finally {
    loading.value = false
  }
}

function showMsg(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

// 保存当前模块到合并文件
async function handleSaveModule() {
  loading.value = true
  try {
    await configStore.saveModuleSection(props.moduleKey)
    // 从文件重新读取，确保显示的是实际保存的内容
    await refreshContent()
    showMsg('已保存到 ' + configStore.COMBINED_FILENAME, 'success')
  } catch (e) {
    showMsg('保存失败: ' + (e.response?.data?.detail || e.message || '未知错误'), 'error')
  } finally {
    loading.value = false
  }
}

// 手动编辑后保存整个文件
async function handleSaveAll() {
  loading.value = true
  try {
    await saveConfig(configStore.COMBINED_FILENAME, content.value)
    showMsg('已保存', 'success')
  } catch (e) {
    showMsg('保存失败', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="config-panel">
    <div class="config-header">
      <span class="config-title">配置信息 — {{ configStore.COMBINED_FILENAME }}</span>
      <button
        class="btn-close"
        @click="emit('close')"
      >
        ✕
      </button>
    </div>

    <div class="config-body">
      <!-- 操作区 -->
      <div class="action-row">
        <button
          class="btn btn-save"
          :disabled="loading"
          @click="handleSaveModule"
        >
          保存当前模块到文件
        </button>
        <button
          class="btn btn-save-all"
          :disabled="loading"
          @click="handleSaveAll"
        >
          保存编辑内容
        </button>
        <button
          class="btn btn-refresh"
          :disabled="loading"
          @click="refreshContent"
        >
          刷新
        </button>
      </div>

      <!-- 消息 -->
      <div
        v-if="message"
        class="msg"
        :class="messageType"
      >
        {{ message }}
      </div>

      <!-- 说明 -->
      <div class="hint">
        所有模块配置保存在同一个文件中，用标记分隔各模块内容，方便整体发送给 AI 大模型。
      </div>

      <!-- 编辑区 -->
      <textarea
        v-model="content"
        class="content-editor"
        placeholder="Markdown 配置内容..."
      ></textarea>
    </div>
  </div>
</template>

<style scoped>
.config-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 460px;
  height: 100vh;
  background: var(--navy2);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 500;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--navy3);
}

.config-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}

.btn-close {
  background: none;
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text3);
  cursor: pointer;
  padding: 2px 8px;
  font-size: 12px;
}

.btn-close:hover {
  border-color: var(--red);
  color: var(--red);
}

.config-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Action row */
.action-row {
  display: flex;
  gap: 6px;
}

/* Buttons */
.btn {
  padding: 7px 12px;
  border-radius: 5px;
  font-size: 10px;
  font-family: var(--sans);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-save {
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
}

.btn-save:hover:not(:disabled) {
  box-shadow: var(--glow-teal);
}

.btn-save-all {
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
}

.btn-save-all:hover:not(:disabled) {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-refresh {
  background: var(--navy);
  color: var(--text3);
  border: 1px solid var(--border2);
}

.btn-refresh:hover:not(:disabled) {
  border-color: var(--text3);
  color: var(--text2);
}

/* Message */
.msg {
  padding: 6px 10px;
  border-radius: 5px;
  font-size: 10px;
}

.msg.info {
  background: rgba(0, 229, 255, 0.08);
  color: var(--teal);
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.msg.success {
  background: rgba(0, 230, 118, 0.08);
  color: var(--green);
  border: 1px solid rgba(0, 230, 118, 0.2);
}

.msg.error {
  background: rgba(255, 61, 87, 0.08);
  color: var(--red);
  border: 1px solid rgba(255, 61, 87, 0.2);
}

/* Hint */
.hint {
  font-size: 10px;
  color: var(--text3);
  padding: 6px 8px;
  background: rgba(0, 229, 255, 0.04);
  border: 1px solid rgba(0, 229, 255, 0.1);
  border-radius: 5px;
}

/* Editor */
.content-editor {
  flex: 1;
  min-height: 400px;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  padding: 10px;
  font-size: 11px;
  font-family: var(--mono);
  line-height: 1.6;
  resize: none;
  outline: none;
}

.content-editor:focus {
  border-color: var(--teal);
}
</style>
