// 全站导航配置（MainLayout 顶栏与智能体页隐藏导航共用，保证两处菜单一致）
export const teacherNavItems = [
  { path: '/home', title: '首页' },
  { path: '/courses', title: '我的课程' },
  { path: '/training', title: '实训任务' },
  { path: '/evaluation', title: '教学智评' },
  { path: '/teacher/monitor', title: '教学监控' },
  { path: '/resources', title: '学习资源' },
  { path: '/system', title: '系统管理' }
]

// 学生端导航：去掉「系统管理」（无权限）
export const studentNavItems = [
  { path: '/home', title: '首页' },
  { path: '/courses', title: '我的课程' },
  { path: '/training', title: '实训任务' },
  { path: '/evaluation', title: '教学智评' },
  { path: '/resources', title: '学习资源' }
]

export function navItemsFor(role) {
  return role === 'teacher' ? teacherNavItems : studentNavItems
}
