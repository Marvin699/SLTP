<template>
  <div class="s4-live">
    <div class="s4-header">
      <div class="h-left">
        <h1>渠阳镇特大水灾 · 无人机医疗救援装载 · AI智能体大屏</h1>
        <span class="h-sub">T/CAEE 0001—2026 · 6组同步装载 · 10分钟时限</span>
      </div>
      <div class="h-center">
        <div class="stage-nav">
          <el-tag :type="phase === 1 ? 'danger' : 'info'" effect="dark" size="small"
            @click="phase = 1" class="phase-tag">① 导入分工</el-tag>
          <el-tag :type="phase === 2 ? 'danger' : 'info'" effect="dark" size="small"
            @click="phase = 2" class="phase-tag">② 实操装载</el-tag>
          <el-tag :type="phase === 3 ? 'danger' : 'info'" effect="dark" size="small"
            @click="phase = 3" class="phase-tag">③ 成果定格</el-tag>
          <el-tag :type="phase === 4 ? 'danger' : 'info'" effect="dark" size="small"
            @click="phase = 4" class="phase-tag">④ 思政升华</el-tag>
        </div>
      </div>
      <div class="h-right">
        <div class="timer-box">
          <span class="timer-label">剩余时间</span>
          <span class="timer-value">{{ formatTime(remainingSec) }}</span>
        </div>
        <el-button v-if="!running" type="primary" size="large" @click="startRun">▶ 开始计时</el-button>
        <el-button v-else type="danger" size="large" plain @click="stopRun">■ 结束</el-button>
        <el-button size="large" plain @click="resetAll">⟲ 重置</el-button>
        <el-button v-if="!achievementFrozen" type="success" size="large" @click="freezeAchievement">🏆 成果定格</el-button>
        <el-tag v-if="exhibitionOn" type="warning" effect="dark" size="large">展览模式</el-tag>
        <el-button type="warning" size="small" plain @click="exhibitionOn = !exhibitionOn">
          {{ exhibitionOn ? '关闭展览' : '开启展览' }}
        </el-button>
      </div>
    </div>

    <div class="s4-grid">
      <div v-for="g in groups" :key="g.id"
        class="group-card"
        :data-gid="g.id"
        :class="{ 'has-red': groupHasLevel(g, 'red'), 'has-orange': groupHasLevel(g, 'orange'), 'has-yellow': groupHasLevel(g, 'yellow'), 'focused': focusedGroup === g.id, 'gc-card--expanded': expandedGroupId === g.id, 'gc-card--hidden': expandedGroupId !== null && expandedGroupId !== g.id }"
        @click="focusedGroup = g.id">

        <button v-if="expandedGroupId === g.id" class="el-button el-button--primary el-button--small gc-collapse-btn" @click="collapseGroup"><span>← 返回总览</span></button>

        <div class="gc-head">
          <div class="gc-badge" :style="{ background: g.color }">{{ g.id }}</div>
          <div class="gc-title">
            <div class="gc-name">{{ g.name }} · {{ g.village }}</div>
            <div class="gc-task">{{ g.task }}</div>
          </div>
          <div class="gc-stage">
            <span class="stage-dot" :class="getStageClass(g)"></span>
            <span>{{ stages[g.stage] }}</span>
          </div>
        </div>

        <div class="gc-role">
          <div class="role-row">
            <span v-for="r in g.roles" :key="r.role" class="role-chip">
              <b>{{ r.role }}</b> <i>{{ r.name }}</i>
            </span>
          </div>
        </div>

        <div class="gc-body">
          <div class="gc-video">
            <img v-if="groupStreamImgs[g.id]" :src="groupStreamImgs[g.id]" class="stream-img" />
            <video v-else :src="groupVideoSrcs[g.id] || ''" autoplay muted playsinline loop :ref="el => setVideoRef(g.id, el)"></video>
            <div class="stream-tip" style="font-size:12px;color:#94a3b8;padding:4px 8px 8px">📷 等待学生端推流…</div>
            <div class="video-placeholder">
              <span>📷 等待学生端推流…</span>
            </div>
            <canvas class="video-overlay" :ref="el => setOverlayRef(g.id, el)"></canvas>
            <div v-if="g.detections.length" class="gc-detections">
              <div v-for="(d, i) in g.detections" :key="i" class="det-tag" :style="d.style">{{ d.label }}</div>
            </div>
          </div>

          <div class="gc-score">
            <div class="score-ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.1)" stroke-width="6" fill="none" />
                <circle cx="50" cy="50" r="44" :stroke="g.scoreColor" stroke-width="6" fill="none"
                  stroke-linecap="round" :stroke-dasharray="`${g.score/100 * 276} 276`" transform="rotate(-90 50 50)" />
              </svg>
              <div class="score-val">{{ g.score }}</div>
            </div>
            <div class="score-label">当前得分</div>
            <div class="score-rfid" v-if="g.rfid">✓ {{ g.rfid.tag }}</div>
          </div>
        </div>

        <div class="gc-checklist">
          <div class="cl-title">工单标准检查</div>
          <div class="cl-list">
            <div v-for="c in g.checklist" :key="c.label" class="cl-item"
              :class="{ done: c.done, warn: c.warn }"
              @click="toggleCheck(g, c)">
              <span class="cl-box">{{ c.done ? '✓' : c.warn ? '!' : '○' }}</span>
              <span class="cl-text">{{ c.label }}</span>
            </div>
          </div>
        </div>

        <div class="gc-events">
          <div class="ev-title">
            <span>AI 事件流</span>
            <el-tag size="small" :type="groupWarnCount(g) ? 'danger' : 'success'">
              {{ groupWarnCount(g) }} 问题
            </el-tag>
          </div>
          <div class="ev-list" ref="el => setEventLogRef(g.id, el)">
            <div v-for="(ev, i) in g.events" :key="i" class="ev-item" :class="ev.level">
              <span class="ev-time">{{ ev.time }}</span>
              <span class="ev-role">{{ ev.role }}</span>
              <span class="ev-text">{{ ev.text }}</span>
            </div>
            <div v-if="!g.events.length" class="ev-empty">暂无提示 · 教师可在控制区触发</div>
          </div>
        </div>

        <div class="gc-quick">
          <button class="el-button el-button--small is-plain" @click="expandGroup(g.id)"><span>🔎 放大</span></button>
          <el-dropdown trigger="click" @command="c => emitAI(g.id, c)" style="display:inline-block">
            <el-button size="small" type="primary" plain>🔍 AI检查</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="k in g.aiKeys" :key="k.text" :command="k.text">{{ k.label }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button size="small" type="warning" plain @click="trigger(g.id, 'yellow')">⚠ 一般</el-button>
          <el-button size="small" type="danger" plain @click="trigger(g.id, 'orange')">⚡ 严重</el-button>
          <el-button size="small" type="danger" @click="trigger(g.id, 'red')">🔴 致命</el-button>
          <el-button size="small" @click="markGood(g.id)">✓ 确认合规</el-button>
          <el-button size="small" plain @click="simulateRfid(g.id)">📡 RFID</el-button>
          <el-button size="small" plain @click="pollGroupStream(g)">📷 🔄</el-button>
        </div>
      </div>
    </div>

    <div class="dvr-bar" style="display:flex;gap:12px;align-items:center;padding:12px 20px;background:#0f172a;border-top:1px solid #1e293b">
      <div style="font-weight:600;color:#f1f5f9">📼 大屏控制</div>
      <button class="el-button el-button--primary el-button--small" @click="recordAll"><span>⏺ 开始总录屏</span></button>
      <button class="el-button el-button--danger el-button--small" @click="stopRecordAll" v-if="recordingAll"><span>⏹ 停止总录屏</span></button>
      <span v-if="recordingAll" style="color:#f87171">● 录制中...</span>
    </div>

    <div class="s4-control">
      <div class="ctrl-left">
        <h3>预设事件库（工单真实场景）</h3>
        <div class="preset-list">
          <div v-for="(p, i) in presets" :key="i" class="preset-item">
            <div class="preset-head">
              <el-tag :type="levelTagType(p.level)" size="small" effect="dark">{{ levelLabel(p.level) }}</el-tag>
              <span class="preset-groups">{{ p.groupName }}</span>
            </div>
            <div class="preset-text">{{ p.text }}</div>
            <div class="preset-actions">
              <el-button size="small" @click="applyPreset(p)">对{{ p.groupName }}触发</el-button>
              <el-button size="small" text @click="applyPreset(p); checkPreset(p)">同步打勾</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="ctrl-right">
        <h3>手动触发</h3>
        <el-input v-model="manualText" placeholder="AI智能体播报内容，如：干冰不足8kg" maxlength="160" />
        <div class="ctrl-row">
          <span>等级</span>
          <el-radio-group v-model="manualLevel">
            <el-radio-button value="yellow">一般</el-radio-button>
            <el-radio-button value="orange">严重</el-radio-button>
            <el-radio-button value="red">致命</el-radio-button>
          </el-radio-group>
        </div>
        <div class="ctrl-row">
          <span>目标组</span>
          <el-checkbox-group v-model="manualGroups">
            <el-checkbox v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</el-checkbox>
          </el-checkbox-group>
        </div>
        <el-button type="primary" @click="fireManual">▶ 立即触发</el-button>

        <h3 style="margin-top: 14px">灾情事件</h3>
        <el-button size="small" type="warning" plain @click="disaster('伤员求助：2名儿童被铁钉扎伤，急需破伤风疫苗，是否优先安排？')">伤员求助</el-button>
        <el-button size="small" type="warning" plain @click="disaster('风速8m/s，货物总重量不得超过10kg，否则飞行不安全')">风速警报</el-button>
        <el-button size="small" type="warning" plain @click="disaster('霍乱疑似病例，需额外增加20盒诺氟沙星胶囊')">霍乱疑似病例</el-button>

        <h3 style="margin-top: 14px">成果定格（脚本分数）</h3>
        <div class="achievement-score">
          <div v-for="a in achievementScores" :key="a.id" class="ach-item">
            <span>{{ a.name }}</span>
            <el-input-number :model-value="a.score" :min="0" :max="100" size="small" controls-position="right"
              @change="v => a.score = v" :disabled="achievementFrozen" style="width:80px" />
          </div>
          <div v-if="achievementFrozen" class="ach-praised">脚本：御风95 揽星92 凌云90 逐日88 巡天87 长空85</div>
        </div>

        <h3 style="margin-top: 14px">📱 学生端 · 扫码进入</h3>
        <div class="stu-qr-grid">
          <div v-for="g in groups" :key="g.id" class="stu-qr-card">
            <div class="stu-qr-header" :style="{ background: g.color }">{{ g.name }}</div>
            <img :src="qrImages[g.id]" :alt="g.name" class="stu-qr-img" />
            <div class="stu-qr-task">{{ g.task }}</div>
            <div class="stu-qr-actions">
              <a :href="stuLink(g)" target="_blank" class="stu-qr-link">打开</a>
              <el-button size="small" text @click="copyStuLink(g)">复制链接</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="disasterDlg" title="灾情事件推送" width="620px" :close-on-click-modal="false">
      <div class="disaster-banner">
        <div class="disaster-icon">🚨</div>
        <div>
          <div class="disaster-title">突发灾情指令</div>
          <div class="disaster-text">{{ disasterMsg }}</div>
        </div>
      </div>
      <div class="disaster-actions">
        <el-button type="primary" @click="disasterAck('ack')">已告知各组</el-button>
        <el-button type="success" @click="disasterAck('adjust')">建议调整方案</el-button>
      </div>
    </el-dialog>

    <el-dialog v-model="rfidDlg" :title="`RFID · ${rfidGroup?.name} 扫描结果`" width="520px">
      <div v-if="rfidGroup" class="rfid-result">
        <div class="rfid-row"><b>物资：</b>{{ rfidGroup.task }}</div>
        <div class="rfid-row"><b>物资清单：</b>{{ rfidGroup.rfidDetails.items }}</div>
        <div class="rfid-row"><b>目的地：</b>{{ rfidGroup.village }}</div>
        <div class="rfid-row"><b>执行标准：</b>{{ rfidGroup.rfidDetails.standard }}</div>
        <div class="rfid-row"><b>无人机绑定：</b>{{ rfidGroup.rfidDetails.drone }}</div>
        <div class="rfid-row"><b>标签编号：</b>{{ rfidGroup.rfidDetails.tagNo }}</div>
        <div class="rfid-success">✓ 一物一码 · 全程可溯 · 已绑定无人机身份</div>
      </div>
      <template #footer>
        <el-button type="primary" @click="rfidDlg = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import QRCode from 'qrcode'

const mk = (label, warn = false, done = false) => ({ label, warn, done })

const groups = reactive([
  {
    id: 1, name: '逐日组', village: '怀渠村', task: '2-8℃ 冷链疫苗', color: '#5b8def', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '黄小懿' },
      { role: '包装员', name: '黄瑞典' },
      { role: '装载员', name: '吴榜明' },
      { role: '安全员', name: '熊丽雪' },
      { role: '数据员', name: '张心怡' },
    ],
    checklist: [
      mk('冰排铺设均匀不留空隙'),
      mk('EPE 2cm缓冲板隔离冰排与疫苗', true),
      mk('疫苗竖直摆放，瓶身间隙1cm'),
      mk('温度探头固定在箱体几何中心'),
      mk('上层缓冲板+剩余冰排'),
      mk('防水胶带密封所有缝隙'),
      mk('RFID电子标签+轻拿轻放标识'),
    ],
    aiKeys: [
      { label: '检查冰排与疫苗隔离', text: '冰排与疫苗之间必须有2cm EPE缓冲板隔离，防止疫苗直接接触冰排导致冻结失效' },
      { label: '检查温度探头位置', text: '温度探头应固定在箱体几何中心的一支疫苗瓶身上，防止温度读数不准' },
      { label: '检查密封与RFID', text: '保温箱密封条必须压实，RFID电子标签粘贴于侧面，轻拿轻放标识6面可见' },
    ],
    rfidDetails: {
      items: '重组乙型肝炎疫苗70支 · 破伤风抗毒素40支 · 30L保温箱 · 生物冰排6块 · EPE缓冲板2张 · 温度记录仪1台',
      standard: 'T/CAEE 0001—2026 第3.2条',
      drone: '百色市消防救援支队无人机A1-01',
      tagNo: 'UHF-RFID-SN20260718-01',
    },
    stream: null, detections: [], events: [], score: 88, scoreColor: '#42d39c',
  },
  {
    id: 2, name: '揽星组', village: '塘麻村', task: '-20℃ 深冷血浆', color: '#c77dff', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '蔡林宏' },
      { role: '包装员', name: '谭玉曼' },
      { role: '装载员', name: '梁庆蝉' },
      { role: '安全员', name: '刘华妮' },
      { role: '数据员', name: '黄雅诗' },
    ],
    checklist: [
      mk('干冰铺设≥8kg并铺平', true),
      mk('血浆袋分2组竖直放在干冰上方', true),
      mk('血浆袋之间用泡沫缓冲块隔开'),
      mk('血浆周围和上方填充剩余干冰'),
      mk('排气阀完全打开·盖子未拧紧', true),
      mk('低温温度记录仪放在血浆层中间'),
      mk('RFID+深冷物品标识'),
    ],
    aiKeys: [
      { label: '检查干冰重量与排气阀', text: '当前干冰重量5.2kg，不足8kg。排气阀必须完全打开，防止干冰升华箱内压力升高爆炸' },
      { label: '检查血浆竖直', text: '12袋血浆必须竖直放置，袋与袋之间用5×5×5cm泡沫缓冲块隔开，防止血浆分层影响质量' },
      { label: '检查温度记录仪', text: '低温温度记录仪应放在血浆层中间位置，测量范围-40℃~+20℃' },
    ],
    rfidDetails: {
      items: '新鲜冰冻血浆12袋 · 20L干冰保温箱(带排气阀) · 干冰≥8kg · 加厚PE袋2个 · 泡沫缓冲块20块 · 低温温度记录仪1台',
      standard: 'T/CAEE 0001—2026 第3.3条',
      drone: '百色市消防救援支队无人机A1-02',
      tagNo: 'UHF-RFID-SN20260718-02',
    },
    stream: null, detections: [], events: [], score: 92, scoreColor: '#42d39c',
  },
  {
    id: 3, name: '驭风组', village: '坡乐村', task: '避光防潮抗生素', color: '#6be6a1', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '王艳' },
      { role: '包装员', name: '莫经玉' },
      { role: '装载员', name: '陆荣旭' },
      { role: '安全员', name: '邹丽丽' },
      { role: '数据员', name: '陈庆业' },
    ],
    checklist: [
      mk('每瓶单独装入铝箔袋挤出空气密封'),
      mk('每层之间铺黑色避光纸', true),
      mk('EPE缓冲材料填满所有空隙'),
      mk('整箱外部包裹黑色塑料膜', true),
      mk('防水胶带密封所有缝隙'),
      mk('RFID+避光防潮标识'),
    ],
    aiKeys: [
      { label: '检查双重避光包装', text: 'WS/T823-2023第4.2条：光敏感药品必须采用"单个铝箔袋+整箱黑色塑料膜"双重防护，装箱时每放一层铺一层黑色避光纸' },
      { label: '检查缝隙密封', text: '防水胶带密封所有缝隙，防止雨水和阳光进入' },
      { label: '检查空隙填充', text: 'EPE缓冲材料填满所有空隙，确保药瓶在箱内不晃动' },
    ],
    rfidDetails: {
      items: '头孢曲松钠60瓶 · 阿莫西林钠克拉维酸钾40瓶 · 铝箔袋100个 · 黑色避光纸10张 · 防水胶带1卷 · 30L周转箱',
      standard: 'WS/T823-2023 第4.2条 + T/CAEE 0001—2026',
      drone: '百色市消防救援支队无人机A1-03',
      tagNo: 'UHF-RFID-SN20260718-03',
    },
    stream: null, detections: [], events: [], score: 95, scoreColor: '#42d39c',
  },
  {
    id: 4, name: '长空组', village: '东风村', task: '易碎防震注射液', color: '#ff9f43', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '徐阳扬' },
      { role: '包装员', name: '谢新锋' },
      { role: '装载员', name: '刘子尧' },
      { role: '安全员', name: '黄宣怡' },
      { role: '数据员', name: '张静怡' },
    ],
    checklist: [
      mk('每支安瓿瓶气泡膜包裹2层两端拧紧'),
      mk('安瓿瓶竖直插入防震卡槽每格1支'),
      mk('EPE泡沫条填满卡槽空隙', true),
      mk('上下层各铺2cm泡沫缓冲板'),
      mk('缓冲材料填满箱体四周空隙'),
      mk('六个面都贴易碎标识'),
      mk('RFID侧面粘贴'),
    ],
    aiKeys: [
      { label: '检查卡槽空隙填充', text: '关键难点！用高密度EPE泡沫条把所有卡槽空隙填满，确保安瓿瓶在卡槽里纹丝不动，泡沫条高度与安瓿瓶一致' },
      { label: '检查安瓿瓶竖直', text: '所有安瓿瓶必须竖直放置，严禁平放或倒置，防止运输中碰撞破碎' },
      { label: '检查易碎标识', text: '箱体六个面都粘贴易碎物品小心轻放标识，侧面粘贴RFID标签' },
    ],
    rfidDetails: {
      items: '盐酸肾上腺素注射液50支 · 盐酸多巴胺注射液40支 · 定制防震卡槽1个 · 气泡膜1卷 · EPE泡沫条50根 · 2cm泡沫缓冲板2张',
      standard: 'T/CAEE 0001—2026 第3.4条',
      drone: '百色市消防救援支队无人机A1-04',
      tagNo: 'UHF-RFID-SN20260718-04',
    },
    stream: null, detections: [], events: [], score: 85, scoreColor: '#ffa94d',
  },
  {
    id: 5, name: '凌云组', village: '古桥村', task: '易燃危险品消毒品', color: '#ff6b81', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '黄怀理' },
      { role: '包装员', name: '檀世长' },
      { role: '装载员', name: '卜天泽' },
      { role: '安全员', name: '许正乾' },
      { role: '数据员', name: '劳凤蓝' },
    ],
    checklist: [
      mk('酒精+84瓶口用密封胶带缠绕2圈', true),
      mk('防火隔板分左右2舱严禁混装', true),
      mk('左右舱各放防泄漏托盘'),
      mk('每个托盘底部铺2张吸附棉'),
      mk('舱室空隙缓冲材料填满'),
      mk('RFID+易燃液体+腐蚀性标识'),
    ],
    aiKeys: [
      { label: '检查酒精84分隔', text: '严重违规！酒精与84消毒液必须用防火隔板完全隔离在两个独立舱室，严禁混装，防止产生有毒气体氯气' },
      { label: '检查防静电与吸附棉', text: '操作酒精必须佩戴防静电手套，每个托盘底部铺2张吸附棉，防止泄漏腐蚀' },
      { label: '检查危险品标识', text: 'RFID标签、易燃液体标识、腐蚀性物品标识三者齐全' },
    ],
    rfidDetails: {
      items: '75%酒精12瓶 · 84消毒液12瓶 · 防火防爆箱(带隔板) · 防泄漏托盘2个 · 吸附棉4张 · 密封胶带1卷',
      standard: 'T/CAEE 0001—2026 第3.5条 + 《民用无人机安全规则》',
      drone: '百色市消防救援支队无人机A1-05',
      tagNo: 'UHF-RFID-SN20260718-05',
    },
    stream: null, detections: [], events: [], score: 90, scoreColor: '#42d39c',
  },
  {
    id: 6, name: '巡天组', village: '新和村', task: '多品类综合药品', color: '#74b9ff', stage: 1,
    rfid: null,
    roles: [
      { role: '物资管理员', name: '施金晓' },
      { role: '包装员', name: '蒙欣欣' },
      { role: '装载员', name: '韦财林' },
      { role: '安全员', name: '韦怡伶' },
      { role: '数据员', name: '邓新祥' },
    ],
    checklist: [
      mk('重下轻上：碘伏布洛芬底层'),
      mk('氨酚烷胺中层'),
      mk('纱布棉签创可贴上层'),
      mk('EPE缓冲材料填满空隙'),
      mk('重心偏差控制在±1cm', true),
      mk('RFID+综合医疗物资标识'),
    ],
    aiKeys: [
      { label: '检查重心与分层', text: '重下轻上，重心偏差必须控制在±1cm以内，否则影响无人机飞行安全；碘伏易碎，放在中间位置周围用缓冲保护' },
      { label: '检查密封与标识', text: '防水胶带密封，RFID标签侧面粘贴，综合医疗物资标识' },
      { label: '检查上层轻物', text: '纱布、棉签、创可贴放在上层，避免被重物压损' },
    ],
    rfidDetails: {
      items: '布洛芬片20瓶 · 氨酚烷胺30板 · 碘伏20瓶 · 纱布30卷 · 棉签40包 · 创可贴10盒 · 30L周转箱',
      standard: 'T/CAEE 0001—2026 第3.6条',
      drone: '百色市消防救援支队无人机A1-06',
      tagNo: 'UHF-RFID-SN20260718-06',
    },
    stream: null, detections: [], events: [], score: 87, scoreColor: '#42d39c',
  },
])

