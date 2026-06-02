import { defineStore } from 'pinia'
import { usePointsStore } from './points'
import { useMaterialsStore } from './materials'
import { useUavsStore } from './uavs'
import { loadConfig, saveConfig } from '../api/config'

const COMBINED_FILENAME = '任务配置信息.md'

// 模块标记
const MARKERS = {
  module1: { start: '<!-- MODULE1_START -->', end: '<!-- MODULE1_END -->' },
  module2: { start: '<!-- MODULE2_START -->', end: '<!-- MODULE2_END -->' },
  module3: { start: '<!-- MODULE3_START -->', end: '<!-- MODULE3_END -->' },
}

export const useConfigStore = defineStore('config', () => {

  // 生成模块一的 Markdown 片段
  function generateModule1Section() {
    const pts = usePointsStore()
    const lines = []

    lines.push(`# 模块一：配送点设置`)
    lines.push('')

    // 配送中心
    lines.push(`## 配送中心`)
    lines.push('')
    if (pts.center) {
      lines.push(`| 属性 | 值 |`)
      lines.push(`|------|-----|`)
      lines.push(`| 名称 | ${pts.center.name} |`)
      lines.push(`| 经度 | ${pts.center.longitude} |`)
      lines.push(`| 纬度 | ${pts.center.latitude} |`)
    } else {
      lines.push('未设置')
    }
    lines.push('')

    // 需求点
    lines.push(`## 需求点（共 ${pts.demands.length} 个）`)
    lines.push('')
    if (pts.demands.length > 0) {
      lines.push(`| 编号 | 名称 | 经度 | 纬度 | 备注 |`)
      lines.push(`|------|------|------|------|------|`)
      pts.demands.forEach((d, i) => {
        lines.push(`| ${i + 1} | ${d.name} | ${d.longitude} | ${d.latitude} | ${d.note || '-'} |`)
      })
    } else {
      lines.push('暂无需求点')
    }
    lines.push('')

    // 距离矩阵
    if (pts.distMatrix.length > 0) {
      lines.push(`## 距离矩阵（km）`)
      lines.push('')
      const header = ['回程距离', ...pts.distLabels]
      lines.push(`| ${header.join(' | ')} |`)
      lines.push(`| ${header.map(() => '---').join(' | ')} |`)
      pts.distMatrix.forEach((row, i) => {
        const cells = [
          pts.distReturn[i].toFixed(2),
          ...row.map((v, j) => i === j ? '0' : v.toFixed(2)),
        ]
        lines.push(`| ${cells.join(' | ')} |`)
      })
      lines.push('')
    }

    // 汇总
    lines.push(`## 汇总`)
    lines.push('')
    lines.push(`- 配送中心：${pts.center ? pts.center.name : '未设置'}`)
    lines.push(`- 需求数量：${pts.demands.length} 个`)
    lines.push(`- 距离矩阵：${pts.distMatrix.length > 0 ? '已生成' : '未生成'}`)
    if (pts.distReturn.length > 0) {
      const maxDist = Math.max(...pts.distReturn).toFixed(2)
      const avgDist = (pts.distReturn.reduce((a, b) => a + b, 0) / pts.distReturn.length).toFixed(2)
      lines.push(`- 最远距离：${maxDist} km`)
      lines.push(`- 平均距离：${avgDist} km`)
    }

    return lines.join('\n')
  }

  // 生成模块二的 Markdown 片段
  function generateModule2Section() {
    const pts = usePointsStore()
    const mat = useMaterialsStore()
    const lines = []

    lines.push(`# 模块二：物资需求`)
    lines.push('')

    // 物资类别总览
    lines.push(`## 物资类别总览`)
    lines.push('')
    lines.push(`| 类别 | 物资 | 默认重量(kg) | 优先级 | 特殊要求 |`)
    lines.push(`|------|------|-------------|--------|----------|`)
    mat.categories.forEach(cat => {
      const itemNames = cat.items.map(it => it.name).join('、')
      lines.push(`| ${cat.icon} ${cat.name} | ${itemNames} | ${cat.total_weight} | ${cat.priority} | ${cat.special} |`)
    })
    lines.push('')

    // 各需求点物资分配
    lines.push(`## 需求点物资分配（共 ${mat.assignedCount} 个已分配）`)
    lines.push('')

    pts.demands.forEach((pt, idx) => {
      const a = mat.getAssignment(pt.id)
      lines.push(`### ${idx + 1}. ${pt.name}`)
      lines.push('')
      if (a) {
        lines.push(`- **物资类别**：${a.supply_types.join(' + ')}`)
        lines.push(`- **总重量**：${a.total_weight} kg`)
        lines.push(`- **优先级**：${a.priority}（${priorityLabel(a.priority)}）`)
        lines.push(`- **特殊要求**：${a.special_requirements}`)
        lines.push(`- **投放风险**：${Array.isArray(a.risk_warnings) ? a.risk_warnings.join('；') : (a.risk_warnings || '无')}`)
        lines.push('')
        lines.push(`| 物资 | 单重(kg) | 数量 | 小计(kg) |`)
        lines.push(`|------|---------|------|----------|`)
        a.items.forEach(item => {
          const uw = item.unit_weight ?? item.weight ?? 0
          const q = item.qty ?? item.quantity ?? 0
          const st = item.subtotal ?? (uw * q)
          lines.push(`| ${item.name} | ${uw} | ${q} | ${st} |`)
        })
      } else {
        lines.push('未分配物资')
      }
      lines.push('')
    })

    // 汇总
    lines.push(`## 汇总`)
    lines.push('')
    lines.push(`- 已分配需求点：${mat.assignedCount} / ${pts.demands.length}`)
    lines.push(`- 总物资重量：${mat.totalWeight} kg`)
    lines.push(`- 最高优先级：${priorityLabel(mat.highestPriority)}`)

    return lines.join('\n')
  }

  // 生成模块三的 Markdown 片段
  function generateModule3Section() {
    const uavs = useUavsStore()
    const pts = usePointsStore()
    const mat = useMaterialsStore()
    const lines = []

    lines.push(`# 模块三：无人机选择`)
    lines.push('')

    // ── 所有内置无人机型号参数（全量写入，供大模型参考）──
    lines.push(`## 系统内置无人机型号库`)
    lines.push('')
    if (uavs.models.length > 0) {
      lines.push(`| 品牌 | 型号 | 最大载重(kg) | 满载航程(km) | 最大速度(km/h) | 货舱容积(L) | 抗风等级 | 防护等级 | 投放方式 | 适用场景 | 说明 |`)
      lines.push(`|------|------|-------------|-------------|---------------|-----------|---------|---------|---------|----------|------|`)
      uavs.models.forEach(m => {
        lines.push(`| ${m.brand} | ${m.model} | ${m.max_payload} | ${m.range_km} | ${m.max_speed} | ${m.cabin_volume} | ${m.wind_resist}级 | ${m.ip_rating} | ${m.drop_mode} | ${m.suitable_for.join('、')} | ${m.description} |`)
      })
    } else {
      lines.push('未加载无人机型号数据')
    }
    lines.push('')

    // ── 当前选择方案 ──
    lines.push(`## 当前选择方案（共 ${uavs.totalCount} 架）`)
    lines.push('')
    if (uavs.selectedDetails.length > 0) {
      lines.push(`| 品牌 | 型号 | 数量 | 单架载重(kg) | 总载重(kg) | 航程(km) | 速度(km/h) |`)
      lines.push(`|------|------|------|-------------|-----------|---------|-----------|`)
      uavs.selectedDetails.forEach(d => {
        lines.push(`| ${d.model.brand} | ${d.model.model} | ${d.quantity} | ${d.model.max_payload} | ${d.model.max_payload * d.quantity} | ${d.model.range_km} | ${d.model.max_speed} |`)
      })
    } else {
      lines.push('未选择无人机')
    }
    lines.push('')

    // 需求概览
    lines.push(`## 需求概览`)
    lines.push('')
    lines.push(`- 需求点数量：${pts.demands.length} 个`)
    lines.push(`- 物资总重量：${mat.totalWeight} kg`)
    lines.push(`- 已选无人机总载重：${uavs.totalPayload} kg`)
    lines.push(`- 载重利用率：${uavs.totalPayload > 0 ? (mat.totalWeight / uavs.totalPayload * 100).toFixed(1) : 0}%`)
    lines.push('')

    // 评估结果
    if (uavs.assessment) {
      lines.push(`## 适配性评估`)
      lines.push('')
      lines.push(`- 总体结论：${uavs.assessment.summary.feasible ? '方案可行' : '方案存在问题'}`)
      lines.push(`- 需求总重：${uavs.assessment.summary.total_demand_weight} kg`)
      lines.push(`- 总载重能力：${uavs.assessment.summary.total_payload_capacity} kg`)
      lines.push(`- 载重利用率：${uavs.assessment.summary.load_ratio}%`)
      lines.push('')

      lines.push(`### 各机型评估`)
      lines.push('')
      uavs.assessment.uavs.forEach(uav => {
        lines.push(`#### ${uav.brand} ${uav.model_name} × ${uav.quantity}`)
        lines.push('')
        lines.push(`- 载重判断：${uav.load_status}（${uav.load_detail}）`)
        lines.push(`- 航程判断：${uav.range_status}（${uav.range_detail}）`)
        lines.push(`- 适配性：${uav.fit_status}`)
        if (uav.fit_issues.length > 0) {
          uav.fit_issues.forEach(issue => {
            lines.push(`  - ${issue}`)
          })
        }
        lines.push('')
      })

      if (uavs.assessment.suggestions.length > 0) {
        lines.push(`### 适配建议`)
        lines.push('')
        uavs.assessment.suggestions.forEach(sug => {
          const icon = sug.type === 'warning' ? '⚠' : sug.type === 'success' ? '✓' : 'ℹ'
          lines.push(`- ${icon} ${sug.content}`)
        })
        lines.push('')
      }
    }

    return lines.join('\n')
  }

  // 将某个模块的内容写入合并文件（保留其他模块内容）
  async function saveModuleSection(moduleKey) {
    const marker = MARKERS[moduleKey]
    if (!marker) return

    // 生成当前模块最新内容
    let sectionContent = ''
    if (moduleKey === 'module1') sectionContent = generateModule1Section()
    if (moduleKey === 'module2') sectionContent = generateModule2Section()
    if (moduleKey === 'module3') sectionContent = generateModule3Section()

    const taggedContent = `${marker.start}\n${sectionContent}\n${marker.end}`

    // 读取已有文件，保留其他模块内容
    let existing = ''
    try {
      const res = await loadConfig(COMBINED_FILENAME)
      existing = res.data.content
    } catch (e) {
      // 文件不存在
    }

    let newContent = ''
    const startIdx = existing.indexOf(marker.start)
    const endMarkerIdx = existing.indexOf(marker.end)

    if (startIdx !== -1 && endMarkerIdx !== -1) {
      const endIdx = endMarkerIdx + marker.end.length
      newContent = existing.substring(0, startIdx) + taggedContent + existing.substring(endIdx)
    } else {
      newContent = existing ? existing.trimEnd() + '\n\n' + taggedContent + '\n' : taggedContent + '\n'
    }

    // 更新头部时间戳
    const now = new Date()
    const ts = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    const headerPattern = /# 低空应急智慧运输 — 任务配置信息\n\n> 更新时间：.*\n\n/
    const header = `# 低空应急智慧运输 — 任务配置信息\n\n> 更新时间：${ts}\n\n`
    if (headerPattern.test(newContent)) {
      newContent = newContent.replace(headerPattern, header)
    } else {
      newContent = header + newContent
    }

    await saveConfig(COMBINED_FILENAME, newContent)
    return newContent
  }

  // 读取合并配置文件
  async function loadCombinedConfig() {
    try {
      const res = await loadConfig(COMBINED_FILENAME)
      return res.data.content
    } catch (e) {
      return ''
    }
  }

  function priorityLabel(p) {
    const map = { 1: '紧急', 2: '高', 3: '中', 4: '低', 5: '普通' }
    return map[p] || '未知'
  }

  return {
    generateModule1Section,
    generateModule2Section,
    generateModule3Section,
    saveModuleSection,
    loadCombinedConfig,
    COMBINED_FILENAME,
  }
})
