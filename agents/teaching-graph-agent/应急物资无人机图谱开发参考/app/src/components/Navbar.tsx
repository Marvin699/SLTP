import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { motion } from 'framer-motion';

export type TabId = 'overview' | 'graph' | 'evaluation' | 'profile';

interface NavbarProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const tabs: { id: TabId; label: string }[] = [
  { id: 'overview', label: '课程总览' },
  { id: 'graph', label: '图谱展示' },
  { id: 'evaluation', label: '教学评价' },
  { id: 'profile', label: '个人画像' },
];

export default function Navbar({ activeTab, onTabChange }: NavbarProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const dateStr = format(currentTime, 'yyyy年MM月dd日 EEEE', { locale: zhCN });
  const timeStr = format(currentTime, 'HH:mm:ss');

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-[100] h-[64px] flex items-center justify-between px-6"
      style={{
        background: 'var(--bg-nav)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(0, 229, 255, 0.15)',
      }}
    >
      {/* Left: Course icon + title */}
      <div className="flex items-center gap-3">
        {/* Hexagon SVG icon */}
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <path
            d="M20 4L35.5 13V31L20 40L4.5 31V13L20 4Z"
            stroke="#00E5FF"
            strokeWidth="2"
            fill="rgba(0, 229, 255, 0.08)"
          />
          {/* Drone silhouette inside */}
          <circle cx="20" cy="18" r="5" fill="#00E5FF" fillOpacity="0.6" />
          <line x1="12" y1="18" x2="8" y2="16" stroke="#00E5FF" strokeWidth="1.5" />
          <line x1="12" y1="18" x2="8" y2="20" stroke="#00E5FF" strokeWidth="1.5" />
          <line x1="28" y1="18" x2="32" y2="16" stroke="#00E5FF" strokeWidth="1.5" />
          <line x1="28" y1="18" x2="32" y2="20" stroke="#00E5FF" strokeWidth="1.5" />
          <line x1="20" y1="23" x2="20" y2="28" stroke="#00E5FF" strokeWidth="1.5" />
        </svg>
        <div>
          <h1
            className="text-[15px] font-bold tracking-[0.04em]"
            style={{
              fontFamily: 'var(--font-noto)',
              color: 'var(--text-primary)',
            }}
          >
            智慧运输运营 · 应急物资低空智慧运输
          </h1>
        </div>
      </div>

      {/* Center: Tab buttons */}
      <div
        className="flex items-center gap-2 rounded-lg p-1"
        style={{ background: 'rgba(15, 23, 42, 0.6)' }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className="relative px-5 py-2 rounded-md text-[15px] font-medium tracking-[0.06em] transition-colors duration-200 cursor-pointer"
              style={{
                fontFamily: 'var(--font-noto)',
                color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                textShadow: isActive ? '0 0 8px rgba(0,229,255,0.3)' : 'none',
                background: isActive ? 'rgba(0, 229, 255, 0.1)' : 'transparent',
                border: isActive ? '1px solid rgba(0, 229, 255, 0.2)' : '1px solid transparent',
              }}
            >
              {tab.label}
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-2 right-2 h-[2px] rounded-full"
                  style={{ background: 'var(--accent-cyan)' }}
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Right: Date/time + semester badge */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <div
            className="text-[12px] tracking-[0.02em]"
            style={{ color: 'var(--text-secondary)' }}
          >
            {dateStr}
          </div>
          <div
            className="text-[14px] font-semibold font-mono tracking-[0.02em]"
            style={{ color: 'var(--text-accent)' }}
          >
            {timeStr}
          </div>
        </div>
        <div
          className="px-3 py-1 rounded-full text-[11px] font-semibold tracking-[0.04em]"
          style={{
            fontFamily: 'var(--font-mono)',
            background: 'rgba(0, 229, 255, 0.1)',
            color: 'var(--accent-cyan)',
            border: '1px solid rgba(0, 229, 255, 0.2)',
          }}
        >
          2026春学期
        </div>
      </div>
    </motion.nav>
  );
}
