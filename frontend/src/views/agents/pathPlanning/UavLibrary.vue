<template>
  <div class="uav-library">
    <div class="action-bar">
      <button class="btn btn-primary" @click="openCreate">+ 新建机型</button>
      <span class="lib-count">共 {{ models.length }} 个机型</span>
    </div>

    <div v-if="loading" class="loading-text">加载中...</div>
    <div v-else-if="!models.length" class="empty-text">暂无机型，点击"新建机型"添加</div>
    <div v-else class="model-grid">
      <div v-for="m in models" :key="m.model_id" class="model-card">
        <div class="model-head">
          <span class="model-name">{{ m.brand }} {{ m.model }}</span>
          <div class="model-actions">
            <button class="btn btn-sm btn-secondary" @click="openEdit(m)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="handleDelete(m)">删除</button>
          </div>
        </div>
        <div class="model-specs">
          <span class="spec">载重 {{ m.max_payload }}kg</span>
          <span class="spec">航程 {{ m.range_km }}km</span>
          <span class="spec">{{ m.max_speed }}km/h</span>
          <span v-if="m.wind_resist" class="spec">抗风{{ m.wind_resist }}级</span>
          <span v-if="m.drop_mode" class="spec">{{ m.drop_mode }}</span>
        </div>
        <div v-if="m.description" class="model-desc">{{ m.description }}</div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editing ? '编辑机型' : '新建机型' }}</h3>
        <div class="form-grid">
          <label class="f-item"><span>品牌</span><input v-model="form.brand" placeholder="如 大疆" /></label>
          <label class="f-item"><span>型号名称</span><input v-model="form.model" placeholder="如 运载先锋 F100" /></label>
          <label class="f-item"><span>最大载重 (kg)</span><input v-model.number="form.max_payload" type="number" min="0.1" step="0.1" /></label>
          <label class="f-item"><span>航程 (km)</span><input v-model.number="form.range_km" type="number" min="1" /></label>
          <label class="f-item"><span>最大速度 (km/h)</span><input v-model.number="form.max_speed" type="number" min="1" /></label>
          <label class="f-item"><span>抗风等级 (级)</span><input v-model.number="form.wind_resist" type="number" min="0" max="12" /></label>
          <label class="f-item f-wide"><span>投放方式</span><input v-model="form.drop_mode" placeholder="如 空投/索降/吊运" /></label>
          <label class="f-item f-wide"><span>适用场景</span><input v-model="form.suitableText" placeholder="逗号分隔，如 应急投送, 物资配送" /></label>
          <label class="f-item f-wide"><span>描述</span><textarea v-model="form.description" rows="2" placeholder="机型的简要说明"></textarea></label>
        </div>
        <div v-if="modalError" class="modal-error">{{ modalError }}</div>
        <div class="modal-actions">
          <button class="btn btn-primary" :disabled="saving" @click="handleSave">{{ saving ? '保存中...' : '保存' }}</button>
          <button class="btn btn-secondary" @click="closeModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 机型库管理面板（信息管理聚合页 - 机型库子页签）
 * 机型的增删改，数据存 uav_params 表，步骤③选型实时生效
 */
import { ref, onMounted } from 'vue'
import { fetchModels, createUAVModel, updateUAVModel, deleteUAVModel } from '@/api/pathPlanning/uavs'

const models = ref([])
const loading = ref(false)

const showModal = ref(false)
const editing = ref(null) // 编辑中的 model_id，null = 新建
const saving = ref(false)
const modalError = ref('')
const emptyForm = {
  brand: '', model: '', max_payload: 10, range_km: 20, max_speed: 60,
  wind_resist: 6, drop_mode: '', suitableText: '', description: '',
}
const form = ref({ ...emptyForm })

