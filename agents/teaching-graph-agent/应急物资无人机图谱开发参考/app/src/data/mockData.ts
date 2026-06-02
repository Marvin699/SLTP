// ============ Student Data (42 students) ============

export interface Student {
  id: string;
  name: string;
  score: number;
  status: 'completed' | 'in-progress' | 'not-started';
  gender: 'male' | 'female';
  completionRate: number;
  taskScores: number[];
  skillScores: number[]; // 6 dimensions
}

const firstNames = [
  '张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴',
  '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
  '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
  '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
  '余', '杜',
];
const lastNames = [
  '伟', '娜', '芳', '洋', '静', '磊', '敏', '磊', '婷', '杰',
  '丽', '强', '军', '平', '刚', '桂', '秀英', '华', '志', '秀兰',
  '霞', '明', '建国', '燕', '红', '平', '辉', '鑫', '磊', '宇',
  '洁', '欣', '思', '雨', '晨', '一', '子', '家', '国', '晓',
  '小', '大',
];

function generateStudents(): Student[] {
  const students: Student[] = [];
  const baseScores = [
    92.5, 88.3, 91.0, 76.5, 85.2, 72.8, 89.7, 65.4, 94.1, 78.9,
    82.3, 71.2, 86.4, 90.1, 77.6, 83.8, 69.5, 87.2, 79.3, 91.6,
    74.1, 88.9, 81.7, 93.2, 70.8, 84.5, 76.9, 89.0, 82.1, 75.4,
    90.7, 68.3, 85.6, 78.2, 92.0, 73.5, 86.8, 80.4, 94.5, 71.9,
    83.1, 87.0,
  ];

  for (let i = 0; i < 42; i++) {
    const name = firstNames[i] + lastNames[i];
    const score = baseScores[i];
    const status: Student['status'] =
      score >= 80 ? 'completed' : score >= 65 ? 'in-progress' : 'not-started';
    const gender: Student['gender'] = i < 28 ? 'male' : 'female';

    // Generate task scores that roughly average to the overall score
    const taskScores = [
      Math.min(100, score + (Math.random() - 0.4) * 12),
      Math.min(100, score + (Math.random() - 0.3) * 14),
      Math.min(100, score + (Math.random() - 0.5) * 16),
      Math.min(100, score + (Math.random() - 0.2) * 10),
      Math.min(100, score + (Math.random() - 0.4) * 14),
      Math.min(100, score + (Math.random() - 0.3) * 16),
      Math.min(100, score + (Math.random() - 0.5) * 20),
      Math.min(100, score + (Math.random() - 0.4) * 24),
    ].map((s) => Math.round(s * 10) / 10);

    const skillScores = [
      clamp(score + (Math.random() - 0.4) * 15),
      clamp(score + (Math.random() - 0.3) * 18),
      clamp(score + (Math.random() - 0.5) * 20),
      clamp(score + (Math.random() - 0.4) * 16),
      clamp(score + (Math.random() - 0.2) * 14),
      clamp(score + (Math.random() - 0.3) * 12),
    ].map((s) => Math.round(s));

    students.push({
      id: `2023${String(i + 1).padStart(3, '0')}`,
      name,
      score,
      status,
      gender,
      completionRate: Math.min(100, Math.round((score / 95) * 100)),
      taskScores,
      skillScores,
    });
  }
  return students;
}

function clamp(v: number): number {
  return Math.max(55, Math.min(98, v));
}

export const students = generateStudents();

// ============ Class Statistics ============

export const classStats = {
  totalStudents: 42,
  maleCount: 28,
  femaleCount: 14,
  completedCount: 38,
  inProgressCount: 4,
  overallCompletion: 90.5,
};

// ============ Task Data (8 tasks) ============

export interface TaskData {
  id: number;
  name: string;
  subProject: string;
  subProjectId: number;
  completion: number;
  avgScore: number;
  status: 'completed' | 'in-progress' | 'not-started';
  completedCount: number;
  totalCount: number;
  dateRange: string;
  week: number;
}

