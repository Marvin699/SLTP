<template>
  <div class="agent-page">
    <!-- 顶部导航栏 -->
    <header class="agent-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn" text>
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <div class="header-divider"></div>
        <div class="header-title">
          <el-icon :size="22"><Share /></el-icon>
          <span>课程图谱智能体</span>
        </div>
      </div>
      <div class="header-right">
        <el-tag type="info" effect="dark" size="small">AI智能分析</el-tag>
      </div>
    </header>

    <!-- 入口卡片区域 -->
    <main class="entry-main">
      <div class="entry-cards">
        <!-- 教学图谱卡片 -->
        <div class="entry-card teaching-card" @click="goToTeachingGraph">
          <div class="card-glow"></div>
          <div class="card-icon">
            <el-icon :size="48"><Share /></el-icon>
          </div>
          <h2 class="card-title">教学图谱</h2>
          <p class="card-subtitle">Teaching Graph</p>
          <div class="card-desc">
            力导向图可视化呈现课程知识体系与能力结构。支持切换不同项目（P1-P5），展示项目→子项目→任务→知识点/技能点的层级关系，点击节点查看详情。
          </div>
          <div class="card-tags">
            <span class="card-tag">知识图谱</span>
            <span class="card-tag">能力图谱</span>
            <span class="card-tag">项目切换</span>
            <span class="card-tag">详情面板</span>
          </div>
          <div class="card-enter">
            进入模块
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <!-- 项目详情卡片 -->
        <div class="entry-card project-card" @click="goToProjectGraph">
          <div class="card-glow project-glow"></div>
          <div class="card-icon project-icon">
            <el-icon :size="48"><DataBoard /></el-icon>
          </div>
          <h2 class="card-title">项目详情</h2>
          <p class="card-subtitle">Project Details</p>
          <div class="card-desc">
            查看所有课程项目（P1-P5）的详细数据，包括子项目结构、任务清单、知识点/技能点分布、关联认证等信息。
          </div>
          <div class="card-tags">
            <span class="card-tag">项目数据</span>
            <span class="card-tag">子项目结构</span>
            <span class="card-tag">任务清单</span>
          </div>
          <div class="card-enter">
            进入模块
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight, Share, DataBoard } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => router.push('/home')
const goToTeachingGraph = () => router.push('/agent/teaching-graph/view')
const goToProjectGraph = () => router.push('/agent/teaching-graph/project')
</script>

<style scoped>
.agent-page {
  min-height: 100vh;
  background: #0a1628;
  color: #e2e8f0;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  background: linear-gradient(90deg, #0d2137 0%, #1a3a5c 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.3);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.back-btn { color: #c0c8d4 !important; font-size: 14px; }
.back-btn:hover { color: #409eff !important; }
.header-divider { width: 1px; height: 20px; background: rgba(255,255,255,0.15); }
.header-title { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; color: #fff; }
.header-title .el-icon { color: #409eff; }

.entry-main {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 56px);
  padding: 40px 24px;
}
.entry-cards { display: flex; gap: 32px; max-width: 900px; width: 100%; }

.entry-card {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, rgba(13, 33, 55, 0.9) 0%, rgba(26, 58, 92, 0.7) 100%);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 16px;
  padding: 32px 28px;
  cursor: pointer;
  transition: all 0.4s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.entry-card:hover {
  border-color: rgba(64, 158, 255, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(64, 158, 255, 0.15);
}
.card-glow {
  position: absolute;
  top: -60px;
  right: -60px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.project-glow { background: radial-gradient(circle, rgba(103, 194, 58, 0.12) 0%, transparent 70%); }
.card-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(64, 158, 255, 0.05));
  border: 1px solid rgba(64, 158, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  margin-bottom: 20px;
}
.project-icon {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2), rgba(103, 194, 58, 0.05));
  border-color: rgba(103, 194, 58, 0.3);
  color: #67c23a;
}
.card-title { font-size: 22px; font-weight: 700; margin: 0 0 4px; color: #fff; }
.card-subtitle { font-size: 13px; color: #c0c8d4; margin: 0 0 16px; }
.card-desc { font-size: 13px; color: #c0c8d4; line-height: 1.7; margin-bottom: 16px; flex: 1; }
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 20px; }
.card-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
  border: 1px solid rgba(64, 158, 255, 0.2);
}
.project-card .card-tag {
  background: rgba(103, 194, 58, 0.12);
  color: #67c23a;
  border-color: rgba(103, 194, 58, 0.2);
}
.card-enter {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 8px;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.2);
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}
.entry-card:hover .card-enter { background: rgba(64, 158, 255, 0.2); border-color: rgba(64, 158, 255, 0.4); }
.project-card .card-enter { background: rgba(103, 194, 58, 0.1); border-color: rgba(103, 194, 58, 0.2); color: #67c23a; }
.project-card:hover .card-enter { background: rgba(103, 194, 58, 0.2); border-color: rgba(103, 194, 58, 0.4); }
</style>
