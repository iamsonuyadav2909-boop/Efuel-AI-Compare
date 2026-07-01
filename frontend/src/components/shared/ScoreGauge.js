import { cn } from '@/lib/utils';

const SIZE_MAP = { sm: 56, md: 88, lg: 120 };

export function ScoreGauge({ score = 0, size = 'md', label, className }) {
  const px = SIZE_MAP[size] || SIZE_MAP.md;
  const radius = (px - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score));
  const offset = circumference - (pct / 100) * circumference;

  const color = pct >= 80 ? 'hsl(var(--success))' : pct >= 60 ? 'hsl(var(--warning))' : 'hsl(var(--destructive))';
  const band = pct >= 80 ? 'Ready' : pct >= 60 ? 'Conditional' : 'Risk';

  return (
    <div className={cn('relative flex flex-col items-center justify-center', className)} data-testid="engineering-score-gauge">
      <svg width={px} height={px} viewBox={`0 0 ${px} ${px}`} className="-rotate-90">
        <circle cx={px / 2} cy={px / 2} r={radius} stroke="hsl(var(--border))" strokeWidth="6" fill="none" />
        <circle
          cx={px / 2} cy={px / 2} r={radius}
          stroke={color}
          strokeWidth="6"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="font-display font-semibold tabular-nums" style={{ fontSize: px * 0.24 }}>{Math.round(pct)}</span>
        {size !== 'sm' && <span className="text-[10px] text-muted-foreground">{label || band}</span>}
      </div>
    </div>
  );
}
