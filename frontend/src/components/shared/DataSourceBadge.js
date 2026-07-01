import { Badge } from '@/components/ui/badge';
import { Radio, BrainCircuit } from 'lucide-react';

export function DataSourceBadge({ mode, confidence }) {
  const isLive = mode === 'live_search';
  return (
    <Badge
      variant="outline"
      className={isLive ? 'gap-1.5 border-success/30 bg-success/10 text-success' : 'gap-1.5 border-info/30 bg-info/10 text-info'}
      data-testid="data-source-badge"
    >
      {isLive ? <Radio className="h-3 w-3" /> : <BrainCircuit className="h-3 w-3" />}
      {isLive ? 'Live Search Data' : 'AI Expert Knowledge'}
      {typeof confidence === 'number' && <span className="tabular-nums">· {Math.round(confidence * 100)}%</span>}
    </Badge>
  );
}
