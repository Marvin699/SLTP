import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactEChartsCore from 'echarts-for-react';
import * as echarts from 'echarts/core';

import Navbar from '@/components/Navbar';
import Panel from '@/components/Panel';
import SectionHeader from '@/components/SectionHeader';
import ParticleBackground from '@/components/ParticleBackground';
import type { TabId } from '@/components/Navbar';
import {
  classStats,
  tasks,
  subProjects,
  skillDimensions,
  classSkillScores,
  targetSkillScores,
  timelineData,
  weeklyParticipation,
  students,
} from '@/data/mockData';
import type { TaskData, SubProjectData } from '@/data/mockData';

/* ─── easing / animation presets ─── */
const panelEasing = [0.22, 1, 0.36, 1] as [number, number, number, number];
const tabTransition = {
  initial: { opacity: 0, scale: 0.98 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.98 },
  transition: { duration: 0.35, ease: 'easeOut' as const },
};

/* ─── Status helpers ─── */
function statusColor(status: TaskData['status']) {
  if (status === 'completed') return '#10B981';
  if (status === 'in-progress') return '#3B82F6';
  return '#64748B';
}

function statusBadge(status: TaskData['status']) {
  if (status === 'completed') {
    return { bg: 'rgba(16,185,129,0.15)', text: '#10B981', border: 'rgba(16,185,129,0.3)' };
  }
  if (status === 'in-progress') {
    return { bg: 'rgba(59,130,246,0.15)', text: '#3B82F6', border: 'rgba(59,130,246,0.3)' };
  }
  return { bg: 'rgba(100,116,139,0.15)', text: '#64748B', border: 'rgba(100,116,139,0.3)' };
}

/* ═══════════════════════════════════════════════════
   Tab 1: 课程总览 (Course Overview) — FULLY IMPLEMENTED
   ═══════════════════════════════════════════════════ */
function CourseOverview() {
  return (
    <div className="h-full flex flex-col gap-5">
      {/* Course Title Banner */}
      <CourseBanner />

      {/* Main grid: stats | tasks | class-info */}
      <div className="flex-1 grid grid-cols-[300px_1fr_340px] grid-rows-[1fr_1fr] gap-5 min-h-0">
        {/* Panel A: 班级统计 (left column, spans 2 rows) */}
        <ClassStatsPanel />

        {/* Panel B: 任务完成情况 (center, top) */}
        <TaskProgressPanel />

        {/* Panel C: 子项目状态概览 (right, top) */}
        <SubProjectPanel />

        {/* Panel D: 能力雷达图 (right, bottom) */}
        <RadarPanel />

        {/* Panel E: 学习进度总览 (bottom, spans left+center) */}
        <TimelinePanel />
      </div>
    </div>
  );
}

