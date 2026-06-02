<template>
  <div class="ai-assistant-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-left">
        <el-button @click="goBack" type="primary" plain size="small">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <h1 class="page-title">小翼 · AI智能助教</h1>
        <el-tag type="success" size="small" effect="dark">在线</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="clearChat" type="danger" plain size="small">
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧数字人区域 -->
      <div class="avatar-section">
        <div class="avatar-stage">
          <!-- 数字人主体 -->
          <div class="digital-avatar" :class="avatarState">
            <!-- 光晕背景 -->
            <div class="avatar-glow"></div>
            <!-- 头部 -->
            <div class="avatar-head">
              <!-- 脸部 -->
              <div class="avatar-face">
                <!-- 眼睛 -->
                <div class="eyes">
                  <div class="eye left">
                    <div class="pupil"></div>
                  </div>
                  <div class="eye right">
                    <div class="pupil"></div>
                  </div>
                </div>
                <!-- 嘴巴 -->
                <div class="mouth" :class="{ talking: avatarState === 'talking' }">
                  <div class="mouth-shape"></div>
                </div>
              </div>
              <!-- 天线/信号 -->
              <div class="antenna">
                <div class="antenna-line"></div>
                <div class="antenna-dot"></div>
              </div>
            </div>
            <!-- 身体 -->
            <div class="avatar-body">
              <div class="body-core">
                <div class="core-ring"></div>
                <div class="core-dot"></div>
              </div>
              <!-- 翅膀/手臂 -->
              <div class="wing left-wing"></div>
              <div class="wing right-wing"></div>
            </div>
          </div>

          <!-- 状态文字 -->
          <div class="avatar-status">
            <span v-if="avatarState === 'idle'">小翼待命中...</span>
            <span v-else-if="avatarState === 'talking'">小翼正在回答</span>
            <span v-else-if="avatarState === 'thinking'">小翼思考中</span>
          </div>
        </div>

        <!-- 快捷问题 -->
        <div class="quick-questions">
          <div class="quick-title">快捷提问</div>
          <div class="quick-list">
            <div v-for="q in quickQuestions" :key="q" class="quick-item" @click="askQuick(q)">
              {{ q }}
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-section">
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(msg, i) in chatMessages" :key="i" class="message" :class="msg.role">
            <div class="msg-avatar-wrap">
              <div class="msg-avatar" :class="msg.role">
                {{ msg.role === 'user' ? '我' : '翼' }}
              </div>
            </div>
            <div class="msg-body">
              <div class="msg-name">{{ msg.role === 'user' ? '我' : '小翼' }}</div>
              <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
              <div class="msg-time">{{ msg.time }}</div>
            </div>
          </div>
          <div v-if="chatLoading" class="message assistant">
            <div class="msg-avatar-wrap">
              <div class="msg-avatar assistant">翼</div>
            </div>
            <div class="msg-body">
              <div class="msg-name">小翼</div>
              <div class="msg-bubble typing-bubble">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-wrap">
            <el-input
              v-model="chatInput"
              type="textarea"
              :rows="2"
              placeholder="输入你的问题，按 Enter 发送..."
              @keydown.enter.exact.prevent="sendChat"
              :disabled="chatLoading"
              resize="none"
            />
          </div>
          <div class="input-actions">
            <span class="char-count">{{ chatInput.length }} 字</span>
            <el-button type="primary" @click="sendChat" :loading="chatLoading" :disabled="!chatInput.trim()">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Delete, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const goBack = () => router.push('/home')

// 聊天状态
const chatMessages = ref([
  {
    role: 'assistant',
    content: '你好！我是小翼，你的AI智能助教。我可以帮你解答关于无人机物流、航线规划、应急运输等方面的问题。有什么我能帮到你的吗？',
    time: formatTime(new Date())
  }
])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessagesRef = ref(null)

// 数字人状态
const avatarState = computed(() => {
  if (chatLoading.value) return 'thinking'
  return 'idle'
})

// 快捷问题
const quickQuestions = [
  '什么是低空应急运输？',
  '无人机航线规划的基本原则？',
  '如何评估运输方案的风险？',
  '装箱优化有哪些常用算法？'
]

