<template>
  <div class="packing-agent-page">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-left">
        <el-button @click="goBack" type="primary" plain size="small">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <h1 class="page-title">无人机物资装箱AI评价智能体</h1>
        <el-tag type="info" size="small">v1.0</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="showHelp" type="info" plain size="small">
          <el-icon><QuestionFilled /></el-icon>
          使用帮助
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧面板 -->
      <aside class="left-panel">
        <!-- 基础信息 -->
        <div class="panel-card">
          <div class="card-header">
            <span class="card-title">基础信息</span>
          </div>
          <div class="card-body">
            <el-form :model="basicInfo" label-position="top" size="small">
              <el-form-item label="学生姓名">
                <el-input v-model="basicInfo.studentName" placeholder="请输入姓名" />
              </el-form-item>
              <el-form-item label="班级">
                <el-input v-model="basicInfo.className" placeholder="请输入班级" />
              </el-form-item>
              <el-form-item label="实训日期">
                <el-date-picker v-model="basicInfo.trainingDate" type="date" placeholder="选择日期" style="width: 100%" />
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 运输箱参数 -->
        <div class="panel-card">
          <div class="card-header">
            <span class="card-title">运输箱参数 (mm)</span>
          </div>
          <div class="card-body">
            <el-form :model="boxParams" label-position="top" size="small">
              <el-form-item label="尺寸 (长×宽×高)">
                <div class="box-dimensions">
                  <el-input-number v-model="boxParams.length" :min="100" :max="2000" :step="50" controls-position="right" />
                  <span class="dimension-separator">×</span>
                  <el-input-number v-model="boxParams.width" :min="100" :max="2000" :step="50" controls-position="right" />
                  <span class="dimension-separator">×</span>
                  <el-input-number v-model="boxParams.height" :min="100" :max="2000" :step="50" controls-position="right" />
                </div>
              </el-form-item>
              <el-form-item label="空箱重量 (kg)">
                <el-input-number v-model="boxParams.emptyWeight" :min="0" :max="50" :step="0.5" controls-position="right" style="width: 100%" />
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 评分概览 -->
        <div class="panel-card" v-if="evaluationResult">
          <div class="card-header">
            <span class="card-title">评分概览</span>
          </div>
          <div class="card-body score-overview">
            <div class="total-score">
              <div class="score-ring" :style="{ '--score-color': getGradeColor(evaluationResult.totalScore) }">
                <span class="score-value">{{ evaluationResult.totalScore }}</span>
                <span class="score-label">总分</span>
              </div>
              <el-tag :color="getGradeColor(evaluationResult.totalScore)" effect="dark" size="large">
                {{ getGradeLabel(evaluationResult.totalScore) }}
              </el-tag>
            </div>
            <div ref="radarChartRef" class="radar-chart"></div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="panel-card">
          <div class="card-header">
            <span class="card-title">快速操作</span>
          </div>
          <div class="card-body">
            <div class="action-buttons">
              <el-button @click="resetScheme" type="warning" plain>
                <el-icon><RefreshLeft /></el-icon>
                <span>重置方案</span>
              </el-button>
              <el-button @click="exportReport" type="success" plain :disabled="!evaluationResult">
                <el-icon><Download /></el-icon>
                <span>导出报告</span>
              </el-button>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="right-content">
        <el-tabs v-model="activeTab" class="main-tabs">
          <!-- Tab 1: 工单选择 -->
          <el-tab-pane label="工单选择" name="workorder">
            <div class="tab-content">
              <div class="section-header">
                <h3>选择实训工单</h3>
                <p class="section-desc">选择预置的应急救援工单模板，自动填充物资清单和运输约束</p>
              </div>

              <div class="workorder-grid">
                <div
                  v-for="template in workOrderTemplates"
                  :key="template.id"
                  class="workorder-card"
                  :class="{ active: selectedTemplate?.id === template.id }"
                  @click="selectTemplate(template)"
                >
                  <div class="wo-header">
                    <span class="wo-icon">{{ template.icon }}</span>
                    <div class="wo-info">
                      <h4>{{ template.name }}</h4>
                      <el-tag :type="getDifficultyType(template.difficulty)" size="small">
                        {{ getDifficultyLabel(template.difficulty) }}
                      </el-tag>
                    </div>
                  </div>
                  <p class="wo-desc">{{ template.description }}</p>
                  <div class="wo-constraints">
                    <span><strong>最大载重:</strong> {{ template.constraints.maxWeight }}kg</span>
                    <span><strong>飞行时间:</strong> {{ template.constraints.flightTime }}分钟</span>
                    <span><strong>投放方式:</strong> {{ template.constraints.landingType }}</span>
                  </div>
                  <div class="wo-requirements">
                    <div v-for="(req, idx) in template.requirements.slice(0, 2)" :key="idx" class="req-item">
                      <el-icon><CircleCheck /></el-icon>
                      <span>{{ req }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 工单详情 -->
              <div v-if="selectedTemplate" class="workorder-detail">
                <div class="detail-header">
                  <h3>{{ selectedTemplate.icon }} {{ selectedTemplate.name }} - 任务要求</h3>
                </div>
                <div class="detail-body">
                  <div class="requirements-list">
                    <div v-for="(req, idx) in selectedTemplate.requirements" :key="idx" class="req-item">
                      <el-icon><CircleCheck /></el-icon>
                      <span>{{ req }}</span>
                    </div>
                  </div>
                  <div class="constraints-info">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="最大载重">{{ selectedTemplate.constraints.maxWeight }}kg</el-descriptions-item>
                      <el-descriptions-item label="飞行时间">{{ selectedTemplate.constraints.flightTime }}分钟</el-descriptions-item>
                      <el-descriptions-item label="天气条件">{{ selectedTemplate.constraints.weatherCondition }}</el-descriptions-item>
                      <el-descriptions-item label="投放方式">{{ selectedTemplate.constraints.landingType }}</el-descriptions-item>
                      <el-descriptions-item v-if="selectedTemplate.constraints.temperatureRange" label="温度要求">
                        {{ selectedTemplate.constraints.temperatureRange }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 物资清单 -->
          <el-tab-pane label="物资清单" name="materials">
            <div class="tab-content">
              <div class="section-header">
                <h3>物资清单</h3>
                <div class="header-actions">
                  <el-button @click="addMaterial" type="primary" size="small">
                    <el-icon><Plus /></el-icon>
                    添加物资
                  </el-button>
                </div>
              </div>

              <el-table :data="materials" border class="materials-table">
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column prop="name" label="物资名称" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.name" size="small" placeholder="物资名称" />
                  </template>
                </el-table-column>
                <el-table-column label="重量(kg)" width="100" align="center">
                  <template #default="{ row }">
                    <el-input-number v-model="row.weight" :min="0" :step="0.1" size="small" controls-position="right" style="width: 80px" />
                  </template>
                </el-table-column>
                <el-table-column label="尺寸(mm)" width="220">
                  <template #default="{ row }">
                    <div class="size-inputs">
                      <el-input-number v-model="row.length" :min="0" :step="10" size="small" controls-position="right" placeholder="长" style="width: 65px" />
                      <span>×</span>
                      <el-input-number v-model="row.width" :min="0" :step="10" size="small" controls-position="right" placeholder="宽" style="width: 65px" />
                      <span>×</span>
                      <el-input-number v-model="row.height" :min="0" :step="10" size="small" controls-position="right" placeholder="高" style="width: 65px" />
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="数量" width="80" align="center">
                  <template #default="{ row }">
                    <el-input-number v-model="row.quantity" :min="1" size="small" controls-position="right" style="width: 60px" />
                  </template>
                </el-table-column>
                <el-table-column label="层级" width="100" align="center">
                  <template #default="{ row }">
                    <el-select v-model="row.layer" size="small" style="width: 80px">
                      <el-option v-for="opt in layerOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="位置" width="100" align="center">
                  <template #default="{ row }">
                    <el-select v-model="row.position" size="small" style="width: 80px">
                      <el-option v-for="opt in positionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="缓冲材料" width="100" align="center">
                  <template #default="{ row }">
                    <el-select v-model="row.bufferMaterial" size="small" style="width: 80px">
                      <el-option v-for="(val, key) in bufferMaterials" :key="key" :label="val.name" :value="key" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="属性" width="100">
                  <template #default="{ row }">
                    <div class="property-tags">
                      <el-checkbox v-model="row.isEmergency" label="应急" size="small" />
                      <el-checkbox v-model="row.isFragile" label="易碎" size="small" />
                      <el-checkbox v-model="row.isLiquid" label="液体" size="small" />
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80" align="center" fixed="right">
                  <template #default="{ $index }">
                    <el-button @click="removeMaterial($index)" type="danger" size="small" link>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <div class="materials-summary">
                <span>物资总数: {{ materials.length }} 种</span>
                <span>总重量: {{ totalMaterialWeight.toFixed(1) }} kg</span>
                <span>应急物资: {{ emergencyCount }} 种</span>
                <span>易碎物品: {{ fragileCount }} 种</span>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 3: 装箱方案 -->
          <el-tab-pane label="装箱方案" name="scheme">
            <div class="tab-content">
              <!-- 四角称重 -->
              <div class="section-card">
                <div class="section-header">
                  <h3>四角称重数据</h3>
                  <p class="section-desc">在运输箱四角放置载重称，记录四个角的重量</p>
                </div>
                <div class="corner-weight-section">
                  <div class="weight-diagram">
                    <div class="box-top-view">
                      <div class="box-label">运输箱俯视图</div>
                      <div class="corner-grid">
                        <div class="corner-item front-left">
                          <span class="corner-label">W1 (左前)</span>
                          <el-input-number v-model="cornerWeights.w1" :min="0" :step="0.1" size="small" controls-position="right" />
                        </div>
                        <div class="corner-item front-right">
                          <span class="corner-label">W2 (右前)</span>
                          <el-input-number v-model="cornerWeights.w2" :min="0" :step="0.1" size="small" controls-position="right" />
                        </div>
                        <div class="corner-item back-left">
                          <span class="corner-label">W3 (左后)</span>
                          <el-input-number v-model="cornerWeights.w3" :min="0" :step="0.1" size="small" controls-position="right" />
                        </div>
                        <div class="corner-item back-right">
                          <span class="corner-label">W4 (右后)</span>
                          <el-input-number v-model="cornerWeights.w4" :min="0" :step="0.1" size="small" controls-position="right" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="weight-results">
                    <div class="result-item">
                      <span class="result-label">总重量 W总</span>
                      <span class="result-value">{{ totalWeight.toFixed(1) }} kg</span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">前后偏移 ΔX</span>
                      <span class="result-value" :class="{ warning: Math.abs(gravityResult.deltaX) > 50 }">
                        {{ gravityResult.deltaX.toFixed(1) }} mm
                      </span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">左右偏移 ΔY</span>
                      <span class="result-value" :class="{ warning: Math.abs(gravityResult.deltaY) > 50 }">
                        {{ gravityResult.deltaY.toFixed(1) }} mm
                      </span>
                    </div>
                    <div class="result-item highlight">
                      <span class="result-label">综合偏移 ΔS</span>
                      <span class="result-value" :class="{ danger: gravityResult.deltaS > 50, success: gravityResult.deltaS <= 50 }">
                        {{ gravityResult.deltaS.toFixed(1) }} mm
                      </span>
                    </div>
                    <div class="result-status">
                      <el-tag :type="gravityResult.deltaS <= 50 ? 'success' : 'danger'" size="large">
                        {{ gravityResult.deltaS <= 50 ? '✓ 重心合格' : '✗ 重心偏移超标' }}
                      </el-tag>
                    </div>
                  </div>
                </div>
                <div class="gravity-formula">
                  <div class="formula-item">W总 = W1 + W2 + W3 + W4 = {{ cornerWeights.w1 }} + {{ cornerWeights.w2 }} + {{ cornerWeights.w3 }} + {{ cornerWeights.w4 }} = {{ totalWeight.toFixed(1) }}kg</div>
                  <div class="formula-item">ΔX = [(W3+W4)-(W1+W2)] × L / (2×W总) = [({{ cornerWeights.w3 }}+{{ cornerWeights.w4 }})-({{ cornerWeights.w1 }}+{{ cornerWeights.w2 }})] × {{ boxParams.length }} / (2×{{ totalWeight.toFixed(1) }}) = {{ gravityResult.deltaX.toFixed(1) }}mm</div>
                  <div class="formula-item">ΔY = [(W2+W4)-(W1+W3)] × W / (2×W总) = [({{ cornerWeights.w2 }}+{{ cornerWeights.w4 }})-({{ cornerWeights.w1 }}+{{ cornerWeights.w3 }})] × {{ boxParams.width }} / (2×{{ totalWeight.toFixed(1) }}) = {{ gravityResult.deltaY.toFixed(1) }}mm</div>
                  <div class="formula-item">ΔS = √(ΔX² + ΔY²) = √({{ gravityResult.deltaX.toFixed(1) }}² + {{ gravityResult.deltaY.toFixed(1) }}²) = {{ gravityResult.deltaS.toFixed(1) }}mm</div>
                </div>
              </div>

              <!-- 装箱布局描述 -->
              <div class="section-card">
                <div class="section-header">
                  <h3>装箱布局描述</h3>
                </div>
                <el-form :model="layoutDescription" label-position="top">
                  <el-form-item label="底层摆放说明">
                    <el-input v-model="layoutDescription.layer1" type="textarea" :rows="2" placeholder="描述底层物资的摆放方式，如：底层放置沙袋和急救药品，重物居中..." />
                  </el-form-item>
                  <el-form-item label="中层摆放说明">
                    <el-input v-model="layoutDescription.layer2" type="textarea" :rows="2" placeholder="描述中层物资的摆放方式..." />
                  </el-form-item>
                  <el-form-item label="上层摆放说明">
                    <el-input v-model="layoutDescription.layer3" type="textarea" :rows="2" placeholder="描述上层物资的摆放方式，应急物资应放在最上层..." />
                  </el-form-item>
                  <el-form-item label="空隙处理">
                    <el-input v-model="layoutDescription.gaps" type="textarea" :rows="2" placeholder="描述如何填充空隙，如：使用泡沫填充所有空隙..." />
                  </el-form-item>
                  <el-form-item label="防水处理">
                    <el-input v-model="layoutDescription.waterproof" type="textarea" :rows="2" placeholder="描述防水措施，如：所有物资使用防水袋包裹..." />
                  </el-form-item>
                </el-form>
              </div>

              <!-- 包装方式 -->
              <div class="section-card">
                <div class="section-header">
                  <h3>包装方式</h3>
                </div>
                <el-form :model="packaging" label-position="top">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="缓冲材料">
                        <el-select v-model="packaging.bufferMaterial" style="width: 100%">
                          <el-option v-for="(val, key) in bufferMaterials" :key="key" :label="val.name" :value="key" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="防水方式">
                        <el-select v-model="packaging.waterproofMethod" style="width: 100%">
                          <el-option v-for="(val, key) in waterproofMethods" :key="key" :label="val.name" :value="key" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="密封方式">
                        <el-select v-model="packaging.sealingMethod" style="width: 100%">
                          <el-option v-for="(val, key) in sealingMethods" :key="key" :label="val.name" :value="key" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="液体容器">
                        <el-select v-model="packaging.liquidContainer" style="width: 100%">
                          <el-option label="独立密封" value="sealed" />
                          <el-option label="普通容器" value="normal" />
                          <el-option label="无" value="none" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
              </div>

              <!-- 提交按钮 -->
              <div class="submit-section">
                <el-button @click="runEvaluation" type="primary" size="large" :disabled="!canEvaluate">
                  <el-icon><VideoPlay /></el-icon>
                  开始评价
                </el-button>
                <span v-if="!canEvaluate" class="submit-hint">请先填写四角称重数据</span>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 4: 评价结果 -->
          <el-tab-pane label="评价结果" name="evaluation">
            <div class="tab-content" v-if="evaluationResult">
              <!-- 总分展示 -->
              <div class="total-score-header">
                <div class="score-display">
                  <span class="big-score" :style="{ color: getGradeColor(evaluationResult.totalScore) }">
                    {{ evaluationResult.totalScore }}
                  </span>
                  <span class="score-unit">分</span>
                </div>
                <el-tag :color="getGradeColor(evaluationResult.totalScore)" effect="dark" size="large" class="grade-tag">
                  {{ getGradeLabel(evaluationResult.totalScore) }}
                </el-tag>
              </div>

              <!-- 场景专项提示 -->
              <div v-if="selectedTemplate" class="scenario-tips-card">
                <div class="tips-header">
                  <span class="tips-icon">{{ selectedTemplate.icon }}</span>
                  <span class="tips-title">{{ selectedTemplate.scenarioName }} - 场景专项提示</span>
                </div>
                <div class="tips-body">
                  <div v-for="(tip, idx) in selectedTemplate.scenarioTips.packingTips" :key="idx" class="tip-item">
                    <el-icon><InfoFilled /></el-icon>
                    <span>{{ tip }}</span>
                  </div>
                </div>
              </div>

              <!-- 各维度评分 -->
              <div class="dimensions-grid">
                <div v-for="(dim, key) in evaluationResult.dimensions" :key="key" class="dimension-card">
                  <div class="dim-header">
                    <span class="dim-name">{{ dim.dimension }}</span>
                    <span class="dim-score">
                      <span class="current">{{ dim.score }}</span>
                      <span class="separator">/</span>
                      <span class="max">{{ dim.maxScore }}</span>
                    </span>
                  </div>
                  <div class="dim-progress">
                    <el-progress
                      :percentage="(dim.score / dim.maxScore) * 100"
                      :color="getDimensionColor(dim.score, dim.maxScore)"
                      :show-text="false"
                      :stroke-width="8"
                    />
                  </div>
                  <div class="dim-details">
                    <div v-for="(detail, idx) in dim.details" :key="idx" class="detail-item" :class="{ failed: !detail.passed }">
                      <div class="detail-main">
                        <el-icon v-if="detail.passed" class="status-icon success"><CircleCheck /></el-icon>
                        <el-icon v-else class="status-icon danger"><CircleClose /></el-icon>
                        <span class="detail-name">{{ detail.item }}</span>
                        <span v-if="detail.value" class="detail-value">{{ detail.value }}</span>
                        <span v-if="detail.standard" class="detail-standard">(标准: {{ detail.standard }})</span>
                      </div>
                      <div v-if="detail.deduction" class="detail-deduction">
                        扣 {{ detail.deduction }} 分
                      </div>
                      <div v-if="detail.desc" class="detail-desc">{{ detail.desc }}</div>
                    </div>
                  </div>
                  <div v-if="dim.deduction > 0" class="dim-deduction-total">
                    本维度共扣 {{ dim.deduction }} 分
                  </div>
                </div>
              </div>

              <!-- 改进建议 -->
              <div class="suggestions-card">
                <div class="suggestions-header">
                  <el-icon><Opportunity /></el-icon>
                  <span>改进建议</span>
                </div>
                <div class="suggestions-body">
                  <div v-for="(suggestion, idx) in evaluationResult.suggestions" :key="idx" class="suggestion-item" :class="suggestion.priority">
                    <div class="suggestion-priority">
                      <el-tag :type="getPriorityType(suggestion.priority)" size="small">
                        {{ getPriorityLabel(suggestion.priority) }}
                      </el-tag>
                    </div>
                    <div class="suggestion-content">
                      <div class="suggestion-category">{{ suggestion.category }}</div>
                      <div class="suggestion-text">{{ suggestion.content }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 重心可视化 -->
              <div class="gravity-visualization">
                <div class="viz-header">
                  <h3>重心偏移可视化</h3>
                </div>
                <div class="viz-body">
                  <div ref="gravityChartRef" class="gravity-chart"></div>
                </div>
              </div>
            </div>
            <div v-else class="empty-evaluation">
              <el-icon :size="64"><DataAnalysis /></el-icon>
              <h3>暂无评价结果</h3>
              <p>请先完成装箱方案录入，然后点击"开始评价"</p>
            </div>
          </el-tab-pane>

          <!-- Tab 5: 历史记录 -->
          <el-tab-pane label="历史记录" name="history">
            <div class="tab-content">
              <div class="section-header">
                <h3>评价历史</h3>
                <span class="history-count">共 {{ historyRecords.length }} 条记录</span>
              </div>

              <div v-if="historyRecords.length > 0" class="history-list">
                <div v-for="(record, idx) in historyRecords" :key="record.id" class="history-card">
                  <div class="history-header">
                    <div class="history-info">
                      <span class="history-student">{{ record.scheme.studentName || '未命名' }}</span>
                      <span class="history-class">{{ record.scheme.className }}</span>
                      <span class="history-date">{{ formatDate(record.result.evaluatedAt) }}</span>
                    </div>
                    <div class="history-score">
                      <span class="score" :style="{ color: getGradeColor(record.result.totalScore) }">
                        {{ record.result.totalScore }}
                      </span>
                      <el-tag :color="getGradeColor(record.result.totalScore)" effect="dark" size="small">
                        {{ getGradeLabel(record.result.totalScore) }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="history-body">
                    <div class="history-template" v-if="record.scheme.workOrder">
                      {{ record.scheme.workOrder.icon }} {{ record.scheme.workOrder.name }}
                    </div>
                    <div class="history-dimensions">
                      <span v-for="(dim, key) in record.result.dimensions" :key="key" class="dim-badge">
                        {{ dim.dimension }}: {{ dim.score }}/{{ dim.maxScore }}
                      </span>
                    </div>
                  </div>
                  <div class="history-actions">
                    <el-button @click="viewHistoryDetail(record)" type="primary" size="small" link>
                      查看详情
                    </el-button>
                    <el-button @click="deleteHistory(idx)" type="danger" size="small" link>
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
              <div v-else class="empty-history">
                <el-icon :size="48"><Clock /></el-icon>
                <p>暂无历史记录</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </main>
    </div>

    <!-- 帮助对话框 -->
    <el-dialog v-model="helpVisible" title="使用帮助" width="600px">
      <div class="help-content">
        <h4>操作流程</h4>
        <ol>
          <li>选择预置工单模板或手动添加物资</li>
          <li>填写装箱方案（布局描述、包装方式）</li>
          <li>输入四角称重数据</li>
          <li>点击"开始评价"获取评分和改进建议</li>
          <li>根据建议调整方案，重新评价</li>
        </ol>
        <h4>评分标准</h4>
        <ul>
          <li><strong>重心平衡 (40分):</strong> 偏移量≤50mm满分，每超10mm扣10分</li>
          <li><strong>物品放置及防水 (30分):</strong> 未上轻下重扣40分、未包裹缓冲扣30分、防水不规范扣15分、液体未密封扣15分</li>
          <li><strong>缓冲固定 (15分):</strong> 空隙未填充扣60分、易碎品未包裹扣40分</li>
          <li><strong>空间利用率 (10分):</strong> 不有序扣20分</li>
          <li><strong>应急适配性 (5分):</strong> 未放易取位置扣100分</li>
        </ul>
        <h4>四角称重方法</h4>
        <p>在运输箱底部四角各放置一个载重称，记录四个角的重量（W1-W4），系统自动计算重心偏移量。</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowLeft, QuestionFilled, RefreshLeft, Download, Plus, Delete,
  CircleCheck, CircleClose, VideoPlay, DataAnalysis, Clock, InfoFilled, Opportunity
} from '@element-plus/icons-vue'

import packingData from '@/data/packing-agent-data.json'

const router = useRouter()

// ============ 数据定义 ============

// 工单模板
const workOrderTemplates = packingData.workOrderTemplates
const selectedTemplate = ref(null)

// 基础信息
const basicInfo = reactive({
  studentName: '',
  className: '',
  trainingDate: new Date()
})

// 运输箱参数
const boxParams = reactive({
  length: 600,
  width: 400,
  height: 300,
  emptyWeight: 5.0
})

// 物资清单
const materials = ref([])

// 四角称重
const cornerWeights = reactive({
  w1: 0,
  w2: 0,
  w3: 0,
  w4: 0
})

// 装箱布局描述
const layoutDescription = reactive({
  layer1: '',
  layer2: '',
  layer3: '',
  gaps: '',
  waterproof: ''
})

// 包装方式
const packaging = reactive({
  bufferMaterial: 'foam',
  waterproofMethod: 'both',
  sealingMethod: 'tape_cross',
  liquidContainer: 'sealed'
})

// 选项配置
const layerOptions = packingData.layerOptions
const positionOptions = packingData.positionOptions
const bufferMaterials = packingData.bufferMaterials
const waterproofMethods = packingData.waterproofMethods
const sealingMethods = packingData.sealingMethods

// 评价结果
const evaluationResult = ref(null)

// 历史记录
const historyRecords = ref([])

// 当前Tab
const activeTab = ref('workorder')

// 帮助对话框
const helpVisible = ref(false)

// 图表引用
const radarChartRef = ref(null)
const gravityChartRef = ref(null)
let radarChart = null
let gravityChart = null

// ============ 计算属性 ============

// 总重量
const totalWeight = computed(() => {
  return cornerWeights.w1 + cornerWeights.w2 + cornerWeights.w3 + cornerWeights.w4
})

// 重心计算结果
const gravityResult = computed(() => {
  const w1 = cornerWeights.w1 || 0
  const w2 = cornerWeights.w2 || 0
  const w3 = cornerWeights.w3 || 0
  const w4 = cornerWeights.w4 || 0
  const L = boxParams.length || 600
  const W = boxParams.width || 400
  const Wtotal = w1 + w2 + w3 + w4

  if (Wtotal === 0) {
    return { deltaX: 0, deltaY: 0, deltaS: 0, totalWeight: 0 }
  }

  const deltaX = ((w3 + w4) - (w1 + w2)) * L / (2 * Wtotal)
  const deltaY = ((w2 + w4) - (w1 + w3)) * W / (2 * Wtotal)
  const deltaS = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

  return {
    deltaX,
    deltaY,
    deltaS,
    totalWeight: Wtotal
  }
})

// 物资总重量
const totalMaterialWeight = computed(() => {
  return materials.value.reduce((sum, m) => sum + (m.weight * m.quantity), 0)
})

// 应急物资数量
const emergencyCount = computed(() => {
  return materials.value.filter(m => m.isEmergency).length
})

// 易碎物品数量
const fragileCount = computed(() => {
  return materials.value.filter(m => m.isFragile).length
})

// 是否可评价
const canEvaluate = computed(() => {
  return totalWeight.value > 0
})

// ============ 方法 ============

// 返回首页
const goBack = () => {
  router.push('/home')
}

// 显示帮助
const showHelp = () => {
  helpVisible.value = true
}

// 获取难度类型
const getDifficultyType = (difficulty) => {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[difficulty] || 'info'
}

// 获取难度标签
const getDifficultyLabel = (difficulty) => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[difficulty] || difficulty
}

// 选择工单模板
const selectTemplate = (template) => {
  selectedTemplate.value = template
  // 填充物资清单
  materials.value = template.materials.map(m => ({
    ...m,
    layer: m.isEmergency ? 3 : (m.weight > 5 ? 1 : 2),
    position: m.isEmergency ? 'accessible' : 'center',
    bufferMaterial: m.isFragile ? 'foam' : 'none'
  }))
  // 填充约束信息
  if (template.constraints.maxWeight) {
    boxParams.emptyWeight = 5.0
  }
  ElMessage.success(`已加载工单: ${template.name}`)
}

// 添加物资
const addMaterial = () => {
  materials.value.push({
    id: `mat_${Date.now()}`,
    name: '',
    category: 'equipment',
    weight: 1.0,
    length: 200,
    width: 150,
    height: 100,
    quantity: 1,
    isEmergency: false,
    isFragile: false,
    isLiquid: false,
    needsWaterproof: false,
    notes: '',
    layer: 2,
    position: 'center',
    bufferMaterial: 'none'
  })
}

// 删除物资
const removeMaterial = (index) => {
  materials.value.splice(index, 1)
}

// 重置方案
const resetScheme = () => {
  ElMessageBox.confirm('确定要重置当前方案吗？所有未保存的数据将丢失。', '确认重置', {
    type: 'warning'
  }).then(() => {
    selectedTemplate.value = null
    materials.value = []
    Object.assign(cornerWeights, { w1: 0, w2: 0, w3: 0, w4: 0 })
    Object.assign(layoutDescription, { layer1: '', layer2: '', layer3: '', gaps: '', waterproof: '' })
    Object.assign(packaging, { bufferMaterial: 'foam', waterproofMethod: 'both', sealingMethod: 'tape_cross', liquidContainer: 'sealed' })
    evaluationResult.value = null
    ElMessage.success('方案已重置')
  }).catch(() => {})
}

// 运行评价
const runEvaluation = () => {
  const result = evaluateScheme()
  evaluationResult.value = result
  activeTab.value = 'evaluation'

  // 保存到历史
  const record = {
    id: `record_${Date.now()}`,
    scheme: {
      ...basicInfo,
      box: { ...boxParams },
      materials: [...materials.value],
      cornerWeights: { ...cornerWeights },
      layoutDescription: { ...layoutDescription },
      packaging: { ...packaging },
      workOrder: selectedTemplate.value ? {
        id: selectedTemplate.value.id,
        name: selectedTemplate.value.name,
        icon: selectedTemplate.value.icon,
        scenario: selectedTemplate.value.scenario
      } : null
    },
    result
  }
  historyRecords.value.unshift(record)
  saveToLocalStorage()

  ElMessage.success('评价完成！')

  // 渲染图表
  nextTick(() => {
    renderRadarChart()
    renderGravityChart()
  })
}

// 评价引擎 - 重心平衡 (40分)
const evaluateBalance = () => {
  const maxScore = 40
  let score = maxScore
  let deduction = 0
  const details = []

  // 偏移量扣分：每超10mm扣10分
  const deltaS = gravityResult.value.deltaS
  if (deltaS > 50) {
    const excessMm = deltaS - 50
    deduction = Math.ceil(excessMm / 10) * 10
    score = Math.max(0, maxScore - deduction)
  }

  details.push({
    item: '重心偏移量',
    value: `${deltaS.toFixed(1)}mm`,
    standard: '≤50mm',
    passed: deltaS <= 50,
    deduction: deduction > 0 ? deduction : 0
  })

  return { dimension: '重心平衡', maxScore, score, deduction, details }
}

// 评价引擎 - 物品放置及防水 (30分)
const evaluatePlacement = () => {
  const maxScore = 30
  let score = maxScore
  const details = []
  let totalDeduction = 0

  // 1. 上轻下重检查
  const layer1Weight = materials.value.filter(m => m.layer === 1).reduce((sum, m) => sum + m.weight * m.quantity, 0)
  const layer3Weight = materials.value.filter(m => m.layer === 3).reduce((sum, m) => sum + m.weight * m.quantity, 0)
  const isBottomHeavy = layer1Weight >= layer3Weight || layer3Weight === 0

  if (!isBottomHeavy && materials.value.length > 0) {
    const deduction = 40
    totalDeduction += deduction
    details.push({ item: '上轻下重', passed: false, deduction, desc: '底层物资重量应大于上层' })
  } else {
    details.push({ item: '上轻下重', passed: true, deduction: 0 })
  }

  // 2. 缓冲包裹检查
  const fragileItems = materials.value.filter(m => m.isFragile)
  const unbufferedItems = fragileItems.filter(m => m.bufferMaterial === 'none')
  if (unbufferedItems.length > 0 && fragileItems.length > 0) {
    const deduction = 30
    totalDeduction += deduction
    details.push({
      item: '缓冲包裹',
      passed: false,
      deduction,
      desc: `${unbufferedItems.map(i => i.name).join('、')}未包裹缓冲材料`
    })
  } else {
    details.push({ item: '缓冲包裹', passed: true, deduction: 0 })
  }

  // 3. 防水规范检查
  if (packaging.waterproofMethod === 'none' || packaging.sealingMethod === 'none') {
    const deduction = 15
    totalDeduction += deduction
    details.push({ item: '防水规范', passed: false, deduction, desc: '未使用防水胶带或密封不规范' })
  } else {
    details.push({ item: '防水规范', passed: true, deduction: 0 })
  }

  // 4. 液体密封检查
  const liquidItems = materials.value.filter(m => m.isLiquid)
  if (liquidItems.length > 0 && packaging.liquidContainer !== 'sealed') {
    const deduction = 15
    totalDeduction += deduction
    details.push({
      item: '液体密封',
      passed: false,
      deduction,
      desc: `${liquidItems.map(i => i.name).join('、')}未独立密封`
    })
  } else {
    details.push({ item: '液体密封', passed: true, deduction: 0 })
  }

  score = Math.max(0, maxScore - totalDeduction)

  return { dimension: '物品放置及防水', maxScore, score, deduction: totalDeduction, details }
}

// 评价引擎 - 缓冲固定 (15分)
const evaluateBuffer = () => {
  const maxScore = 15
  let score = maxScore
  const details = []
  let totalDeduction = 0

  // 1. 空隙填充检查
  const gapsFilled = layoutDescription.gaps && layoutDescription.gaps.length > 10
  if (!gapsFilled && materials.value.length > 0) {
    const deduction = 60
    totalDeduction += deduction
    details.push({ item: '空隙填充', passed: false, deduction, desc: '未描述空隙填充方式或填充不到位' })
  } else {
    details.push({ item: '空隙填充', passed: true, deduction: 0 })
  }

  // 2. 易碎品包裹检查
  const fragileItems = materials.value.filter(m => m.isFragile)
  const unwrappedFragile = fragileItems.filter(m => m.bufferMaterial === 'none')
  if (unwrappedFragile.length > 0 && fragileItems.length > 0) {
    const deduction = 40
    totalDeduction += deduction
    details.push({
      item: '易碎品包裹',
      passed: false,
      deduction,
      desc: `${unwrappedFragile.map(i => i.name).join('、')}未包裹保护`
    })
  } else {
    details.push({ item: '易碎品包裹', passed: true, deduction: 0 })
  }

  score = Math.max(0, maxScore - totalDeduction)

  return { dimension: '缓冲固定', maxScore, score, deduction: totalDeduction, details }
}

// 评价引擎 - 空间利用率 (10分)
const evaluateSpaceUtilization = () => {
  const maxScore = 10
  let score = maxScore
  const details = []
  let totalDeduction = 0

  // 计算空间利用率
  const boxVolume = boxParams.length * boxParams.width * boxParams.height
  const materialsVolume = materials.value.reduce((sum, m) => {
    return sum + (m.length * m.width * m.height * m.quantity)
  }, 0)
  const utilization = boxVolume > 0 ? (materialsVolume / boxVolume) * 100 : 0

  // 整齐有序检查（从布局描述判断）
  const hasOrderlyDesc = layoutDescription.layer1 || layoutDescription.layer2 || layoutDescription.layer3
  if (!hasOrderlyDesc && materials.value.length > 0) {
    const deduction = 20
    totalDeduction += deduction
    details.push({ item: '整齐有序', passed: false, deduction, desc: '未描述物资摆放布局' })
  } else {
    details.push({ item: '整齐有序', passed: true, deduction: 0 })
  }

  details.unshift({
    item: '空间利用率',
    value: `${utilization.toFixed(1)}%`,
    standard: '≥70%',
    passed: utilization >= 70 || materials.value.length === 0
  })

  score = Math.max(0, maxScore - totalDeduction)

  return { dimension: '空间利用率', maxScore, score, deduction: totalDeduction, details, utilization }
}

// 评价引擎 - 应急适配性 (5分)
const evaluateEmergency = () => {
  const maxScore = 5
  let score = maxScore
  const details = []
  let totalDeduction = 0

  // 检查应急物资是否在易取位置
  const emergencyItems = materials.value.filter(m => m.isEmergency)
  const notAccessible = emergencyItems.filter(m =>
    m.layer !== 3 && m.position !== 'accessible' && m.position !== 'top'
  )

  if (notAccessible.length > 0 && emergencyItems.length > 0) {
    const deduction = 100
    totalDeduction += deduction
    details.push({
      item: '应急物资易取',
      passed: false,
      deduction,
      desc: `${notAccessible.map(i => i.name).join('、')}未放置在易取位置`
    })
  } else {
    details.push({ item: '应急物资易取', passed: true, deduction: 0 })
  }

  score = Math.max(0, maxScore - totalDeduction)

  return { dimension: '应急适配性', maxScore, score, deduction: totalDeduction, details }
}

// 生成改进建议
const generateSuggestions = (dimensions) => {
  const suggestions = []

  // 基于扣分项生成建议
  Object.values(dimensions).forEach(dim => {
    dim.details.forEach(detail => {
      if (!detail.passed) {
        suggestions.push({
          priority: dim.maxScore >= 30 ? 'high' : (dim.maxScore >= 15 ? 'medium' : 'low'),
          category: dim.dimension,
          content: getSpecificSuggestion(detail.item, selectedTemplate.value?.scenario)
        })
      }
    })
  })

  // 场景化建议
  if (selectedTemplate.value) {
    const scenario = selectedTemplate.value.scenario
    const scenarioTips = selectedTemplate.value.scenarioTips

    suggestions.push({
      priority: 'high',
      category: '场景专项',
      content: scenarioTips.waterproofTips || ''
    })

    if (scenario === 'earthquake') {
      suggestions.push({
        priority: 'medium',
        category: '场景专项',
        content: '地震灾区有余震风险，建议增加物资固定措施，重心尽量降低'
      })
    } else if (scenario === 'flood') {
      suggestions.push({
        priority: 'medium',
        category: '场景专项',
        content: '洪灾场景物资必须全面防水，建议使用防水袋完全包裹'
      })
    } else if (scenario === 'coldchain') {
      suggestions.push({
        priority: 'medium',
        category: '场景专项',
        content: '冷链运输需确保温度记录仪正常工作，冷藏箱四周需固定'
      })
    }
  }

  // 如果全部通过
  if (suggestions.length === 0) {
    suggestions.push({
      priority: 'low',
      category: '优化建议',
      content: '当前装箱方案评分优秀，可进一步优化重心平衡和空间利用率'
    })
  }

  return suggestions
}

// 获取具体建议
const getSpecificSuggestion = (item, scenario) => {
  const suggestions = {
    '重心偏移量': '建议将较重物资向中心靠拢，调整左右/前后配重平衡',
    '上轻下重': '将重物移至底层，轻质物品放在上层',
    '缓冲包裹': '为易碎物品增加泡沫或气泡膜包裹保护',
    '防水规范': '使用防水袋包裹物资，接缝处用防水胶带密封',
    '液体密封': '液体物资需独立密封，防止泄漏污染其他物资',
    '空隙填充': '使用泡沫、气泡膜或气垫填充所有空隙，防止物资移动',
    '易碎品包裹': '易碎物品需单独包裹缓冲材料，建议使用泡沫+气泡膜双重保护',
    '整齐有序': '物资应按层级整齐摆放，避免杂乱堆放',
    '应急物资易取': '应急物资（药品、通讯设备）应放在最上层或易取位置'
  }

  let suggestion = suggestions[item] || '请检查并改进此项'

  // 场景化补充
  if (scenario === 'flood' && item === '防水规范') {
    suggestion += '，洪灾场景建议使用双层防水'
  } else if (scenario === 'earthquake' && item === '空隙填充') {
    suggestion += '，地震场景需特别注意固定，防止余震导致物资移位'
  }

  return suggestion
}

// 完整评价流程
const evaluateScheme = () => {
  const balance = evaluateBalance()
  const placement = evaluatePlacement()
  const buffer = evaluateBuffer()
  const space = evaluateSpaceUtilization()
  const emergency = evaluateEmergency()

  const dimensions = { balance, placement, buffer, space, emergency }
  const totalScore = Object.values(dimensions).reduce((sum, d) => sum + d.score, 0)

  // 等级判定
  let grade
  if (totalScore >= 90) grade = '优秀'
  else if (totalScore >= 80) grade = '良好'
  else if (totalScore >= 60) grade = '合格'
  else grade = '不合格'

  const suggestions = generateSuggestions(dimensions)

  return {
    id: `eval_${Date.now()}`,
    evaluatedAt: new Date().toISOString(),
    scenario: selectedTemplate.value?.scenario || 'custom',
    scenarioName: selectedTemplate.value?.scenarioName || '自定义',
    totalScore,
    grade,
    centerOfGravity: {
      totalWeight: gravityResult.value.totalWeight,
      deltaX: gravityResult.value.deltaX,
      deltaY: gravityResult.value.deltaY,
      deltaS: gravityResult.value.deltaS,
      isQualified: gravityResult.value.deltaS <= 50
    },
    dimensions,
    suggestions
  }
}

// 渲染雷达图
const renderRadarChart = () => {
  if (!radarChartRef.value || !evaluationResult.value) return

  if (radarChart) {
    radarChart.dispose()
  }

  radarChart = echarts.init(radarChartRef.value)

  const dimensions = evaluationResult.value.dimensions
  const indicator = [
    { name: '重心平衡', max: 40 },
    { name: '物品放置', max: 30 },
    { name: '缓冲固定', max: 15 },
    { name: '空间利用', max: 10 },
    { name: '应急适配', max: 5 }
  ]

  const values = [
    dimensions.balance.score,
    dimensions.placement.score,
    dimensions.buffer.score,
    dimensions.space.score,
    dimensions.emergency.score
  ]

  const option = {
    backgroundColor: 'transparent',
    radar: {
      indicator,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#c0c8d4',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(59, 130, 246, 0.05)', 'rgba(59, 130, 246, 0.1)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '评分',
        areaStyle: {
          color: 'rgba(59, 130, 246, 0.3)'
        },
        lineStyle: {
          color: '#3b82f6',
          width: 2
        },
        itemStyle: {
          color: '#3b82f6'
        }
      }]
    }]
  }

  radarChart.setOption(option)
}