/* ─── Course Banner ─── */
function CourseBanner() {
  const overallProgress = Math.round(
    tasks.reduce((s, t) => s + t.completion, 0) / tasks.length
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0 }}
      className="glass-panel flex items-center justify-between h-[72px]"
      style={{ padding: '0 24px' }}
    >
      <div>
        <h2
          className="text-[22px] font-bold tracking-[0.04em]"
          style={{ fontFamily: 'var(--font-orbitron)', color: 'var(--text-primary)' }}
        >
          智慧运输运营 · 项目五：应急物资低空智慧运输
        </h2>
        <p className="text-[14px] mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          16学时 · 3个子项目 · 8个任务
        </p>
      </div>
      <div className="flex items-center gap-4 min-w-[200px]">
        <span
          className="text-[14px] font-mono font-bold"
          style={{ color: 'var(--text-accent)' }}
        >
          {overallProgress}% 完成
        </span>
        <div className="flex-1 h-[8px] rounded-full overflow-hidden" style={{ background: 'var(--bg-chart-area)' }}>
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #00B4D8, #00E5FF)' }}
            initial={{ width: 0 }}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
          />
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Panel A: 班级统计 ─── */
function ClassStatsPanel() {
  const donutOption = {
    series: [
      {
        type: 'pie',
        radius: ['60%', '80%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        emphasis: { label: { show: false } },
        labelLine: { show: false },
        data: [
          {
            value: classStats.overallCompletion,
            name: '已完成',
            itemStyle: { color: '#00E5FF' },
          },
          {
            value: 100 - classStats.overallCompletion,
            name: '未完成',
            itemStyle: { color: 'rgba(30, 58, 95, 0.4)' },
          },
        ],
        animationType: 'scale',
        animationDuration: 1000,
      },
    ],
  };

  const sparklineOption = {
    grid: { top: 4, right: 4, bottom: 4, left: 4 },
    xAxis: { type: 'category', show: false, data: ['1', '2', '3', '4', '5', '6', '7', '8'] },
    yAxis: { type: 'value', show: false },
    series: [
      {
        type: 'line',
        data: weeklyParticipation,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#00E5FF', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 229, 255, 0.25)' },
            { offset: 1, color: 'rgba(0, 229, 255, 0.02)' },
          ]),
        },
        animationDuration: 1200,
      },
    ],
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 0.1, ease: panelEasing }}
      className="row-span-2"
    >
      <Panel className="h-full flex flex-col">
        <SectionHeader title="班级统计" />

        <div className="flex-1 flex flex-col gap-5 overflow-auto">
          {/* Row 1: Total students */}
          <div className="text-center">
            <div
              className="text-[36px] font-bold tracking-[-0.02em]"
              style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-accent)' }}
            >
              {classStats.totalStudents}
              <span className="text-[18px] ml-1" style={{ color: 'var(--text-secondary)' }}>人</span>
            </div>
            <div className="text-[13px] mt-1" style={{ color: 'var(--text-secondary)' }}>
              班级总人数
            </div>
          </div>

          {/* Row 2: Gender split */}
          <div>
            <div className="flex items-center justify-center gap-8 mb-3">
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2">
                  <circle cx="12" cy="7" r="4" /><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                </svg>
                <span className="text-[18px] font-semibold font-mono" style={{ color: '#3B82F6' }}>
                  {classStats.maleCount}人
                </span>
              </div>
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#EC4899" strokeWidth="2">
                  <circle cx="12" cy="7" r="4" /><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                </svg>
                <span className="text-[18px] font-semibold font-mono" style={{ color: '#EC4899' }}>
                  {classStats.femaleCount}人
                </span>
              </div>
            </div>
            {/* Stacked gender bar */}
            <div className="h-[8px] rounded-full overflow-hidden flex" style={{ background: 'var(--bg-chart-area)' }}>
              <div
                className="h-full rounded-l-full"
                style={{ width: `${(classStats.maleCount / classStats.totalStudents) * 100}%`, background: '#3B82F6' }}
              />
              <div
                className="h-full rounded-r-full"
                style={{ width: `${(classStats.femaleCount / classStats.totalStudents) * 100}%`, background: '#EC4899' }}
              />
            </div>
            <div className="flex justify-between text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>
              <span>{(classStats.maleCount / classStats.totalStudents * 100).toFixed(1)}%</span>
              <span>{(classStats.femaleCount / classStats.totalStudents * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Row 3: Participation */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 rounded-full" style={{ background: '#10B981' }} />
                <span className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>已完成</span>
              </div>
              <div className="text-[18px] font-semibold font-mono" style={{ color: '#10B981' }}>
                {classStats.completedCount}人
              </div>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-2 h-2 rounded-full" style={{ background: '#EF4444' }} />
                <span className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>未完成</span>
              </div>
              <div className="text-[18px] font-semibold font-mono" style={{ color: '#EF4444' }}>
                {classStats.inProgressCount}人
              </div>
            </div>
            {/* Donut */}
            <div className="w-[100px] h-[100px] relative">
              <ReactEChartsCore
                option={donutOption}
                style={{ width: '100%', height: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[14px] font-bold font-mono" style={{ color: 'var(--text-accent)' }}>
                  {classStats.overallCompletion}%
                </span>
              </div>
            </div>
          </div>

          {/* Row 4: Weekly sparkline */}
          <div className="mt-auto">
            <div className="text-[12px] mb-2" style={{ color: 'var(--text-muted)' }}>每周活跃人数</div>
            <div className="h-[50px]">
              <ReactEChartsCore
                option={sparklineOption}
                style={{ width: '100%', height: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>
        </div>
      </Panel>
    </motion.div>
  );
}

/* ─── Panel B: 任务完成情况 ─── */
function TaskProgressPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2, ease: panelEasing }}
    >
      <Panel className="h-full flex flex-col">
        <SectionHeader title="任务完成情况" />
        <div className="flex-1 grid grid-cols-2 gap-3 overflow-auto min-h-0">
          {tasks.map((task, index) => (
            <TaskCard key={task.id} task={task} index={index} />
          ))}
        </div>
      </Panel>
    </motion.div>
  );
}

