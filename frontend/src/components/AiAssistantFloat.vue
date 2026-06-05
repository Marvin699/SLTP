<template>
  <div class="ai-float-wrapper">
    <!-- 悬浮球按钮 -->
    <div
      class="float-button"
      :class="{ 'is-open': isOpen, 'is-thinking': thinking, 'has-badge': hasUnread }"
      @click="togglePanel"
    >
      <div class="float-avatar">
        <img
          src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20blue%20futuristic%20AI%20robot%20mascot%20character%20with%20wings%20and%20antenna%2C%20friendly%20smile%2C%20high%20quality%20digital%20art%2C%203D%20render%2C%20clean%20background%2C%20simple%20PNG%20icon%2C%20front%20view&image_size=square_hd"
          alt="小翼"
          @error="onAvatarError"
        />
        <div class="avatar-glow"></div>
        <div v-if="thinking" class="thinking-ring"></div>
      </div>
      <span class="float-label">小翼</span>
      <div class="float-badge" v-if="hasUnread">1</div>
    </div>

    <!-- 对话面板 -->
    <transition name="float-panel">
      <div v-if="isOpen" class="float-panel">
        <div class="panel-header">
          <div class="panel-title">
            <span class="panel-avatar">翼</span>
            <span class="panel-name">小翼 · AI智能助教</span>
            <el-tag type="success" size="small" effect="dark">在线</el-tag>
          </div>
          <div class="panel-actions">
            <el-tooltip content="最小化" placement="top">
              <button class="panel-btn" @click="isOpen = false">
                <el-icon><Minus /></el-icon>
              </button>
            </el-tooltip>
            <el-tooltip content="全屏对话" placement="top">
              <button class="panel-btn" @click="openFull">
                <el-icon><FullScreen /></el-icon>
              </button>
            </el-tooltip>
          </div>
        </div>

        <div class="panel-messages" ref="messagesRef">
          <div
            v-for="(msg, i) in chatMessages"
            :key="i"
            class="msg-item"
            :class="msg.role"
          >
            <div class="msg-avatar" :class="msg.role">
              {{ msg.role === 'user' ? '我' : '翼' }}
            </div>
            <div class="msg-body">
              <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
              <div class="msg-time">{{ msg.time }}</div>
            </div>
          </div>
          <div v-if="chatLoading" class="msg-item assistant">
            <div class="msg-avatar assistant">翼</div>
            <div class="msg-body">
              <div class="msg-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-quick">
          <div
            v-for="q in quickQs"
            :key="q"
            class="quick-q"
            @click="askQuick(q)"
          >{{ q }}</div>
        </div>

        <div class="panel-input">
          <el-input
            v-model="chatInput"
            size="small"
            type="textarea"
            :rows="2"
            placeholder="问小翼一个问题..."
            @keydown.enter.exact.prevent="sendChat"
            :disabled="chatLoading"
            resize="none"
          />
          <el-button
            type="primary"
            size="small"
            @click="sendChat"
            :loading="chatLoading"
            :disabled="!chatInput.trim()"
            circle
          >
            <el-icon><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Minus, FullScreen, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const isOpen = ref(false)
const thinking = ref(false)
const chatInput = ref('')
const chatLoading = ref(false)
const messagesRef = ref(null)
const hasUnread = ref(false)

const quickQs = [
  '什么是低空应急运输？',
  '无人机航线规划原则？',
  '如何评估运输方案？',
  '装箱优化常用算法？'
]

const chatMessages = ref([
  {
    role: 'assistant',
    content: '你好！我是小翼 🛩️，你的AI智能助教。点击下方问我问题吧～',
    time: formatTime(new Date())
  }
])

function togglePanel() {
  isOpen.value = !isOpen.value
  if (isOpen.value) hasUnread.value = false
}

function onAvatarError(e) {
  const img = e.target
  img.style.display = 'none'
}

function openFull() {
  isOpen.value = false
  router.push('/ai-assistant')
}