// 渲染重心偏移图
const renderGravityChart = () => {
  if (!gravityChartRef.value || !evaluationResult.value) return

  if (gravityChart) {
    gravityChart.dispose()
  }

  gravityChart = echarts.init(gravityChartRef.value)

  const deltaX = evaluationResult.value.centerOfGravity.deltaX
  const deltaY = evaluationResult.value.centerOfGravity.deltaY

  const option = {
    backgroundColor: 'transparent',
    grid: {
      top: 30,
      right: 30,
      bottom: 30,
      left: 50
    },
    xAxis: {
      type: 'value',
      min: -100,
      max: 100,
      name: '前后偏移 (mm)',
      nameTextStyle: { color: '#c0c8d4' },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } },
      axisLabel: { color: '#c0c8d4' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
    },
    yAxis: {
      type: 'value',
      min: -100,
      max: 100,
      name: '左右偏移 (mm)',
      nameTextStyle: { color: '#c0c8d4' },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } },
      axisLabel: { color: '#c0c8d4' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
    },
    series: [
      {
        type: 'scatter',
        data: [[deltaY, deltaX]],
        symbolSize: 20,
        itemStyle: {
          color: evaluationResult.value.centerOfGravity.isQualified ? '#10b981' : '#ef4444'
        },
        label: {
          show: true,
          formatter: `ΔS=${evaluationResult.value.centerOfGravity.deltaS.toFixed(1)}mm`,
          position: 'right',
          color: '#fff'
        }
      },
      {
        type: 'graph',
        layout: 'none',
        symbolSize: 0,
        data: [],
        lineStyle: {
          color: 'rgba(255,255,255,0.2)',
          width: 1,
          type: 'dashed'
        },
        // 绘制合格区域圆圈
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: {
            color: '#10b981',
            type: 'dashed',
            width: 1
          },
          data: [
            { xAxis: 0 },
            { yAxis: 0 }
          ]
        }
      }
    ],
    graphic: [
      {
        type: 'circle',
        shape: { cx: '50%', cy: '50%', r: 80 },
        style: {
          fill: 'none',
          stroke: 'rgba(16, 185, 129, 0.3)',
          lineWidth: 1,
          lineDash: [5, 5]
        }
      },
      {
        type: 'text',
        left: 'center',
        top: 10,
        style: {
          text: '绿色圆圈内为合格区域 (≤50mm)',
          fill: '#c0c8d4',
          fontSize: 12
        }
      }
    ]
  }

  gravityChart.setOption(option)
}

