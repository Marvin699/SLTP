<template>
  <div class="graph-view-page">
    <!-- 顶部导航 -->
    <header class="view-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn" text>
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-divider"></div>
        <div class="header-course">
          <span class="course-name">智慧运输运营</span>
          <span class="course-sep">·</span>
          <span class="project-name">{{ currentProjectName }}</span>
        </div>
      </div>
      <div class="header-right">
        <!-- 项目选择器（所有tab都可用） -->
        <el-select
          v-if="projectList.length"
          v-model="selectedProjectId"
          size="small"
          placeholder="选择项目"
          style="width: 200px"
          @change="selectProject"
        >
          <el-option
            v-for="p in projectList"
            :key="p.project_id"
            :label="`${p.project_id} - ${p.name}`"
            :value="p.project_id"
          />
        </el-select>
        <el-radio-group v-if="activeTab === 'course' && currentProject" v-model="viewMode" size="small" @change="handleViewChange">
          <el-radio-button value="all">显示全部</el-radio-button>
          <el-radio-button value="basic">基础学习</el-radio-button>
          <el-radio-button value="advanced">进阶提升</el-radio-button>
        </el-radio-group>
        <el-tag type="success" effect="dark" size="small">2026春学期</el-tag>
      </div>
    </header>

    <!-- 7个图谱Tab导航 -->
    <nav class="main-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        class="main-tab"
        :class="{ active: activeTab === tab.key }"
        @click="switchTab(tab.key)"
      >
        <el-icon :size="16"><component :is="tab.icon" /></el-icon>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </nav>

    <!-- 主体内容 -->
    <div class="view-body">
      <!-- 左侧面板 -->
      <aside class="left-panel">
        <div class="panel-section">
          <h4 class="panel-title"><span class="title-bar"></span>图谱控制</h4>
          <div class="panel-group">
            <div class="group-label">视图操作</div>
            <button class="ctrl-btn" @click="zoomIn"><el-icon><ZoomIn /></el-icon> 放大</button>
            <button class="ctrl-btn" @click="zoomOut"><el-icon><ZoomOut /></el-icon> 缩小</button>
            <button class="ctrl-btn" @click="resetView"><el-icon><RefreshRight /></el-icon> 重置</button>
            <button class="ctrl-btn" :class="{ active: focusedNodeId }" @click="clearFocus"><el-icon><Aim /></el-icon> 取消聚焦</button>
          </div>
          <div class="panel-group">
            <div class="group-label">搜索节点</div>
            <el-input
              v-model="searchKeyword"
              placeholder="输入节点名称..."
              clearable
              size="small"
              @input="onSearch"
              @clear="clearSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div v-if="searchResults.length" class="search-results">
              <div
                v-for="r in searchResults"
                :key="r.id"
                class="search-item"
                @click="locateNode(r)"
              >
                <span class="search-dot" :style="{ background: r.color }"></span>
                {{ r.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- 项目信息 -->
        <div class="panel-section" v-if="activeTab === 'course' && currentProject">
          <h4 class="panel-title"><span class="title-bar"></span>项目信息</h4>
          <div class="info-stats">
            <div class="info-stat-box">
              <div class="info-stat-num">{{ currentProject.hours }}</div>
              <div class="info-stat-label">总学时</div>
            </div>
            <div class="info-stat-box">
              <div class="info-stat-num">{{ currentProject.task_count }}</div>
              <div class="info-stat-label">任务数</div>
            </div>
          </div>
          <div v-if="currentProject.certifications" class="info-certs">
            <div v-for="cert in currentProject.certifications" :key="cert" class="cert-tag">
              <el-icon><Medal /></el-icon>
              {{ cert }}
            </div>
          </div>
          <div v-if="currentProject.description" class="info-desc">
            {{ currentProject.description }}
          </div>
        </div>

        <!-- 图谱统计 -->
        <div class="panel-section" v-if="activeTab !== 'standards' && activeTab !== 'requirements' && activeTab !== 'course'">
          <h4 class="panel-title"><span class="title-bar"></span>图谱统计</h4>
          <div class="data-source" v-if="currentProject">
            <span class="source-dot" :style="{ background: hasProjectGraphData ? '#67c23a' : '#e6a23c' }"></span>
            {{ hasProjectGraphData ? '项目专属数据' : '自动生成数据' }}
          </div>
          <div class="graph-stats-list">
            <div class="graph-stat-row" v-for="s in graphStats" :key="s.label">
              <span class="graph-stat-dot" :style="{ background: s.color }"></span>
              <span class="graph-stat-label">{{ s.label }}</span>
              <span class="graph-stat-value">{{ s.count }}</span>
            </div>
          </div>
        </div>

        <!-- 非课程Tab时显示当前项目信息 -->
        <div class="panel-section" v-if="activeTab !== 'course' && currentProject">
          <h4 class="panel-title"><span class="title-bar"></span>项目信息</h4>
          <div class="info-stats">
            <div class="info-stat-box">
              <div class="info-stat-num">{{ currentProject.hours }}</div>
              <div class="info-stat-label">总学时</div>
            </div>
            <div class="info-stat-box">
              <div class="info-stat-num">{{ currentProject.task_count }}</div>
              <div class="info-stat-label">任务数</div>
            </div>
          </div>
          <div v-if="currentProject.certifications" class="info-certs">
            <div v-for="cert in currentProject.certifications" :key="cert" class="cert-tag">
              <el-icon><Medal /></el-icon>
              {{ cert }}
            </div>
          </div>
          <div v-if="currentProject.description" class="info-desc">
            {{ currentProject.description }}
          </div>
        </div>

        <div class="panel-tips">
          <div class="tips-title">操作提示：</div>
          <p>滚轮缩放，拖拽平移，点击节点查看详情</p>
        </div>
      </aside>

      <!-- 中间：图谱主区域 -->
      <main class="center-graph">
        <div class="graph-header">
          <div class="graph-title">
            <span class="title-dot"></span>
            {{ currentTabLabel }}
          </div>
          <div class="graph-stats">
            <span class="stat-item"><span class="stat-num">{{ nodeCount }}</span> 节点</span>
            <span class="stat-sep">·</span>
            <span class="stat-item"><span class="stat-num">{{ linkCount }}</span> 关系</span>
          </div>
        </div>
        <div v-loading="loading" class="graph-container">
          <!-- 图谱类型(力导向图) -->
          <div 
            v-show="activeTab !== 'standards' && activeTab !== 'requirements'" 
            ref="chartRef" 
            class="chart-area"
            @touchstart.passive="handleTouchStart"
            @touchmove.passive="handleTouchMove"
            @touchend="handleTouchEnd"
          ></div>
          <!-- 标准规范表格 -->
          <div v-if="activeTab === 'standards'" class="standards-panel">
            <div class="standards-grid">
              <div v-for="(std, idx) in graphData.standards" :key="idx" class="standard-card">
                <div class="std-header">
                  <span class="std-level-tag" :class="getLevelClass(std.level)">{{ std.level }}</span>
                  <span class="std-type-tag">{{ std.type }}</span>
                </div>
                <div class="std-name">{{ std.name }}</div>
                <div class="std-code">{{ std.code }}</div>
              </div>
            </div>
          </div>
          <!-- 四维要求 -->
          <div v-if="activeTab === 'requirements'" class="requirements-panel">
            <!-- A: 反向设计 -->
            <div class="req-section">
              <h3 class="req-title"><span class="req-tag tag-a">A</span> {{ graphData.four_requirements.requirement_a.title }}</h3>
              <p class="req-desc">{{ graphData.four_requirements.requirement_a.description }}</p>
              <div class="req-table-wrapper">
                <table class="req-table">
                  <thead>
                    <tr>
                      <th>岗位任务</th><th>核心能力</th><th>技能点</th><th>知识点</th><th>课程模块</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(r, i) in graphData.four_requirements.requirement_a.rows" :key="i">
                      <td>{{ r.job_task }}</td><td>{{ r.core_capability }}</td><td>{{ r.skill }}</td><td>{{ r.knowledge }}</td><td>{{ r.course_module }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <!-- B: 岗课赛证 -->
            <div class="req-section">
              <h3 class="req-title"><span class="req-tag tag-b">B</span> {{ graphData.four_requirements.requirement_b.title }}</h3>
              <div class="req-subsection">
                <h4>证书体系</h4>
                <div v-for="(cert, ci) in graphData.four_requirements.requirement_b.certificates" :key="ci" class="cert-block">
                  <div class="cert-name">{{ cert.name }} <span class="cert-issuer">({{ cert.issuer }})</span></div>
                  <div class="cert-levels">
                    <span v-for="(lv, li) in cert.levels" :key="li" class="cert-level-tag">
                      {{ lv.level }}: {{ lv.tasks.join(', ') }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="req-subsection">
                <h4>技能大赛</h4>
                <div v-for="(comp, cpi) in graphData.four_requirements.requirement_b.competitions" :key="cpi" class="comp-block">
                  <span class="comp-name">{{ comp.name }}</span>
                  <el-tag size="small" effect="dark" type="warning">{{ comp.level }}</el-tag>
                  <span class="comp-tasks">{{ comp.tasks.join(', ') }}</span>
                </div>
              </div>
            </div>
            <!-- C: 课程类型 -->
            <div class="req-section">
              <h3 class="req-title"><span class="req-tag tag-c">C</span> {{ graphData.four_requirements.requirement_c.title }}</h3>
              <div class="req-table-wrapper">
                <table class="req-table">
                  <thead>
                    <tr>
                      <th>任务</th><th>学时</th><th>必修/选修</th><th>实践类型</th><th>对应证书</th><th>对应大赛</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(r, i) in graphData.four_requirements.requirement_c.rows" :key="i">
                      <td>{{ r.task }}</td><td>{{ r.hours }}</td><td>{{ r.required }}</td><td>{{ r.practice }}</td><td>{{ r.certificate }}</td><td>{{ r.competition }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <!-- D: 五新融入 -->
            <div class="req-section">
              <h3 class="req-title"><span class="req-tag tag-d">D</span> {{ graphData.four_requirements.requirement_d.title }}</h3>
              <div class="five-new-grid">
                <div v-for="(cat, fi) in graphData.four_requirements.requirement_d.five_new" :key="fi" class="five-new-block">
                  <h4 class="five-new-cat">{{ cat.category }}</h4>
                  <div class="five-new-items">
                    <div v-for="(item, ii) in cat.items" :key="ii" class="five-new-item">
                      <div class="five-new-name">{{ item.name }}</div>
                      <div class="five-new-desc">{{ item.desc }}</div>
                      <div class="five-new-tasks">{{ item.tasks.join(', ') }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 图例 -->
        <div class="graph-legend" v-if="activeTab !== 'standards' && activeTab !== 'requirements'">
          <div class="legend-group">
            <span class="legend-label">节点类型</span>
            <template v-if="activeTab === 'course'">
              <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>项目</span>
              <span class="legend-item"><span class="legend-dot" style="background:#e67e22"></span>子项目</span>
              <span class="legend-item"><span class="legend-dot" style="background:#f39c12"></span>任务</span>
              <span class="legend-item"><span class="legend-dot" style="background:#2ecc71"></span>技能点</span>
              <span class="legend-item"><span class="legend-dot" style="background:#3498db"></span>知识点</span>
              <span class="legend-item"><span class="legend-dot" style="background:#9b59b6"></span>素养/思政</span>
            </template>
            <template v-else-if="activeTab === 'knowledge'">
              <span class="legend-item"><span class="legend-dot" style="background:#3498db"></span>基础知识</span>
              <span class="legend-item"><span class="legend-dot" style="background:#2ecc71"></span>专业知识</span>
              <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>拓展知识</span>
              <span class="legend-item"><span class="legend-dot" style="background:#9b59b6"></span>前沿技术</span>
            </template>
            <template v-else-if="activeTab === 'capability'">
              <span class="legend-item"><span class="legend-dot" style="background:#3498db"></span>初级</span>
              <span class="legend-item"><span class="legend-dot" style="background:#f39c12"></span>中级</span>
              <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>高级</span>
            </template>
            <template v-else-if="activeTab === 'problem'">
              <span class="legend-item"><span class="legend-dot" style="background:#1a3a5c;border:2px solid #409eff"></span>任务中心</span>
              <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>问题</span>
              <span class="legend-item"><span class="legend-dot" style="background:#f39c12"></span>分析</span>
              <span class="legend-item"><span class="legend-dot" style="background:#2ecc71"></span>方案</span>
            </template>
            <template v-else-if="activeTab === 'ideological'">
              <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span>家国情怀</span>
              <span class="legend-item"><span class="legend-dot" style="background:#f39c12"></span>工匠精神</span>
              <span class="legend-item"><span class="legend-dot" style="background:#3498db"></span>法治意识</span>
              <span class="legend-item"><span class="legend-dot" style="background:#2ecc71"></span>创新意识</span>
              <span class="legend-item"><span class="legend-dot" style="background:#9b59b6"></span>团队协作</span>
              <span class="legend-item"><span class="legend-dot" style="background:#1abc9c"></span>生态文明</span>
            </template>
          </div>
        </div>
      </main>

      <!-- 右侧：详情面板(节点点击 或 基础/进阶选择) -->
      <aside class="right-detail" v-if="selectedNode || (activeTab === 'course' && viewMode !== 'all')">
          <!-- 学习路径卡片（基础/进阶） -->
          <template v-if="activeTab === 'course' && viewMode !== 'all' && !selectedNode">
            <div class="detail-header">
              <div class="detail-title-row">
                <span class="detail-type-tag" :style="{ background: viewMode === 'basic' ? '#2ecc71' : '#e74c3c' }">
                  {{ viewMode === 'basic' ? '基础学习' : '进阶提升' }}
                </span>
                <h3>{{ viewMode === 'basic' ? '基础学习路径' : '进阶提升路径' }}</h3>
              </div>
              <button class="detail-close" @click="viewMode = 'all'; initChart()">
                <el-icon><Close /></el-icon>
              </button>
            </div>
            <div class="detail-body">
              <div class="learning-goal">
                <h4>学习目标</h4>
                <p v-if="viewMode === 'basic'">掌握无人机物流运输的基本概念、操作流程和法规要求，具备独立完成简单运输任务的基础能力。</p>
                <p v-else>具备复杂场景下的多机协同调度、精准投放和应急处置能力，能独立完成高难度运输方案的设计与实施。</p>
              </div>
              <div class="learning-path">
                <h4>推荐学习路径</h4>
                <div class="path-steps">
                  <div v-for="(step, si) in (viewMode === 'basic' ? basicPath : advancedPath)" :key="si" class="path-step">
                    <span class="step-num">{{ si + 1 }}</span>
                    <div class="step-content">
                      <div class="step-title">{{ step.title }}</div>
                      <div class="step-desc">{{ step.desc }}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="learning-suggestion">
                <h4>学习建议</h4>
                <p v-if="viewMode === 'basic'">建议先完成任务1-4的基础知识学习，重点理解需求分析、航线规划和包装装载的核心流程，再进行实操练习。</p>
                <p v-else>建议在完成基础学习后，重点突破任务3、5、7中的协同调度和精准投放技术，结合仿真环境反复练习。</p>
              </div>
            </div>
          </template>
          <!-- 节点详情 -->
          <template v-else-if="selectedNode">
            <div class="detail-header">
              <div class="detail-title-row">
                <span class="detail-type-tag" :style="{ background: selectedNodeColor }">{{ selectedNodeTypeName }}</span>
                <h3>{{ selectedNode.name }}</h3>
              </div>
              <button class="detail-close" @click="selectedNode = null">
                <el-icon><Close /></el-icon>
              </button>
            </div>
            <div class="detail-body">
              <!-- 知识图谱节点详情 -->
              <template v-if="activeTab === 'knowledge' && selectedNode.rawData">
                <div class="detail-section">
                  <h4>描述</h4>
                  <p>{{ selectedNode.rawData.description || '暂无描述' }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.category">
                  <h4>所属模块</h4>
                  <el-tag size="small" effect="dark" :type="getKnowledgeCategoryType(selectedNode.rawData.category)">
                    {{ getKnowledgeCategoryName(selectedNode.rawData.category) }}
                  </el-tag>
                </div>
                <div class="detail-section" v-if="getNodeRelatedTasks(selectedNode.rawData.id).length">
                  <h4>关联任务</h4>
                  <div class="detail-tags">
                    <el-tag v-for="t in getNodeRelatedTasks(selectedNode.rawData.id)" :key="t" size="small" effect="plain" type="warning">{{ t }}</el-tag>
                  </div>
                </div>
                <div class="detail-section" v-if="getNodeRelatedKnowledge(selectedNode.rawData.id).length">
                  <h4>关联知识点</h4>
                  <div class="detail-tags">
                    <el-tag v-for="k in getNodeRelatedKnowledge(selectedNode.rawData.id)" :key="k" size="small" effect="plain">{{ k }}</el-tag>
                  </div>
                </div>
              </template>
              <!-- 能力图谱节点详情 -->
              <template v-else-if="activeTab === 'capability' && selectedNode.rawData">
                <div class="detail-section">
                  <h4>能力描述</h4>
                  <p>{{ selectedNode.rawData.description || '暂无描述' }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.level">
                  <h4>能力层级</h4>
                  <el-tag :type="getLevelType(selectedNode.rawData.level)" size="small" effect="dark">{{ selectedNode.rawData.level }}</el-tag>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.support_knowledge">
                  <h4>支撑知识</h4>
                  <p>{{ selectedNode.rawData.support_knowledge }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.evaluation">
                  <h4>评价方式</h4>
                  <p>{{ selectedNode.rawData.evaluation }}</p>
                </div>
              </template>
              <!-- 问题图谱节点详情 -->
              <template v-else-if="activeTab === 'problem' && selectedNode.rawData">
                <div class="detail-section" v-if="selectedNode.rawData.problem">
                  <h4>问题</h4>
                  <p>{{ selectedNode.rawData.problem }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.scenario">
                  <h4>真实场景</h4>
                  <p>{{ selectedNode.rawData.scenario }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.challenge">
                  <h4>挑战</h4>
                  <p>{{ selectedNode.rawData.challenge }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.key_factors">
                  <h4>关键因素</h4>
                  <div class="detail-tags">
                    <el-tag v-for="f in selectedNode.rawData.key_factors" :key="f" size="small" effect="plain">{{ f }}</el-tag>
                  </div>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.method">
                  <h4>分析方法</h4>
                  <p>{{ selectedNode.rawData.method }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.solution">
                  <h4>解决方案</h4>
                  <p>{{ selectedNode.rawData.solution }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.outcome">
                  <h4>预期成果</h4>
                  <p>{{ selectedNode.rawData.outcome }}</p>
                </div>
              </template>
              <!-- 思政图谱节点详情 -->
              <template v-else-if="activeTab === 'ideological' && selectedNode.rawData">
                <div class="detail-section">
                  <h4>思政内容</h4>
                  <p>{{ selectedNode.rawData.content || '暂无' }}</p>
                </div>
                <div class="detail-section">
                  <h4>融入方法</h4>
                  <p>{{ selectedNode.rawData.method || '暂无' }}</p>
                </div>
                <div class="detail-section">
                  <h4>预期成效</h4>
                  <p>{{ selectedNode.rawData.outcome || '暂无' }}</p>
                </div>
                <div class="detail-section" v-if="selectedNode.rawData.task">
                  <h4>对应任务</h4>
                  <el-tag size="small" effect="dark">{{ selectedNode.rawData.task }}</el-tag>
                </div>
              </template>
              <!-- 课程图谱节点详情 -->
              <template v-else-if="activeTab === 'course'">
                <!-- 知识点/技能点详情 -->
                <template v-if="selectedNode.data">
                  <div class="detail-section">
                    <h4>描述</h4>
                    <p>{{ selectedNode.data.desc || selectedNode.data.description || '暂无描述' }}</p>
                  </div>
                  <div class="detail-section" v-if="selectedNode.data.type">
                    <h4>类型</h4>
                    <el-tag size="small" effect="dark">{{ selectedNode.data.type }}</el-tag>
                  </div>
                  <div class="detail-section" v-if="selectedNode.data.level">
                    <h4>难度等级</h4>
                    <el-tag :type="getLevelType(selectedNode.data.level)" size="small" effect="dark">{{ selectedNode.data.level }}</el-tag>
                  </div>
                  <!-- 教学达成状态卡片 -->
                  <div class="detail-card teaching-status-card" v-if="currentNodeTaskId">
                    <div class="card-header">
                      <span class="card-icon">📋</span>
                      <span class="card-title">教学达成状态</span>
                      <el-tag v-if="getTeachingStatusInfo(currentNodeTaskId)" size="small" :color="getTeachingStatusInfo(currentNodeTaskId).color" effect="dark" style="margin-left: auto;">
                        {{ getTeachingStatusInfo(currentNodeTaskId).icon }} {{ getTeachingStatusInfo(currentNodeTaskId).label }}
                      </el-tag>
                    </div>
                    <div class="card-body">
                      <el-radio-group
                        :model-value="getTeachingStatus(currentNodeTaskId) || ''"
                        @change="(val) => onTeachingStatusChange(currentNodeTaskId, val, selectedNode.name)"
                        class="status-radio-group"
                      >
                        <el-radio v-for="opt in TEACHING_STATUS_OPTIONS" :key="opt.value" :value="opt.value" class="status-radio">
                          <span class="radio-icon">{{ opt.icon }}</span>
                          <span :style="{ color: getTeachingStatus(currentNodeTaskId) === opt.value ? opt.color : '' }">{{ opt.label }}</span>
                        </el-radio>
                      </el-radio-group>
                    </div>
                  </div>
                  <!-- 智能体方案评价卡片 -->
                  <div class="detail-card eval-link-card" v-if="getNodeSectionLinks(selectedNode.data).length">
                    <div class="card-header">
                      <span class="card-icon">🤖</span>
                      <span class="card-title">智能体方案评价</span>
                    </div>
                    <div class="card-body">
                      <div v-for="link in getNodeSectionLinks(selectedNode.data)" :key="link.sectionId" class="eval-link-item" @click="goToEvaluation(link.sectionId)">
                        <div class="eval-link-name">{{ link.sectionName }}</div>
                        <el-icon class="eval-link-arrow"><ArrowRight /></el-icon>
                      </div>
                    </div>
                  </div>
                </template>
                <!-- 任务详情 -->
                <template v-else-if="selectedNode.type === 'task'">
                  <div class="detail-section">
                    <h4>所属子项目</h4>
                    <p>{{ selectedNode.parentName || '-' }}</p>
                  </div>
                  <div class="detail-section">
                    <h4>包含知识点/技能点</h4>
                    <div class="detail-tags">
                      <el-tag v-for="pt in selectedNode.points" :key="pt.id" size="default" :type="pt.type === 'knowledge' ? 'info' : 'success'" effect="plain">
                        {{ pt.name }}
                      </el-tag>
                    </div>
                  </div>
                </template>
                <!-- 子项目详情 -->
                <template v-else-if="selectedNode.type === 'subProject'">
                  <div class="detail-section">
                    <h4>包含任务</h4>
                    <div class="detail-task-list">
                      <div v-for="t in selectedNode.tasks" :key="t.id" class="detail-task-item">
                        <span class="task-dot"></span>
                        {{ t.name }}
                      </div>
                    </div>
                  </div>
                  <div class="detail-section">
                    <h4>学时</h4>
                    <p>{{ selectedNode.hours || '-' }}学时</p>
                  </div>
                </template>
                <!-- 根节点 -->
                <template v-else-if="selectedNode.type === 'root'">
                  <div class="detail-section">
                    <h4>项目信息</h4>
                    <p>{{ currentProject?.description || '暂无描述' }}</p>
                  </div>
                </template>
              </template>
            </div>
          </template>
        </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowLeft, ArrowRight, ZoomIn, ZoomOut, RefreshRight, Search, Medal, Close,
  Connection, TrendCharts, QuestionFilled, Reading, Document, List, Share, Aim
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import graphData from '@/data/four-graph-data.json'
import { fetchProjects, fetchProject, fetchTeachingStatus, updateTeachingStatus } from '@/api/courseGraph'
import { getProjectGraphs } from '@/utils/graphGenerator'

const router = useRouter()
const route = useRoute()

// === Tab定义 ===
const tabs = [
  { key: 'knowledge', label: '知识图谱', icon: Connection },
  { key: 'capability', label: '能力图谱', icon: TrendCharts },
  { key: 'problem', label: '问题图谱', icon: QuestionFilled },
  { key: 'ideological', label: '思政图谱', icon: Reading },
  { key: 'standards', label: '标准规范', icon: Document },
  { key: 'requirements', label: '四维要求', icon: List },
  { key: 'course', label: '课程图谱', icon: Share }
]
const activeTab = ref('course')

const currentTabLabel = computed(() => {
  const t = tabs.find(t => t.key === activeTab.value)
  return t ? t.label : ''
})

// === 项目数据 ===
const projectList = ref([])
const selectedProjectId = ref(null)
const currentProject = ref(null)
const loading = ref(false)
const viewMode = ref('all')
const projectGraphs = ref(null) // 当前项目的四图谱（自动生成或数据库自带）

const currentProjectName = computed(() => {
  if (currentProject.value) return currentProject.value.name
  const p = projectList.value.find(p => p.project_id === selectedProjectId.value)
  return p?.name || graphData.course_info.project_name
})

// === 图谱 ===
const chartRef = ref(null)
let chart = null
const searchKeyword = ref('')
const searchResults = ref([])
const selectedNode = ref(null)
const nodeCount = ref(0)

// 聚焦节点状态
const focusedNodeId = ref(null)

// 当前选中小节点所属的任务ID
const currentNodeTaskId = computed(() => {
  if (!selectedNode.value?.data) return null
  const task = findParentTask(selectedNode.value.data)
  return task ? task.id : null
})
const linkCount = ref(0)

// --- 教学达成状态 ---
const teachingStatusMap = ref({}) // { nodeId: { status, node_name } }

// 任务→教学智评环节映射（目前只有任务8有环节配置）
const TASK_SECTION_MAP = {
  8: [
    { sectionId: 'section1', sectionName: '环节一：运输方案汇报与知识深化' },
    { sectionId: 'section2', sectionName: '环节二：应急推演与工单处置' },
    { sectionId: 'section3', sectionName: '环节三：飞行演练与裁判评分' },
  ],
}

const TEACHING_STATUS_OPTIONS = [
  { value: 'achieved', label: '已达成', color: '#67c23a', icon: '✅' },
  { value: 'partial', label: '部分达成，需课后强化', color: '#f59c0b', icon: '⚠️' },
  { value: 'not_achieved', label: '未达成', color: '#e74c3c', icon: '❌' },
]

function getTaskSectionLinks(taskId) {
  return TASK_SECTION_MAP[taskId] || []
}

function getNodeSectionLinks(nodeData) {
  const task = findParentTask(nodeData)
  return task ? (TASK_SECTION_MAP[task.id] || []) : []
}

function findParentTask(nodeData) {
  if (!nodeData || !currentProject.value?.sub_projects) return null
  for (const sp of currentProject.value.sub_projects) {
    for (const task of (sp.tasks || [])) {
      for (const pt of (task.points || [])) {
        if (pt.id === nodeData.id) return task
      }
    }
  }
  return null
}

function getTeachingStatus(nodeId) {
  return teachingStatusMap.value[nodeId]?.status || null
}

function getTeachingStatusInfo(nodeId) {
  const s = teachingStatusMap.value[nodeId]?.status
  return TEACHING_STATUS_OPTIONS.find(o => o.value === s) || null
}

async function onTeachingStatusChange(taskId, status, taskName) {
  if (!currentProject.value) return
  try {
    await updateTeachingStatus({
      project_id: currentProject.value.project_id,
      node_id: String(taskId),
      node_name: taskName,
      status,
    })
    teachingStatusMap.value[String(taskId)] = { status, node_name: taskName }
    // 更新图谱节点颜色
    updateGraphNodeColor(taskId, status)
  } catch (e) {
    console.error('保存教学状态失败', e)
  }
}

function updateGraphNodeColor(taskId, status) {
  if (!chart) return
  const opt = chart.getOption()
  if (!opt.series?.[0]?.data) return
  const nodes = opt.series[0].data
  const statusColor = TEACHING_STATUS_OPTIONS.find(o => o.value === status)?.color
  const defaultColor = '#f39c12'
  // 找到对应的任务节点并更新颜色
  nodes.forEach((n, i) => {
    if (n.id === String(taskId) || n.id === taskId) {
      chart.dispatchAction({ type: 'downplay', dataIndex: i })
      chart.setOption({ series: [{ data: nodes.map((nd, j) => {
        if (j === i) {
          return { ...nd, itemStyle: { ...nd.itemStyle, color: statusColor || defaultColor, borderColor: statusColor || defaultColor, borderWidth: 3 } }
        }
        return nd
      }) }] })
    }
  })
}

async function loadTeachingStatus(projectId) {
  try {
    const res = await fetchTeachingStatus(projectId)
    teachingStatusMap.value = res.data || {}
  } catch {
    teachingStatusMap.value = {}
  }
}

function goToEvaluation(sectionId) {
  const projectId = currentProject.value?.project_id || 'P5'
  const taskId = selectedNode.value?.taskId || 8
  router.push({ path: '/evaluation', query: { project: projectId, task: taskId, section: sectionId, tab: 'ai' } })
}

// === 节点聚焦功能（点击节点后高亮关联节点，淡化无关节点）===
function focusOnNode(nodeId) {
  if (!chart) return
  
  focusedNodeId.value = nodeId
  
  const option = chart.getOption()
  if (!option.series?.[0]?.data) return
  
  const nodes = option.series[0].data
  const links = option.series[0].links || []
  
  // 找到聚焦节点及其关联节点
  const focusedNode = nodes.find(n => n.id === nodeId)
  if (!focusedNode) return
  
  // 获取所有关联节点（通过连线）
  const relatedNodeIds = new Set([nodeId])
  links.forEach(link => {
    if (link.source === nodeId || link.target === nodeId) {
      relatedNodeIds.add(link.source)
      relatedNodeIds.add(link.target)
    }
  })
  
  // 更新节点：关联节点高亮，无关节点淡化
  chart.setOption({
    series: [{
      data: nodes.map(n => {
        const isRelated = relatedNodeIds.has(n.id)
        const isFocused = n.id === nodeId
        
        // 使用原始大小（如果已保存），否则使用当前大小作为基准（只保存一次）
        const baseSize = n._originalSymbolSize || n.symbolSize
        
        return {
          ...n,
          _originalSymbolSize: n._originalSymbolSize || n.symbolSize, // 保存原始大小，避免累积放大
          _originalItemStyle: n._originalItemStyle || { ...n.itemStyle }, // 保存原始样式
          _originalLabel: n._originalLabel || { ...n.label }, // 保存原始标签
          itemStyle: {
            ...(n._originalItemStyle || n.itemStyle),
            opacity: isRelated ? 1 : 0.25,
            shadowBlur: isFocused ? 25 : (isRelated ? 18 : 2),
            shadowColor: isFocused ? (n._originalItemStyle?.color || '#409eff') + 'cc' : (isRelated ? (n._originalItemStyle?.color || '#409eff') + '88' : 'transparent'),
            borderWidth: isFocused ? 4 : (isRelated ? 3 : 1),
            borderColor: isFocused ? '#fff' : (isRelated ? (n._originalItemStyle?.color || '#409eff') : 'rgba(255,255,255,0.2)'),
            brightness: isRelated ? 1.1 : 0.9
          },
          label: {
            ...(n._originalLabel || n.label),
            show: true,
            opacity: isRelated ? 1 : 0.45,
            fontSize: isFocused ? ((n._originalLabel?.fontSize || 12) * 1.3) : (isRelated ? ((n._originalLabel?.fontSize || 12) * 1.15) : (n._originalLabel?.fontSize || 12)),
            fontWeight: isRelated ? 'bold' : (n._originalLabel?.fontWeight || 'normal')
          },
          symbolSize: isFocused ? baseSize * 1.35 : (isRelated ? baseSize * 1.15 : Math.max(baseSize * 0.75, 8))
        }
      }),
      links: links.map(l => {
        const isRelatedLink = relatedNodeIds.has(l.source) && relatedNodeIds.has(l.target)
        const baseWidth = l._originalLineStyle?.width || l.lineStyle?.width || 2
        
        return {
          ...l,
          _originalLineStyle: l._originalLineStyle || { ...l.lineStyle }, // 保存原始连线样式
          lineStyle: {
            ...(l._originalLineStyle || l.lineStyle),
            opacity: isRelatedLink ? 0.85 : 0.15,
            width: isRelatedLink ? baseWidth * 1.8 : baseWidth * 0.6,
            color: isRelatedLink ? '#409eff' : (l._originalLineStyle?.color),
            shadowBlur: isRelatedLink ? 10 : 0,
            shadowColor: isRelatedLink ? '#409eff88' : 'transparent'
          }
        }
      })
    }]
  })
}

function clearFocus() {
  if (!chart) return
  
  focusedNodeId.value = null
  
  const option = chart.getOption()
  if (!option.series?.[0]?.data) return
  
  const nodes = option.series[0].data
  const links = option.series[0].links || []
  
  // 恢复所有节点和连线的原始状态
  chart.setOption({
    series: [{
      data: nodes.map(n => ({
        ...n,
        itemStyle: n._originalItemStyle || n.itemStyle,
        label: n._originalLabel || n.label,
        symbolSize: n._originalSymbolSize || n.symbolSize
      })),
      links: links.map(l => ({
        ...l,
        lineStyle: l._originalLineStyle || l.lineStyle
      }))
    }]
  })
}

// 学习路径数据
const basicPath = [
  { title: '任务1 需求分析', desc: '学习应急物流需求分析与飞行计划编制' },
  { title: '任务2 航线规划', desc: '掌握单点航线设计与空域申请流程' },
  { title: '任务4 包装载', desc: '学习物资包装、重量配平与安全检查' },
  { title: '任务6 飞行模拟', desc: '在仿真环境中进行飞行训练与特情处置' }
]
const advancedPath = [
  { title: '任务3 网络调度', desc: '掌握多站点协同调度与智能运力配置' },
  { title: '任务5 集群装调', desc: '完成多机集群系统安装、配置与联调' },
  { title: '任务7 飞行实操', desc: '真机操控与应急物资精准投放' },
  { title: '任务8 综合演练', desc: '组织综合演练、方案优化与汇报答辩' }
]

// === 知识图谱颜色映射 ===
const knowledgeCategoryColors = { KC: '#3498db', KP: '#2ecc71', KE: '#e74c3c', KF: '#9b59b6' }
const knowledgeCategoryNames = { KC: '基础知识模块', KP: '专业知识模块', KE: '拓展知识模块', KF: '前沿技术模块' }

// === 思政图谱颜色 ===
const ideologicalDimColors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c']

function getKnowledgeCategoryType(cat) {
  const map = { KC: 'info', KP: 'success', KE: 'danger', KF: 'warning' }
  return map[cat] || 'info'
}
function getKnowledgeCategoryName(cat) {
  return knowledgeCategoryNames[cat] || cat
}
function getLevelType(level) {
  const map = { '初级': 'success', '中级': 'primary', '高级': 'danger' }
  return map[level] || 'info'
}
function getLevelClass(level) {
  const map = { '国家': 'level-national', '行业': 'level-industry' }
  return map[level] || ''
}

// 查找包含某知识点的任务
function getNodeRelatedTasks(nodeId) {
  if (!currentProject.value?.sub_projects) return []
  const tasks = []
  currentProject.value.sub_projects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      if ((task.points || []).some(p => p.id === nodeId)) {
        tasks.push(task.name)
      }
    })
  })
  return tasks
}

// 查找同任务内的其他知识点
function getNodeRelatedKnowledge(nodeId) {
  if (!currentProject.value?.sub_projects) return []
  const related = new Set()
  currentProject.value.sub_projects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      const pts = task.points || []
      if (pts.some(p => p.id === nodeId)) {
        pts.forEach(p => {
          if (p.id !== nodeId && p.type === 'knowledge') related.add(p.name)
        })
      }
    })
  })
  return [...related].slice(0, 8)
}

// 图谱统计信息
const graphStats = computed(() => {
  if (!currentProject.value?.sub_projects) return []
  const subProjects = currentProject.value.sub_projects
  if (activeTab.value === 'knowledge') {
    const cats = { KC: 0, KP: 0, KE: 0, KF: 0 }
    const kg = projectGraphs.value?.knowledge_graph
    if (kg?.nodes) {
      kg.nodes.forEach(n => { if (cats[n.category] !== undefined) cats[n.category]++ })
    }
    return [
      { label: '基础知识', count: cats.KC, color: '#3498db' },
      { label: '专业知识', count: cats.KP, color: '#2ecc71' },
      { label: '拓展知识', count: cats.KE, color: '#e74c3c' },
      { label: '前沿技术', count: cats.KF, color: '#9b59b6' },
    ]
  }
  if (activeTab.value === 'capability') {
    const cards = projectGraphs.value?.capability_graph?.template3_capability_cards?.cards || []
    const levels = { '初级': 0, '中级': 0, '高级': 0 }
    cards.forEach(c => { if (levels[c.level] !== undefined) levels[c.level]++ })
    return [
      { label: '初级能力', count: levels['初级'], color: '#3498db' },
      { label: '中级能力', count: levels['中级'], color: '#f39c12' },
      { label: '高级能力', count: levels['高级'], color: '#e74c3c' },
    ]
  }
  if (activeTab.value === 'problem') {
    const pg = projectGraphs.value?.problem_graph
    return [
      { label: '问题数', count: pg?.levels?.[0]?.problems?.length || 0, color: '#e74c3c' },
      { label: '分析数', count: pg?.levels?.[1]?.analyses?.length || 0, color: '#f39c12' },
      { label: '方案数', count: pg?.levels?.[2]?.solutions?.length || 0, color: '#2ecc71' },
    ]
  }
  if (activeTab.value === 'ideological') {
    const ig = projectGraphs.value?.ideological_graph
    return (ig?.dimensions || []).map((d, i) => ({
      label: d.dimension,
      count: d.elements?.length || 0,
      color: ideologicalDimColors[i],
    }))
  }
  return []
})

// 当前项目是否有自带的四图谱数据
const hasProjectGraphData = computed(() => {
  if (!currentProject.value) return false
  const graphKey = { knowledge: 'knowledge_graph', capability: 'capability_graph', problem: 'problem_graph', ideological: 'ideological_graph' }
  return !!currentProject.value[graphKey[activeTab.value]]
})

// === 数据加载 ===
async function loadProjects() {
  try {
    const res = await fetchProjects()
    projectList.value = res.data || []
    const queryProject = route.query.project
    if (queryProject && projectList.value.find(p => p.project_id === queryProject)) {
      selectProject(queryProject)
    } else if (projectList.value.length && !selectedProjectId.value) {
      selectProject(projectList.value[0].project_id)
    }
  } catch (e) {
    console.error('加载项目列表失败', e)
  }
}

async function selectProject(projectId) {
  selectedProjectId.value = projectId
  selectedNode.value = null
  loading.value = true
  try {
    const res = await fetchProject(projectId)
    currentProject.value = res.data
    // 生成或获取四图谱数据
    projectGraphs.value = getProjectGraphs(res.data)
    // 加载教学达成状态
    await loadTeachingStatus(projectId)
    nextTick(() => initChart())
  } catch (e) {
    console.error('加载项目数据失败', e)
  } finally {
    loading.value = false
  }
}

// === Tab切换 ===
function switchTab(key) {
  activeTab.value = key
  selectedNode.value = null
  viewMode.value = 'all'
  searchKeyword.value = ''
  searchResults.value = []
  nextTick(() => initChart())
}

function handleViewChange() {
  nextTick(() => {
    initChart()
    chart?.resize()
  })
}

// === 图谱初始化（分发到各tab） ===
function initChart() {
  if (activeTab.value === 'standards' || activeTab.value === 'requirements') {
    // 表格/卡片模式，不需要ECharts
    if (chart) { chart.dispose(); chart = null }
    return
  }
  if (!chartRef.value) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)

  switch (activeTab.value) {
    case 'knowledge': initKnowledgeChart(); break
    case 'capability': initCapabilityChart(); break
    case 'problem': initProblemChart(); break
    case 'ideological': initIdeologicalChart(); break
    case 'course': initCourseChart(); break
  }
}

// === 知识图谱 ===
function initKnowledgeChart() {
  const kg = projectGraphs.value?.knowledge_graph || graphData.knowledge_graph
  const nodes = []
  const links = []

  // 按分类分组
  const catGroups = {}
  kg.nodes.forEach(n => {
    if (!catGroups[n.category]) catGroups[n.category] = []
    catGroups[n.category].push(n)
  })

  // 创建4个分类中心节点（大）
  kg.categories.forEach((cat, ci) => {
    nodes.push({
      id: `cat-${cat.id}`, name: cat.name, category: ci,
      symbolSize: 40,
      itemStyle: { color: cat.color, borderColor: '#fff', borderWidth: 2, shadowBlur: 12, shadowColor: cat.color + '88' },
      label: { fontSize: 14, color: '#fff', show: true, fontWeight: 'bold' },
      _type: 'categoryCenter'
    })
  })

  // 知识点小节点连接到分类中心
  kg.nodes.forEach(n => {
    const catIdx = kg.categories.findIndex(c => c.id === n.category)
    nodes.push({
      id: n.id, name: n.name, category: catIdx,
      symbolSize: 26,
      itemStyle: { color: knowledgeCategoryColors[n.category] || '#999', opacity: 0.85 },
      label: { fontSize: 13, color: '#ddd', show: true, position: 'right', distance: 2 },
      _raw: n
    })
    // 连接到分类中心
    links.push({
      source: `cat-${n.category}`, target: n.id,
      lineStyle: { color: knowledgeCategoryColors[n.category] || '#4a6a8a', width: 2.5, opacity: 0.4, curveness: 0.15 }
    })
  })

  // 保留原有的跨节点关系连线
  kg.links.forEach(l => {
    if (nodes.find(n => n.id === l.source) && nodes.find(n => n.id === l.target)) {
      links.push({
        source: l.source, target: l.target,
        label: { show: true, formatter: l.relation, fontSize: 11, color: '#718096' },
        lineStyle: { color: '#4a6a8a', width: 2.5, curveness: 0.2, type: 'dashed' }
      })
    }
  })

  nodeCount.value = nodes.length
  linkCount.value = links.length

  chart.setOption(getForceOption(
    nodes, links,
    kg.categories.map(c => ({ name: c.name, itemStyle: { color: c.color } })),
    { repulsion: 250, edgeLength: [50, 140], gravity: 0.12 }
  ))

  chart.on('click', (params) => {
    if (params.dataType !== 'node') { selectedNode.value = null; return }
    const d = params.data
    selectedNode.value = { name: d.name, rawData: d._raw || {} }
    // 点击节点时聚焦
    if (params.data.id) {
      focusOnNode(params.data.id)
    }
  })
}

// === 能力图谱 ===
function initCapabilityChart() {
  const capData = projectGraphs.value?.capability_graph || graphData.capability_graph
  const cards = capData.template3_capability_cards.cards
  const levelColors = { '初级': '#3498db', '中级': '#f39c12', '高级': '#e74c3c' }
  const nodes = []
  const links = []

  // 创建3个等级中心节点（大）
  const levels = ['初级', '中级', '高级']
  levels.forEach((lvl, li) => {
    nodes.push({
      id: `level-${lvl}`, name: lvl, category: li,
      symbolSize: 40,
      itemStyle: { color: levelColors[lvl], borderColor: '#fff', borderWidth: 2, shadowBlur: 12, shadowColor: levelColors[lvl] + '88' },
      label: { fontSize: 14, color: '#fff', show: true, fontWeight: 'bold' },
      _type: 'levelCenter'
    })
  })

  // 能力卡片小节点连接到等级中心
  cards.forEach(c => {
    nodes.push({
      id: c.id, name: c.name,
      category: levels.indexOf(c.level),
      symbolSize: 26,
      itemStyle: { color: levelColors[c.level] || '#999', opacity: 0.85 },
      label: { fontSize: 13, color: '#ddd', show: true, position: 'right', distance: 2 },
      _raw: c
    })
    links.push({
      source: `level-${c.level}`, target: c.id,
      lineStyle: { color: levelColors[c.level] || '#4a6a8a', width: 2.5, opacity: 0.4, curveness: 0.15 }
    })
  })

  nodeCount.value = nodes.length
  linkCount.value = links.length

  chart.setOption(getForceOption(
    nodes, links,
    levels.map(l => ({ name: l, itemStyle: { color: levelColors[l] } })),
    { repulsion: 250, edgeLength: [50, 140], gravity: 0.12 }
  ))

  chart.on('click', (params) => {
    if (params.dataType !== 'node') { selectedNode.value = null; return }
    selectedNode.value = { name: params.data.name, rawData: params.data._raw || {} }
    // 点击节点时聚焦
    if (params.data.id) {
      focusOnNode(params.data.id)
    }
  })
}

// === 问题图谱 ===
function initProblemChart() {
  const pg = projectGraphs.value?.problem_graph || graphData.problem_graph
  const nodes = []
  const links = []
  const categories = [
    { name: '任务中心', itemStyle: { color: '#1a3a5c' } },
    { name: '问题导向层', itemStyle: { color: '#e74c3c' } },
    { name: '问题分析层', itemStyle: { color: '#f39c12' } },
    { name: '问题解决层', itemStyle: { color: '#2ecc71' } }
  ]

  const problems = pg.levels[0].problems || []
  const analyses = pg.levels[1].analyses || []
  const solutions = pg.levels[2].solutions || []

  problems.forEach((p, i) => {
    const taskId = `task-${i}`
    // 中心任务节点
    nodes.push({
      id: taskId, name: p.task, category: 0,
      symbolSize: 42,
      itemStyle: { color: '#1a3a5c', borderColor: '#409eff', borderWidth: 2, shadowBlur: 12, shadowColor: 'rgba(64,158,255,0.4)' },
      label: { fontSize: 14, color: '#fff', show: true, fontWeight: 'bold' },
      _type: 'taskCenter', _raw: p
    })

    // 问题节点（红色）
    const problemId = `prob-${i}`
    nodes.push({
      id: problemId, name: `问题`, category: 1,
      symbolSize: 24,
      itemStyle: { color: '#e74c3c', shadowBlur: 6, shadowColor: 'rgba(231,76,60,0.3)' },
      label: { fontSize: 13, color: '#fff', show: true },
      _raw: p, _problemName: p.problem
    })
    links.push({
      source: taskId, target: problemId,
      lineStyle: { color: '#e74c3c', width: 2.5, curveness: 0.2, opacity: 0.6 }
    })

    // 分析节点（橙色）
    if (analyses[i]) {
      const analysisId = `ana-${i}`
      nodes.push({
        id: analysisId, name: `分析`, category: 2,
        symbolSize: 22,
        itemStyle: { color: '#f39c12', shadowBlur: 5, shadowColor: 'rgba(243,156,18,0.3)' },
        label: { fontSize: 13, color: '#fff', show: true },
        _raw: analyses[i]
      })
      links.push({
        source: taskId, target: analysisId,
        lineStyle: { color: '#f39c12', width: 2.5, curveness: 0.2, opacity: 0.5 }
      })
    }

    // 方案节点（绿色）
    if (solutions[i]) {
      const solutionId = `sol-${i}`
      nodes.push({
        id: solutionId, name: `方案`, category: 3,
        symbolSize: 22,
        itemStyle: { color: '#2ecc71', shadowBlur: 5, shadowColor: 'rgba(46,204,113,0.3)' },
        label: { fontSize: 13, color: '#fff', show: true },
        _raw: solutions[i]
      })
      links.push({
        source: taskId, target: solutionId,
        lineStyle: { color: '#2ecc71', width: 2.5, curveness: 0.2, opacity: 0.5 }
      })
    }
  })

  nodeCount.value = nodes.length
  linkCount.value = links.length

  chart.setOption(getForceOption(
    nodes, links, categories,
    { repulsion: 500, edgeLength: [80, 180], gravity: 0.1 }
  ))

  chart.on('click', (params) => {
    if (params.dataType !== 'node') { selectedNode.value = null; return }
    const d = params.data
    if (d._type === 'taskCenter') {
      selectedNode.value = { name: d.name, rawData: d._raw }
    } else {
      selectedNode.value = { name: d._problemName || d.name, rawData: d._raw }
    }
    // 点击节点时聚焦
    if (params.data.id) {
      focusOnNode(params.data.id)
    }
  })
}

// === 思政图谱 ===
function initIdeologicalChart() {
  const ig = projectGraphs.value?.ideological_graph || graphData.ideological_graph
  const nodes = []
  const links = []
  const categories = ig.dimensions.map((d, i) => ({
    name: d.dimension,
    itemStyle: { color: ideologicalDimColors[i] }
  }))

  // 中心主题节点
  nodes.push({
    id: 'center', name: '课程思政', category: -1,
    symbolSize: 48,
    itemStyle: { color: '#1a3a5c', borderColor: '#409eff', borderWidth: 2, shadowBlur: 15, shadowColor: 'rgba(64,158,255,0.4)' },
    label: { fontSize: 16, color: '#fff', show: true, fontWeight: 'bold' }
  })

  // 维度节点（中等大小）+ 元素节点（小）
  ig.dimensions.forEach((dim, di) => {
    const dimId = `DIM-${di}`
    nodes.push({
      id: dimId, name: dim.dimension, category: di,
      symbolSize: 36,
      itemStyle: { color: ideologicalDimColors[di], shadowBlur: 8, shadowColor: ideologicalDimColors[di] + '66' },
      label: { fontSize: 14, color: '#fff', show: true, fontWeight: 'bold' }
    })
    links.push({
      source: 'center', target: dimId,
      lineStyle: { color: ideologicalDimColors[di], width: 3, opacity: 0.5 }
    })

    dim.elements.forEach(el => {
      nodes.push({
        id: el.id, name: el.id, category: di,
        symbolSize: 20,
        itemStyle: { color: ideologicalDimColors[di], opacity: 0.8 },
        label: { fontSize: 12, color: '#ddd', show: true, position: 'right', distance: 2 },
        _raw: el
      })
      links.push({
        source: dimId, target: el.id,
        lineStyle: { color: ideologicalDimColors[di], width: 2.5, opacity: 0.35, curveness: 0.2 }
      })
    })
  })

  nodeCount.value = nodes.length
  linkCount.value = links.length

  chart.setOption(getForceOption(
    nodes, links, categories,
    { repulsion: 250, edgeLength: [50, 140], gravity: 0.12 }
  ))

  chart.on('click', (params) => {
    if (params.dataType !== 'node') { selectedNode.value = null; return }
    const d = params.data
    selectedNode.value = { name: d._raw ? `${d._raw.content?.substring(0, 20)}...` : d.name, rawData: d._raw || { content: d.name, method: '', outcome: '' } }
    // 点击节点时聚焦
    if (params.data.id) {
      focusOnNode(params.data.id)
    }
  })
}

// === 课程图谱（从API数据） ===
function initCourseChart() {
  if (!currentProject.value?.sub_projects) return

  const mode = viewMode.value
  const subProjects = currentProject.value.sub_projects
  const nodes = []
  const links = []

  // 根节点
  nodes.push({
    id: 'root',
    name: currentProject.value.name,
    category: 0,
    symbolSize: 60,
    itemStyle: { color: '#e74c3c', shadowBlur: 25, shadowColor: 'rgba(231,76,60,0.5)' },
    label: { fontSize: 16, fontWeight: 'bold', color: '#fff', show: true },
    _type: 'root',
    _data: currentProject.value
  })

  subProjects.forEach(sp => {
    const spId = `sp-${sp.id || sp.name}`
    const hasBasic = (sp.tasks || []).some(t => t.type === 'basic')
    const hasAdvanced = (sp.tasks || []).some(t => t.type === 'advanced')
    const visible = mode === 'all' || (mode === 'basic' && hasBasic) || (mode === 'advanced' && hasAdvanced)
    const opacity = visible ? 1 : 0.15

    nodes.push({
      id: spId,
      name: sp.name,
      category: 1,
      symbolSize: 40,
      itemStyle: { color: '#e67e22', opacity, shadowBlur: visible ? 10 : 0, shadowColor: visible ? 'rgba(230,126,34,0.4)' : 'transparent' },
      label: { fontSize: 14, fontWeight: 'bold', color: opacity === 1 ? '#fff' : 'rgba(255,255,255,0.3)', show: true },
      _type: 'subProject',
      _data: sp,
      _tasks: sp.tasks || []
    })
    links.push({ source: 'root', target: spId, lineStyle: { color: '#95a5a6', opacity, width: 3 } })

    ;(sp.tasks || []).forEach(task => {
      const tId = `t-${task.id || task.name}`
      const isBasicTask = task.type === 'basic'
      const taskVisible = mode === 'all' || (mode === 'basic' && isBasicTask) || (mode === 'advanced' && !isBasicTask)
      const taskOpacity = taskVisible ? 1 : 0.15

      // 根据教学状态设置节点颜色
      const taskStatus = getTeachingStatus(String(task.id))
      const taskStatusColor = taskStatus ? TEACHING_STATUS_OPTIONS.find(o => o.value === taskStatus)?.color : null
      const taskBaseColor = taskStatusColor || '#f39c12'

      nodes.push({
        id: tId,
        name: task.name,
        category: 2,
        symbolSize: 30,
        itemStyle: { color: taskBaseColor, borderColor: taskStatusColor ? taskStatusColor : 'transparent', borderWidth: taskStatusColor ? 2 : 0, opacity: taskOpacity, shadowBlur: taskVisible ? 6 : 0, shadowColor: taskVisible ? 'rgba(243,156,18,0.3)' : 'transparent' },
        label: { fontSize: 13, color: taskOpacity === 1 ? '#fff' : 'rgba(255,255,255,0.3)', show: true },
        _type: 'task',
        _taskId: task.id,
        _parentName: sp.name,
        _points: task.points || []
      })
      links.push({ source: spId, target: tId, lineStyle: { color: '#95a5a6', opacity: taskOpacity, width: 2.5 } })

      ;(task.points || []).forEach(pt => {
        const ptVisible = taskVisible
        const ptOpacity = ptVisible ? 1 : 0.15
        const ptColor = typeColors[pt.type] || '#999'
        const catIdx = pt.type === 'knowledge' ? 4 : pt.type === 'skill' ? 3 : 5

        nodes.push({
          id: pt.id,
          name: pt.name,
          category: catIdx,
          symbolSize: 18,
          itemStyle: { color: ptColor, opacity: ptOpacity },
          label: { fontSize: 12, color: '#ddd', position: 'right', distance: 3, show: ptOpacity === 1 },
          _type: pt.type,
          _data: pt
        })
        links.push({ source: tId, target: pt.id, lineStyle: { color: ptColor, opacity: ptOpacity * 0.5, width: 2 } })
      })
    })
  })

  // 跨项目关联
  subProjects.forEach(sp => {
    ;(sp.tasks || []).forEach(task => {
      ;(task.points || []).forEach(pt => {
        if (pt.appliesTo) {
          pt.appliesTo.forEach(targetId => {
            const targetNode = nodes.find(n => n.id === targetId)
            if (targetNode) {
              links.push({
                source: pt.id, target: targetId,
                lineStyle: { color: '#3498db', type: 'dashed', opacity: 0.35, width: 2.5 }
              })
            }
          })
        }
      })
    })
  })

  nodeCount.value = nodes.length
  linkCount.value = links.length

  chart.setOption(getForceOption(
    nodes, links,
    [
      { name: '项目', itemStyle: { color: '#e74c3c' } },
      { name: '子项目', itemStyle: { color: '#e67e22' } },
      { name: '任务', itemStyle: { color: '#f39c12' } },
      { name: '技能点', itemStyle: { color: '#2ecc71' } },
      { name: '知识点', itemStyle: { color: '#3498db' } },
      { name: '素养/思政', itemStyle: { color: '#9b59b6' } }
    ],
    { repulsion: mode === 'all' ? 250 : 320, edgeLength: mode === 'all' ? [50, 160] : [70, 200] }
  ))

  chart.on('click', (params) => {
    if (params.dataType !== 'node') { selectedNode.value = null; return }
    const d = params.data
    selectedNode.value = {
      name: d.name,
      type: d._type,
      data: d._data,
      taskId: d._taskId,
      parentName: d._parentName,
      points: d._points,
      tasks: d._tasks,
      hours: d._data?.hours
    }
    // 点击节点时聚焦
    if (params.data.id) {
      focusOnNode(params.data.id)
    }
  })
}

const typeColors = {
  root: '#e74c3c', subProject: '#e67e22', task: '#f39c12',
  knowledge: '#3498db', skill: '#2ecc71', '素养': '#9b59b6', '思政': '#9b59b6'
}

const selectedNodeColor = computed(() => {
  if (!selectedNode.value) return '#409eff'
  if (activeTab.value === 'knowledge') {
    const cat = selectedNode.value.rawData?.category
    return knowledgeCategoryColors[cat] || '#409eff'
  }
  if (activeTab.value === 'capability') {
    const lvl = selectedNode.value.rawData?.level
    const map = { '初级': '#3498db', '中级': '#f39c12', '高级': '#e74c3c' }
    return map[lvl] || '#409eff'
  }
  if (activeTab.value === 'problem') return '#e74c3c'
  if (activeTab.value === 'ideological') return '#9b59b6'
  // course tab
  const d = selectedNode.value
  if (d.type === 'root') return typeColors.root
  if (d.type === 'subProject') return typeColors.subProject
  if (d.type === 'task') return typeColors.task
  if (d.data) return typeColors[d.data.type] || '#999'
  return '#409eff'
})

const selectedNodeTypeName = computed(() => {
  if (!selectedNode.value) return ''
  if (activeTab.value === 'knowledge') return '知识点'
  if (activeTab.value === 'capability') return '能力项'
  if (activeTab.value === 'problem') {
    const d = selectedNode.value
    if (d.type === 'taskCenter') return '任务'
    if (d.rawData?.problem) return '问题'
    if (d.rawData?.key_factors) return '分析'
    if (d.rawData?.solution) return '方案'
    return '问题'
  }
  if (activeTab.value === 'ideological') return '思政点'
  // course
  const map = { root: '项目', subProject: '子项目', task: '任务' }
  const d = selectedNode.value
  if (map[d.type]) return map[d.type]
  if (d.data?.type === 'knowledge') return '知识点'
  if (d.data?.type === 'skill') return '技能点'
  return '节点'
})

// === 通用力导向图配置 ===
function getForceOption(nodes, links, categories, forceConfig) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(8,20,40,0.95)',
      borderColor: 'rgba(64,158,255,0.35)',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      extraCssText: 'border-radius:10px;backdrop-filter:blur(8px);box-shadow:0 8px 32px rgba(0,0,0,0.5);max-width:320px;',
      formatter: (params) => {
        if (params.dataType === 'node') {
          const d = params.data
          const color = d.itemStyle?.color || '#409eff'
          let desc = ''
          if (d._raw) {
            desc = d._raw.description || d._raw.content || d._raw.problem || ''
            if (desc.length > 80) desc = desc.substring(0, 80) + '...'
          }
          let extra = ''
          if (d._raw?.level) extra += `<br/><span style="color:#718096;font-size:11px">层级: ${d._raw.level}</span>`
          if (d._raw?.evaluation) extra += `<br/><span style="color:#718096;font-size:11px">评价: ${d._raw.evaluation}</span>`
          if (d._raw?.method && activeTab.value === 'problem') extra += `<br/><span style="color:#718096;font-size:11px">方法: ${d._raw.method}</span>`
          if (d._raw?.scenario) extra += `<br/><span style="color:#718096;font-size:11px">场景: ${d._raw.scenario.substring(0, 50)}</span>`
          return `<b style="color:${color}">${d.name}</b>${extra}${desc ? `<br/><span style="color:#c0c8d4;font-size:11px;line-height:1.5">${desc}</span>` : ''}`
        }
        if (params.dataType === 'edge') {
          const label = params.data?.label?.formatter
          return label ? `<b>${label}</b>` : ''
        }
        return ''
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      force: {
        repulsion: forceConfig?.repulsion || 300,
        edgeLength: forceConfig?.edgeLength || [60, 160],
        gravity: forceConfig?.gravity || 0.15,
        friction: 0.6
      },
      categories: categories || [],
      data: nodes,
      links: links,
      lineStyle: { opacity: 0.6, width: 2.5, curveness: 0.1 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3 }
      },
      label: { position: 'right', distance: 5, textShadowColor: 'rgba(0,0,0,0.4)', textShadowBlur: 3 }
    }]
  }
}

// === 图谱操作 ===
function zoomIn() {
  if (!chart) return
  const opt = chart.getOption()
  const s = opt.series?.[0]
  if (!s) return
  const curZoom = s.zoom || 1
  const curCenter = s.center || ['50%', '50%']
  chart.setOption({ series: [{ zoom: curZoom * 1.3, center: curCenter }] })
}

function zoomOut() {
  if (!chart) return
  const opt = chart.getOption()
  const s = opt.series?.[0]
  if (!s) return
  const curZoom = s.zoom || 1
  const curCenter = s.center || ['50%', '50%']
  chart.setOption({ series: [{ zoom: curZoom * 0.77, center: curCenter }] })
}

function resetView() {
  if (!chart) return
  chart.setOption({ series: [{ zoom: 1, center: ['50%', '50%'] }] })
  selectedNode.value = null
}

// === 搜索 ===
function onSearch() {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) { searchResults.value = []; return }
  const opt = chart?.getOption()
  if (!opt?.series?.[0]) return
  const nodes = opt.series[0].data || []
  searchResults.value = nodes
    .filter(n => n.name?.toLowerCase().includes(kw))
    .slice(0, 10)
    .map(n => ({ id: n.id, name: n.name, color: n.itemStyle?.color || '#999' }))
}