function TaskCard({ task, index }: { task: TaskData; index: number }) {
  const badge = statusBadge(task.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 + index * 0.08, ease: 'easeOut' }}
      className="flex gap-3 p-3 rounded-lg"
      style={{
        background: 'var(--bg-chart-area)',
        border: '1px solid rgba(0, 229, 255, 0.08)',
      }}
    >
      {/* Task number badge */}
      <div
        className="w-[28px] h-[28px] rounded-full flex items-center justify-center text-[12px] font-bold font-mono flex-shrink-0 mt-0.5"
        style={{ background: statusColor(task.status), color: '#0B1120' }}
      >
        {String(task.id).padStart(2, '0')}
      </div>

      <div className="flex-1 min-w-0">
        {/* Task name */}
        <div className="text-[13px] font-bold truncate" style={{ color: 'var(--text-primary)' }}>
          {task.name}
        </div>

        {/* Sub-project tag + status badge */}
        <div className="flex items-center gap-2 mt-1">
          <span
            className="text-[10px] px-1.5 py-0.5 rounded font-mono"
            style={{
              background: task.subProjectId === 1
                ? 'rgba(0, 229, 255, 0.1)' : task.subProjectId === 2
                  ? 'rgba(139, 92, 246, 0.1)' : 'rgba(245, 158, 11, 0.1)',
              color: task.subProjectId === 1
                ? '#00E5FF' : task.subProjectId === 2
                  ? '#8B5CF6' : '#F59E0B',
            }}
          >
            {task.subProject}
          </span>
          <span
            className="text-[10px] px-1.5 py-0.5 rounded font-mono"
            style={{ background: badge.bg, color: badge.text, border: `1px solid ${badge.border}` }}
          >
            {task.status === 'completed' ? '已完成' : task.status === 'in-progress' ? '进行中' : '未开始'}
          </span>
        </div>

        {/* Progress bar */}
        <div className="mt-2">
          <div className="h-[6px] rounded-full overflow-hidden" style={{ background: 'var(--bg-chart-area)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ background: 'linear-gradient(90deg, #3B82F6, #00E5FF)' }}
              initial={{ width: 0 }}
              animate={{ width: `${task.completion}%` }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 + index * 0.1 }}
            />
          </div>
          <div className="flex justify-between text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>
            <span>完成: {task.completedCount}/{task.totalCount}</span>
            <span>均分: {task.avgScore}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Panel C: 子项目状态概览 ─── */
function SubProjectPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 0.15, ease: panelEasing }}
    >
      <Panel className="h-full flex flex-col">
        <SectionHeader title="子项目状态概览" />
        <div className="flex-1 flex flex-col gap-3 min-h-0 overflow-auto">
          {subProjects.map((sp, i) => (
            <SubProjectCard key={sp.id} sp={sp} index={i} />
          ))}
        </div>
      </Panel>
    </motion.div>
  );
}