const stages = ['待开始', '物资分拣', '包装装载', '固定贴标', '重心测量', '行前检查', '完成']

const presets = [
  { groupName: '逐日组', groups: [1], level: 'yellow',
    text: '冰排与疫苗之间未放置2cm EPE缓冲板，疫苗直接接触冰排可能冻结失效，请立即铺设缓冲板隔离',
  },
  { groupName: '逐日组', groups: [1], level: 'yellow',
    text: '温度探头未固定在箱体几何中心，请固定在中心位置的一支疫苗瓶身上，确保读数准确',
  },
  { groupName: '揽星组', groups: [2], level: 'orange',
    text: '当前干冰重量 5.2kg，不足8kg。请补充干冰至8kg以上，-20℃以下是深冷血浆存储标准',
  },
  { groupName: '揽星组', groups: [2], level: 'yellow',
    text: '干冰保温箱排气阀必须完全打开，盖子轻轻扣上不要拧紧，防止干冰升华箱内压力过大爆炸',
  },
  { groupName: '驭风组', groups: [3], level: 'yellow',
    text: '包装正确 ✓ 但装箱时每层之间要铺黑色避光纸，最后箱子外面再包一层黑色塑料膜做双重避光',
  },
  { groupName: '长空组', groups: [4], level: 'orange',
    text: '安瓿瓶放对了，但卡槽之间的空隙没有填充任何材料！必须用EPE泡沫条把所有空隙填满，确保纹丝不动',
  },
  { groupName: '凌云组', groups: [5], level: 'red',
    text: '严重违规！酒精和84消毒液混装会产生有毒气体氯气，请立即用防火隔板将它们分隔在两个独立舱室！',
  },
  { groupName: '凌云组', groups: [5], level: 'yellow',
    text: '操作酒精时必须佩戴防静电手套，每个托盘底部铺2张吸附棉防止泄漏腐蚀',
  },
  { groupName: '巡天组', groups: [6], level: 'yellow',
    text: '当前重心偏左2.3cm，请调整药品位置，使箱体重心偏差控制在±1cm以内，否则影响无人机飞行安全',
  },
  { groupName: '巡天组', groups: [6], level: 'yellow',
    text: '必须遵循"重下轻上"原则：碘伏消毒液瓶放在中间位置，周围用缓冲材料保护',
  },
]