export const tasks: TaskData[] = [
  {
    id: 1, name: '需求分析与飞行计划制定', subProject: '子项目一', subProjectId: 1,
    completion: 100, avgScore: 87.5, status: 'completed', completedCount: 42, totalCount: 42,
    dateRange: '3.01-3.07', week: 1,
  },
  {
    id: 2, name: '单点航线规划与空域申请', subProject: '子项目一', subProjectId: 1,
    completion: 95, avgScore: 82.3, status: 'completed', completedCount: 40, totalCount: 42,
    dateRange: '3.08-3.14', week: 2,
  },
  {
    id: 3, name: '网络航线规划与协同调度', subProject: '子项目一', subProjectId: 1,
    completion: 95, avgScore: 79.8, status: 'completed', completedCount: 40, totalCount: 42,
    dateRange: '3.15-3.21', week: 3,
  },
  {
    id: 4, name: '物资包装装载与行前准备', subProject: '子项目二', subProjectId: 2,
    completion: 90, avgScore: 86.2, status: 'completed', completedCount: 38, totalCount: 42,
    dateRange: '3.22-3.28', week: 4,
  },
  {
    id: 5, name: '多机协同装调与系统调试', subProject: '子项目二', subProjectId: 2,
    completion: 85, avgScore: 81.5, status: 'completed', completedCount: 36, totalCount: 42,
    dateRange: '3.29-4.04', week: 5,
  },
  {
    id: 6, name: '飞行模拟与虚拟仿真演练', subProject: '子项目三', subProjectId: 3,
    completion: 80, avgScore: 78.6, status: 'in-progress', completedCount: 34, totalCount: 42,
    dateRange: '4.05-4.11', week: 6,
  },
  {
    id: 7, name: '飞行实操与物资精准投放', subProject: '子项目三', subProjectId: 3,
    completion: 75, avgScore: 74.2, status: 'in-progress', completedCount: 32, totalCount: 42,
    dateRange: '4.12-4.18', week: 7,
  },
  {
    id: 8, name: '方案汇报与应急模拟演练', subProject: '子项目三', subProjectId: 3,
    completion: 70, avgScore: 72.0, status: 'in-progress', completedCount: 29, totalCount: 42,
    dateRange: '4.19-4.25', week: 8,
  },
];

// ============ Sub-Project Data (3 sub-projects) ============

export interface SubProjectData {
  id: number;
  name: string;
  title: string;
  hours: number;
  taskCount: number;
  completion: number;
  avgScore: number;
  color: string;
  tasks: number[]; // task IDs
}

export const subProjects: SubProjectData[] = [
  {
    id: 1, name: '子项目一', title: '飞行任务规划', hours: 6, taskCount: 3,
    completion: 96.7, avgScore: 83.2, color: '#00E5FF', tasks: [1, 2, 3],
  },
  {
    id: 2, name: '子项目二', title: '飞行设备准备', hours: 4, taskCount: 2,
    completion: 87.5, avgScore: 83.9, color: '#8B5CF6', tasks: [4, 5],
  },
  {
    id: 3, name: '子项目三', title: '飞行运输实操', hours: 6, taskCount: 3,
    completion: 75.0, avgScore: 74.9, color: '#F59E0B', tasks: [6, 7, 8],
  },
];

// ============ Skill Dimensions (6 dimensions) ============

export const skillDimensions = [
  '飞行规划能力',
  '设备调试能力',
  '协同调度能力',
  '应急处理能力',
  '数据分析能力',
  '安全规范意识',
];

export const classSkillScores = [82, 78, 75, 80, 85, 88];
export const targetSkillScores = [90, 90, 90, 90, 90, 90];

// ============ Knowledge Graph Data ============

export interface GraphNode {
  id: string;
  name: string;
  category: number;
  symbolSize: number;
  value?: number;
  label?: { show?: boolean; fontSize?: number; fontWeight?: string };
  itemStyle?: { color?: string };
}

export interface GraphLink {
  source: string;
  target: string;
  lineStyle?: { width?: number; type?: string; color?: string; opacity?: number };
}

