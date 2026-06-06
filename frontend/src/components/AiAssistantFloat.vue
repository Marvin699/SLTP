<template>
  <div class="ai-float-wrapper">
    <!-- 悬浮球按钮 -->
    <div
      class="float-button"
      :class="{ 'is-open': isOpen }"
      @click="togglePanel"
    >
      <!-- 和原AI助教页面一样的数字人，整体缩小 -->
      <div class="mini-digital-avatar" :class="{ idle: true, thinking: thinking }">
        <div class="mini-avatar-glow"></div>
        <div class="mini-avatar-head">
          <div class="mini-avatar-face">
            <div class="mini-eyes">
              <div class="mini-eye"><div class="mini-pupil"></div></div>
              <div class="mini-eye"><div class="mini-pupil"></div></div>
            </div>
            <div class="mini-mouth" :class="{ talking: thinking }">
              <div class="mini-mouth-shape"></div>
            </div>
          </div>
          <div class="mini-antenna">
            <div class="mini-antenna-line"></div>
            <div class="mini-antenna-dot"></div>
          </div>
        </div>
        <div class="mini-avatar-body">
          <div class="mini-body-core">
            <div class="mini-core-ring"></div>
            <div class="mini-core-dot"></div>
          </div>
          <div class="mini-wing mini-left-wing"></div>
          <div class="mini-wing mini-right-wing"></div>
        </div>
      </div>
      <span class="float-label">小翼</span>
    </div>

    <!-- 对话面板 -->
    <transition name="float-panel">
      <div v-if="isOpen" class="float-panel">
        <div class="panel-header">
          <div class="panel-title">
            <div class="panel-avatar">翼</div>
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
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Minus, FullScreen, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const isOpen = ref(false)
const thinking = ref(false)
const chatInput = ref('')
const chatLoading = ref(false)
const messagesRef = ref(null)

const quickQs = [
  '什么是低空应急运输？',
  '无人机航线规划原则？',
  '如何评估运输方案？',
  '装箱优化常用算法？'
]

const chatMessages = ref([
  {
    role: 'assistant',
    content: '你好！我是小翼，你的AI智能助教。点击下方问我问题吧～',
    time: formatTime(new Date())
  }
])

function togglePanel() {
  isOpen.value = !isOpen.value
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
  width: 88px;
  height: 96px;
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

/* ===== 和原AI助教页面一模一样的数字人，整体缩小 ===== */
.mini-digital-avatar {
  position: relative;
  width: 72px;
  height: 88px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: miniAvatarFloat 3s ease-in-out infinite;
}

@keyframes miniAvatarFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.mini-digital-avatar.thinking {
  animation: miniAvatarThinking 0.6s ease-in-out infinite;
}
@keyframes miniAvatarThinking {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-1px) scale(1.04); }
}

/* 光晕 */
.mini-avatar-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 229, 255, 0.25) 0%, transparent 70%);
  animation: miniGlowPulse 3s ease-in-out infinite;
}

@keyframes miniGlowPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
}

.mini-digital-avatar.thinking .mini-avatar-glow {
  animation: miniGlowThinking 0.8s ease-in-out infinite;
}
@keyframes miniGlowThinking {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
  50% { transform: translate(-50%, -50%) scale(1.25); opacity: 1; }
}

/* 头部 */
.mini-avatar-head {
  position: relative;
  width: 48px;
  height: 48px;
  z-index: 2;
}

.mini-avatar-face {
  width: 48px;
  height: 43px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 19px 19px 16px 16px;
  border: 1px solid rgba(0, 229, 255, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.25), inset 0 0 8px rgba(0, 229, 255, 0.1);
}

/* 眼睛 */
.mini-eyes {
  display: flex;
  gap: 12px;
}

.mini-eye {
  width: 9px;
  height: 9px;
  background: #0a1628;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 229, 255, 0.6);
}

.mini-pupil {
  width: 4px;
  height: 4px;
  background: #00e5ff;
  border-radius: 50%;
  animation: miniBlink 4s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.9);
}

@keyframes miniBlink {
  0%, 45%, 55%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

/* 嘴巴 */
.mini-mouth {
  width: 10px;
  height: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-mouth-shape {
  width: 8px;
  height: 2px;
  background: rgba(0, 229, 255, 0.6);
  border-radius: 0 0 4px 4px;
  transition: all 0.15s;
}

.mini-mouth.talking .mini-mouth-shape {
  height: 5px;
  border-radius: 2px;
  animation: miniTalk 0.3s ease-in-out infinite alternate;
  background: rgba(0, 229, 255, 0.85);
}

@keyframes miniTalk {
  0% { height: 2px; width: 7px; }
  100% { height: 5px; width: 10px; }
}

/* 天线 */
.mini-antenna {
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mini-antenna-line {
  width: 1px;
  height: 7px;
  background: linear-gradient(to top, rgba(0, 229, 255, 0.6), rgba(0, 229, 255, 0.2));
}

.mini-antenna-dot {
  width: 3px;
  height: 3px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.9);
  animation: miniAntennaBlink 2s ease-in-out infinite;
}

@keyframes miniAntennaBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 身体 */
.mini-avatar-body {
  position: relative;
  width: 38px;
  height: 34px;
  margin-top: -2px;
  z-index: 1;
}

.mini-body-core {
  width: 28px;
  height: 24px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 7px 7px 12px 12px;
  border: 1px solid rgba(0, 229, 255, 0.4);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 0 8px rgba(0, 229, 255, 0.2);
}

.mini-core-ring {
  width: 12px;
  height: 12px;
  border: 1px solid rgba(0, 229, 255, 0.5);
  border-radius: 50%;
  position: absolute;
  animation: miniCoreRotate 4s linear infinite;
}

@keyframes miniCoreRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mini-core-dot {
  width: 4px;
  height: 4px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.9);
}

/* 翅膀 */
.mini-wing {
  position: absolute;
  width: 10px;
  height: 18px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 229, 255, 0.1));
  border: 1px solid rgba(0, 229, 255, 0.3);
  top: 2px;
}

.mini-left-wing {
  left: -4px;
  border-radius: 5px 0 0 8px;
  transform-origin: right center;
  animation: miniWingFlap 2s ease-in-out infinite;
}

.mini-right-wing {
  right: -4px;
  border-radius: 0 5px 8px 0;
  transform-origin: left center;
  animation: miniWingFlap 2s ease-in-out infinite reverse;
}

@keyframes miniWingFlap {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-8deg); }
}

.float-label {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  font-weight: 600;
  color: #00e5ff;
  background: rgba(10, 22, 40, 0.85);
  padding: 1px 8px;
  border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.35);
  white-space: nowrap;
  letter-spacing: 2px;
}

/* ===== 对话面板 ===== */
.float-panel {
  position: absolute;
  bottom: 100px;
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
  background: #f0f9ff;
  border: 1px solid #7dd3fc;
  color: #0c4a6e;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.panel-input :deep(.el-textarea__inner:focus) {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.15);
  background: white;
}
.panel-input :deep(.el-textarea__inner::placeholder) {
  color: #7dd3fc;
}

.panel-input .el-button {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
}
</style>
