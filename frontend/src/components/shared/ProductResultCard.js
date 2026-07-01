import { useState } from 'react';
import { cn } from '@/lib/utils';
import { ScoreGauge } from './ScoreGauge';
import { SpecTable } from './SpecTable';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { CheckCircle2, XCircle, ExternalLink, Star, GitCompareArrows, Crown } from 'lucide-react';

export function ProductRankedRow({ product, active, onClick, testId }) {
  return (
    <button
      onClick={onClick}
      data-testid={testId || 'ranked-result-row'}
      className={cn(
        'flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-all hover:border-primary/30 hover:shadow-[var(--shadow-sm)]',
        active ? 'border-primary/40 bg-accent/60 shadow-[var(--shadow-sm)]' : 'bg-card'
      )}
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-secondary font-display text-sm font-semibold">
        {product.rank}
      </div>
      <ScoreGauge score={product.engineering_score} size="sm" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold">{product.name}</p>
        <p className="truncate text-xs text-muted-foreground">{product.brand}</p>
      </div>
      {product.rank === 1 && <Crown className="h-4 w-4 shrink-0 text-warning" />}
    </button>
  );
}

export function ProductDetailPanel({ product, onFavorite, onAddCompare, isFavorite, inCompare, compareFull }) {
  const [tab, setTab] = useState('overview');
  if (!product) return null;

  return (
    <div className="rounded-xl border bg-card p-5" data-testid="product-detail-panel">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-display text-lg font-semibold">{product.name}</h3>
            <Badge variant="secondary">{product.brand}</Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{product.ai_recommendation}</p>
          {product.estimated_price_range && (
            <p className="mt-1 text-xs text-muted-foreground">Est. price: <span className="font-mono">{product.estimated_price_range}</span></p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={isFavorite ? 'default' : 'outline'}
            size="sm"
            onClick={onFavorite}
            data-testid="add-favorite-button"
          >
            <Star className={cn('h-3.5 w-3.5', isFavorite && 'fill-current')} /> {isFavorite ? 'Saved' : 'Favorite'}
          </Button>
          <Button
            variant={inCompare ? 'default' : 'outline'}
            size="sm"
            onClick={onAddCompare}
            disabled={!inCompare && compareFull}
            data-testid="add-compare-button"
          >
            <GitCompareArrows className="h-3.5 w-3.5" /> {inCompare ? 'In Compare' : 'Compare'}
          </Button>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab} className="mt-5">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" data-testid="tab-overview">Overview</TabsTrigger>
          <TabsTrigger value="specs" data-testid="tab-specs">Specs</TabsTrigger>
          <TabsTrigger value="pros-cons" data-testid="tab-pros-cons">Pros/Cons</TabsTrigger>
          <TabsTrigger value="sources" data-testid="tab-sources">Sources</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {product.score_breakdown && Object.entries(product.score_breakdown).map(([k, v]) => (
              <div key={k} className="rounded-lg border p-2.5">
                <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">{k.replace(/_/g, ' ')}</p>
                <p className="font-mono text-sm font-semibold tabular-nums">{v}/10</p>
              </div>
            ))}
          </div>
          <div>
            <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Engineering Notes</p>
            <p className="text-sm">{product.engineering_notes}</p>
          </div>
          {product.industrial_applications?.length > 0 && (
            <div>
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Industrial Applications</p>
              <div className="flex flex-wrap gap-1.5">
                {product.industrial_applications.map((a, i) => <Badge key={i} variant="secondary">{a}</Badge>)}
              </div>
            </div>
          )}
          {product.certifications?.length > 0 && (
            <div>
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Certifications</p>
              <div className="flex flex-wrap gap-1.5">
                {product.certifications.map((a, i) => <Badge key={i} variant="outline">{a}</Badge>)}
              </div>
            </div>
          )}
          {product.alternatives?.length > 0 && (
            <div>
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Alternatives</p>
              <div className="flex flex-wrap gap-1.5">
                {product.alternatives.map((a, i) => <Badge key={i} variant="secondary" className="bg-secondary/60">{a}</Badge>)}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="specs" className="mt-4">
          <SpecTable specifications={product.specifications} />
        </TabsContent>

        <TabsContent value="pros-cons" className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-success">
              <CheckCircle2 className="h-3.5 w-3.5" /> Pros
            </p>
            <ul className="space-y-1.5">
              {(product.pros || []).map((p, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-success" /> {p}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-destructive">
              <XCircle className="h-3.5 w-3.5" /> Cons
            </p>
            <ul className="space-y-1.5">
              {(product.cons || []).map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-destructive" /> {c}
                </li>
              ))}
            </ul>
          </div>
          {product.compatibility?.length > 0 && (
            <div className="sm:col-span-2">
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Compatibility</p>
              <div className="flex flex-wrap gap-1.5">
                {product.compatibility.map((c, i) => <Badge key={i} variant="secondary">{c}</Badge>)}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="sources" className="mt-4">
          {product.source_urls?.length > 0 ? (
            <ul className="space-y-2">
              {product.source_urls.map((url, i) => (
                <li key={i}>
                  <a href={url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-primary hover:underline">
                    <ExternalLink className="h-3.5 w-3.5 shrink-0" /> <span className="truncate">{url}</span>
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">
              No live source citations available for this result \u2014 generated from AI expert engineering knowledge.
              Configure Tavily &amp; Firecrawl API keys in Admin to enable live manufacturer source citations.
            </p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
