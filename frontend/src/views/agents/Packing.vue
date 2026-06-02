<template>
  <div class="agent-page">
    <div class="agent-header">
      <el-button @click="goBack" type="primary" plain>
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-button>
      <h1>装箱评价智能体</h1>
    </div>
    <div class="agent-content">
      <div class="placeholder">
        <el-icon :size="64"><Box /></el-icon>
        <h2>智能体页面开发中</h2>
        <p>装箱评价智能体将在此页面展示</p>
        <p>功能：装箱空间利用率、重量平衡分析、安全性评价</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, Box } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.push('/home')
}
</script>

<style scoped>
.agent-page {
  min-height: 100vh;
  background: #0a1628;
  color: #fff;
  padding: 20px;
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
}

.agent-header h1 {
  font-size: 24px;
}

.agent-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.placeholder {
  text-align: center;
  color: #c0c8d4;
}

.placeholder h2 {
  margin: 20px 0 10px;
  color: #fff;
}

.placeholder p {
  margin: 5px 0;
}
</style>
