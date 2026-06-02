/**
 * 根据项目的 sub_projects 数据自动生成四个图谱
 * 如果项目有自己的 knowledge_graph/capability_graph 等则使用项目的
 * 否则从 sub_projects 动态生成
 */

// 颜色常量
const COLORS = {
  knowledge: { basic: '#3498db', professional: '#2ecc71', extension: '#e74c3c', frontier: '#9b59b6' },
  capability: { junior: '#3498db', mid: '#f39c12', senior: '#e74c3c' },
  problem: { question: '#e74c3c', analysis: '#f39c12', solution: '#2ecc71' },
  ideological: ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c'],
}

const IDEOLOGICAL_DIMENSIONS = [
  { dimension: '家国情怀', keywords: ['应急', '救援', '保障', '民生'] },
  { dimension: '工匠精神', keywords: ['精准', '标准', '规范', '检查'] },
  { dimension: '法治意识', keywords: ['法规', '空域', '审批', '安全'] },
  { dimension: '创新意识', keywords: ['智能', '优化', '协同', '网络'] },
  { dimension: '团队协作', keywords: ['协同', '编队', '多机', '调度'] },
  { dimension: '生态文明', keywords: ['绿色', '环保', '低碳', '新能源'] },
]

/**
 * 从中文名称中提取关键词片段，用于跨任务相似度匹配
 */
function extractKeywords(name) {
  if (!name) return []
  // 按常见分隔符切分，并过滤空串和过短串
  const raw = name
    .split(/[/\\、，,：:；;\s\-—_()（）\[\]【】]+/)
    .filter(s => s.length >= 2)
  return raw
}

/**
 * 判断两个关键词集合是否有交集（共享至少一个关键词片段）
 */
function shareKeywords(kwA, kwB) {
  const setA = new Set(kwA)
  return kwB.some(kw => setA.has(kw))
}

/**
 * 从 sub_projects 生成知识图谱
 */