function formatTime(d) {
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatMessage(c) {
  return c.replace(/\n/g, '<br>')
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  chatMessages.value.push({
    role: 'user',
    content: text,
    time: formatTime(new Date())
  })
  chatInput.value = ''
  chatLoading.value = true
  thinking.value = true
  await nextTick()
  scrollBottom()

  try {
    const res = await axios.post('/api/ai-chat/chat', {
      messages: chatMessages.value
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }))
    })
    if (res.data.success) {
      chatMessages.value.push({
        role: 'assistant',
        content: res.data.reply,
        time: formatTime(new Date())
      })
    } else {
      chatMessages.value.push({
        role: 'assistant',
        content: res.data.message || '抱歉，暂时无法响应。',
        time: formatTime(new Date())
      })
    }
  } catch (e) {
    chatMessages.value.push({
      role: 'assistant',
      content: '网络异常，请稍后重试。',
      time: formatTime(new Date())
    })
  } finally {
    chatLoading.value = false
    thinking.value = false
    await nextTick()
    scrollBottom()
  }
}

function askQuick(q) {
  chatInput.value = q
  sendChat()
}

function scrollBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-float-wrapper {
  position: fixed;
  right: 24px;
  bottom: 28px;
  z-index: 9998;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ===== 悬浮球按钮 ===== */
.float-button {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.float-button:hover {
  transform: scale(1.08);
}

.float-button.is-open {
  transform: scale(0);
  pointer-events: none;
}

.float-avatar {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #14b8a6 100%);
  box-shadow: 0 6px 24px rgba(14, 165, 233, 0.45), 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.float-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-glow {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6, #0ea5e9);
  z-index: -1;
  animation: glowPulse 2.8s ease-in-out infinite;
  filter: blur(8px);
  opacity: 0.7;
}

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 0.9; }
}

.thinking-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #0ea5e9;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.float-label {
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #0ea5e9;
  background: rgba(255, 255, 255, 0.95);
  padding: 2px 10px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  white-space: nowrap;
}

.float-badge {
  position: absolute;
  top: -2px;
  right: 0;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background: #ef4444;
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.4);
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

/* ===== 对话面板 ===== */
.float-panel {
  position: absolute;
  bottom: 84px;
  right: 0;
  width: 380px;
  height: 520px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18), 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(14, 165, 233, 0.15);
  animation: floatIn 0.3s ease-out;
}

@keyframes floatIn {
  from { opacity: 0; transform: translateY(16px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.float-panel.float-panel-leave {
  animation: floatOut 0.2s ease-in forwards;
}

@keyframes floatOut {
  to { opacity: 0; transform: translateY(10px) scale(0.95); }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfeff 100%);
  border-bottom: 1px solid rgba(14, 165, 233, 0.12);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: white;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-name {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.panel-actions {
  display: flex;
  gap: 4px;
}

.panel-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.panel-btn:hover {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
}

/* 消息区 */
.panel-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 12px 4px;
  background: #fafbfc;
}

.msg-item {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.msg-item.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.msg-avatar.user {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.msg-avatar.assistant {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6);
  color: white;
}

.msg-body {
  max-width: 80%;
  display: flex;
  flex-direction: column;
}

.msg-item.user .msg-body {
  align-items: flex-end;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.55;
  word-break: break-word;
}

.msg-item.user .msg-bubble {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-item.assistant .msg-bubble {
  background: white;
  color: #1e293b;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.msg-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  justify-content: center;
}

.typing span {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typingBounce 1.2s ease-in-out infinite;
}

.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* 快捷问题 */
.panel-quick {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 12px;
  background: #fafbfc;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.quick-q {
  font-size: 12px;
  padding: 4px 10px;
  background: white;
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: #0ea5e9;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-q:hover {
  background: rgba(14, 165, 233, 0.08);
  border-color: #0ea5e9;
}

/* 输入区 */
.panel-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 12px 14px;
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.panel-input :deep(.el-textarea__inner) {
  border-radius: 10px;
  font-size: 14px;
  resize: none;
}

.panel-input .el-button {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
}
</style>