const achievementScores = reactive([
  { id: 1, name: '逐日组', score: 88 },
  { id: 2, name: '揽星组', score: 92 },
  { id: 3, name: '驭风组', score: 95 },
  { id: 4, name: '长空组', score: 85 },
  { id: 5, name: '凌云组', score: 90 },
  { id: 6, name: '巡天组', score: 87 },
])

const running = ref(false)
const remainingSec = ref(600)
const exhibitionOn = ref(false)
const focusedGroup = ref(1)
const phase = ref(2)
const achievementFrozen = ref(false)
const manualText = ref('')
const manualLevel = ref('yellow')
const manualGroups = ref([1, 2, 3, 4, 5, 6])
const disasterDlg = ref(false)
const disasterMsg = ref('')
const rfidDlg = ref(false)
const rfidGroup = ref(null)
const eventLogRefs = reactive({})
const videoRefs = reactive({})
const overlayRefs = reactive({})
const groupVideoSrcs = reactive({})
const groupStreamImgs = reactive({})
const groupPrevImgUrls = reactive({})

const groupWs = reactive({})

function liveWsUrl() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${location.host}/api/calls/ws`
}

function connectLiveWs(g) {
  try {
    const ws = new WebSocket(liveWsUrl())
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({ role: 'live', group_id: g.id }))
    })
    ws.addEventListener('message', (ev) => {
      try {
        const j = JSON.parse(ev.data)
        if (j.type === 'frame' && j.data) {
          const dataUrl = `data:image/jpeg;base64,${j.data}`
          if (groupPrevImgUrls[g.id]) {
            try { URL.revokeObjectURL(groupPrevImgUrls[g.id]) } catch (_) {}
          }
          groupPrevImgUrls[g.id] = dataUrl
          g.stream = true
          groupStreamImgs[g.id] = dataUrl
        }
      } catch (_) {}
    })
    ws.addEventListener('close', () => {
      groupWs[g.id] = null
      setTimeout(() => connectLiveWs(g), 2000)
    })
    ws.addEventListener('error', () => {})
    groupWs[g.id] = ws
  } catch (_) {}
}

let runTimer = null
let scoreTick = null
let detTick = null

function formatTime(s) {
  const m = Math.floor(s / 60).toString().padStart(2, '0')
  const sec = (s % 60).toString().padStart(2, '0')
  return `${m}:${sec}`
}

function getStageClass(g) {
  const classes = ['wait', '', 'packing', 'packing', 'packing', 'packing', 'done']
  return classes[g.stage] || ''
}

function groupHasLevel(g, lv) { return g.events.some(e => e.level === lv) }
function groupWarnCount(g) { return g.events.filter(e => e.level === 'orange' || e.level === 'red').length }
function levelLabel(lv) { return lv === 'yellow' ? '一般' : lv === 'orange' ? '严重' : '致命' }
function levelTagType(lv) { return lv === 'yellow' ? 'warning' : lv === 'orange' ? 'danger' : 'danger' }

function stuHost() {
  const h = location.hostname
  if (h === 'localhost' || h === '127.0.0.1') {
    const lan = window.__ifaceIPs && window.__ifaceIPs.find(ip => ip.startsWith('192.168.'))
    if (lan) return `${location.protocol}//${lan}:${location.port}`
  }
  return location.origin
}