function formatTime(date) {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatMessage(content) {
  // 简单的换行转换
  return content.replace(/\n/g, '<br>')
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
  await nextTick()
  scrollToBottom()

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
        content: res.data.message || '抱歉，小翼暂时无法响应，请稍后再试。',
        time: formatTime(new Date())
      })
    }
  } catch (e) {
    chatMessages.value.push({
      role: 'assistant',
      content: '网络连接异常，请检查网络后重试。',
      time: formatTime(new Date())
    })
  } finally {
    chatLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function askQuick(question) {
  chatInput.value = question
  sendChat()
}

function clearChat() {
  chatMessages.value = [
    {
      role: 'assistant',
      content: '对话已清空。我是小翼，随时为你服务！',
      time: formatTime(new Date())
    }
  ]
}

function scrollToBottom() {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.ai-assistant-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: #0a1628;
  color: #e2e8f0;
}

/* 顶部导航 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(90deg, #0d2137, #132840);
  border-bottom: 1px solid rgba(0, 229, 255, 0.2);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(90deg, #00e5ff, #00b4cc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧数字人区域 */
.avatar-section {
  width: 320px;
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95), rgba(10, 22, 40, 0.98));
  border-right: 1px solid rgba(0, 229, 255, 0.15);
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.avatar-stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

/* 数字人 */
.digital-avatar {
  position: relative;
  width: 160px;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 光晕 */
.avatar-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 229, 255, 0.2) 0%, transparent 70%);
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
}

/* 头部 */
.avatar-head {
  position: relative;
  width: 100px;
  height: 100px;
  z-index: 2;
}

.avatar-face {
  width: 100px;
  height: 90px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 40px 40px 35px 35px;
  border: 2px solid rgba(0, 229, 255, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.25), inset 0 0 15px rgba(0, 229, 255, 0.1);
}

/* 眼睛 */
.eyes {
  display: flex;
  gap: 24px;
}

.eye {
  width: 18px;
  height: 18px;
  background: #0a1628;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid rgba(0, 229, 255, 0.6);
}

.pupil {
  width: 8px;
  height: 8px;
  background: #00e5ff;
  border-radius: 50%;
  animation: blink 4s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.9);
}

@keyframes blink {
  0%, 45%, 55%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

/* 嘴巴 */
.mouth {
  width: 20px;
  height: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mouth-shape {
  width: 16px;
  height: 4px;
  background: rgba(0, 229, 255, 0.6);
  border-radius: 0 0 8px 8px;
  transition: all 0.15s;
}

.mouth.talking .mouth-shape {
  height: 10px;
  border-radius: 4px;
  animation: talk 0.3s ease-in-out infinite alternate;
}

@keyframes talk {
  0% { height: 4px; width: 14px; }
  100% { height: 12px; width: 18px; }
}

/* 天线 */
.antenna {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.antenna-line {
  width: 2px;
  height: 14px;
  background: linear-gradient(to top, rgba(0, 229, 255, 0.6), rgba(0, 229, 255, 0.2));
}

.antenna-dot {
  width: 6px;
  height: 6px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.9);
  animation: antennaBlink 2s ease-in-out infinite;
}

@keyframes antennaBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 身体 */
.avatar-body {
  position: relative;
  width: 80px;
  height: 70px;
  margin-top: -5px;
  z-index: 1;
}

.body-core {
  width: 60px;
  height: 50px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 15px 15px 25px 25px;
  border: 2px solid rgba(0, 229, 255, 0.4);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
}

.core-ring {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 229, 255, 0.5);
  border-radius: 50%;
  position: absolute;
  animation: coreRotate 4s linear infinite;
}

@keyframes coreRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.core-dot {
  width: 8px;
  height: 8px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.9);
}

/* 翅膀 */
.wing {
  position: absolute;
  width: 20px;
  height: 35px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 229, 255, 0.1));
  border: 1px solid rgba(0, 229, 255, 0.3);
  top: 5px;
}

