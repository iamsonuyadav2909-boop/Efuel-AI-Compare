import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { ScoreGauge } from '@/components/shared/ScoreGauge';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getBasket, removeFromBasket, clearBasket } from '@/lib/compareBasket';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { GitCompareArrows, X, Trophy, DollarSign, Factory, Sparkles } from 'lucide-react';

export default function Compare() {
  const navigate = useNavigate();
  const [basket, setBasket] = useState(getBasket());
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [diffOnly, setDiffOnly] = useState(false);

  useEffect(() => {
    const onUpdate = () => setBasket(getBasket());
    window.addEventListener('efuel-basket-updated', onUpdate);
    return () => window.removeEventListener('efuel-basket-updated', onUpdate);
  }, []);

  const handleRemove = (p) => {
    setBasket(removeFromBasket(p.name, p.brand));
    setResult(null);
  };

  const handleCompare = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await api.post('/compare', {
        products: basket,
        query_category: basket[0]?.category || '',
      });
      setResult(res.data);
    } catch (error) {
      toast.error(getErrorMessage(error, 'AI Compare Engine failed to generate a comparison.'));
    } finally {
      setLoading(false);
    }
  };

  const allSpecNames = result?.spec_comparison?.map((s) => s.spec_name) || [];

  return (
    <div>
      <PageHeader
        title="Compare Engine"
        description="Compare up to 4 researched components side-by-side with an AI-generated engineering recommendation."
        actions={basket.length > 0 && (
          <Button variant="outline" size="sm" onClick={() => { clearBasket(); setBasket([]); setResult(null); }} data-testid="clear-compare-basket-button">
            Clear all
          </Button>
        )}
      />

      {basket.length === 0 ? (
        <EmptyState
          icon={GitCompareArrows}
          title="No products selected for comparison"
          description="Search for components in AI Search or Component Library and click 'Compare' to add up to 4 products here."
          action={<Button onClick={() => navigate('/search')} data-testid="compare-empty-go-search">Go to AI Search</Button>}
        />
      ) : (
        <>
          <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {basket.map((p, i) => (
              <div key={i} className="relative rounded-xl border bg-card p-3" data-testid="compare-basket-item">
                <button onClick={() => handleRemove(p)} className="absolute right-2 top-2 rounded-full p-1 text-muted-foreground hover:bg-secondary hover:text-foreground" data-testid="compare-remove-item-button">
                  <X className="h-3.5 w-3.5" />
                </button>
                <div className="flex items-center gap-3">
                  <ScoreGauge score={p.engineering_score} size="sm" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{p.name}</p>
                    <p className="truncate text-xs text-muted-foreground">{p.brand}</p>
                  </div>
                </div>
              </div>
            ))}
            {basket.length < 4 && (
              <button
                onClick={() => navigate('/search')}
                className="flex items-center justify-center gap-2 rounded-xl border border-dashed p-3 text-sm text-muted-foreground hover:border-primary/30 hover:text-primary"
                data-testid="compare-add-more-button"
              >
                <Sparkles className="h-4 w-4" /> Add product
              </button>
            )}
          </div>

          <Button onClick={handleCompare} disabled={basket.length < 2 || loading} size="lg" data-testid="compare-generate-button">
            {loading ? 'Analyzing...' : `Compare ${basket.length} Products`}
          </Button>
          {basket.length < 2 && <p className="mt-2 text-xs text-muted-foreground">Add at least 2 products to compare.</p>}

          {loading && (
            <div className="mt-8 space-y-3">
              <Skeleton className="h-24 w-full rounded-xl" />
              <Skeleton className="h-64 w-full rounded-xl" />
            </div>
          )}

          {!loading && result && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-8 space-y-6">
              <div className="rounded-xl border bg-secondary/30 p-4 text-sm">{result.comparison_summary}</div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl border border-warning/30 bg-warning/10 p-4" data-testid="compare-winner-overall">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-warning"><Trophy className="h-3.5 w-3.5" /> Overall Winner</p>
                  <p className="mt-1.5 font-display font-semibold">{result.winner_overall}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{result.winner_reason}</p>
                </div>
                <div className="rounded-xl border border-success/30 bg-success/10 p-4" data-testid="compare-best-value">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-success"><DollarSign className="h-3.5 w-3.5" /> Best Value</p>
                  <p className="mt-1.5 font-display font-semibold">{result.best_value}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{result.best_value_reason}</p>
                </div>
                <div className="rounded-xl border border-info/30 bg-info/10 p-4" data-testid="compare-best-industrial">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-info"><Factory className="h-3.5 w-3.5" /> Best Industrial Fit</p>
                  <p className="mt-1.5 font-display font-semibold">{result.best_industrial}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{result.best_industrial_reason}</p>
                </div>
              </div>

              <div>
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="font-display text-base font-semibold">Specification Comparison</h3>
                  <label className="flex items-center gap-2 text-xs text-muted-foreground">
                    <input type="checkbox" checked={diffOnly} onChange={(e) => setDiffOnly(e.target.checked)} data-testid="compare-differences-toggle" />
                    Differences only
                  </label>
                </div>
                <div className="overflow-x-auto rounded-xl border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-secondary/40">
                        <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">Spec</th>
                        {basket.map((p, i) => (
                          <th key={i} className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">{p.name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {allSpecNames.map((specName, i) => {
                        const row = result.spec_comparison[i];
                        const values = basket.map((p) => row.values?.[p.name] ?? '\u2014');
                        const allSame = values.every((v) => v === values[0]);
                        if (diffOnly && allSame) return null;
                        return (
                          <tr key={i} className="border-b last:border-0">
                            <td className="p-3 font-medium">{specName}</td>
                            {values.map((v, j) => <td key={j} className="p-3 font-mono tabular-nums">{v}</td>)}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {result.feature_comparison?.length > 0 && (
                <div>
                  <h3 className="mb-3 font-display text-base font-semibold">Feature Comparison</h3>
                  <div className="space-y-2">
                    {result.feature_comparison.map((f, i) => (
                      <div key={i} className="rounded-lg border p-3 text-sm">
                        <p className="font-medium">{f.feature}</p>
                        <p className="mt-0.5 text-muted-foreground">{f.notes}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid gap-4 sm:grid-cols-2">
                {basket.map((p, i) => (
                  <div key={i} className="rounded-xl border p-4">
                    <p className="mb-2 font-display font-semibold">{p.name}</p>
                    <div className="mb-2">
                      <p className="text-xs font-semibold uppercase text-success">Advantages</p>
                      <ul className="mt-1 space-y-1 text-sm">
                        {(result.per_product_advantages?.[p.name] || []).map((a, j) => <li key={j}>• {a}</li>)}
                      </ul>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase text-destructive">Disadvantages</p>
                      <ul className="mt-1 space-y-1 text-sm">
                        {(result.per_product_disadvantages?.[p.name] || []).map((a, j) => <li key={j}>• {a}</li>)}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}
