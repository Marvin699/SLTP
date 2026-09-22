<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import XiaoyiCompanion from '@/components/XiaoyiCompanion.vue'

const route = useRoute()
// 全站常驻小翼（科技风+可放大）；已有完整版小翼的页面与全屏大屏页隐藏
const hideXiaoyi = computed(() => {
  const p = route.path
  return (
    p.startsWith('/login') || p.startsWith('/register') || p.startsWith('/score') ||
    p.startsWith('/change-password') ||
    p.startsWith('/ai-assistant') ||
    p === '/evaluation/dashboard' ||
    p === '/evaluation/task8' ||
    p === '/evaluation/section/task4/live'
  )
})
</script>

<template>
  <router-view />
  <XiaoyiCompanion v-if="!hideXiaoyi" />
</template>