function stuLink(g) {
  return `${stuHost()}/evaluation/task4/student?group=${g.id}`
}

function copyStuLink(g) {
  const u = stuLink(g)
  navigator.clipboard.writeText(u).then(() => {
    ElMessage.success(`${g.name} 链接已复制`)
  }).catch(() => { ElMessage.info(u) })
}

async function loadLanIPs() {
  try {
    const r = await fetch('/__lan_ips')
    window.__ifaceIPs = await r.json()
  } catch (e) {
    window.__ifaceIPs = []
  }
}

const qrImages = reactive({})
async function buildQRs() {
  for (const g of groups) {
    try {
      qrImages[g.id] = await QRCode.toDataURL(stuLink(g), { margin: 1, scale: 3, width: 160 })
    } catch { qrImages[g.id] = '' }
  }
}

function setVideoRef(id, el) { if (el) videoRefs[id] = el }
function setOverlayRef(id, el) { if (el) overlayRefs[id] = el }
function setEventLogRef(id, el) { if (el) eventLogRefs[id] = el }

function scrollLog(id) {
  requestAnimationFrame(() => {
    const el = eventLogRefs[id]
    if (el) el.scrollTop = 0
  })
}

function emit(groupId, level, text, role = 'AI智能体') {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  const t = new Date()
  const time = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`
  g.events.unshift({ level, text, role, time })
  if (g.events.length > 20) g.events.pop()
  scrollLog(groupId)
  if (role === 'AI智能体' && text) speak(text)
  const tagColor = level === 'yellow' ? '#e6a23c' : level === 'orange' ? '#ff6b81' : '#ff4757'
  ElMessage({ message: `【${g.name}·${levelLabel(level)}】${text}`, type: level === 'yellow' ? 'warning' : 'error', duration: 4000 })
  bumpScore(g, level)
}

function bumpScore(g, level) {
  const delta = level === 'yellow' ? -2 : level === 'orange' ? -5 : -10
  g.score = Math.max(0, Math.min(100, +(g.score + delta).toFixed(1)))
  updateScoreColor(g)
}

function updateScoreColor(g) {
  g.scoreColor = g.score >= 90 ? '#42d39c' : g.score >= 75 ? '#ffa94d' : '#ff4757'
}

function speak(text) {
  try {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text.slice(0, 200))
    u.lang = 'zh-CN'; u.rate = 1.05; u.pitch = 1
    window.speechSynthesis.speak(u)
  } catch {}
}

function toggleCheck(g, c) {
  if (achievementFrozen.value) return
  if (!c.done && !c.warn) { c.warn = true }
  else if (c.warn) { c.warn = false; c.done = true }
  else { c.done = false }
  if (c.done) {
    emit(g.id, 'yellow', `${g.name} · ${c.label} 已完成 ✓`, '教师')
    g.score = Math.min(100, +(g.score + 1).toFixed(1))
    updateScoreColor(g)
  }
}

function trigger(groupId, level) {
  const g = groups.find(x => x.id === groupId)
  const pick = presets.filter(p => p.level === level && p.groups.includes(groupId))
  if (pick.length) {
    const p = pick[Math.floor(Math.random() * pick.length)]
    emit(groupId, level, p.text, 'AI智能体')
  } else {
    emit(groupId, level,
      level === 'red' ? '致命错误！立即暂停操作，当前动作存在重大安全隐患' :
      level === 'orange' ? '严重错误，请立即停止当前动作并按照工单标准流程整改' :
      '操作不规范，请参考工单标准要求修正')
  }
}

function markGood(groupId) {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  emit(groupId, 'yellow', `${g.name} 已确认当前操作符合工单标准 ✓`, '教师')
  g.score = Math.min(100, +(g.score + 2).toFixed(1))
  updateScoreColor(g)
}

function emitAI(groupId, text) {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  emit(groupId, 'yellow', text, 'AI智能体')
}

function applyPreset(p) {
  p.groups.forEach(gid => emit(gid, p.level, p.text, 'AI智能体'))
}

function checkPreset(p) {
  const gid = p.groups[0]
  const g = groups.find(x => x.id === gid)
  if (!g) return
  const map = {
    1: { '冰排': 0, '温度探头': 2, '排气阀': 0, '双重避光': 1, '空隙': 2, '酒精': 1, '重心': 4, '干冰': 0 },
  }
  for (const key in map) {
    if (p.text.includes(key) || p.text.includes(g.checklist[map[key]].label.slice(0, 4))) {
      const c = g.checklist[map[key]]
      if (c) { c.warn = false; c.done = true }
    }
  }
}

function fireManual() {
  if (!manualText.value.trim()) return
  manualGroups.value.forEach(gid => emit(gid, manualLevel.value, manualText.value.trim(), '教师'))
  manualText.value = ''
}

function disaster(msg) {
  disasterMsg.value = msg
  disasterDlg.value = true
  groups.forEach(g => emit(g.id, 'orange', `灾情指令：${msg}`, '指挥中心'))
}

function disasterAck(action) {
  disasterDlg.value = false
  emit(3, 'yellow', action === 'adjust' ? '驭风组方案调整为优先包装诺氟沙星胶囊，其他药品压缩重量应对风速限制' : '已向各组传达灾情事件', '教师')
}

function simulateRfid(groupId) {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  g.rfid = { tag: `✓ ${g.rfidDetails.tagNo.slice(-10)}` }
  rfidGroup.value = g
  rfidDlg.value = true
  emit(groupId, 'yellow', `✓ ${g.name} RFID电子标签扫描成功 · 物资名称、数量、批次、目的地、无人机绑定已上传大屏`, '教师')
  g.score = Math.min(100, +(g.score + 1.5).toFixed(1))
  updateScoreColor(g)
}

async function startCamera(g) {
  console.log('[大屏] 学生端摄像头由前端轮流拉取，无需本地开启', g.id)
}

const STREAM_POLL_MS = 1500
const streamTimers = {}

const groupVideoLatestName = reactive({})
const groupVideoBlobUrl = reactive({})

async function pollGroupStream(g) {
  try {
    const r = await fetch(`/api/calls/latest?group_id=${g.id}&t=${Date.now()}`)
    const data = await r.json()
    if (data.ok && data.item) {
      const prevName = groupVideoLatestName[g.id]
      const videoEl = videoRefs[g.id]
      g.stream = true
      if (prevName !== data.item.name) {
        groupVideoLatestName[g.id] = data.item.name
        if (groupVideoBlobUrl[g.id]) {
          try { URL.revokeObjectURL(groupVideoBlobUrl[g.id]) } catch (_) {}
        }
        try {
          const resp = await fetch(data.item.url + `?t=${Date.now()}`)
          const blob = await resp.blob()
          const burl = URL.createObjectURL(blob)
          groupVideoBlobUrl[g.id] = burl
          groupVideoSrcs[g.id] = burl
        } catch (_) {
          groupVideoSrcs[g.id] = data.item.url + `?t=${Date.now()}`
        }
      }
      if (videoEl && groupVideoSrcs[g.id]) {
        videoEl.muted = true
        videoEl.playsInline = true
        videoEl.loop = true
        if (videoEl.paused || videoEl.ended) {
          try { await videoEl.play() } catch (_) {}
        }
      }
    }
  } catch (e) {}
}

function startStreamPolling() {
  groups.forEach(g => {
    if (streamTimers[g.id]) clearInterval(streamTimers[g.id])
    streamTimers[g.id] = setInterval(() => pollGroupStream(g), STREAM_POLL_MS)
    pollGroupStream(g)
  })
}

const expandedGroupId = ref(null)
function expandGroup(id) { expandedGroupId.value = id }
function collapseGroup() { expandedGroupId.value = null }

const recordingAll = ref(false)
async function recordAll() {
  recordingAll.value = true
  ElMessage.success('大屏已进入"总录屏"模式；每路最新录像将持续刷新')
}
async function stopRecordAll() {
  recordingAll.value = false
  const r = await fetch('/api/calls/list')
  const data = await r.json()
  const listText = (data.items || []).map(i => `${i.group_id || '?'} ${i.name || ''} ${i.url}`).join('\n')
  const blob = new Blob([listText], { type: 'text/plain;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `task4_recordings_${Date.now()}.txt`
  a.click()
  ElMessage.success('已导出录像清单，请到"成果定格"中按组查看')
}

const DETECT_LIBRARY = {
  1: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['疫苗周转箱', '生物冰排', 'EPE缓冲板'],
    包装: ['疫苗瓶', '温度记录仪', '缓冲板'],
    固定: ['RFID标签', '防水胶带', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['温湿度计', '无人机挂钩', '自检表'],
  },
  2: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['深冷箱', '血浆袋', '干冰'],
    包装: ['血浆袋(竖摆)', '缓冲隔热膜'],
    固定: ['排气阀(全开)', '密封压条', 'RFID标签'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['温度计(-20℃)', '无人机挂钩', '自检表'],
  },
  3: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['抗生素盒', '铝箔袋', '避光纸'],
    包装: ['双重避光包装', '防潮干燥剂'],
    固定: ['RFID标签', '密封压条', '标识'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['湿度表', '无人机挂钩', '自检表'],
  },
  4: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['安瓿瓶', '防震卡槽', '气泡膜'],
    包装: ['卡槽就位', 'EPE泡沫条', '缓冲垫'],
    固定: ['RFID标签', '防水胶带', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['破损巡检', '无人机挂钩', '自检表'],
  },
  5: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['防火隔板', '酒精瓶', '84瓶'],
    包装: ['防火分舱', '吸附棉', '酒精/84分离'],
    固定: ['RFID标签', '防火标识', '密封压条'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['酒精检测仪', '无人机挂钩', '自检表'],
  },
  6: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['布洛芬瓶', '创可贴', '纱布'],
    包装: ['综合箱', '缓冲垫', '固定带'],
    固定: ['RFID标签', '密封压条', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['抽检', '无人机挂钩', '自检表'],
  },
}

function detColor(groupColor, label) {
  if (label.includes('员')) return '#4fc3f7'
  if (label.includes('RFID') || label.includes('标签') || label.includes('轻拿轻放') || label.includes('防火')) return '#ff6b81'
  if (label.includes('平衡') || label.includes('电子秤') || label.includes('挂钩')) return '#ffb74d'
  return groupColor
}

const trackersMap = new Map()
const lastTickMap = new Map()
const loopedMap = new Map()

function seedTrackers(group) {
  const lib = DETECT_LIBRARY[group.id] || DETECT_LIBRARY[1]
  const stage = group.stage < 2 ? '分拣' : group.stage === 2 ? '包装' : group.stage === 3 ? '固定' : group.stage === 4 ? '重心' : group.stage === 5 ? '行前' : '包装'
  const items = [
    ...(lib.person || []).slice(0, 1 + Math.floor(Math.random() * 2)),
    ...(lib[stage] || []).slice(0, 2 + Math.floor(Math.random() * 2)),
  ]
  const W = 480, H = 360
  const trs = items.map((lab, i) => ({
    id: `${group.id}_${Date.now()}_${i}`,
    label: lab,
    color: detColor(group.color, lab),
    x: 30 + Math.random() * (W - 180),
    y: 30 + Math.random() * (H - 160),
    w: lab.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40,
    h: lab.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40,
    tx: 0, ty: 0, tw: 0, th: 0,
    alpha: 0,
    created: Date.now(),
    labelChanged: Date.now(),
    conf: 0.82 + Math.random() * 0.16,
  }))
  trs.forEach(t => { t.tx = t.x; t.ty = t.y; t.tw = t.w; t.th = t.h })
  trackersMap.set(group.id, trs)
}

function tickTrackerTargets(group) {
  const trs = trackersMap.get(group.id) || []
  const W = 480, H = 360
  const lib = DETECT_LIBRARY[group.id] || DETECT_LIBRARY[1]
  const stage = group.stage < 2 ? '分拣' : group.stage === 2 ? '包装' : group.stage === 3 ? '固定' : group.stage === 4 ? '重心' : group.stage === 5 ? '行前' : '包装'
  trs.forEach(tr => {
    if (Date.now() - tr.labelChanged > 5000 && Math.random() < 0.6) {
      const pool = lib.person.concat(lib[stage] || [])
      const newLab = pool[Math.floor(Math.random() * pool.length)]
      tr.label = newLab
      tr.color = detColor(group.color, newLab)
      tr.labelChanged = Date.now()
      tr.conf = 0.82 + Math.random() * 0.16
    }
    if (Math.random() < 0.04) {
      tr.tx = 20 + Math.random() * (W - 160)
      tr.ty = 20 + Math.random() * (H - 160)
      tr.tw = tr.label.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40
      tr.th = tr.label.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40
    }
  })
  const targetCount = Math.min(7, 2 + group.stage)
  if (trs.length < targetCount && Math.random() < 0.08) {
    const pool = lib.person.concat(lib[stage] || [])
    const lab = pool[Math.floor(Math.random() * pool.length)]
    trs.push({
      id: `${group.id}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      label: lab,
      color: detColor(group.color, lab),
      x: 20 + Math.random() * (W - 160),
      y: 20 + Math.random() * (H - 160),
      w: lab.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40,
      h: lab.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40,
      tx: 0, ty: 0, tw: 0, th: 0,
      alpha: 0,
      created: Date.now(),
      labelChanged: Date.now(),
      conf: 0.82 + Math.random() * 0.16,
    })
    const n = trs.length - 1
    trs[n].tx = trs[n].x; trs[n].ty = trs[n].y; trs[n].tw = trs[n].w; trs[n].th = trs[n].h
  }
  if (trs.length > targetCount + 2 && Math.random() < 0.05) {
    const oldest = trs.reduce((a, b) => (b.created - a.created > 5000 ? b : a), trs[0])
    oldest.alpha = -1
  }
  trackersMap.set(group.id, trs.filter(t => t.alpha >= 0 || Date.now() - t.created < 25000))
}

