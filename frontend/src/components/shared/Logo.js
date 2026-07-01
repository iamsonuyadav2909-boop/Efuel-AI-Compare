import { cn } from '@/lib/utils';
import { Zap } from 'lucide-react';

export function Logo({ className, iconOnly = false, dark = false }) {
  return (
    <div className={cn('flex items-center gap-2', className)} data-testid="efuel-logo">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-[var(--shadow-sm)]">
        <Zap className="h-4.5 w-4.5" strokeWidth={2.5} size={18} />
      </div>
      {!iconOnly && (
        <span className={cn('font-display text-lg font-semibold tracking-tight', dark ? 'text-white' : 'text-foreground')}>
          EFUEL <span className="text-primary">Hub</span>
        </span>
      )}
    </div>
  );
}