function generateKnowledgeGraph(subProjects) {
  const nodes = []
  const links = []
  const categories = [
    { id: 'KC', name: '基础知识模块', color: COLORS.knowledge.basic },
    { id: 'KP', name: '专业知识模块', color: COLORS.knowledge.professional },
    { id: 'KE', name: '拓展知识模块', color: COLORS.knowledge.extension },
    { id: 'KF', name: '前沿技术模块', color: COLORS.knowledge.frontier },
  ]

  const seenPoints = new Map() // id → node
  // id → keyword fragments extracted from name
  const keywordMap = new Map()
  // id → set of task names that contain this knowledge point
  const taskMembership = new Map()

  // 1) Collect all knowledge nodes and their keywords
  subProjects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      ;(task.points || []).forEach(pt => {
        if (pt.type !== 'knowledge') return
        if (seenPoints.has(pt.id)) {
          // record additional task membership
          const set = taskMembership.get(pt.id) || new Set()
          set.add(task.name)
          taskMembership.set(pt.id, set)
          return
        }

        // 根据名称推断分类
        let category = 'KP'
        const name = pt.name || ''
        if (/基础|概论|原理|管理/.test(name)) category = 'KC'
        else if (/仿真|数字|AI|智能|集群|5G|北斗/.test(name)) category = 'KF'
        else if (/拓展|创新|前沿|新兴/.test(name)) category = 'KE'

        const node = {
          id: pt.id,
          name: pt.name,
          category: categories.findIndex(c => c.id === category),
          symbolSize: 22,
          itemStyle: {
            color: COLORS.knowledge[category === 'KC' ? 'basic' : category === 'KP' ? 'professional' : category === 'KE' ? 'extension' : 'frontier'],
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.3)',
          },
          label: { fontSize: 11, color: '#fff', show: true, fontWeight: 'bold' },
          _raw: pt,
        }
        seenPoints.set(pt.id, node)
        keywordMap.set(pt.id, extractKeywords(name))
        const set = new Set()
        set.add(task.name)
        taskMembership.set(pt.id, set)
        nodes.push(node)
      })
    })
  })

  // 2) Intra-task links: knowledge points within the same task are linked sequentially
  subProjects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      const kPoints = (task.points || []).filter(p => p.type === 'knowledge')
      for (let i = 0; i < kPoints.length - 1; i++) {
        const src = kPoints[i].id
        const tgt = kPoints[i + 1].id
        if (seenPoints.has(src) && seenPoints.has(tgt)) {
          links.push({
            source: src, target: tgt,
            relation: '关联',
            lineStyle: { color: '#4a6a8a', width: 1.5, curveness: 0.2 },
          })
        }
      }
    })
  })

  // 3) Cross-task links: find knowledge points from different tasks that share keywords
  //    or appear in multiple tasks, and add cross-links between them
  const linkSet = new Set()
  const allIds = Array.from(seenPoints.keys())
  for (let i = 0; i < allIds.length; i++) {
    for (let j = i + 1; j < allIds.length; j++) {
      const idA = allIds[i]
      const idB = allIds[j]
      const keyA = keywordMap.get(idA) || []
      const keyB = keywordMap.get(idB) || []

      let shouldLink = false

      // Case 1: both nodes belong to the same knowledge category
      const catA = seenPoints.get(idA).category
      const catB = seenPoints.get(idB).category
      const sameCategory = catA === catB

      // Case 2: share at least one keyword fragment
      const kwMatch = shareKeywords(keyA, keyB)

      // Case 3: one node appears in multiple tasks (hub concept)
      const tasksA = taskMembership.get(idA) || new Set()
      const tasksB = taskMembership.get(idB) || new Set()
      const bothMultiTask = tasksA.size > 1 && tasksB.size > 1

      // Link if keywords match, or both are multi-task AND same category
      if (kwMatch && sameCategory) {
        shouldLink = true
      } else if (kwMatch && !sameCategory) {
        // cross-category keyword match — still link but with a dashed style
        shouldLink = true
      } else if (bothMultiTask && sameCategory) {
        shouldLink = true
      }

      if (shouldLink) {
        const linkKey = `${idA}-${idB}`
        if (!linkSet.has(linkKey)) {
          linkSet.add(linkKey)
          links.push({
            source: idA, target: idB,
            relation: kwMatch ? '知识关联' : '跨任务关联',
            lineStyle: {
              color: kwMatch ? '#6ab0de' : '#8a6a4a',
              width: kwMatch ? 1.2 : 1,
              curveness: 0.3,
              type: kwMatch ? 'solid' : 'dashed',
            },
          })
        }
      }
    }
  }

  // 4) Hub score: count connections per node and scale symbolSize accordingly
  const connectionCount = new Map()
  links.forEach(l => {
    connectionCount.set(l.source, (connectionCount.get(l.source) || 0) + 1)
    connectionCount.set(l.target, (connectionCount.get(l.target) || 0) + 1)
  })
  nodes.forEach(node => {
    const count = connectionCount.get(node.id) || 0
    if (count >= 5) {
      node.symbolSize = 30
    } else if (count >= 3) {
      node.symbolSize = 26
    }
    // store hub score for consumers that want it
    node.hubScore = count
  })

  return { title: '知识图谱', description: '课程知识点网络关系图', categories, nodes, links }
}

/**
 * 从 sub_projects 生成能力图谱
 */
function generateCapabilityGraph(subProjects) {
  const cards = []
  const links = []
  const levelMap = { basic: '初级', intermediate: '中级', advanced: '高级' }

  // Track task name → card ids for sibling linking
  const taskCardIds = new Map()

  let cardIdx = 1
  subProjects.forEach((sp, spIdx) => {
    ;(sp.tasks || []).forEach((task, tIdx) => {
      const skills = (task.points || []).filter(p => p.type === 'skill')
      if (skills.length === 0) return

      const level = task.type === 'basic' ? '初级' : task.type === 'advanced' ? '高级' : '中级'
      const cardIdsForTask = []

      skills.forEach(skill => {
        const cardId = `C${spIdx + 1}-${cardIdx}`
        // Build a richer description that includes the skill description
        const skillDesc = skill.description || skill.desc || ''
        const fullDescription = skillDesc
          ? skillDesc
          : `掌握${skill.name}的相关技能，能够在实际场景中灵活运用`

        cards.push({
          id: cardId,
          name: skill.name,
          description: fullDescription,
          tooltip: fullDescription,
          level,
          support_knowledge: `关联任务：${task.name}`,
          evaluation: '实操考核+项目评价',
        })
        cardIdsForTask.push(cardId)
        cardIdx++
      })

      // Record cards belonging to the same task for sibling linking
      if (cardIdsForTask.length > 1) {
        taskCardIds.set(task.name, cardIdsForTask)
      }
    })
  })

  // Add sibling links between capability cards that share the same task
  taskCardIds.forEach((cardIds) => {
    for (let i = 0; i < cardIds.length - 1; i++) {
      for (let j = i + 1; j < cardIds.length; j++) {
        links.push({
          source: cardIds[i],
          target: cardIds[j],
          relation: '同任务技能',
          lineStyle: { color: '#f39c12', width: 1.2, curveness: 0.2 },
        })
      }
    }
  })

  return {
    title: '能力图谱',
    description: '课程能力图谱矩阵 + 技能点分解表',
    template3_capability_cards: {
      title: '模板3：能力描述卡片',
      structure: '能力编号/名称/描述/适用层级/支撑知识/评价方式',
      cards,
    },
    links,
  }
}