function drawTrackers(group) {
  const overlay = overlayRefs[group.id]
  const v = videoRefs[group.id]
  if (!overlay || (!v && !group.stream)) return
  let w = 480, h = 360
  if (v && v.videoWidth && v.videoHeight) { w = v.videoWidth; h = v.videoHeight }
  if (overlay.width !== w) { overlay.width = w; overlay.height = h }
  const ctx = overlay.getContext('2d')
  ctx.clearRect(0, 0, w, h)

  const trs = trackersMap.get(group.id) || []
  trs.forEach(tr => {
    tr.x += (tr.tx - tr.x) * 0.1
    tr.y += (tr.ty - tr.y) * 0.1
    tr.w += (tr.tw - tr.w) * 0.1
    tr.h += (tr.th - tr.h) * 0.1
    if (tr.alpha < 1 && tr.alpha >= 0) tr.alpha = Math.min(1, tr.alpha + 0.06)
    if (tr.alpha < 0) tr.alpha = Math.max(-1, tr.alpha - 0.12)

    const a = tr.alpha
    if (a <= -1) return
    ctx.globalAlpha = Math.max(0, Math.min(1, a))
    ctx.lineWidth = 2
    ctx.strokeStyle = tr.color
    ctx.strokeRect(tr.x, tr.y, tr.w, tr.h)
    ctx.fillStyle = tr.color
    ctx.font = 'bold 12px -apple-system, sans-serif'
    const labelY = tr.y < 18 ? tr.y + 14 : tr.y - 4
    ctx.fillText(tr.label, tr.x + 4, labelY)
    ctx.font = '10px -apple-system, sans-serif'
    ctx.fillStyle = tr.color
    ctx.globalAlpha = Math.max(0, Math.min(1, a)) * 0.7
    ctx.fillText(`置信 ${(tr.conf * 100).toFixed(0)}%`, tr.x + 4, labelY + 12)
  })
  ctx.globalAlpha = 1
}