// 获取等级颜色
const getGradeColor = (score) => {
  if (score >= 90) return '#10b981'
  if (score >= 80) return '#3b82f6'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

// 获取等级标签
const getGradeLabel = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '合格'
  return '不合格'
}

// 获取维度颜色
const getDimensionColor = (score, max) => {
  const ratio = score / max
  if (ratio >= 0.9) return '#10b981'
  if (ratio >= 0.7) return '#3b82f6'
  if (ratio >= 0.5) return '#f59e0b'
  return '#ef4444'
}

// 获取优先级类型
const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

// 获取优先级标签
const getPriorityLabel = (priority) => {
  const map = { high: '重要', medium: '建议', low: '优化' }
  return map[priority] || priority
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 查看历史详情
const viewHistoryDetail = (record) => {
  // 恢复数据
  Object.assign(basicInfo, {
    studentName: record.scheme.studentName,
    className: record.scheme.className,
    trainingDate: record.scheme.trainingDate
  })
  Object.assign(boxParams, record.scheme.box)
  materials.value = [...record.scheme.materials]
  Object.assign(cornerWeights, record.scheme.cornerWeights)
  Object.assign(layoutDescription, record.scheme.layoutDescription)
  Object.assign(packaging, record.scheme.packaging)

  if (record.scheme.workOrder) {
    selectedTemplate.value = workOrderTemplates.find(t => t.id === record.scheme.workOrder.id) || null
  }

  evaluationResult.value = record.result
  activeTab.value = 'evaluation'

  nextTick(() => {
    renderRadarChart()
    renderGravityChart()
  })

  ElMessage.success('已加载历史记录')
}

// 删除历史记录
const deleteHistory = (index) => {
  ElMessageBox.confirm('确定要删除这条历史记录吗？', '确认删除', {
    type: 'warning'
  }).then(() => {
    historyRecords.value.splice(index, 1)
    saveToLocalStorage()
    ElMessage.success('已删除')
  }).catch(() => {})
}

// 导出报告
const exportReport = () => {
  if (!evaluationResult.value) return

  const report = {
    基础信息: basicInfo,
    运输箱参数: boxParams,
    物资清单: materials.value.map(m => ({
      名称: m.name,
      重量: `${m.weight}kg`,
      尺寸: `${m.length}×${m.width}×${m.height}mm`,
      数量: m.quantity,
      层级: layerOptions.find(l => l.value === m.layer)?.label,
      位置: positionOptions.find(p => p.value === m.position)?.label
    })),
    四角称重: cornerWeights,
    重心计算: evaluationResult.value.centerOfGravity,
    评分结果: {
      总分: evaluationResult.value.totalScore,
      等级: evaluationResult.value.grade,
      各维度: Object.values(evaluationResult.value.dimensions).map(d => ({
        维度: d.dimension,
        得分: `${d.score}/${d.maxScore}`,
        扣分: d.deduction
      }))
    },
    改进建议: evaluationResult.value.suggestions.map(s => `[${s.priority}]${s.category}: ${s.content}`)
  }

  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `装箱评价报告_${basicInfo.studentName || '未命名'}_${formatDate(new Date().toISOString())}.json`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已导出')
}

// localStorage 操作
const saveToLocalStorage = () => {
  const data = {
    history: historyRecords.value,
    settings: {
      boxDimensions: { ...boxParams }
    },
    meta: {
      version: '1.0.0',
      lastSaved: new Date().toISOString()
    }
  }
  localStorage.setItem('packing_agent_data', JSON.stringify(data))
}

const loadFromLocalStorage = () => {
  try {
    const data = JSON.parse(localStorage.getItem('packing_agent_data'))
    if (data) {
      historyRecords.value = data.history || []
      if (data.settings?.boxDimensions) {
        Object.assign(boxParams, data.settings.boxDimensions)
      }
    }
  } catch (e) {
    console.error('Failed to load from localStorage:', e)
  }
}

// ============ 生命周期 ============

onMounted(() => {
  // 覆盖 Element Plus 的 CSS 变量，彻底解决白色问题
  // Element Plus 用 --el-fill-color-blank 作为 input wrapper 的 box-shadow 颜色（默认白色）
  document.documentElement.style.setProperty('--el-fill-color-blank', 'rgba(0, 0, 0, 0.4)')
  document.documentElement.style.setProperty('--el-fill-color', 'rgba(0, 0, 0, 0.3)')
  document.documentElement.style.setProperty('--el-bg-color', '#0a1628')
  document.documentElement.style.setProperty('--el-bg-color-overlay', '#0d2137')
  document.documentElement.style.setProperty('--el-bg-color-page', '#0a1628')

  // 同时用 MutationObserver 监听，确保下拉面板弹出时也覆盖
  const observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node.nodeType !== 1) continue
        // 下拉面板
        if (node.classList?.contains('el-select-dropdown')) {
          node.style.setProperty('background', 'rgba(10, 25, 50, 0.95)', 'important')
          node.style.setProperty('border', '1px solid rgba(64, 158, 255, 0.25)', 'important')
        }
        // 下拉选项 - 强制深色背景
        node.querySelectorAll?.('.el-select-dropdown__item')?.forEach(item => {
          item.style.setProperty('background', 'transparent', 'important')
          item.style.setProperty('background-color', 'transparent', 'important')
          item.style.setProperty('color', '#c0ccda', 'important')
        })
      }
      // 监听属性变化（hover 类名变化时也覆盖）
      if (m.type === 'attributes' && m.target?.classList?.contains('el-select-dropdown__item')) {
        m.target.style.setProperty('background', 'transparent', 'important')
        m.target.style.setProperty('background-color', 'transparent', 'important')
        m.target.style.setProperty('color', '#e2e8f0', 'important')
      }
    }
  })
  observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] })

  loadFromLocalStorage()

  // 监听窗口大小变化，重新渲染图表
  window.addEventListener('resize', () => {
    radarChart?.resize()
    gravityChart?.resize()
  })
})