// Context-aware problem generation patterns based on task content keywords
const PROBLEM_PATTERNS = [
  { match: /航线|路径|飞行|航路/i, templates: [
    (name) => `复杂地形条件下的${name}安全评估方法是什么？`,
    (name) => `${name}中如何平衡飞行时效性与安全保障？`,
    (name) => `城市密集建筑群环境中${name}的主要障碍因素有哪些？`,
  ]},
  { match: /载荷|货物|物资|运输|配送|装载|打包|装箱/i, templates: [
    (name) => `${name}中不同规格物资的装载重心稳定性如何保障？`,
    (name) => `紧急情况下${name}的快速调整方案如何制定？`,
    (name) => `${name}过程中物资损耗如何最小化？`,
  ]},
  { match: /调度|编队|集群|协同|多机/i, templates: [
    (name) => `多架无人机${name}时的冲突检测与避让策略是什么？`,
    (name) => `${name}场景下通信链路中断后的自主决策机制如何设计？`,
    (name) => `任务优先级动态变化时${name}如何实时重规划？`,
  ]},
  { match: /气象|天气|风|雨|能见度/i, templates: [
    (name) => `突发气象变化对${name}的影响评估及应急措施是什么？`,
    (name) => `${name}中低能见度条件下的飞行安全保障方案如何制定？`,
  ]},
  { match: /法规|空域|审批|合规|监管/i, templates: [
    (name) => `${name}中空域申请流程的合规审查要点有哪些？`,
    (name) => `跨区域${name}的法规协调与审批衔接如何处理？`,
  ]},
  { match: /通信|信号|数据|链路|5G|北斗/i, templates: [
    (name) => `${name}中远距离通信信号衰减问题如何解决？`,
    (name) => `多源异构数据融合在${name}中的关键技术挑战是什么？`,
  ]},
  { match: /仿真|数字|模型|模拟/i, templates: [
    (name) => `${name}的数字孪生模型精度验证标准是什么？`,
    (name) => `仿真环境与真实场景差异对${name}结果的影响如何量化？`,
  ]},
  { match: /应急|救援|灾|紧急/i, templates: [
    (name) => `${name}中信息不完整条件下的应急决策依据是什么？`,
    (name) => `多部门联合${name}时的指挥协调机制如何建立？`,
  ]},
  { match: /绿色|环保|低碳|能源|电池/i, templates: [
    (name) => `${name}中无人机电池回收与环保处置方案如何设计？`,
    (name) => `低碳目标约束下${name}的能耗优化策略是什么？`,
  ]},
  { match: /安全|检查|维护|保障/i, templates: [
    (name) => `${name}中飞行前安全检查的关键遗漏点有哪些？`,
    (name) => `长期运行条件下${name}的设备疲劳检测方案如何制定？`,
  ]},
]

/**
 * 根据任务名称生成上下文相关的问题描述
 */
function generateContextualProblem(taskName) {
  // Try to match against known patterns
  for (const pattern of PROBLEM_PATTERNS) {
    if (pattern.match.test(taskName)) {
      const templates = pattern.templates
      // Pick the first template (can cycle based on some deterministic factor)
      return templates[0](taskName)
    }
  }
  // Fallback: generate a slightly more specific default
  return `${taskName}中理论知识向实际操作转化的关键难点是什么？`
}

/**
 * 根据任务名称生成上下文相关的挑战描述
 */
function generateContextualChallenge(taskName) {
  for (const pattern of PROBLEM_PATTERNS) {
    if (pattern.match.test(taskName)) {
      return `${taskName}涉及多学科知识交叉融合，需要综合运用理论分析与实践操作能力`
    }
  }
  return `将${taskName}的理论知识应用于真实工程场景，考验综合分析与解决问题的能力`
}

/**
 * 根据任务名称和知识点生成分析方法描述
 */
function generateAnalysisMethod(taskName, pointNames) {
  for (const pattern of PROBLEM_PATTERNS) {
    if (pattern.match.test(taskName)) {
      return `结合${pointNames.slice(0, 2).join('与')}的理论基础，采用案例分析+场景仿真+实操验证`
    }
  }
  return '案例分析+实践操作+反思总结'
}

