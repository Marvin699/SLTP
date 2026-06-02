interface SectionHeaderProps {
  title: string;
  className?: string;
}

export default function SectionHeader({ title, className = '' }: SectionHeaderProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <div className="flex items-center gap-2">
        {/* Left accent bar */}
        <div
          className="w-[4px] h-[20px] rounded-full"
          style={{ backgroundColor: 'var(--accent-cyan)' }}
        />
        {/* Title text */}
        <h3
          className="text-[18px] font-bold tracking-[0.04em]"
          style={{
            fontFamily: 'var(--font-noto)',
            color: 'var(--text-primary)',
          }}
        >
          {title}
        </h3>
      </div>
      {/* Decorative gradient line */}
      <div className="section-header-line" />
    </div>
  );
}
