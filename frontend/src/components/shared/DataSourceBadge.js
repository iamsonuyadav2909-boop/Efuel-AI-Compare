import { Badge } from '@/components/ui/badge';
import { ShieldCheck } from 'lucide-react';

/** Every result the user ever sees is now strictly live/verified data - there is no
 * "AI expert knowledge" mode anymore. This badge confirms the result was grounded
 * in real, live-crawled manufacturer/search sources. */
export function DataSourceBadge({ mode, confidence, provider }) {
  const isLive = mode === 'live_search';
  if (!isLive) return null;
  return (
    <Badge
      variant="outline"
      className="gap-1.5 border-success/30 bg-success/10 text-success"
      data-testid="data-source-badge"
    >
      <ShieldCheck className="h-3 w-3" />
      Live Verified Data
      {provider && <span className="capitalize text-success/80">· {provider}</span>}
      {typeof confidence === 'number' && <span className="tabular-nums">· {Math.round(confidence * 100)}%</span>}
    </Badge>
  );
}