export const knowledgeGraphNodes: GraphNode[] = [
  { id: 'center', name: '应急物资低空智慧运输', category: 0, symbolSize: 80, label: { show: true, fontSize: 16, fontWeight: 'bold' }, itemStyle: { color: '#00E5FF' } },
  // Task nodes (layer 2)
  { id: 't1', name: '需求分析与飞行计划制定', category: 1, symbolSize: 50, itemStyle: { color: '#3B82F6' } },
  { id: 't2', name: '单点航线规划与空域申请', category: 1, symbolSize: 50, itemStyle: { color: '#2563EB' } },
  { id: 't3', name: '网络航线规划与协同调度', category: 1, symbolSize: 50, itemStyle: { color: '#60A5FA' } },
  { id: 't4', name: '物资包装装载与行前准备', category: 1, symbolSize: 50, itemStyle: { color: '#8B5CF6' } },
  { id: 't5', name: '多机协同装调与系统调试', category: 1, symbolSize: 50, itemStyle: { color: '#A78BFA' } },
  { id: 't6', name: '飞行模拟与虚拟仿真演练', category: 1, symbolSize: 50, itemStyle: { color: '#F59E0B' } },
  { id: 't7', name: '飞行实操与物资精准投放', category: 1, symbolSize: 50, itemStyle: { color: '#FBBF24' } },
  { id: 't8', name: '方案汇报与应急模拟演练', category: 1, symbolSize: 50, itemStyle: { color: '#00E5FF' } },
  // Knowledge point nodes (layer 3) — sub-project 1 (cyan tones)
  { id: 'k1', name: '需求分析方法', category: 2, symbolSize: 32, itemStyle: { color: '#22D3EE' } },
  { id: 'k2', name: '飞行计划编制', category: 2, symbolSize: 35, itemStyle: { color: '#06B6D4' } },
  { id: 'k3', name: '应急评估', category: 2, symbolSize: 28, itemStyle: { color: '#67E8F9' } },
  { id: 'k4', name: '航线规划算法', category: 2, symbolSize: 34, itemStyle: { color: '#0891B2' } },
  { id: 'k5', name: '空域管理规定', category: 2, symbolSize: 30, itemStyle: { color: '#164E63' } },
  { id: 'k6', name: 'GIS应用', category: 2, symbolSize: 28, itemStyle: { color: '#155E75' } },
  { id: 'k7', name: '网络优化', category: 2, symbolSize: 32, itemStyle: { color: '#0E7490' } },
  { id: 'k8', name: '协同调度策略', category: 2, symbolSize: 30, itemStyle: { color: '#06B6D4' } },
  { id: 'k9', name: '多目标规划', category: 2, symbolSize: 28, itemStyle: { color: '#67E8F9' } },
  // Knowledge point nodes — sub-project 2 (violet tones)
  { id: 'k10', name: '物资分类', category: 3, symbolSize: 30, itemStyle: { color: '#A78BFA' } },
  { id: 'k11', name: '包装标准', category: 3, symbolSize: 28, itemStyle: { color: '#8B5CF6' } },
  { id: 'k12', name: '载重计算', category: 3, symbolSize: 34, itemStyle: { color: '#7C3AED' } },
  { id: 'k13', name: '多机通信', category: 3, symbolSize: 32, itemStyle: { color: '#6D28D9' } },
  { id: 'k14', name: '传感器校准', category: 3, symbolSize: 30, itemStyle: { color: '#5B21B6' } },
  { id: 'k15', name: '系统联调', category: 3, symbolSize: 35, itemStyle: { color: '#8B5CF6' } },
  // Knowledge point nodes — sub-project 3 (amber tones)
  { id: 'k16', name: '仿真建模', category: 4, symbolSize: 34, itemStyle: { color: '#F59E0B' } },
  { id: 'k17', name: '飞行控制', category: 4, symbolSize: 32, itemStyle: { color: '#D97706' } },
  { id: 'k18', name: '虚拟测试', category: 4, symbolSize: 28, itemStyle: { color: '#B45309' } },
  { id: 'k19', name: '手动操控', category: 4, symbolSize: 30, itemStyle: { color: '#F59E0B' } },
  { id: 'k20', name: '自动投放', category: 4, symbolSize: 35, itemStyle: { color: '#FBBF24' } },
  { id: 'k21', name: '精准定位', category: 4, symbolSize: 32, itemStyle: { color: '#FCD34D' } },
  { id: 'k22', name: '方案撰写', category: 4, symbolSize: 28, itemStyle: { color: '#F59E0B' } },
  { id: 'k23', name: '汇报技巧', category: 4, symbolSize: 28, itemStyle: { color: '#D97706' } },
  { id: 'k24', name: '应急决策', category: 4, symbolSize: 34, itemStyle: { color: '#B45309' } },
];