async function loadModels() {
  loading.value = true
  try {
    const res = await fetchModels()
    models.value = res.data || []
  } catch {
    models.value = []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.value = { ...emptyForm }
  modalError.value = ''
  showModal.value = true
}

function openEdit(m) {
  editing.value = m.model_id
  form.value = {
    brand: m.brand || '',
    model: m.model || '',
    max_payload: m.max_payload,
    range_km: m.range_km,
    max_speed: m.max_speed,
    wind_resist: m.wind_resist || 0,
    drop_mode: m.drop_mode || '',
    suitableText: (m.suitable_for || []).join(', '),
    description: m.description || '',
  }
  modalError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function handleSave() {
  if (!form.value.model?.trim()) {
    modalError.value = '请填写型号名称'
    return
  }
  saving.value = true
  modalError.value = ''
  const payload = {
    brand: form.value.brand?.trim() || '自定义',
    model: form.value.model.trim(),
    max_payload: form.value.max_payload,
    range_km: form.value.range_km,
    max_speed: form.value.max_speed,
    wind_resist: form.value.wind_resist || null,
    drop_mode: form.value.drop_mode?.trim() || '',
    suitable_for: (form.value.suitableText || '').split(/[,，]/).map(s => s.trim()).filter(Boolean),
    description: form.value.description?.trim() || '',
  }
  try {
    if (editing.value) {
      await updateUAVModel(editing.value, payload)
    } else {
      await createUAVModel(payload)
    }
    showModal.value = false
    await loadModels()
  } catch (e) {
    modalError.value = e.response?.data?.detail || e.message
  } finally {
    saving.value = false
  }
}

async function handleDelete(m) {
  if (!confirm(`确定删除机型「${m.brand} ${m.model}」？\n删除后学生选型列表将不再显示该机型。`)) return
  try {
    await deleteUAVModel(m.model_id)
    await loadModels()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(loadModels)
</script>

<style scoped>
/* 按钮体系（scoped 样式无法继承父组件 Module7 的 .btn 定义，需自带） */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text, #e2e8f0);
  font-size: 13px;
  padding: 7px 14px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn:hover { border-color: rgba(255, 255, 255, 0.3); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary {
  background: var(--teal, #2dd4bf);
  border-color: var(--teal, #2dd4bf);
  color: #04211d;
  font-weight: 600;
}
.btn-primary:hover { filter: brightness(1.1); }
.btn-secondary { color: var(--text2, #c0c8d4); }
.btn-danger {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(248, 113, 113, 0.06);
}
.btn-danger:hover { background: rgba(248, 113, 113, 0.15); }
.btn-sm { padding: 4px 10px; font-size: 12px; border-radius: 6px; }

.action-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.lib-count { font-size: 13px; color: #64748b; }
.loading-text, .empty-text { text-align: center; color: #64748b; padding: 30px 0; font-size: 13px; }
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.model-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 12px 14px;
}
.model-head { display: flex; justify-content: space-between; align-items: center; }
.model-name { font-weight: 600; color: var(--text, #e2e8f0); font-size: 14px; }
.model-actions { display: flex; gap: 6px; }
.model-specs { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.spec {
  font-size: 11px;
  color: #60a5fa;
  background: rgba(96,165,250,0.08);
  border: 1px solid rgba(96,165,250,0.2);
  border-radius: 6px;
  padding: 1px 7px;
}
.model-desc { margin-top: 8px; font-size: 12px; color: var(--text3, #8a97a8); line-height: 1.5; }

.modal-mask {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.modal {
  width: min(560px, 92vw);
  max-height: 86vh;
  overflow-y: auto;
  background: #101b33;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 20px 22px;
}
.modal h3 { margin: 0 0 14px; color: var(--text, #e2e8f0); font-size: 16px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; }
.f-item { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--text3, #8a97a8); }
.f-item.f-wide { grid-column: 1 / -1; }
.f-item input, .f-item textarea {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: var(--text, #e2e8f0);
  padding: 7px 9px;
  font-size: 13px;
  outline: none;
}
.f-item input:focus, .f-item textarea:focus { border-color: var(--teal, #2dd4bf); }
.modal-error { margin-top: 10px; color: #f56c6c; font-size: 12px; }
.modal-actions { display: flex; gap: 10px; margin-top: 16px; }
</style>