function loopGroup(group) {
  const now = Date.now()
  const last = lastTickMap.get(group.id) || 0
  if (!trackersMap.has(group.id) || now - last > 30000) {
    seedTrackers(group)
  }
  if (now - last > 600) {
    tickTrackerTargets(group)
    lastTickMap.set(group.id, now)
  }
  drawTrackers(group)
  if (group.stream || !group.stream) {
    requestAnimationFrame(() => loopGroup(group))
  }
}

function startFakeDetection(g, noCamera = false) {
  if (!trackersMap.has(g.id) || (trackersMap.get(g.id) || []).length === 0) {
    seedTrackers(g)
  }
  if (!loopedMap.get(g.id)) {
    loopedMap.set(g.id, true)
    loopGroup(g)
  }
}

function tickScoreWave() {
  groups.forEach(g => {
    if (!running.value && !exhibitionOn.value && !achievementFrozen.value) return
    if (achievementFrozen.value) return
    const sigma = 1.2
    const drift = (g.score - 88) * -0.03
    const noise = (Math.random() - 0.5) * sigma * 2
    g.score = Math.max(0, Math.min(100, +(g.score + noise + drift).toFixed(1)))
    updateScoreColor(g)

    if (running.value) {
      const elapsed = 600 - remainingSec.value
      if (elapsed > 40) g.stage = Math.min(6, Math.max(2, 3))
      if (elapsed > 80) g.stage = Math.min(6, Math.max(3, 4))
      if (elapsed > 200) g.stage = 5
      if (elapsed > 360) g.stage = 6
      if (elapsed > 500) g.stage = 6
    }
  })
}