function clearSearch() {
  searchResults.value = []
  searchKeyword.value = ''
}

function locateNode(node) {
  chart?.dispatchAction({ type: 'highlight', seriesIndex: 0, name: node.name })
  setTimeout(() => {
    chart?.dispatchAction({ type: 'downplay', seriesIndex: 0, name: node.name })
  }, 2000)
}

// === 生命周期 ===
const goBack = () => router.push('/agent/teaching-graph')

onMounted(() => {
  loadProjects()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  chart?.resize()
}

// 右侧面板打开/关闭时，延迟resize图谱以适应新的容器尺寸
watch([selectedNode, viewMode], () => {
  nextTick(() => {
    setTimeout(() => chart?.resize(), 350)
  })
})

// === 触屏手势支持 ===
let touchStartX = 0
let touchStartY = 0
let touchStartDistance = 0
let isPinching = false

function handleTouchStart(e) {
  if (e.touches.length === 2) {
    isPinching = true
    const touch1 = e.touches[0]
    const touch2 = e.touches[1]
    touchStartDistance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY)
  } else if (e.touches.length === 1) {
    isPinching = false
    touchStartX = e.touches[0].clientX
    touchStartY = e.touches[0].clientY
  }
}

function handleTouchMove(e) {
  if (!chart) return
  
  if (e.touches.length === 2 && isPinching) {
    e.preventDefault()
    const touch1 = e.touches[0]
    const touch2 = e.touches[1]
    const currentDistance = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY)
    const scale = currentDistance / touchStartDistance
    
    if (scale > 1.05) {
      zoomIn()
      touchStartDistance = currentDistance
    } else if (scale < 0.95) {
      zoomOut()
      touchStartDistance = currentDistance
    }
  } else if (e.touches.length === 1 && !isPinching) {
    const deltaX = e.touches[0].clientX - touchStartX
    const deltaY = e.touches[0].clientY - touchStartY
    
    if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
      const dispatchAction = chart.getOption().series?.[0]?.type === 'graph' ? 'drag' : ''
      if (dispatchAction) {
        chart.dispatchAction({
          type: 'drag',
          dx: deltaX,
          dy: deltaY
        })
      }
      touchStartX = e.touches[0].clientX
      touchStartY = e.touches[0].clientY
    }
  }
}