.left-wing {
  left: -8px;
  border-radius: 10px 0 0 15px;
  transform-origin: right center;
  animation: wingFlap 2s ease-in-out infinite;
}

.right-wing {
  right: -8px;
  border-radius: 0 10px 15px 0;
  transform-origin: left center;
  animation: wingFlap 2s ease-in-out infinite reverse;
}

@keyframes wingFlap {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-8deg); }
}

/* 浮动动画 */
.digital-avatar.idle {
  animation: avatarFloat 3s ease-in-out infinite;
}

@keyframes avatarFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 思考状态 */
.digital-avatar.thinking .avatar-face {
  border-color: rgba(255, 179, 0, 0.5);
  box-shadow: 0 0 20px rgba(255, 179, 0, 0.25), inset 0 0 15px rgba(255, 179, 0, 0.1);
}

.digital-avatar.thinking .pupil {
  background: #ffb300;
  box-shadow: 0 0 10px rgba(255, 179, 0, 0.9);
  animation: thinkPulse 1s ease-in-out infinite;
}

@keyframes thinkPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.digital-avatar.thinking .core-dot {
  background: #ffb300;
  box-shadow: 0 0 10px rgba(255, 179, 0, 0.8);
}

.digital-avatar.thinking .antenna-dot {
  background: #ffb300;
  box-shadow: 0 0 10px rgba(255, 179, 0, 0.8);
}

/* 状态文字 */
.avatar-status {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

/* 快捷问题 */
.quick-questions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 229, 255, 0.15);
}

.quick-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-item {
  padding: 10px 14px;
  background: rgba(0, 229, 255, 0.06);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-item:hover {
  background: rgba(0, 229, 255, 0.15);
  border-color: rgba(0, 229, 255, 0.4);
  transform: translateX(4px);
  color: #00e5ff;
}

/* 右侧聊天区域 */
.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 消息 */
.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar-wrap {
  flex-shrink: 0;
}

.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.msg-avatar.assistant {
  background: linear-gradient(135deg, #00e5ff, #00b4cc);
  box-shadow: 0 2px 10px rgba(0, 229, 255, 0.3);
}

.msg-avatar.user {
  background: linear-gradient(135deg, #9c27b0, #7b1fa2);
  box-shadow: 0 2px 10px rgba(156, 39, 176, 0.3);
}

.msg-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.msg-name {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.message.user .msg-name {
  text-align: right;
}

.msg-bubble {
  padding: 14px 18px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.92);
}

.message.assistant .msg-bubble {
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-top-left-radius: 4px;
}

.message.user .msg-bubble {
  background: rgba(156, 39, 176, 0.15);
  border: 1px solid rgba(156, 39, 176, 0.25);
  border-top-right-radius: 4px;
}

.msg-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
}

.message.user .msg-time {
  text-align: right;
}

/* 打字动画 */
.typing-bubble {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 18px 22px !important;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: rgba(0, 229, 255, 0.7);
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 20px;
  background: rgba(13, 33, 55, 0.8);
  border-top: 1px solid rgba(0, 229, 255, 0.2);
}

.input-wrap :deep(.el-textarea__inner) {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(0, 229, 255, 0.2) !important;
  border-radius: 10px !important;
  color: #e2e8f0 !important;
  font-size: 14px;
  padding: 12px 16px;
}

.input-wrap :deep(.el-textarea__inner:focus) {
  border-color: rgba(0, 229, 255, 0.5) !important;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.15) !important;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.char-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .avatar-section {
    width: 100%;
    flex-direction: row;
    padding: 12px;
    gap: 16px;
    border-right: none;
    border-bottom: 1px solid rgba(0, 229, 255, 0.15);
  }

  .avatar-stage {
    flex-direction: row;
    gap: 12px;
  }

  .digital-avatar {
    transform: scale(0.6);
    transform-origin: center;
  }

  .quick-questions {
    flex: 1;
    margin-top: 0;
    padding-top: 0;
    border-top: none;
    border-left: 1px solid rgba(0, 229, 255, 0.15);
    padding-left: 16px;
  }

  .message {
    max-width: 90%;
  }
}
</style>