export const knowledgeGraphLinks: GraphLink[] = [
  // Center to tasks
  { source: 'center', target: 't1', lineStyle: { width: 2, color: '#00E5FF', opacity: 0.6 } },
  { source: 'center', target: 't2', lineStyle: { width: 2, color: '#00E5FF', opacity: 0.6 } },
  { source: 'center', target: 't3', lineStyle: { width: 2, color: '#00E5FF', opacity: 0.6 } },
  { source: 'center', target: 't4', lineStyle: { width: 2, color: '#8B5CF6', opacity: 0.6 } },
  { source: 'center', target: 't5', lineStyle: { width: 2, color: '#8B5CF6', opacity: 0.6 } },
  { source: 'center', target: 't6', lineStyle: { width: 2, color: '#F59E0B', opacity: 0.6 } },
  { source: 'center', target: 't7', lineStyle: { width: 2, color: '#F59E0B', opacity: 0.6 } },
  { source: 'center', target: 't8', lineStyle: { width: 2, color: '#00E5FF', opacity: 0.6 } },
  // Task 1 to knowledge points
  { source: 't1', target: 'k1', lineStyle: { width: 1, type: 'dashed', color: '#22D3EE', opacity: 0.4 } },
  { source: 't1', target: 'k2', lineStyle: { width: 1, type: 'dashed', color: '#22D3EE', opacity: 0.4 } },
  { source: 't1', target: 'k3', lineStyle: { width: 1, type: 'dashed', color: '#22D3EE', opacity: 0.4 } },
  // Task 2 to knowledge points
  { source: 't2', target: 'k4', lineStyle: { width: 1, type: 'dashed', color: '#0891B2', opacity: 0.4 } },
  { source: 't2', target: 'k5', lineStyle: { width: 1, type: 'dashed', color: '#0891B2', opacity: 0.4 } },
  { source: 't2', target: 'k6', lineStyle: { width: 1, type: 'dashed', color: '#0891B2', opacity: 0.4 } },
  // Task 3 to knowledge points
  { source: 't3', target: 'k7', lineStyle: { width: 1, type: 'dashed', color: '#06B6D4', opacity: 0.4 } },
  { source: 't3', target: 'k8', lineStyle: { width: 1, type: 'dashed', color: '#06B6D4', opacity: 0.4 } },
  { source: 't3', target: 'k9', lineStyle: { width: 1, type: 'dashed', color: '#06B6D4', opacity: 0.4 } },
  // Task 4 to knowledge points
  { source: 't4', target: 'k10', lineStyle: { width: 1, type: 'dashed', color: '#A78BFA', opacity: 0.4 } },
  { source: 't4', target: 'k11', lineStyle: { width: 1, type: 'dashed', color: '#A78BFA', opacity: 0.4 } },
  { source: 't4', target: 'k12', lineStyle: { width: 1, type: 'dashed', color: '#A78BFA', opacity: 0.4 } },
  // Task 5 to knowledge points
  { source: 't5', target: 'k13', lineStyle: { width: 1, type: 'dashed', color: '#8B5CF6', opacity: 0.4 } },
  { source: 't5', target: 'k14', lineStyle: { width: 1, type: 'dashed', color: '#8B5CF6', opacity: 0.4 } },
  { source: 't5', target: 'k15', lineStyle: { width: 1, type: 'dashed', color: '#8B5CF6', opacity: 0.4 } },
  // Task 6 to knowledge points
  { source: 't6', target: 'k16', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
  { source: 't6', target: 'k17', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
  { source: 't6', target: 'k18', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
  // Task 7 to knowledge points
  { source: 't7', target: 'k19', lineStyle: { width: 1, type: 'dashed', color: '#FBBF24', opacity: 0.4 } },
  { source: 't7', target: 'k20', lineStyle: { width: 1, type: 'dashed', color: '#FBBF24', opacity: 0.4 } },
  { source: 't7', target: 'k21', lineStyle: { width: 1, type: 'dashed', color: '#FBBF24', opacity: 0.4 } },
  // Task 8 to knowledge points
  { source: 't8', target: 'k22', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
  { source: 't8', target: 'k23', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
  { source: 't8', target: 'k24', lineStyle: { width: 1, type: 'dashed', color: '#F59E0B', opacity: 0.4 } },
];

// ============ Teaching Evaluation Data ============

export const evaluationScores = {
  tasks: ['任务1', '任务2', '任务3', '任务4', '任务5', '任务6', '任务7', '任务8'],
  知识掌握: [90, 86, 83, 88, 85, 80, 75, 72],
  技能操作: [85, 82, 78, 87, 80, 76, 72, 70],
  团队协作: [88, 85, 80, 82, 86, 78, 74, 76],
  安全规范: [92, 90, 88, 91, 89, 85, 80, 78],
};

export const classTrend = {
  weeks: ['第0周', '第1周', '第2周', '第3周', '第4周', '第5周', '第6周', '第7周', '第8周'],
  scores: [0, 72, 78, 82, 80, 83, 81, 79, 77],
};

export const radarEvalData = {
  班级平均: [82, 78, 75, 80, 85, 88],
  优秀标杆: [94, 92, 90, 93, 95, 96],
  目标值: [85, 85, 85, 85, 85, 85],
};

export const skillBarData = skillDimensions.map((dim, i) => ({
  name: dim,
  score: classSkillScores[i],
}));

// ============ Certificate & Competition Data ============

export const certStats = {
  certCount: 3,
  certPassRate: 86.7,
  competitionCount: 2,
  awardWinners: 6,
  certNames: ['无人机驾驶员', '物流管理师', '应急救援员'],
  competitionNames: ['全国无人机大赛', '物流仿真竞赛'],
};

export const certRelevanceScores = [88, 85, 82, 90, 87, 80, 78, 75];

// ============ Timeline Data ============

export const timelineData = tasks.map((t) => ({
  week: t.week,
  name: t.name,
  dateRange: t.dateRange,
  status: t.status,
  completion: t.completion,
}));

// ============ Weekly participation sparkline ============

export const weeklyParticipation = [38, 40, 41, 39, 40, 36, 34, 32];
