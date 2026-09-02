<template>
  <div class="xy-avatar" :class="state" :style="{ width: size + 'px', height: size + 'px' }">
    <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- 晶体切面：受光面亮、背光面深，伪造 3D 光照 -->
        <linearGradient :id="`xyTL-${uid}`" x1="60" y1="12" x2="37" y2="56" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#dcfeff"/><stop offset="1" stop-color="#7ce4ef"/>
        </linearGradient>
        <linearGradient :id="`xyTR-${uid}`" x1="83" y1="12" x2="60" y2="56" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#f2ffff"/><stop offset="1" stop-color="#9deeea"/>
        </linearGradient>
        <linearGradient :id="`xyBL-${uid}`" x1="37" y1="52" x2="60" y2="106" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#5fc9da"/><stop offset="1" stop-color="#2b86b4"/>
        </linearGradient>
        <linearGradient :id="`xyBR-${uid}`" x1="83" y1="52" x2="60" y2="106" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#3fa3c2"/><stop offset="1" stop-color="#1e6a99"/>
        </linearGradient>
        <radialGradient :id="`xyCore-${uid}`" cx="0.5" cy="0.45" r="0.6">
          <stop offset="0" stop-color="#f4fffe"/><stop offset="0.45" stop-color="#9df2f4"/><stop offset="1" stop-color="rgba(110,231,240,0)"/>
        </radialGradient>
        <radialGradient :id="`xyHalo-${uid}`" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stop-color="rgba(125,232,244,0.28)"/><stop offset="1" stop-color="rgba(125,232,244,0)"/>
        </radialGradient>
      </defs>

      <!-- 背景星尘（远景粒子，暗、小、慢） -->
      <g class="xy-dust">
        <circle class="xy-p" cx="18" cy="30" r="1.1" fill="#9aeef4"/>
        <circle class="xy-p d2" cx="102" cy="24" r="0.9" fill="#bdf6fa"/>
        <circle class="xy-p d3" cx="106" cy="88" r="1.2" fill="#8adfe8"/>
        <circle class="xy-p d2" cx="14" cy="86" r="0.8" fill="#bdf6fa"/>
        <circle class="xy-p d3" cx="30" cy="106" r="1" fill="#9aeef4"/>
        <circle class="xy-p" cx="94" cy="104" r="0.9" fill="#8adfe8"/>
      </g>

      <!-- 晶体环境辉光 -->
      <ellipse class="xy-halo" cx="60" cy="58" rx="34" ry="38" :fill="`url(#xyHalo-${uid})`"/>

      <!-- 晶体主体（四面体切面 + 棱边高光） -->
      <g class="xy-crystal">
        <path :fill="`url(#xyTL-${uid})`" d="M60 12 L37 52 L60 56 Z"/>
        <path :fill="`url(#xyTR-${uid})`" d="M60 12 L83 52 L60 56 Z"/>
        <path :fill="`url(#xyBL-${uid})`" d="M37 52 L60 106 L60 56 Z"/>
        <path :fill="`url(#xyBR-${uid})`" d="M60 56 L60 106 L83 52 Z"/>
        <!-- 棱边 -->
        <path d="M60 12 L37 52 L60 106 L83 52 Z M37 52 L83 52 M60 12 L60 106"
              stroke="rgba(235,255,255,0.4)" stroke-width="0.8" stroke-linejoin="round"/>
        <!-- 内核 -->
        <ellipse class="xy-core" cx="60" cy="57" rx="9" ry="15" :fill="`url(#xyCore-${uid})`"/>

        <!-- 眼睛：待机/聆听 = 晶体小圆点（会眨） -->
        <g v-if="state === 'idle' || state === 'listening'" class="xy-eyes">
          <circle class="xy-eye" cx="54" cy="57" r="1.7" fill="#0c3b4a"/>
          <circle class="xy-eye" cx="66" cy="57" r="1.7" fill="#0c3b4a"/>
        </g>
        <!-- 思考：双眼变旋转小弧 -->
        <g v-else-if="state === 'thinking'" class="xy-think">
          <circle class="xy-think-ring" cx="54" cy="57" r="3.2" stroke="#0c3b4a" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="12 9" fill="none"/>
          <circle class="xy-think-ring rev" cx="66" cy="57" r="3.2" stroke="#0c3b4a" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="12 9" fill="none"/>
        </g>
        <!-- 回答：弯眼 ^ ^ -->
        <g v-else class="xy-happy">
          <path d="M51 58 Q54 54.5 57 58" stroke="#0c3b4a" stroke-width="1.5" stroke-linecap="round" fill="none"/>
          <path d="M63 58 Q66 54.5 69 58" stroke="#0c3b4a" stroke-width="1.5" stroke-linecap="round" fill="none"/>
        </g>
      </g>

      <!-- 轨道环 A（能量流 + 环绕光点） -->
      <g class="xy-orbit orbit-a" transform="rotate(-16 60 60)">
        <ellipse class="xy-ring-glow" cx="60" cy="60" rx="52" ry="19"/>
        <ellipse class="xy-ring" cx="60" cy="60" rx="52" ry="19" pathLength="100"/>
        <circle class="xy-comet" r="2" fill="#e8feff"/>
        <circle class="xy-comet c2" r="1.2" fill="#9df2f6"/>
      </g>

      <!-- 轨道环 B（反向） -->
      <g class="xy-orbit orbit-b" transform="rotate(14 60 60)">
        <ellipse class="xy-ring-glow" cx="60" cy="60" rx="48" ry="16"/>
        <ellipse class="xy-ring" cx="60" cy="60" rx="48" ry="16" pathLength="100"/>
        <circle class="xy-comet" r="1.7" fill="#dcf9ff"/>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  size: { type: Number, default: 48 },
  // idle=待机(眨眼) thinking=思考(双眼转弧+能流加速) talking=回答(弯眼+核心呼吸) listening=聆听(辉光脉动)
  state: { type: String, default: 'idle' },
})

