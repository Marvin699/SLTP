import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/home/index.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('../views/courses/index.vue'),
        meta: { title: '课程中心' }
      },
      {
        path: 'training',
        name: 'Training',
        component: () => import('../views/training/index.vue'),
        meta: { title: '实训任务' }
      },
      {
        path: 'evaluation',
        name: 'Evaluation',
        component: () => import('../views/evaluation/index.vue'),
        meta: { title: '教学智评' }
      },
      {
        path: 'evaluation/section/:sectionId',
        name: 'SectionDetail',
        component: () => import('../views/evaluation/SectionDetail.vue'),
        meta: { title: '环节详情' }
      },
      {
        path: 'evaluation/section/:sectionId/ai-analysis',
        name: 'AiAnalysis',
        component: () => import('../views/evaluation/AiAnalysisView.vue'),
        meta: { title: 'AI教学分析' }
      },
      {
        path: 'evaluation/task7',
        name: 'Task7Score',
        component: () => import('../views/evaluation/Task7Score.vue'),
        meta: { title: '任务7评分' }
      },
      {
        path: 'evaluation/section/task4/live',
        name: 'Section4Live',
        component: () => import('../views/evaluation/Section4Live.vue'),
        meta: { title: '应急装载AI智能体大屏' }
      },
      {
        path: 'evaluation/task4/student',
        name: 'Section4Student',
        component: () => import('../views/evaluation/Section4Student.vue'),
        meta: { title: '任务4 · AI智能体子系统' }
      },
      {
        path: 'evaluation/task8',
        name: 'Task8Dashboard',
        component: () => import('../views/evaluation/Task8Dashboard.vue'),
        meta: { title: '任务8大屏 · 方案优化与应急模拟演练' }
      },
      {
        path: 'evaluation/task8/heatmap',
        name: 'Task8Heatmap',
        component: () => import('../views/evaluation/Task8Heatmap.vue'),
        meta: { title: '任务8 · 班级热力图' }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('../views/resources/index.vue'),
        meta: { title: '学习资源' }
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('../views/system/index.vue'),
        meta: { title: '系统管理' }
      },
      {
        path: 'system/course-data',
        name: 'CourseDataManage',
        component: () => import('../views/system/CourseDataManage.vue'),
        meta: { title: '课程数据管理' }
      }
    ]
  },
  {
    path: '/agent/path-planning',
    name: 'PathPlanningAgent',
    component: () => import('../views/agents/PathPlanningAgentView.vue'),
    meta: { title: '路径规划智能体' }
  },
  {
    path: '/agent/packing',
    name: 'PackingAgent',
    component: () => import('../views/agents/PackingAgentView.vue'),
    meta: { title: '装箱评价智能体' }
  },
  {
    path: '/agent/teaching-graph',
    name: 'TeachingGraphAgent',
    component: () => import('../views/agents/TeachingGraph.vue'),
    meta: { title: '课程图谱智能体' }
  },
  {
    path: '/agent/teaching-graph/view',
    name: 'TeachingGraphView',
    component: () => import('../views/agents/TeachingGraphView.vue'),
    meta: { title: '教学图谱' }
  },
  {
    path: '/agent/teaching-graph/project',
    name: 'ProjectGraphView',
    component: () => import('../views/agents/ProjectGraphView.vue'),
    meta: { title: '项目图谱' }
  },
  {
    path: '/ai-assistant',
    name: 'AiAssistant',
    component: () => import('../views/ai-assistant/index.vue'),
    meta: { title: '小翼 · AI智能助教' }
  },
  {
    path: '/score/:token',
    name: 'ScorePage',
    component: () => import('../views/score/ScorePage.vue'),
    meta: { title: '评分', public: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/login/index.vue'),
    meta: { title: '404', public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  if (to.path && (to.path.startsWith('/hybridaction') || to.path.startsWith('/zyb') || to.path.startsWith('/brush'))) {
    next('/home')
    return
  }

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 智慧低空应急运输教学平台`
  }

  // 公开页面不需要登录
  if (to.meta.public) {
    next()
    return
  }

  // 检查登录状态
  const user = JSON.parse(localStorage.getItem('sltp_user') || 'null')
  if (!user || !user.username) {
    next('/login')
    return
  }

  next()
})

export default router
