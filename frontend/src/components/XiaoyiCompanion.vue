<template>
  <div class="xy-companion">
    <!-- 迷你聊天抽屉 -->
    <Transition name="xy-pop">
      <div v-if="open" class="xy-panel">
        <div class="xy-head">
          <div class="xy-head-left">
            <XiaoYiAvatar :size="30" :state="chatLoading ? 'thinking' : 'idle'" />
            <div class="xy-head-text">
              <b>小翼 · AI助教</b>
              <i><span class="xy-online-dot"></span>在线 · 随时提问</i>
            </div>
          </div>
          <div class="xy-head-actions">
            <button class="xy-icon-btn" title="进入完整对话页" @click="goFull">
              <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M19 19H5V5h6V3H3v18h18v-8h-2v6zM14 3v2h4.6l-7.3 7.3 1.4 1.4L20 6.4V11h2V3h-8z"/></svg>
            </button>
            <button class="xy-icon-btn" title="收起 (ESC)" @click="closePanel">✕</button>
          </div>
        </div>

        <div class="xy-messages" ref="msgsRef">
          <div v-for="(m, i) in messages" :key="i" class="xy-msg" :class="m.role">
            <div v-if="m.role !== 'user'" class="xy-msg-avatar"><XiaoYiAvatar :size="22" /></div>
            <div class="xy-bubble">
              <span v-if="m.tools && m.tools.length" class="xy-tools">🔧 {{ m.tools.join('、') }}</span>
              <div v-html="fmt(m.content)"></div>
            </div>
          </div>
          <div v-if="chatLoading" class="xy-msg assistant">
            <div class="xy-msg-avatar"><XiaoYiAvatar :size="22" state="thinking" /></div>
            <div class="xy-bubble typing"><span></span><span></span><span></span></div>
          </div>
        </div>

        <div class="xy-quick">
          <button v-for="q in quicks" :key="q" @click="askQuick(q)">{{ q }}</button>
        </div>

        <div class="xy-input-row">
          <input
            v-model="input"
            :disabled="chatLoading"
            placeholder="输入问题，Enter 发送…"
            @keydown.enter="send"
          />
          <button class="xy-send" :disabled="chatLoading || !input.trim()" @click="send">➤</button>
        </div>
      </div>
    </Transition>

    <!-- 悬浮小翼（直接使用原有水晶精灵形象，带名字标签） -->
    <div class="xy-ball" :class="{ active: open }" @click="open = !open">
      <XiaoYiAvatar :size="52" :state="open ? 'thinking' : 'idle'" />
      <span v-if="!open && showLabel" class="xy-name">小翼</span>
      <span v-if="!open" class="xy-tip">有问题，随时问我</span>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import XiaoYiAvatar from '@/components/XiaoYiAvatar.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const open = ref(false)
const input = ref('')
// 三大智能体页面小翼不带名字标签，其他页面带
const showLabel = computed(() => !route.path.startsWith('/agent'))
const chatLoading = ref(false)
const messages = ref([
  { role: 'assistant', content: '你好！我是小翼，我在平台的任何页面都能陪你对话。关于无人机物流、航线规划、应急运输的问题，随时问我～', tools: [] }
])
const msgsRef = ref(null)
const quicks = ['这个页面是做什么的？', '如何开始路径规划？', '无人机装载有什么原则？', '课程图谱怎么用？']

function fmt(c) { return String(c || '').replace(/\n/g, '<br>') }

function scrollBottom() {
  if (msgsRef.value) msgsRef.value.scrollTop = msgsRef.value.scrollHeight
}

async function send() {
  const text = input.value.trim()
  if (!text || chatLoading.value) return
  messages.value.push({ role: 'user', content: text, tools: [] })
  input.value = ''
  chatLoading.value = true
  await nextTick()
  scrollBottom()
  try {
    const res = await axios.post('/api/ai-chat/chat', {
      messages: messages.value
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }))
    }, { headers: { Authorization: `Bearer ${userStore.token}` } })
    if (res.data.success) {
      messages.value.push({ role: 'assistant', content: res.data.reply, tools: res.data.tools_used || [] })
    } else {
      messages.value.push({ role: 'assistant', content: res.data.message || '抱歉，小翼暂时无法响应，请稍后再试。', tools: [] })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '网络连接异常，请检查网络后重试。', tools: [] })
  } finally {
    chatLoading.value = false
    await nextTick()
    scrollBottom()
  }
}