function handleTouchEnd() {
  isPinching = false
}
</script>

<style scoped>
.graph-view-page {
  min-height: 100vh;
  background: #0a1628;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
}

/* 顶部导航 */
.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 52px;
  background: linear-gradient(90deg, #0d2137 0%, #1a3a5c 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.3);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.header-right :deep(.el-select) {
  --el-select-input-color: rgba(13, 33, 55, 0.8);
}
.header-right :deep(.el-input__wrapper) {
  background: rgba(13, 33, 55, 0.8);
  border-color: rgba(64, 158, 255, 0.3);
  box-shadow: none;
  color: #e2e8f0;
}
.header-right :deep(.el-input__inner) {
  color: #e2e8f0;
}
.header-right :deep(.el-input__wrapper:hover) {
  border-color: rgba(64, 158, 255, 0.5);
}
.back-btn { color: #c0c8d4 !important; font-size: 13px; }
.back-btn:hover { color: #409eff !important; }
.header-divider { width: 1px; height: 18px; background: rgba(255,255,255,0.15); }
.header-course { font-size: 15px; display: flex; align-items: center; gap: 6px; }
.course-name { color: #c0c8d4; }
.course-sep { color: rgba(255,255,255,0.3); }
.project-name { color: #fff; font-weight: 600; }

.header-right :deep(.el-radio-button__inner) {
  background: rgba(13, 33, 55, 0.8);
  border-color: rgba(64, 158, 255, 0.2);
  color: #c0c8d4;
  font-size: 13px;
  padding: 6px 18px;
}
.header-right :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #409eff, #337ecc);
  border-color: #409eff;
  color: #fff;
  box-shadow: -1px 0 0 0 #409eff;
}

/* 7个Tab导航 */
.main-tabs {
  display: flex;
  gap: 4px;
  padding: 8px 20px;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.8) 0%, rgba(13, 33, 55, 0.5) 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.15);
  overflow-x: auto;
  flex-shrink: 0;
}
.main-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 13px;
  color: #c0c8d4;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  border: 1px solid transparent;
}
.main-tab:hover {
  color: #409eff;
  background: rgba(64, 158, 255, 0.08);
}
.main-tab.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.25), rgba(64, 158, 255, 0.1));
  border-color: rgba(64, 158, 255, 0.4);
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.15);
}
.tab-label { font-weight: 500; }

