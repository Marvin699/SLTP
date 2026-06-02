import type { ReactNode } from 'react';
import { forwardRef } from 'react';

interface PanelProps {
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
  noCorners?: boolean;
  style?: React.CSSProperties;
}

const Panel = forwardRef<HTMLDivElement, PanelProps>(
  ({ children, className = '', noPadding = false, noCorners = false, style }, ref) => {
    return (
      <div
        ref={ref}
        className={`glass-panel glass-panel-hover relative ${noCorners ? '' : 'corner-brackets'} ${className}`}
        style={{
          padding: noPadding ? 0 : undefined,
          ...style,
        }}
      >
        {!noCorners && (
          <>
            <span className="absolute bottom-0 left-0 w-[12px] h-[12px] border-l-2 border-b-2 border-[rgba(0,229,255,0.3)] rounded-bl-[2px] pointer-events-none" />
            <span className="absolute bottom-0 right-0 w-[12px] h-[12px] border-r-2 border-b-2 border-[rgba(0,229,255,0.3)] rounded-br-[2px] pointer-events-none" />
          </>
        )}
        {children}
      </div>
    );
  }
);

Panel.displayName = 'Panel';

export default Panel;