// 渐变 id 每实例唯一，避免同页多实例冲突
const uid = ref(Math.random().toString(36).slice(2, 8))
</script>

<style scoped>
.xy-avatar { display: block; }
.xy-avatar svg {
  width: 100%;
  height: 100%;
  overflow: visible;
  animation: xy-float 3.6s ease-in-out infinite;
  filter: drop-shadow(0 4px 14px rgba(34, 211, 238, 0.2));
}
@keyframes xy-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

/* 晶体呼吸（轻微涨缩，像核心在搏动） */
.xy-crystal {
  transform-box: fill-box;
  transform-origin: center;
  animation: xy-crystal 4s ease-in-out infinite;
}
@keyframes xy-crystal {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.025); }
}

/* 内核搏动 */
.xy-core {
  filter: blur(1.2px);
  animation: xy-core 4s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}
@keyframes xy-core {
  0%, 100% { opacity: 0.85; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* 环境辉光呼吸 */
.xy-halo {
  transform-box: fill-box;
  transform-origin: center;
  animation: xy-halo 4s ease-in-out infinite;
}
@keyframes xy-halo {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.06); }
}

/* ── 轨道环：点状能量流 ── */
.xy-ring-glow {
  fill: none;
  stroke: rgba(125, 232, 244, 0.18);
  stroke-width: 3.4;
}
.xy-ring {
  fill: none;
  stroke: #8ff0f7;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-dasharray: 1.2 6.3;
  animation: xy-flow 3s linear infinite;
  opacity: 0.85;
}
@keyframes xy-flow {
  to { stroke-dashoffset: -15; }  /* pathLength=100，1.2+6.3=7.5 的整数倍保证无缝 */
}
.thinking .xy-ring { animation-duration: 0.9s; }

/* 环绕光点：沿椭圆轨道公转 */
.xy-comet {
  offset-path: path('M 8 60 a 52 19 0 1 0 104 0 a 52 19 0 1 0 -104 0');
  animation: xy-orbit 7s linear infinite;
  filter: drop-shadow(0 0 3px rgba(160, 245, 250, 0.9));
}
.xy-comet.c2 { animation-delay: -3.5s; }
.orbit-b .xy-comet {
  offset-path: path('M 12 60 a 48 16 0 1 0 96 0 a 48 16 0 1 0 -96 0');
  animation-duration: 9s;
  animation-direction: reverse;
}
@keyframes xy-orbit {
  to { offset-distance: 100%; }
}

/* ── 眼睛 ── */
.xy-eye {
  transform-box: fill-box;
  transform-origin: center;
  animation: xy-blink 4.8s ease-in-out infinite;
}
@keyframes xy-blink {
  0%, 91%, 97%, 100% { transform: scaleY(1); }
  94% { transform: scaleY(0.1); }
}

/* 思考小弧 */
.xy-think-ring {
  transform-box: fill-box;
  transform-origin: center;
  animation: xy-rotate 1.1s linear infinite;
}
.xy-think-ring.rev { animation-direction: reverse; }
@keyframes xy-rotate { to { transform: rotate(360deg); } }

/* ── 状态差异 ── */
/* 聆听：整体辉光脉动 + 粒子闪烁加快 */
.listening svg { animation: xy-float 3.6s ease-in-out infinite, xy-pulse 1.8s ease-in-out infinite; }
@keyframes xy-pulse {
  0%, 100% { filter: drop-shadow(0 4px 14px rgba(34, 211, 238, 0.2)); }
  50% { filter: drop-shadow(0 4px 22px rgba(34, 211, 238, 0.5)); }
}

/* 回答：核心呼吸加快、更亮 */
.talking .xy-core { animation-duration: 1.4s; }
.talking .xy-halo { animation-duration: 1.4s; }

/* 背景粒子闪烁 */
.xy-p { animation: xy-twinkle 3.6s ease-in-out infinite; }
.xy-p.d2 { animation-delay: -1.2s; }
.xy-p.d3 { animation-delay: -2.4s; }
@keyframes xy-twinkle {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.9; }
}
</style>