// 监听评价结果变化，渲染图表
watch(evaluationResult, () => {
  if (evaluationResult.value) {
    nextTick(() => {
      renderRadarChart()
      renderGravityChart()
    })
  }
})
</script>

<style scoped>
/* ============ 全局布局 ============ */
.packing-agent-page {
  min-height: 100vh;
  background: #0a1628;
  color: #fff;
  display: flex;
  flex-direction: column;
}

/* 顶部导航 */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: rgba(13, 33, 55, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 顶部按钮深色主题 */
.top-header :deep(.el-button--primary.is-plain) {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.top-header :deep(.el-button--primary.is-plain:hover) {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.top-header :deep(.el-button--info.is-plain) {
  border-color: rgba(160, 174, 192, 0.3);
  background: rgba(160, 174, 192, 0.05);
  color: #c0c8d4;
}

.top-header :deep(.el-button--info.is-plain:hover) {
  border-color: rgba(160, 174, 192, 0.5);
  background: rgba(160, 174, 192, 0.1);
  color: #c0c8d4;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 300px;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.left-panel .panel-card {
  width: 100%;
  box-sizing: border-box;
}

.panel-card {
  background: rgba(13, 33, 55, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}

.card-body {
  padding: 16px;
}

/* 深色主题表单元素 */
.panel-card :deep(.el-form-item__label) {
  color: #c0c8d4;
  font-size: 13px;
}

.panel-card :deep(.el-input-number) {
  width: 100%;
}

.panel-card :deep(.el-date-editor) {
  width: 100%;
}

/* 运输箱尺寸输入 */
.box-dimensions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.box-dimensions .el-input-number {
  width: 80px;
}

.dimension-separator {
  color: #c0c8d4;
}

/* 评分概览 */
.score-overview {
  text-align: center;
}

.total-score {
  margin-bottom: 16px;
}

.score-ring {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 4px solid var(--score-color, #3b82f6);
  margin-bottom: 8px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--score-color, #3b82f6);
}

.score-label {
  font-size: 12px;
  color: #c0c8d4;
}

.radar-chart {
  height: 200px;
  width: 100%;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

/* 深色主题按钮样式覆盖 */
.action-buttons :deep(.el-button) {
  width: 100%;
  margin-left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  transition: all 0.3s ease;
}

.action-buttons :deep(.el-button:hover) {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: translateY(-1px);
}

.action-buttons :deep(.el-button--warning.is-plain) {
  border-color: rgba(245, 158, 11, 0.5);
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.action-buttons :deep(.el-button--warning.is-plain:hover) {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.action-buttons :deep(.el-button--success.is-plain) {
  border-color: rgba(16, 185, 129, 0.5);
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-buttons :deep(.el-button--success.is-plain:hover) {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.action-buttons :deep(.el-button--success.is-plain.is-disabled) {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.05);
  color: rgba(16, 185, 129, 0.5);
  cursor: not-allowed;
  transform: none;
}

.action-buttons :deep(.el-button .el-icon) {
  font-size: 16px;
}

.action-buttons :deep(.el-button span) {
  flex: 1;
  text-align: center;
}

/* 右侧内容区 */
.right-content {
  flex: 1;
  background: rgba(13, 33, 55, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
  background: rgba(0, 0, 0, 0.2);
}

.main-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.main-tabs :deep(.el-tabs__item) {
  color: #c0c8d4;
  font-size: 14px;
}

.main-tabs :deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}

.main-tabs :deep(.el-tabs__active-bar) {
  background: #3b82f6;
}

.main-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.main-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
}

.tab-content {
  padding: 24px;
}

/* ============ 右侧Tab内容区域深色主题 ============ */

/* InputNumber 深色主题 */
.tab-content :deep(.el-input-number) {
  background: transparent;
}

/* 表格深色主题 */
.tab-content :deep(.el-table .el-table__body tr:hover > td) {
  background: rgba(59, 130, 246, 0.06) !important;
}
.tab-content :deep(.el-table__empty-text) { color: #4a5568 !important; }
.tab-content :deep(.el-table--border .el-table__cell) { border-right: 1px solid rgba(255,255,255,0.05) !important; }

.tab-content :deep(.el-table .el-checkbox__label) {
  font-size: 12px;
}

/* Descriptions 深色主题 */
.el-descriptions {
  --el-descriptions-item-bordered-label-background: rgba(0, 0, 0, 0.3);
}

/* Button 在表格中的深色主题 */
.tab-content :deep(.el-button--danger.is-link) {
  color: #ef4444 !important;
}

.tab-content :deep(.el-button--danger.is-link:hover) {
  color: #f87171 !important;
}

/* 深色全局 - 弹出框和日期选择器 */
.packing-agent-page :deep(.el-select-dropdown) { background: rgba(10,25,50,0.95) !important; border: 1px solid rgba(64,158,255,0.25) !important; }
.packing-agent-page :deep(.el-select-dropdown__item) { color: #c0ccda !important; }
.packing-agent-page :deep(.el-select-dropdown__item:hover),
.packing-agent-page :deep(.el-select-dropdown__item.hover) { background: rgba(64,158,255,0.12) !important; color: #e2e8f0 !important; }
.packing-agent-page :deep(.el-select-dropdown__item.selected) { color: #3b82f6 !important; font-weight: 600; }
.packing-agent-page :deep(.el-picker-panel) { background: rgba(10,25,50,0.95) !important; border: 1px solid rgba(64,158,255,0.25) !important; color: #e2e8f0 !important; }

/* 区域头部 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.section-desc {
  color: #c0c8d4;
  font-size: 13px;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 工单选择 */
.workorder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.workorder-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.workorder-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.workorder-card.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.wo-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.wo-icon {
  font-size: 32px;
}

.wo-info h4 {
  font-size: 15px;
  margin-bottom: 4px;
}

.wo-desc {
  font-size: 13px;
  color: #c0c8d4;
  margin-bottom: 12px;
  line-height: 1.5;
}

.wo-constraints {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #718096;
  margin-bottom: 12px;
}

.wo-constraints strong {
  color: #c0c8d4;
}

.wo-requirements {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #10b981;
}

/* 工单详情 */
.workorder-detail {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.detail-header {
  padding: 16px 20px;
  background: rgba(59, 130, 246, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-header h3 {
  font-size: 15px;
}

.detail-body {
  padding: 20px;
}

.requirements-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.constraints-info {
  margin-top: 16px;
}

/* 物资表格 */
.materials-table {
  width: 100%;
}

.materials-table :deep(.el-table__header th) {
  background: rgba(0, 0, 0, 0.3) !important;
  color: #c0c8d4;
}

.materials-table :deep(.el-table__body td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.size-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.size-inputs span {
  color: #c0c8d4;
}

.property-tags {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.materials-table :deep(.el-checkbox__label) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

.materials-table :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #e2e8f0 !important;
}

.materials-summary {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 13px;
  color: #c0c8d4;
}

/* 四角称重 */
.section-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

/* section-card 内深色输入框 */
.section-card :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
}

.section-card :deep(.el-input__wrapper:hover) {
  border-color: rgba(59, 130, 246, 0.3) !important;
}

.section-card :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(59, 130, 246, 0.6) !important;
}

.section-card :deep(.el-input__inner) {
  color: #e2e8f0 !important;
}

.section-card :deep(.el-input__inner::placeholder) {
  color: rgba(160, 174, 192, 0.4) !important;
}

/* section-card 内下拉选择 */
.section-card :deep(.el-select .el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3) !important;
}

.section-card :deep(.el-select-dropdown) {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
}

.section-card :deep(.el-select-dropdown__item) {
  color: #c0ccda !important;
}

.section-card :deep(.el-select-dropdown__item.hover),
.section-card :deep(.el-select-dropdown__item:hover) {
  background: rgba(64, 158, 255, 0.12) !important;
}

.section-card :deep(.el-select-dropdown__item.selected) {
  color: #3b82f6 !important;
}

/* section-card 内数字输入框 */
.section-card :deep(.el-input-number .el-input-number__decrease),
.section-card :deep(.el-input-number .el-input-number__increase) {
  background: rgba(10, 25, 50, 0.8) !important;
  border-color: rgba(255, 255, 255, 0.08) !important;
  color: #c0c8d4 !important;
}

.section-card :deep(.el-input-number .el-input-number__decrease:hover),
.section-card :deep(.el-input-number .el-input-number__increase:hover) {
  color: #3b82f6 !important;
}

/* section-card 内表单标签 */
.section-card :deep(.el-form-item__label) {
  color: #c0c8d4 !important;
}

.corner-weight-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}

.weight-diagram {
  display: flex;
  justify-content: center;
}

.box-top-view {
  width: 100%;
  max-width: 400px;
}

.box-label {
  text-align: center;
  color: #c0c8d4;
  font-size: 13px;
  margin-bottom: 12px;
}

.corner-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.corner-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.corner-label {
  font-size: 13px;
  color: #c0c8d4;
}

.weight-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.result-label {
  font-size: 13px;
  color: #c0c8d4;
}

.result-value {
  font-weight: 600;
  font-size: 15px;
}

.result-value.warning {
  color: #f59e0b;
}

.result-value.danger {
  color: #ef4444;
}

.result-value.success {
  color: #10b981;
}

.result-item.highlight {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.result-status {
  text-align: center;
  margin-top: 8px;
}

.gravity-formula {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 16px;
  font-family: monospace;
  font-size: 12px;
  color: #718096;
  line-height: 1.8;
}

.formula-item {
  margin-bottom: 4px;
}

/* 提交区域 */
.submit-section {
  text-align: center;
  margin-top: 24px;
}

.submit-hint {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: #f59e0b;
}

/* 评价结果 */
.total-score-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
  border-radius: 12px;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.big-score {
  font-size: 64px;
  font-weight: 700;
}

.score-unit {
  font-size: 20px;
  color: #c0c8d4;
}

.grade-tag {
  font-size: 18px;
  padding: 8px 20px;
}

/* 场景专项提示 */
.scenario-tips-card {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 12px;
  margin-bottom: 24px;
  overflow: hidden;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 193, 7, 0.1);
}

.tips-icon {
  font-size: 24px;
}

.tips-title {
  font-weight: 600;
  color: #f59e0b;
}

.tips-body {
  padding: 16px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #c0c8d4;
}

.tip-item .el-icon {
  color: #f59e0b;
  margin-top: 2px;
}

/* 维度评分卡片 */
.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.dimension-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dim-name {
  font-weight: 600;
  font-size: 15px;
}

.dim-score {
  font-size: 14px;
}

.dim-score .current {
  font-size: 20px;
  font-weight: 700;
  color: #3b82f6;
}

.dim-score .separator {
  color: #c0c8d4;
  margin: 0 2px;
}

.dim-score .max {
  color: #c0c8d4;
}

.dim-progress {
  margin-bottom: 12px;
}

.dim-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.detail-item.failed {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.detail-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-icon.success {
  color: #10b981;
}

.status-icon.danger {
  color: #ef4444;
}

.detail-name {
  font-size: 13px;
}

.detail-value {
  color: #3b82f6;
  font-weight: 600;
  margin-left: auto;
}

.detail-standard {
  color: #718096;
  font-size: 12px;
}

.detail-deduction {
  color: #ef4444;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.detail-desc {
  color: #c0c8d4;
  font-size: 12px;
  margin-top: 4px;
}

.dim-deduction-total {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #ef4444;
  font-size: 13px;
  font-weight: 600;
}

/* 改进建议 */
.suggestions-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 24px;
  overflow: hidden;
}

.suggestions-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
}

.suggestions-header .el-icon {
  color: #3b82f6;
}

.suggestions-body {
  padding: 16px 20px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border-left: 3px solid transparent;
}

.suggestion-item.high {
  border-left-color: #ef4444;
}

.suggestion-item.medium {
  border-left-color: #f59e0b;
}

.suggestion-item.low {
  border-left-color: #3b82f6;
}

.suggestion-category {
  font-size: 12px;
  color: #c0c8d4;
  margin-bottom: 4px;
}

.suggestion-text {
  font-size: 13px;
  line-height: 1.5;
}

/* 重心可视化 */
.gravity-visualization {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.viz-header {
  padding: 16px 20px;
  background: rgba(59, 130, 246, 0.1);
}

.viz-header h3 {
  font-size: 15px;
}

.viz-body {
  padding: 20px;
}

.gravity-chart {
  height: 300px;
  width: 100%;
}

/* 空状态 */
.empty-evaluation,
.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #718096;
}

.empty-evaluation h3,
.empty-history h3 {
  margin: 16px 0 8px;
  color: #c0c8d4;
}

/* 历史记录 */
.history-count {
  color: #c0c8d4;
  font-size: 13px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s;
}

.history-card:hover {
  background: rgba(255, 255, 255, 0.08);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-student {
  font-weight: 600;
  font-size: 15px;
}

.history-class {
  color: #c0c8d4;
  font-size: 13px;
}

.history-date {
  color: #718096;
  font-size: 12px;
}

.history-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-score .score {
  font-size: 24px;
  font-weight: 700;
}

.history-body {
  margin-bottom: 12px;
}

.history-template {
  font-size: 13px;
  color: #c0c8d4;
  margin-bottom: 8px;
}

.history-dimensions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dim-badge {
  font-size: 12px;
  padding: 2px 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  color: #3b82f6;
}

.history-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 帮助对话框 */
.help-content h4 {
  margin: 16px 0 8px;
  color: #3b82f6;
}

.help-content ol,
.help-content ul {
  padding-left: 20px;
  margin-bottom: 12px;
}

.help-content li {
  margin-bottom: 6px;
  line-height: 1.6;
}

/* ============ 深色输入框样式 ============ */

/* el-input 输入框 */
.packing-agent-page :deep(.el-input__wrapper) {
  background: rgba(10, 25, 50, 0.8) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
  box-shadow: none !important;
  border-radius: 6px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.packing-agent-page :deep(.el-input__wrapper:hover) {
  border-color: rgba(64, 158, 255, 0.4) !important;
}

.packing-agent-page :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(64, 158, 255, 0.7) !important;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.15) !important;
}

.packing-agent-page :deep(.el-input__inner) {
  color: #e2e8f0 !important;
  font-size: 13px;
}

.packing-agent-page :deep(.el-input__inner::placeholder) {
  color: rgba(160, 174, 192, 0.5) !important;
}

/* el-input-number 数字输入框 */
.packing-agent-page :deep(.el-input-number .el-input__wrapper) {
  background: rgba(10, 25, 50, 0.8) !important;
}

.packing-agent-page :deep(.el-input-number .el-input-number__decrease),
.packing-agent-page :deep(.el-input-number .el-input-number__increase) {
  background: rgba(15, 35, 65, 0.9) !important;
  border-color: rgba(64, 158, 255, 0.15) !important;
  color: #c0c8d4 !important;
}

.packing-agent-page :deep(.el-input-number .el-input-number__decrease:hover),
.packing-agent-page :deep(.el-input-number .el-input-number__increase:hover) {
  color: #3b82f6 !important;
  background: rgba(20, 45, 80, 0.9) !important;
}

/* el-select 下拉选择 */
.packing-agent-page :deep(.el-select .el-input__wrapper) {
  background: rgba(10, 25, 50, 0.8) !important;
}

.packing-agent-page :deep(.el-select-dropdown) {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.25) !important;
  backdrop-filter: blur(10px);
}

.packing-agent-page :deep(.el-select-dropdown__item) {
  color: #c0ccda !important;
}

.packing-agent-page :deep(.el-select-dropdown__item.hover),
.packing-agent-page :deep(.el-select-dropdown__item:hover) {
  background: rgba(64, 158, 255, 0.12) !important;
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-select-dropdown__item.selected) {
  color: #3b82f6 !important;
  font-weight: 600;
}

/* el-textarea 多行文本 */
.packing-agent-page :deep(.el-textarea__inner) {
  background: rgba(10, 25, 50, 0.8) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
  box-shadow: none !important;
  color: #e2e8f0 !important;
  border-radius: 6px;
  transition: border-color 0.3s;
}

.packing-agent-page :deep(.el-textarea__inner:hover) {
  border-color: rgba(64, 158, 255, 0.4) !important;
}

.packing-agent-page :deep(.el-textarea__inner:focus) {
  border-color: rgba(64, 158, 255, 0.7) !important;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.15) !important;
}

.packing-agent-page :deep(.el-textarea__inner::placeholder) {
  color: rgba(160, 174, 192, 0.5) !important;
}

/* el-date-picker 日期选择 */
.packing-agent-page :deep(.el-date-editor .el-input__wrapper) {
  background: rgba(10, 25, 50, 0.8) !important;
}

.packing-agent-page :deep(.el-picker-panel) {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.25) !important;
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-picker-panel__body) {
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-date-table td.today span) {
  color: #3b82f6 !important;
}

.packing-agent-page :deep(.el-date-table td.current:not(.disabled) span) {
  background: #3b82f6 !important;
  color: #fff !important;
}

.packing-agent-page :deep(.el-date-picker__header-label) {
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-date-picker__header .el-icon) {
  color: #c0c8d4 !important;
}

/* el-table 表格 */
.packing-agent-page :deep(.el-table) {
  --el-table-bg-color: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: rgba(0, 0, 0, 0.2) !important;
  --el-table-row-hover-bg-color: rgba(64, 158, 255, 0.08) !important;
  --el-table-border-color: rgba(64, 158, 255, 0.12) !important;
  --el-table-text-color: #c0ccda !important;
  --el-table-header-text-color: #c0c8d4 !important;
  color: #c0ccda !important;
}

.packing-agent-page :deep(.el-table th.el-table__cell) {
  background: rgba(0, 0, 0, 0.2) !important;
  color: #c0c8d4 !important;
  font-weight: 600;
  font-size: 12px;
  border-bottom: 1px solid rgba(64, 158, 255, 0.15) !important;
}

.packing-agent-page :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(64, 158, 255, 0.08) !important;
}

.packing-agent-page :deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: rgba(64, 158, 255, 0.06) !important;
}

/* el-button 按钮 */
.packing-agent-page :deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.packing-agent-page :deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.packing-agent-page :deep(.el-button--default) {
  background: rgba(15, 30, 60, 0.6) !important;
  border-color: rgba(64, 158, 255, 0.3) !important;
  color: #c0c8d4 !important;
}

.packing-agent-page :deep(.el-button--default:hover) {
  border-color: rgba(64, 158, 255, 0.5) !important;
  color: #e2e8f0 !important;
  background: rgba(20, 40, 75, 0.8) !important;
}

.packing-agent-page :deep(.el-button--danger) {
  background: rgba(220, 38, 38, 0.15) !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  color: #f87171 !important;
}

.packing-agent-page :deep(.el-button--danger:hover) {
  background: rgba(220, 38, 38, 0.25) !important;
}

/* el-descriptions 描述列表 */
.packing-agent-page :deep(.el-descriptions) {
  --el-descriptions-item-bordered-label-background: rgba(0, 0, 0, 0.2) !important;
}

.packing-agent-page :deep(.el-descriptions__label) {
  color: #c0c8d4 !important;
  background: rgba(0, 0, 0, 0.2) !important;
}

.packing-agent-page :deep(.el-descriptions__content) {
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-descriptions__body) {
  background: transparent !important;
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-descriptions__cell) {
  border-color: rgba(64, 158, 255, 0.1) !important;
}

/* el-tag 标签 */
.packing-agent-page :deep(.el-tag) {
  border-color: rgba(64, 158, 255, 0.25) !important;
}

/* el-tooltip */
.packing-agent-page :deep(.el-popper) {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.25) !important;
  color: #e2e8f0 !important;
}

/* el-empty 空状态 */
.packing-agent-page :deep(.el-empty__description p) {
  color: #c0c8d4 !important;
}

/* el-dialog 弹窗 */
.packing-agent-page :deep(.el-dialog) {
  background: rgba(13, 33, 55, 0.98) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
}

.packing-agent-page :deep(.el-dialog__title) {
  color: #e2e8f0 !important;
}

.packing-agent-page :deep(.el-dialog__body) {
  color: #c0ccda !important;
}

/* 响应式 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .panel-card {
    flex: 1;
    min-width: 250px;
  }

  .corner-weight-section {
    grid-template-columns: 1fr;
  }

  .dimensions-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<!-- 非作用域样式：覆盖 teleport 到 body 的弹出框 -->
<style>
/* Select 下拉面板 */
.packing-agent-page .el-select-dropdown {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.25) !important;
}
.packing-agent-page .el-select-dropdown__item {
  color: #c0ccda !important;
  font-size: 13px;
}
.packing-agent-page .el-select-dropdown__item:hover,
.packing-agent-page .el-select-dropdown__item.hover,
.packing-agent-page .el-select-dropdown__item.is-hovering {
  background: rgba(64, 158, 255, 0.15) !important;
  color: #e2e8f0 !important;
}
.packing-agent-page .el-select-dropdown__item.selected {
  color: #3b82f6 !important;
  font-weight: 600;
}
.packing-agent-page .el-select-dropdown__empty {
  color: #c0c8d4 !important;
}

/* Date Picker 面板 */
.packing-agent-page .el-picker-panel {
  background: rgba(10, 25, 50, 0.95) !important;
  border: 1px solid rgba(64, 158, 255, 0.25) !important;
  color: #e2e8f0 !important;
}
.packing-agent-page .el-picker-panel__body {
  color: #e2e8f0 !important;
}
.packing-agent-page .el-date-picker__header-label {
  color: #e2e8f0 !important;
}
.packing-agent-page .el-date-picker__header .el-icon {
  color: #c0c8d4 !important;
}
.packing-agent-page .el-date-table td.today span {
  color: #3b82f6 !important;
}
.packing-agent-page .el-date-table td.current:not(.disabled) span {
  background: #3b82f6 !important;
  color: #fff !important;
}
.packing-agent-page .el-picker-panel__icon-btn {
  color: #c0c8d4 !important;
}
.packing-agent-page .el-date-picker__header-label:hover,
.packing-agent-page .el-picker-panel__icon-btn:hover {
  color: #3b82f6 !important;
}

/* 表单标签 */
.packing-agent-page .el-form-item__label {
  color: #c0c8d4 !important;
}
</style>