function startRun() {
  running.value = true
  achievementFrozen.value = false
  remainingSec.value = 600
  groups.forEach(g => {
    g.stage = 1
    g.events = []
    g.score = 85 + (Math.random() - 0.5) * 8
    g.checklist.forEach(c => { c.done = false; c.warn = false })
    g.rfid = null
    updateScoreColor(g)
  })
  phase.value = 2
  emit(0, 'yellow', '计时开始！渠阳镇特大水灾，6组立即就位，10分钟内完成标准化包装装载', '指挥中心')
  runTimer = setInterval(() => {
    if (remainingSec.value > 0) remainingSec.value--
    else { stopRun(); ElMessage.success('时间到！所有小组停止操作，请展示货盘') }
  }, 1000)
  scoreTick = setInterval(tickScoreWave, 400)
  detTick = setInterval(() => {
    groups.forEach(g => { if (g.stream) startFakeDetection(g) })
  }, 2000)
}

function freezeAchievement() {
  achievementFrozen.value = true
  phase.value = 3
  remainingSec.value = 0
  groups.forEach(g => {
    const a = achievementScores.find(x => x.id === g.id)
    if (a) g.score = a.score
    updateScoreColor(g)
    g.stage = 6
  })
  const sorted = [...groups].sort((a, b) => b.score - a.score)
  emit(0, 'yellow', `AI初步评分：${sorted.map(g => `${g.name}${g.score}`).join(' / ')} 。AI记录：缓冲材料填充不够密实、危险品标识粘贴不规范、长空组安瓿瓶包装速度偏慢`, 'AI智能体')
  speak('成果定格！驭风组95分 · 揽星组92分 · 凌云组90分 · 逐日组88分 · 巡天组87分 · 长空组85分')
  ElMessage.success('🏆 成果定格 · AI初步评分已冻结')
}

function stopRun() {
  running.value = false
  if (runTimer) clearInterval(runTimer); runTimer = null
  if (scoreTick) clearInterval(scoreTick); scoreTick = null
  if (detTick) clearInterval(detTick); detTick = null
}

function resetAll() {
  stopRun()
  achievementFrozen.value = false
  phase.value = 2
  remainingSec.value = 600
  groups.forEach(g => {
    g.events = []; g.score = 85; updateScoreColor(g); g.stage = 1; g.rfid = null
    g.checklist.forEach(c => { c.done = false; c.warn = false })
    if (g.stream) { g.stream.getTracks().forEach(t => t.stop()); g.stream = null }
  })
}

onMounted(async () => {
  await loadLanIPs()
  groups.forEach(g => updateScoreColor(g))
  await buildQRs()
  groups.forEach(g => connectLiveWs(g))
})

onUnmounted(() => {
  Object.values(streamTimers).forEach(t => clearInterval(t))
  Object.values(groupWs).forEach(ws => { try { ws.close() } catch (_) {} })
  Object.values(groupPrevImgUrls).forEach(u => { try { URL.revokeObjectURL(u) } catch (_) {} })
  stopRun()
  groups.forEach(g => {
    if (g.stream && typeof g.stream.getTracks === 'function') g.stream.getTracks().forEach(t => t.stop())
  })
  try { window.speechSynthesis.cancel() } catch {}
})
</script>