function askQuick(q) {
  if (chatLoading.value) return
  input.value = q
  send()
}

function closePanel() { open.value = false }
function goFull() {
  open.value = false
  router.push('/ai-assistant')
}
function onEsc(e) { if (e.key === 'Escape' && open.value) open.value = false }
onMounted(() => document.addEventListener('keydown', onEsc))
onUnmounted(() => document.removeEventListener('keydown', onEsc))
</script>

<style scoped>
.xy-companion { position: fixed; right: 12px; bottom: 16px; z-index: 3500; display: flex; flex-direction: column; align-items: flex-end; gap: 14px; pointer-events: none; }
.xy-companion > * { pointer-events: auto; }

/* ── 悬浮小翼（无底座，直接显示水晶精灵） ── */
.xy-ball {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: transform 0.22s ease, filter 0.22s ease;
}
.xy-ball:hover { transform: translateY(-3px) scale(1.04); filter: drop-shadow(0 6px 16px rgba(0, 229, 255, 0.35)); }
.xy-tip {
  position: absolute; right: 72px; top: 50%; transform: translateY(-50%);
  white-space: nowrap;
  font-size: 12px; color: #bfeaff; letter-spacing: 1px;
  background: rgba(8, 22, 40, 0.92);
  border: 1px solid rgba(0, 229, 255, 0.35);
  border-radius: 8px;
  padding: 5px 12px;
  opacity: 0; pointer-events: none;
  transition: opacity 0.2s;
}
.xy-ball:hover .xy-tip { opacity: 1; }

/* ── 聊天抽屉 ── */
.xy-panel {
  width: 380px;
  height: 520px;
  max-height: calc(100vh - 140px);
  display: flex; flex-direction: column;
  background: linear-gradient(165deg, rgba(13, 33, 55, 0.96), rgba(8, 20, 38, 0.97));
  border: 1px solid rgba(0, 229, 255, 0.32);
  border-radius: 16px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.55), 0 0 24px rgba(0, 229, 255, 0.12);
  overflow: hidden;
}
.xy-pop-enter-active, .xy-pop-leave-active { transition: all 0.24s ease; }
.xy-pop-enter-from, .xy-pop-leave-to { opacity: 0; transform: translateY(14px) scale(0.96); }

