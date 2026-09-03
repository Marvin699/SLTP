<script setup>
/**
 * 用户使用手册弹窗
 * 内容源：仓库根目录 docs/用户使用手册.md（单一来源，?raw 导入）
 * 按章节切分，支持 学生版 / 教师版 切换（默认跟随当前用户角色）
 */
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import manualMd from '../../../docs/用户使用手册.md?raw'

const userStore = useUserStore()
const visible = defineModel({ type: Boolean, default: false })
const roleTab = ref(userStore.role === 'teacher' ? 'teacher' : 'student')

watch(visible, (v) => {
  if (v) roleTab.value = userStore.role === 'teacher' ? 'teacher' : 'student'
})

// ── 按章节标题切分手册 ──
const CHAPTER_HEADS = [
  '## 一、快速开始',
  '## 二、学生版使用说明',
  '## 三、教师版使用说明',
  '## 四、常见问题',
]

function splitChapters(md) {
  const lines = md.split('\n')
  const chunks = { head: [], s1: [], s2: [], s3: [], s4: [] }
  let cur = 'head'
  for (const line of lines) {
    const hit = CHAPTER_HEADS.findIndex((h) => line.startsWith(h))
    if (hit >= 0) cur = ['s1', 's2', 's3', 's4'][hit]
    chunks[cur].push(line)
  }
  return Object.fromEntries(Object.entries(chunks).map(([k, v]) => [k, v.join('\n')]))
}

const chapters = splitChapters(manualMd)

const mdSource = computed(() => {
  if (roleTab.value === 'teacher') {
    return [chapters.head, chapters.s1, chapters.s3, chapters.s4].join('\n')
  }
  return [chapters.head, chapters.s1, chapters.s2, chapters.s4].join('\n')
})

const html = computed(() => marked.parse(mdSource.value, { async: false }))

function goAnchor(e) {
  // 站内锚点链接一律拦截，手册内不跳转页面
  const a = e.target.closest('a')
  if (a && a.getAttribute('href')?.startsWith('/')) e.preventDefault()
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="min(920px, 94vw)"
    top="4vh"
    :show-close="true"
    append-to-body
    class="manual-dialog"
  >
    <template #header>
      <div class="manual-head">
        <span class="manual-title">📖 使用手册</span>
        <div class="role-switch">
          <button
            class="rs-btn"
            :class="{ active: roleTab === 'student' }"
            @click="roleTab = 'student'"
          >学生版</button>
          <button
            class="rs-btn"
            :class="{ active: roleTab === 'teacher' }"
            @click="roleTab = 'teacher'"
          >教师版</button>
        </div>
      </div>
    </template>
    <div class="manual-body" @click="goAnchor" v-html="html"></div>
  </el-dialog>
</template>

<style scoped>
.manual-head {
  display: flex;
  align-items: center;
  gap: 18px;
}
.manual-title {
  font-size: 17px;
  font-weight: 800;
  color: #e8f6ff;
  letter-spacing: 1px;
}
.role-switch {
  display: inline-flex;
  gap: 4px;
  padding: 3px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.rs-btn {
  padding: 4px 16px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: #9db2c9;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.rs-btn.active {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.25), rgba(59, 130, 246, 0.2));
  color: #67e8f9;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.2);
}

/* ── 正文 prose 样式（深空主题） ── */
.manual-body {
  max-height: calc(88vh - 90px);
  overflow-y: auto;
  padding: 4px 10px 30px;
  color: #c7d2e0;
  font-size: 13.5px;
  line-height: 1.75;
}
.manual-body :deep(h1) {
  font-size: 20px;
  color: #f0f9ff;
  padding-left: 12px;
  border-left: 4px solid #22d3ee;
  margin: 8px 0 14px;
}
.manual-body :deep(h2) {
  font-size: 16.5px;
  color: #67e8f9;
  margin: 26px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(34, 211, 238, 0.18);
}
.manual-body :deep(h3) {
  font-size: 14.5px;
  color: #a5e8f5;
  margin: 18px 0 8px;
}
.manual-body :deep(h4) {
  font-size: 13.5px;
  color: #93c5fd;
  margin: 14px 0 6px;
}
.manual-body :deep(p) { margin: 8px 0; }
.manual-body :deep(blockquote) {
  margin: 10px 0;
  padding: 8px 14px;
  border-left: 3px solid rgba(34, 211, 238, 0.5);
  background: rgba(34, 211, 238, 0.06);
  border-radius: 0 8px 8px 0;
  color: #9adbe8;
  font-size: 12.5px;
}
.manual-body :deep(blockquote p) { margin: 2px 0; }
.manual-body :deep(ul), .manual-body :deep(ol) { padding-left: 22px; margin: 8px 0; }
.manual-body :deep(li) { margin: 4px 0; }
.manual-body :deep(strong) { color: #e8f6ff; }
.manual-body :deep(code) {
  background: rgba(34, 211, 238, 0.1);
  color: #7dd3fc;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
}
.manual-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 12.5px;
}
.manual-body :deep(th) {
  background: rgba(34, 211, 238, 0.12);
  color: #a5e8f5;
  font-weight: 700;
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
}
.manual-body :deep(td) {
  padding: 7px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  vertical-align: top;
}
.manual-body :deep(tr:nth-child(even) td) { background: rgba(255, 255, 255, 0.02); }
.manual-body :deep(hr) {
  border: none;
  border-top: 1px dashed rgba(255, 255, 255, 0.12);
  margin: 20px 0;
}
.manual-body :deep(a) { color: #67e8f9; text-decoration: none; }
</style>

<style>
/* el-dialog 深色化（append-to-body 需非 scoped） */
.manual-dialog .el-dialog {
  background: rgba(10, 18, 32, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}
.manual-dialog .el-dialog__header {
  padding: 18px 24px 12px;
  margin-right: 0;
}
.manual-dialog .el-dialog__title { color: #e8f6ff; }
.manual-dialog .el-dialog__body { padding: 4px 24px 16px; }
.manual-dialog .el-dialog__headerbtn .el-dialog__close {
  color: #9db2c9;
  font-size: 18px;
}
.manual-dialog .el-dialog__headerbtn .el-dialog__close:hover { color: #67e8f9; }
</style>