<style scoped>
.s4-live { display: flex; flex-direction: column; gap: 14px; padding: 14px; height: calc(100vh - 110px); overflow: auto; background: linear-gradient(160deg, #0a1a2e 0%, #16213e 60%, #0f3460 100%); color: #e6ebf5; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
.s4-header { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px 18px; backdrop-filter: blur(6px); flex-wrap: wrap; gap: 10px; }
.s4-header h1 { margin: 0; font-size: 17px; font-weight: 700; letter-spacing: 1px; }
.h-sub { margin-left: 10px; font-size: 11px; opacity: 0.75; }
.h-center { display: flex; gap: 8px; }
.stage-nav { display: flex; gap: 6px; }
.phase-tag { cursor: pointer; }
.h-right { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.timer-box { display: flex; flex-direction: column; align-items: center; padding: 0 14px; border-left: 1px solid rgba(255,255,255,0.15); border-right: 1px solid rgba(255,255,255,0.15); }
.timer-label { font-size: 11px; opacity: 0.6; }
.timer-value { font-family: Menlo, monospace; font-size: 24px; font-weight: 700; color: #4fc3f7; }

.s4-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; flex: 1; }
.group-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 8px; transition: all .2s; }
.group-card:hover { transform: translateY(-1px); border-color: rgba(79,195,247,0.4); }
.group-card.has-yellow { box-shadow: inset 0 0 0 1px rgba(230,162,60,0.5), 0 0 14px rgba(230,162,60,0.15); }
.group-card.has-orange { box-shadow: inset 0 0 0 1px rgba(255,107,129,0.55), 0 0 16px rgba(255,107,129,0.2); }
.group-card.has-red { box-shadow: inset 0 0 0 1px rgba(255,71,87,0.7), 0 0 20px rgba(255,71,87,0.3); }

.gc-head { display: flex; align-items: center; gap: 10px; }
.gc-badge { width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: #fff; }
.gc-name { font-weight: 700; font-size: 14px; }
.gc-task { font-size: 10px; opacity: 0.7; }
.gc-stage { display: flex; align-items: center; gap: 5px; font-size: 10px; opacity: 0.7; }
.stage-dot { width: 8px; height: 8px; border-radius: 50%; background: #555; }
.stage-dot.packing { background: #ffa94d; box-shadow: 0 0 8px #ffa94d; }
.stage-dot.done { background: #42d39c; box-shadow: 0 0 8px #42d39c; }

.gc-role { margin-top: -2px; }
.role-row { display: flex; flex-wrap: wrap; gap: 4px; }
.role-chip { font-size: 10px; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px; white-space: nowrap; }
.role-chip b { color: #4fc3f7; margin-right: 2px; }
.role-chip i { opacity: 0.75; font-style: normal; }

.gc-body { display: grid; grid-template-columns: 1fr 80px; gap: 8px; }
.gc-video { position: relative; background: #000; border-radius: 8px; aspect-ratio: 4/3; overflow: hidden; min-height: 110px; }
.gc-video video { width: 100%; height: 100%; object-fit: cover; }
.gc-video .stream-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-placeholder { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; font-size: 12px; opacity: 0.6; }
.video-overlay { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.gc-detections { position: absolute; top: 4px; left: 4px; display: flex; flex-direction: column; gap: 2px; }
.det-tag { font-size: 9px; padding: 2px 5px; background: rgba(0,0,0,0.55); border-radius: 3px; font-family: monospace; }

.gc-score { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.score-ring { position: relative; width: 68px; height: 68px; }
.score-val { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; font-family: Menlo, monospace; }
.score-label { font-size: 10px; opacity: 0.6; margin-top: 2px; }
.score-rfid { font-size: 9px; color: #42d39c; margin-top: 2px; }

.gc-checklist { background: rgba(0,0,0,0.22); border-radius: 8px; padding: 8px 10px; }
.cl-title { font-size: 11px; opacity: 0.7; margin-bottom: 4px; font-weight: 700; }
.cl-list { display: flex; flex-direction: column; gap: 2px; max-height: 120px; overflow-y: auto; }
.cl-item { display: flex; align-items: center; gap: 6px; padding: 3px 5px; border-radius: 4px; font-size: 10px; cursor: pointer; background: rgba(255,255,255,0.03); }
.cl-item.done { background: rgba(66,211,156,0.1); color: #42d39c; text-decoration: line-through; opacity: 0.8; }
.cl-item.warn { background: rgba(255,169,77,0.15); color: #ffa94d; }
.cl-box { font-size: 11px; font-family: monospace; width: 14px; }

.gc-events { background: rgba(0,0,0,0.25); border-radius: 8px; padding: 8px; }
.ev-title { display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-bottom: 4px; opacity: 0.85; }
.ev-list { max-height: 75px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
.ev-item { display: flex; gap: 5px; font-size: 11px; padding: 3px 5px; border-radius: 4px; background: rgba(255,255,255,0.04); }
.ev-item.yellow { background: rgba(230,162,60,0.18); border-left: 2px solid #e6a23c; }
.ev-item.orange { background: rgba(255,107,129,0.2); border-left: 2px solid #ff6b81; }
.ev-item.red { background: rgba(255,71,87,0.25); border-left: 2px solid #ff4757; animation: pulseRed 1.2s infinite; }
@keyframes pulseRed { 0%,100% { opacity: 1 } 50% { opacity: 0.7 } }
.ev-time { font-family: monospace; font-size: 9px; opacity: 0.6; min-width: 55px; }
.ev-role { font-weight: 700; min-width: 44px; }
.ev-empty { text-align: center; opacity: 0.5; font-size: 11px; padding: 6px 0; }

.gc-quick { display: flex; gap: 5px; flex-wrap: wrap; }

.s4-control { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px 14px; border: 1px solid rgba(255,255,255,0.08); }
.s4-control h3 { margin: 0 0 8px; font-size: 13px; }
.preset-list { display: flex; flex-direction: column; gap: 6px; max-height: 300px; overflow-y: auto; }
.preset-item { background: rgba(0,0,0,0.25); border-radius: 8px; padding: 6px 10px; }
.preset-head { display: flex; gap: 8px; align-items: center; margin-bottom: 2px; }
.preset-text { font-size: 11.5px; line-height: 1.5; }
.preset-actions { margin-top: 4px; display: flex; gap: 6px; }

.ctrl-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; font-size: 12px; }

.achievement-score { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 4px; }
.ach-item { display: flex; gap: 6px; align-items: center; font-size: 11px; background: rgba(0,0,0,0.2); padding: 3px 8px; border-radius: 5px; }
.ach-praised { font-size: 11px; color: #42d39c; margin-top: 6px; }

.disaster-banner { display: flex; gap: 14px; align-items: center; background: linear-gradient(120deg, #ff475722, #ffa94d22); border-left: 4px solid #ff4757; border-radius: 8px; padding: 12px; }
.disaster-icon { font-size: 32px; }
.disaster-title { font-weight: 700; font-size: 14px; margin-bottom: 4px; }
.disaster-text { font-size: 12px; line-height: 1.6; }
.disaster-actions { display: flex; gap: 10px; justify-content: flex-end; }

.rfid-result { display: flex; flex-direction: column; gap: 8px; }
.rfid-row { font-size: 13px; line-height: 1.8; }
.rfid-success { margin-top: 10px; padding: 10px; background: rgba(66,211,156,0.12); border-radius: 8px; color: #42d39c; font-weight: 700; text-align: center; }

.stu-qr-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 6px; }
.stu-qr-card { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 6px 6px 8px; text-align: center; }
.stu-qr-header { color: #fff; font-weight: 700; font-size: 12px; padding: 4px 6px; border-radius: 5px; margin-bottom: 4px; }
.stu-qr-img { width: 120px; height: 120px; background: #fff; border-radius: 5px; padding: 3px; }
.stu-qr-task { font-size: 10px; color: #9fb3c8; margin-top: 3px; }
.stu-qr-actions { margin-top: 3px; display: flex; justify-content: center; gap: 6px; }
.stu-qr-link { color: #f8c537; font-size: 11px; text-decoration: none; }
.stu-qr-link:hover { text-decoration: underline; }

.group-card.gc-card--expanded {
  position: fixed !important; inset: 0 !important; z-index: 9999 !important;
  width: 100vw !important; height: 100vh !important;
  background: rgba(10,15,25,0.96);
  display: flex !important; flex-direction: column;
}
.group-card.gc-card--hidden { display: none !important; }
.gc-collapse-btn { position: absolute; top: 12px; right: 12px; z-index: 10; }
</style>