.xy-head {
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(0, 229, 255, 0.18);
  background: rgba(0, 229, 255, 0.05);
}
.xy-head-left { display: flex; align-items: center; gap: 10px; }
.xy-head-text { display: flex; flex-direction: column; gap: 1px; }
.xy-head-text b { color: #e6f3ff; font-size: 13px; letter-spacing: 1px; }
.xy-head-text i { font-style: normal; color: rgba(140, 190, 230, 0.6); font-size: 10px; display: flex; align-items: center; gap: 5px; }
.xy-online-dot { width: 6px; height: 6px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 6px rgba(74, 222, 128, 0.9); }
.xy-close {
  width: 26px; height: 26px;
  border: none; border-radius: 7px;
  background: transparent; color: #8fb8dd;
  font-size: 13px; cursor: pointer; transition: all 0.18s;
}
.xy-close:hover { background: rgba(255, 120, 120, 0.14); color: #ff9b9b; }

.xy-head-actions { display: flex; align-items: center; gap: 4px; }
.xy-icon-btn {
  width: 26px; height: 26px;
  border: none; border-radius: 7px;
  background: transparent; color: #8fb8dd;
  cursor: pointer; transition: all 0.18s;
  display: flex; align-items: center; justify-content: center;
}
.xy-icon-btn:hover { background: rgba(0, 229, 255, 0.12); color: #22d3ee; }

/* ── 名字标签（智能体页面隐藏） ── */
.xy-name {
  position: absolute; bottom: -16px; left: 50%; transform: translateX(-50%);
  font-size: 11px; font-weight: 600; color: #00e5ff; letter-spacing: 2px;
  background: rgba(10, 22, 40, 0.88);
  padding: 1px 9px; border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.35);
  white-space: nowrap;
  pointer-events: none;
}

.xy-messages {
  flex: 1; min-height: 0;
  overflow-y: auto;
  padding: 14px;
  display: flex; flex-direction: column; gap: 12px;
}
.xy-messages::-webkit-scrollbar { width: 5px; }
.xy-messages::-webkit-scrollbar-thumb { background: rgba(0, 229, 255, 0.2); border-radius: 3px; }

.xy-msg { display: flex; gap: 8px; align-items: flex-start; }
.xy-msg.user { flex-direction: row-reverse; }
.xy-msg-avatar { flex-shrink: 0; margin-top: 2px; }
.xy-bubble {
  max-width: 78%;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px; line-height: 1.65;
  word-break: break-word;
}
.xy-msg.assistant .xy-bubble {
  background: rgba(0, 229, 255, 0.07);
  border: 1px solid rgba(0, 229, 255, 0.16);
  color: #d8ecff;
  border-top-left-radius: 3px;
}
.xy-msg.user .xy-bubble {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.22), rgba(0, 160, 220, 0.22));
  border: 1px solid rgba(0, 229, 255, 0.4);
  color: #eaf7ff;
  border-top-right-radius: 3px;
}
.xy-tools { display: block; font-size: 10px; color: #7fd8ee; margin-bottom: 4px; opacity: 0.85; }
.xy-bubble.typing { display: flex; gap: 4px; align-items: center; padding: 10px 14px; }
.xy-bubble.typing span {
  width: 6px; height: 6px; border-radius: 50%;
  background: #00e5ff; opacity: 0.4;
  animation: xyDot 1.2s ease-in-out infinite;
}
.xy-bubble.typing span:nth-child(2) { animation-delay: 0.18s; }
.xy-bubble.typing span:nth-child(3) { animation-delay: 0.36s; }
@keyframes xyDot { 0%, 100% { opacity: 0.25; transform: translateY(0); } 50% { opacity: 1; transform: translateY(-3px); } }

.xy-quick {
  flex-shrink: 0;
  display: flex; gap: 6px; flex-wrap: wrap;
  padding: 8px 12px;
  border-top: 1px dashed rgba(0, 229, 255, 0.14);
}
.xy-quick button {
  border: 1px solid rgba(0, 229, 255, 0.28);
  background: rgba(0, 229, 255, 0.05);
  color: #9fd8ee;
  font-size: 11px;
  border-radius: 999px;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.18s;
}
.xy-quick button:hover { background: rgba(0, 229, 255, 0.16); color: #e6f3ff; }

.xy-input-row {
  flex-shrink: 0;
  display: flex; gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid rgba(0, 229, 255, 0.16);
  background: rgba(0, 0, 0, 0.18);
}
.xy-input-row input {
  flex: 1; min-width: 0;
  background: rgba(0, 229, 255, 0.06);
  border: 1px solid rgba(0, 229, 255, 0.22);
  border-radius: 9px;
  padding: 8px 12px;
  color: #e6f3ff;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}
.xy-input-row input:focus { border-color: rgba(0, 229, 255, 0.55); }
.xy-input-row input::placeholder { color: rgba(140, 180, 215, 0.45); }
.xy-send {
  flex-shrink: 0;
  width: 38px;
  border: 1px solid rgba(0, 229, 255, 0.45);
  border-radius: 9px;
  background: rgba(0, 229, 255, 0.14);
  color: #00e5ff;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.18s;
}
.xy-send:hover:not(:disabled) { background: rgba(0, 229, 255, 0.28); box-shadow: 0 0 12px rgba(0, 229, 255, 0.3); }
.xy-send:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