/**
 * 根据任务名称生成解决方案描述
 */
function generateSolutionDescription(taskName) {
  for (const pattern of PROBLEM_PATTERNS) {
    if (pattern.match.test(taskName)) {
      return `梳理${taskName}核心知识→搭建仿真验证环境→分步实践操作→总结经验并优化流程`
    }
  }
  return `学习相关知识点→掌握操作技能→完成实践任务→总结反思优化`
}

/**
 * 根据任务名称生成成果描述
 */
function generateOutcomeDescription(taskName) {
  for (const pattern of PROBLEM_PATTERNS) {
    if (pattern.match.test(taskName)) {
      return `形成${task_name_safe(taskName)}的完整解决方案，具备独立分析与处置能力`
    }
  }
  return `完成${taskName}的学习目标`
}

function task_name_safe(name) {
  // Return name trimmed to reasonable length for display
  return name.length > 20 ? name.substring(0, 20) + '…' : name
}

/**
 * 从 sub_projects 生成问题图谱
 */
function generateProblemGraph(subProjects) {
  const problems = []
  const analyses = []
  const solutions = []

  let pIdx = 1
  subProjects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      const taskId = `任务${pIdx}`
      const pointNames = (task.points || []).map(p => p.name)

      // Generate contextually relevant problem
      const problemText = generateContextualProblem(task.name)
      const scenario = task.description || `${task.name}的真实工作场景`

      problems.push({
        id: `P${String(pIdx).padStart(2, '0')}`,
        task: taskId,
        problem: problemText,
        scenario,
        challenge: generateContextualChallenge(task.name),
      })

      analyses.push({
        for_task: taskId,
        key_factors: pointNames.slice(0, 4),
        method: generateAnalysisMethod(task.name, pointNames),
      })

      solutions.push({
        for_task: taskId,
        solution: generateSolutionDescription(task.name),
        outcome: generateOutcomeDescription(task.name),
      })
      pIdx++
    })
  })

  return {
    title: '问题图谱',
    description: '课程问题链设计',
    levels: [
      { level: '问题导向层', description: '真实工单驱动的问题导入', problems },
      { level: '问题分析层', description: '分解问题的关键要素与分析方法', analyses },
      { level: '问题解决层', description: '解决问题的方案与步骤', solutions },
    ],
  }
}

/**
 * 从 sub_projects 生成思政图谱
 */
function generateIdeologicalGraph(subProjects) {
  const dimensions = IDEOLOGICAL_DIMENSIONS.map((dim, di) => {
    const elements = []
    let eIdx = 1
    subProjects.forEach(sp => {
      ;(sp.tasks || []).forEach(task => {
        const taskText = `${task.name} ${task.description || ''}`
        // 检查任务内容是否与该维度的关键词匹配
        const matched = dim.keywords.some(kw => taskText.includes(kw))
        if (matched) {
          // Generate more specific content based on dimension + task context
          const content = generateIdeologicalContent(dim.dimension, task.name, task.description)
          const method = generateIdeologicalMethod(dim.dimension, task.name)
          const outcome = generateIdeologicalOutcome(dim.dimension, task.name)

          elements.push({
            id: `S${di + 1}-${eIdx}`,
            task: `任务${elements.length + 1}`,
            content,
            method,
            outcome,
          })
          eIdx++
        }
      })
    })
    // 确保每个维度至少有1个元素
    if (elements.length === 0) {
      elements.push({
        id: `S${di + 1}-1`,
        task: '综合',
        content: `在课程各环节中系统融入${dim.dimension}教育，实现知识传授与价值引领的有机统一`,
        method: `通过课程整体设计，将${dim.dimension}贯穿于理论教学与实践训练全过程`,
        outcome: `培养学生的${dim.dimension}，使其具备良好的职业素养与社会责任感`,
      })
    }
    return { dimension: dim.dimension, elements }
  })

  return {
    title: '思政图谱',
    description: '课程思政元素融入设计',
    dimensions,
  }
}

// ----- Ideological content generation helpers -----