function SubProjectCard({ sp, index }: { sp: SubProjectData; index: number }) {
  const gaugeOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 90,
        endAngle: -270,
        pointer: { show: false },
        progress: {
          show: true,
          overlap: false,
          roundCap: true,
          clip: false,
          itemStyle: { color: sp.color },
        },
        axisLine: { lineStyle: { width: 6, color: [[1, 'rgba(30, 58, 95, 0.3)']] } },
        splitLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        detail: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          fontFamily: 'Roboto Mono',
          color: sp.color,
          formatter: '{value}%',
          offsetCenter: [0, 0],
        },
        data: [{ value: sp.completion }],
        animationDuration: 1200,
        animationDelay: 300 + index * 150,
      },
    ],
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.15 + index * 0.1, ease: panelEasing }}
      className="flex gap-3 p-3 rounded-lg"
      style={{
        background: 'var(--bg-chart-area)',
        borderLeft: `4px solid ${sp.color}`,
        border: `1px solid rgba(0, 229, 255, 0.08)`,
        borderLeftWidth: '4px',
        borderLeftColor: sp.color,
      }}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[15px] font-bold truncate" style={{ color: 'var(--text-primary)' }}>
            {sp.name}：{sp.title}
          </span>
        </div>
        <div className="flex items-center gap-3 mb-2">
          <span
            className="text-[10px] px-1.5 py-0.5 rounded font-mono"
            style={{ background: `${sp.color}18`, color: sp.color, border: `1px solid ${sp.color}40` }}
          >
            {sp.hours}学时
          </span>
          <span className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>
            {sp.taskCount}个任务
          </span>
        </div>
        {/* Mini task dots */}
        <div className="flex items-center gap-1.5 mb-2">
          {sp.tasks.map((taskId) => {
            const task = tasks.find((t) => t.id === taskId);
            const completed = task ? task.completion >= 100 : false;
            return (
              <div
                key={taskId}
                className="w-2.5 h-2.5 rounded-full"
                style={{
                  background: completed ? sp.color : 'rgba(100, 116, 139, 0.3)',
                  boxShadow: completed ? `0 0 4px ${sp.color}60` : 'none',
                }}
              />
            );
          })}
        </div>
        {/* Average score */}
        <div className="text-[18px] font-semibold font-mono" style={{ color: sp.color }}>
          {sp.avgScore}
          <span className="text-[11px] ml-1" style={{ color: 'var(--text-muted)' }}>均分</span>
        </div>
      </div>

      {/* Gauge */}
      <div className="w-[80px] h-[80px] flex-shrink-0">
        <ReactEChartsCore
          option={gaugeOption}
          style={{ width: '100%', height: '100%' }}
          opts={{ renderer: 'canvas' }}
        />
      </div>
    </motion.div>
  );
}

/* ─── Panel D: 能力雷达图 ─── */
function RadarPanel() {
  const radarOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(0, 229, 255, 0.3)',
      textStyle: { color: '#F1F5F9', fontSize: 12 },
    },
    legend: {
      data: ['班级平均', '目标标准'],
      bottom: 0,
      textStyle: { color: '#94A3B8', fontSize: 11, fontFamily: 'Noto Sans SC' },
      itemWidth: 12,
      itemHeight: 8,
    },
    radar: {
      indicator: skillDimensions.map((d) => ({ name: d, max: 100 })),
      shape: 'polygon' as const,
      radius: '65%',
      center: ['50%', '48%'],
      axisName: {
        color: '#94A3B8',
        fontSize: 11,
        fontFamily: 'Noto Sans SC',
      },
      splitLine: { lineStyle: { color: 'rgba(100, 116, 139, 0.2)' } },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 229, 255, 0.03)', 'transparent'],
        },
      },
      axisLine: { lineStyle: { color: 'rgba(100, 116, 139, 0.3)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: classSkillScores,
            name: '班级平均',
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { color: '#00E5FF', width: 2 },
            areaStyle: { color: 'rgba(0, 229, 255, 0.2)' },
            itemStyle: { color: '#00E5FF' },
          },
          {
            value: targetSkillScores,
            name: '目标标准',
            symbol: 'none',
            lineStyle: { color: '#10B981', width: 1, type: 'dashed' as const },
            areaStyle: { color: 'rgba(16, 185, 129, 0.1)' },
            itemStyle: { color: '#10B981' },
          },
        ],
        animationDuration: 1200,
        animationEasing: 'cubicOut',
      },
    ],
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: panelEasing }}
    >
      <Panel className="h-full flex flex-col">
        <SectionHeader title="课程能力模型" />
        <div className="flex-1 min-h-0">
          <ReactEChartsCore
            option={radarOption}
            style={{ width: '100%', height: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        </div>
      </Panel>
    </motion.div>
  );
}

