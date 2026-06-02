<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/home')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <el-divider direction="vertical" />
        <h1>系统管理</h1>
      </div>
    </div>
    <div class="card-grid">
      <div class="manage-card" @click="$router.push('/system/course-data')">
        <div class="card-icon">
          <el-icon :size="36"><DataBoard /></el-icon>
        </div>
        <h3>课程数据管理</h3>
        <p>管理课程图谱项目数据，支持导入/导出JSON文件</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DataBoard, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.page-container {
  padding: 20px;
  color: #fff;
}
.page-header {
  margin-bottom: 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}
.back-btn {
  color: #c0c8d4 !important;
  font-size: 14px;
}
.back-btn:hover {
  color: #409eff !important;
}
.page-container h1 {
  margin: 0;
  font-size: 22px;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.manage-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 28px 24px;
  cursor: pointer;
  transition: all 0.3s;
}
.manage-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.4);
  transform: translateY(-2px);
}
.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #337ecc);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #fff;
}
.manage-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #e2e8f0;
}
.manage-card p {
  margin: 0;
  font-size: 13px;
  color: #c0c8d4;
  line-height: 1.6;
}
</style>