const IDEOLOGICAL_CONTENT_TEMPLATES = {
  '家国情怀': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中的真实案例与行业背景',
    suffix: [
      '，引导学生理解应急运输保障对国家安全和民生保障的重要意义',
      '，激发学生投身低空经济建设、服务国家战略的责任担当',
      '，让学生深刻体会无人机应急运输在守护人民生命财产安全中的关键作用',
    ],
  },
  '工匠精神': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中的标准化操作要求与精准控制环节',
    suffix: [
      '，培养学生精益求精、追求卓越的专业态度',
      '，引导学生养成严谨细致、一丝不苟的工作习惯',
      '，使学生认识到精准操作对保障飞行安全和任务成败的决定性作用',
    ],
  },
  '法治意识': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中涉及的空域管理与安全规范内容',
    suffix: [
      '，强化学生的航空法规意识和合规操作自觉性',
      '，引导学生树立依法依规开展无人机作业的法治理念',
      '，让学生理解遵守法规是保障低空飞行安全的底线要求',
    ],
  },
  '创新意识': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中的智能化技术应用与优化设计环节',
    suffix: [
      '，激发学生运用新技术解决实际问题的创新思维',
      '，培养学生敢于突破传统方案、探索更优解的创新精神',
      '，引导学生认识技术创新是推动低空应急运输发展的核心驱动力',
    ],
  },
  '团队协作': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中的多人协同作业与编队配合环节',
    suffix: [
      '，培养学生在复杂任务中的沟通协调与团队合作能力',
      '，引导学生理解多机协同对提升应急运输效率的关键作用',
      '，使学生认识到高效团队协作是完成大规模应急任务的必要条件',
    ],
  },
  '生态文明': {
    prefix: [
      '通过',
      '借助',
      '利用',
    ],
    middle: '任务中的绿色低碳理念与环保要求',
    suffix: [
      '，引导学生将生态文明理念融入无人机运输方案设计',
      '，培养学生在低空经济发展中兼顾效率与环保的可持续发展观',
      '，使学生认识到新能源应用和节能减排是行业绿色转型的重要方向',
    ],
  },
}

function pickFrom(arr, index) {
  return arr[index % arr.length]
}

function generateIdeologicalContent(dimension, taskName, taskDesc) {
  const tmpl = IDEOLOGICAL_CONTENT_TEMPLATES[dimension]
  if (tmpl) {
    const prefix = pickFrom(tmpl.prefix, taskName.length)
    return `${prefix}${taskName}任务中的真实案例，${tmpl.suffix[taskName.length % tmpl.suffix.length]}`
  }
  // Generic fallback
  return `通过${taskName}中的典型案例分析与实践体验，深化学生对${dimension}的理解与认同`
}

function generateIdeologicalMethod(dimension, taskName) {
  const methods = {
    '家国情怀': `结合${taskName}中的应急救援案例，组织专题讨论与情景模拟，引导学生感悟使命担当`,
    '工匠精神': `在${taskName}实操环节设置标准化考核指标，通过反复训练与对比分析培养精益求精的态度`,
    '法治意识': `融入${taskName}相关法规条款学习，通过案例警示和合规审查练习强化法治观念`,
    '创新意识': `在${taskName}中设置开放性问题和优化挑战，鼓励学生提出创新方案并进行可行性论证`,
    '团队协作': `在${taskName}中设计多人协作任务，通过角色分工、沟通演练和复盘总结提升团队能力`,
    '生态文明': `在${taskName}方案设计中融入环保评估环节，引导学生对比分析不同方案的环境影响`,
  }
  return methods[dimension] || `通过${taskName}的实践训练，系统培养学生的${dimension}`
}

function generateIdeologicalOutcome(dimension, taskName) {
  const outcomes = {
    '家国情怀': `增强学生服务国家战略、投身应急救援事业的使命感和责任感`,
    '工匠精神': `养成学生在无人机操作与方案设计中追求精准、注重细节的职业习惯`,
    '法治意识': `使学生自觉遵守航空法规，在实际工作中做到依法合规操作`,
    '创新意识': `培养学生善于发现问题、勇于技术创新、持续优化方案的创新素养`,
    '团队协作': `提升学生在复杂应急任务中的沟通表达、角色适应和协调配合能力`,
    '生态文明': `使学生在低空运输实践中主动考虑环保因素，践行绿色发展理念`,
  }
  return outcomes[dimension] || `培养学生的${dimension}，提升综合职业素养`
}

/**
 * 主函数：获取项目的四个图谱数据
 * 优先使用项目自带的数据，否则自动生成
 */
export function getProjectGraphs(project) {
  if (!project) return null

  const subProjects = project.sub_projects || []

  return {
    knowledge_graph: project.knowledge_graph || generateKnowledgeGraph(subProjects),
    capability_graph: project.capability_graph || generateCapabilityGraph(subProjects),
    problem_graph: project.problem_graph || generateProblemGraph(subProjects),
    ideological_graph: project.ideological_graph || generateIdeologicalGraph(subProjects),
  }
}