/* 主体布局 */
.view-body {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  flex: 1;
  min-height: 0;
}

/* 左侧面板 */
.left-panel {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}
.panel-section {
  background: rgba(13, 33, 55, 0.6);
  border: 1px solid rgba(64, 158, 255, 0.12);
  border-radius: 12px;
  padding: 16px;
}
.panel-title {
  font-size: 14px;
  margin: 0 0 12px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-bar {
  width: 3px;
  height: 14px;
  border-radius: 2px;
  background: #409eff;
}
.panel-group { margin-bottom: 14px; }
.group-label { font-size: 12px; color: #c0c8d4; margin-bottom: 8px; }
.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  margin: 0 6px 6px 0;
  border-radius: 6px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  background: rgba(13, 33, 55, 0.8);
  color: #c0c8d4;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}
.ctrl-btn:hover { border-color: #409eff; color: #409eff; background: rgba(64, 158, 255, 0.1); }

.search-results {
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}
.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.search-item:hover { background: rgba(64, 158, 255, 0.1); }
.search-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.info-stats { display: flex; gap: 10px; margin-bottom: 12px; }
.info-stat-box {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid rgba(64, 158, 255, 0.15);
}
.info-stat-num {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.info-stat-label { font-size: 11px; color: #c0c8d4; margin-top: 2px; }
.info-certs { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.cert-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.15);
  font-size: 12px;
  color: #c0c8d4;
}
.cert-tag .el-icon { color: #409eff; }
.info-desc { font-size: 12px; color: #c0c8d4; line-height: 1.6; }

.graph-stats-list { display: flex; flex-direction: column; gap: 8px; }
.graph-stat-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.graph-stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.graph-stat-label { flex: 1; color: #c0c8d4; }
.graph-stat-value { color: #409eff; font-weight: 700; }
.data-source { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #718096; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); }
.source-dot { width: 6px; height: 6px; border-radius: 50%; }

.panel-tips {
  padding: 12px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(64, 158, 255, 0.15);
}
.tips-title { font-size: 12px; color: #409eff; margin-bottom: 4px; font-weight: 600; }
.panel-tips p { font-size: 11px; color: #c0c8d4; margin: 0; line-height: 1.5; }

/* 中间图谱 */
.center-graph {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.graph-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.graph-title {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #409eff;
}
.graph-stats { font-size: 12px; color: #c0c8d4; }
.stat-num { color: #409eff; font-weight: 700; }
.stat-sep { margin: 0 6px; }

.graph-container {
  flex: 1;
  background: rgba(13, 33, 55, 0.5);
  border: 1px solid rgba(64, 158, 255, 0.15);
  border-radius: 12px;
  min-height: 400px;
  overflow: auto;
}
.chart-area { width: 100%; height: 100%; min-height: 400px; }

.graph-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 10px 16px;
  margin-top: 10px;
  background: rgba(13, 33, 55, 0.6);
  border: 1px solid rgba(64, 158, 255, 0.12);
  border-radius: 8px;
}
.legend-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.legend-label { font-size: 12px; color: #c0c8d4; font-weight: 600; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #c0c8d4; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* 标准规范面板 */
.standards-panel {
  padding: 20px;
  min-height: 400px;
}
.standards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}
.standard-card {
  background: rgba(13, 33, 55, 0.7);
  border: 1px solid rgba(64, 158, 255, 0.15);
  border-radius: 10px;
  padding: 14px;
  transition: all 0.3s;
}
.standard-card:hover {
  border-color: rgba(64, 158, 255, 0.4);
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.1);
}
.std-header { display: flex; gap: 8px; margin-bottom: 8px; }
.std-level-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
  font-weight: 600;
  background: #409eff;
}
.std-level-tag.level-national { background: #e74c3c; }
.std-level-tag.level-industry { background: #f39c12; }
.std-type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #c0c8d4;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.2);
}
.std-name { font-size: 13px; color: #e2e8f0; font-weight: 500; margin-bottom: 4px; }
.std-code { font-size: 11px; color: #c0c8d4; }

/* 四维要求面板 */
.requirements-panel {
  padding: 20px;
  min-height: 400px;
  overflow-y: auto;
  max-height: calc(100vh - 250px);
}
.req-section {
  margin-bottom: 28px;
  background: rgba(13, 33, 55, 0.5);
  border: 1px solid rgba(64, 158, 255, 0.12);
  border-radius: 12px;
  padding: 20px;
}
.req-title {
  font-size: 16px;
  color: #fff;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.req-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}
.tag-a { background: #e74c3c; }
.tag-b { background: #f39c12; }
.tag-c { background: #3498db; }
.tag-d { background: #2ecc71; }
.req-desc { font-size: 13px; color: #c0c8d4; margin: 0 0 14px; }
.req-table-wrapper { overflow-x: auto; }
.req-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.req-table th {
  background: rgba(64, 158, 255, 0.1);
  color: #c0c8d4;
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid rgba(64, 158, 255, 0.2);
  white-space: nowrap;
  font-weight: 600;
}
.req-table td {
  padding: 9px 12px;
  color: #c0c8d4;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  line-height: 1.5;
}
.req-table tr:hover td {
  background: rgba(64, 158, 255, 0.05);
}
.req-subsection { margin-top: 16px; }
.req-subsection h4 {
  font-size: 14px;
  color: #e2e8f0;
  margin: 0 0 10px;
}
.cert-block {
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 8px;
}
.cert-name { font-size: 13px; color: #e2e8f0; font-weight: 500; margin-bottom: 6px; }
.cert-issuer { color: #c0c8d4; font-weight: 400; }
.cert-levels { display: flex; flex-wrap: wrap; gap: 6px; }
.cert-level-tag {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #c0c8d4;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.15);
}
.comp-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 6px;
}
.comp-name { font-size: 13px; color: #e2e8f0; }
.comp-tasks { font-size: 11px; color: #c0c8d4; }

/* 五新融入 */
.five-new-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}
.five-new-block {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 14px;
  border: 1px solid rgba(64, 158, 255, 0.1);
}
.five-new-cat {
  font-size: 14px;
  color: #409eff;
  margin: 0 0 10px;
  font-weight: 600;
}
.five-new-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.five-new-item {
  padding: 8px 10px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid #409eff;
}
.five-new-name { font-size: 13px; color: #e2e8f0; font-weight: 500; }
.five-new-desc { font-size: 11px; color: #c0c8d4; margin-top: 2px; }
.five-new-tasks { font-size: 10px; color: #6b7b8d; margin-top: 2px; }

/* 右侧详情面板 */
.right-detail {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(135deg, rgba(13, 33, 55, 0.9), rgba(26, 58, 92, 0.7));
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 22px 24px;
  border-bottom: 1px solid rgba(64, 158, 255, 0.15);
}
.detail-title-row { display: flex; flex-direction: column; gap: 10px; }
.detail-type-tag {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 5px;
  font-size: 15px;
  color: #fff;
  font-weight: 600;
}
.detail-header h3 { margin: 0; font-size: 22px; color: #fff; line-height: 1.4; font-weight: 600; }
.detail-close {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  background: rgba(13, 33, 55, 0.8);
  color: #c0c8d4;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
  font-size: 18px;
}
.detail-close:hover { border-color: #f56c6c; color: #f56c6c; background: rgba(245, 108, 108, 0.1); }
.detail-body {
  flex: 1;
  padding: 22px 24px;
  overflow-y: auto;
}
.detail-section { margin-bottom: 22px; }
.detail-section h4 {
  font-size: 18px;
  color: #c0c8d4;
  margin: 0 0 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-weight: 500;
}
.detail-section p {
  font-size: 18px;
  color: #c0c8d4;
  line-height: 1.7;
  margin: 0;
}
.detail-tags { display: flex; flex-wrap: wrap; gap: 10px; }
.detail-task-list { display: flex; flex-direction: column; gap: 10px; }
.detail-task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  color: #c0c8d4;
}
.task-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #f39c12;
  flex-shrink: 0;
}

/* 任务详情卡片 */
.detail-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
.detail-card .card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-card .card-icon {
  font-size: 26px;
}
.detail-card .card-title {
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
}
.detail-card .card-body {
  padding: 0;
}

/* 教学达成状态 */
.status-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.status-radio {
  display: flex;
  align-items: center;
  height: 50px;
  width: 100%;
  padding: 0 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s;
  box-sizing: border-box;
}
.status-radio:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
}
:deep(.status-radio .el-radio__input) {
  margin-right: 10px;
}
:deep(.status-radio .el-radio__label) {
  color: #c0c8d4;
  font-size: 17px;
  padding-left: 2px;
  width: 100%;
}
:deep(.detail-tags .el-tag) {
  font-size: 16px;
  padding: 6px 12px;
  height: auto;
  line-height: 1.4;
}
:deep(.status-radio.el-radio) {
  margin-right: 0;
  width: 100%;
}
.radio-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 智能体评价链接 */
.eval-link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  margin-bottom: 10px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.15);
  cursor: pointer;
  transition: all 0.2s;
}
.eval-link-item:hover {
  background: rgba(64, 158, 255, 0.15);
  border-color: rgba(64, 158, 255, 0.3);
}
.eval-link-name {
  font-size: 18px;
  color: #a0c4ff;
  flex: 1;
  font-weight: 500;
}
.eval-link-arrow {
  color: #409eff;
  font-size: 20px;
  margin-left: 10px;
}

/* 学习路径卡片 */
.learning-goal,
.learning-path,
.learning-suggestion { margin-bottom: 24px; }
.learning-goal h4,
.learning-path h4,
.learning-suggestion h4 {
  font-size: 18px;
  color: #c0c8d4;
  margin: 0 0 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-weight: 500;
}
.learning-goal p,
.learning-suggestion p {
  font-size: 18px;
  color: #c0c8d4;
  line-height: 1.7;
  margin: 0;
}
.path-steps { display: flex; flex-direction: column; gap: 14px; }
.path-step {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  border-left: 4px solid #409eff;
}
.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}
.step-content { flex: 1; }
.step-title { font-size: 18px; color: #e2e8f0; font-weight: 600; }
.step-desc { font-size: 16px; color: #c0c8d4; margin-top: 4px; }

/* 右侧面板过渡 */
.right-detail {
  animation: slideIn 0.3s ease;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
