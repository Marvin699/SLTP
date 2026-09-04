// 小组名单（虚拟仿真视频按组绑定）
// 学生 group_no 与视频标注的 group_no 都使用这些组名；
// normalizeGroup 可将组名/序号/"第N组" 统一归一化为序号字符串做匹配
export const GROUP_NAMES = ['御风组', '揽星组', '长空组', '巡天组', '逐日组', '凌云组']

/**
 * 归一化小组标识 → 序号字符串（'1'~'6'）
 * "御风组"/"御风" → '1'；"第3组"/"3组"/"3" → '3'；无法识别时返回小写原文
 */
export function normalizeGroup(s) {
  const str = String(s || '').trim()
  if (!str) return ''
  const exact = GROUP_NAMES.indexOf(str)
  if (exact >= 0) return String(exact + 1)
  const m = str.match(/\d+/)
  if (m) return String(Number(m[0]))
  const stripped = str.replace(/组$/, '')
  const idx = GROUP_NAMES.findIndex((g) => g.replace(/组$/, '') === stripped)
  return idx >= 0 ? String(idx + 1) : str.toLowerCase()
}