/* ─── Panel E: 学习进度时间线 ─── */
function TimelinePanel() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.25, ease: panelEasing }}
      className="col-span-2"
    >
      <Panel className="h-full flex flex-col">
        <SectionHeader title="学习进度时间线" />
        <div className="flex-1 flex items-center min-h-0 px-4">
          <TimelineContent />
        </div>
      </Panel>
    </motion.div>
  );
}

function TimelineContent() {
  return (
    <div className="w-full relative">
      {/* Horizontal line */}
      <div
        className="absolute top-[12px] left-[12px] right-[12px] h-[2px] rounded-full"
        style={{ background: 'linear-gradient(90deg, #3B82F6, #00E5FF)' }}
      />

      {/* Nodes */}
      <div className="relative flex justify-between">
        {timelineData.map((item, i) => {
          const isCompleted = item.status === 'completed';
          const isInProgress = item.status === 'in-progress';

          return (
            <motion.div
              key={item.week}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.4 + i * 0.15, ease: 'easeOut' }}
              className="flex flex-col items-center"
              style={{ width: `${100 / timelineData.length}%` }}
            >
              {/* Week badge above */}
              <div
                className="text-[10px] px-1.5 py-0.5 rounded font-mono mb-2"
                style={{
                  background: isCompleted
                    ? 'rgba(16, 185, 129, 0.15)' : isInProgress
                      ? 'rgba(0, 229, 255, 0.15)' : 'rgba(100, 116, 139, 0.1)',
                  color: isCompleted
                    ? '#10B981' : isInProgress
                      ? '#00E5FF' : '#64748B',
                }}
              >
                第{item.week}周
              </div>

              {/* Node circle */}
              <div
                className={`w-[24px] h-[24px] rounded-full flex items-center justify-center z-10 ${isInProgress ? 'animate-pulse-glow' : ''}`}
                style={{
                  background: isCompleted
                    ? '#10B981' : isInProgress
                      ? '#00E5FF' : 'transparent',
                  border: isCompleted
                    ? '2px solid #10B981' : isInProgress
                      ? '2px solid #00E5FF' : '2px solid #64748B',
                  boxShadow: isInProgress ? '0 0 12px rgba(0, 229, 255, 0.4)' : 'none',
                }}
              >
                {isCompleted && (
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0B1120" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
                {isInProgress && (
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0B1120" strokeWidth="2.5">
                    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                  </svg>
                )}
              </div>

              {/* Task name below */}
              <div
                className="text-[10px] mt-2 text-center leading-tight max-w-[90%]"
                style={{ color: 'var(--text-secondary)' }}
              >
                {item.name.length > 8 ? item.name.slice(0, 8) + '...' : item.name}
              </div>
              <div className="text-[9px] mt-0.5 font-mono" style={{ color: 'var(--text-muted)' }}>
                {item.dateRange}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Tab 2: 图谱展示 (Graph Visualization) — PLACEHOLDER
   ═══════════════════════════════════════════════════ */
function GraphVisualization() {
  return (
    <motion.div {...tabTransition} className="h-full">
      <div className="h-full grid grid-cols-[260px_1fr_300px] gap-5">
        <Panel>
          <SectionHeader title="图谱类型" />
          <div className="flex flex-col gap-3 mt-4">
            {[
              { title: '知识图谱', subtitle: 'Knowledge Graph', color: '#00E5FF' },
              { title: '能力图谱', subtitle: 'Capability Graph', color: '#8B5CF6' },
              { title: '问题图谱', subtitle: 'Problem Graph', color: '#F59E0B' },
              { title: '思政图谱', subtitle: 'Ideology Graph', color: '#EC4899' },
            ].map((g, i) => (
              <div
                key={i}
                className="p-3 rounded-lg cursor-pointer transition-all duration-200"
                style={{
                  borderLeft: `4px solid ${g.color}`,
                  background: 'var(--bg-chart-area)',
                }}
              >
                <div className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>{g.title}</div>
                <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{g.subtitle}</div>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <div className="h-full flex items-center justify-center">
            <span className="text-[14px]" style={{ color: 'var(--text-muted)' }}>
              力导向图谱可视化区域
            </span>
          </div>
        </Panel>
        <Panel>
          <SectionHeader title="图谱详情" />
          <div className="mt-4 text-[13px]" style={{ color: 'var(--text-secondary)' }}>
            选择图谱节点查看详细信息
          </div>
        </Panel>
      </div>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════════
   Tab 3: 教学评价 (Teaching Evaluation) — PLACEHOLDER
   ═══════════════════════════════════════════════════ */
function TeachingEvaluation() {
  return (
    <motion.div {...tabTransition} className="h-full">
      <div className="h-full grid grid-cols-[1fr_340px] grid-rows-[auto_1fr_240px] gap-5">
        <Panel>
          <SectionHeader title="各任务评价数据" />
        </Panel>
        <Panel className="row-span-3">
          <SectionHeader title="技能达成度分析" />
        </Panel>
        <Panel>
          <SectionHeader title="班级平均成绩趋势" />
        </Panel>
        <Panel>
          <SectionHeader title="证书与竞赛对接" />
        </Panel>
      </div>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════════
   Tab 4: 个人画像 (Personal Profile) — PLACEHOLDER
   ═══════════════════════════════════════════════════ */
function PersonalProfile() {
  return (
    <motion.div {...tabTransition} className="h-full">
      <div className="h-full grid grid-cols-[280px_1fr_360px] grid-rows-[auto_1fr] gap-5">
        <Panel>
          <SectionHeader title="学生选择" />
          <div className="mt-2 space-y-2">
            {students.slice(0, 8).map((s) => (
              <div key={s.id} className="flex items-center gap-2 p-2 rounded-lg" style={{ background: 'var(--bg-chart-area)' }}>
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-[11px] font-bold"
                  style={{ background: 'rgba(0, 229, 255, 0.2)', color: '#00E5FF' }}>
                  {s.name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-[13px] font-medium truncate" style={{ color: 'var(--text-primary)' }}>{s.name}</div>
                  <div className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{s.id}</div>
                </div>
                <div className="text-[13px] font-mono font-semibold" style={{ color: s.score >= 85 ? '#10B981' : s.score >= 70 ? '#00E5FF' : '#EF4444' }}>
                  {s.score}
                </div>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <SectionHeader title="个人能力分析" />
        </Panel>
        <Panel>
          <SectionHeader title="任务表现详情" />
        </Panel>
        <Panel className="col-span-2">
          <SectionHeader title="个人成绩趋势" />
        </Panel>
        <Panel>
          <SectionHeader title="个人成就" />
        </Panel>
      </div>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════════
   Main Dashboard Component
   ═══════════════════════════════════════════════════ */
export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  // Keyboard shortcuts: 1/2/3/4 for tabs
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '1') setActiveTab('overview');
      if (e.key === '2') setActiveTab('graph');
      if (e.key === '3') setActiveTab('evaluation');
      if (e.key === '4') setActiveTab('profile');
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const renderTab = useCallback(() => {
    switch (activeTab) {
      case 'overview':
        return <CourseOverview key="overview" />;
      case 'graph':
        return <GraphVisualization key="graph" />;
      case 'evaluation':
        return <TeachingEvaluation key="evaluation" />;
      case 'profile':
        return <PersonalProfile key="profile" />;
    }
  }, [activeTab]);

  return (
    <div className="relative w-screen h-[100dvh] overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Background layers */}
      <ParticleBackground />

      {/* Dot grid overlay */}
      <div
        className="fixed inset-0 z-[1] pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle, rgba(0,229,255,0.04) 1px, transparent 1px)`,
          backgroundSize: '30px 30px',
        }}
      />

      {/* Hero gradient */}
      <div
        className="fixed inset-0 z-[1] pointer-events-none"
        style={{ background: 'var(--grad-hero)' }}
      />

      {/* Content layer */}
      <div className="relative z-[2] h-full flex flex-col">
        <Navbar activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Tab content area */}
        <main className="flex-1 pt-[64px] overflow-hidden">
          <div className="h-full p-5">
            <AnimatePresence mode="wait">
              {renderTab()}
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
}
