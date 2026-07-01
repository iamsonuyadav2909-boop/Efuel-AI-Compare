import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api, { getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { DataSourceBadge } from '@/components/shared/DataSourceBadge';
import { ProductRankedRow, ProductDetailPanel } from '@/components/shared/ProductResultCard';
import { EmptyState } from '@/components/shared/EmptyState';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { addToBasket, removeFromBasket, isInBasket, getBasket } from '@/lib/compareBasket';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { Sparkles, Search, Loader2, GitCompareArrows, ShieldAlert, KeyRound } from 'lucide-react';

const EXAMPLE_CHIPS = [
  'MCB', 'MCCB', 'SPD', 'Contactor', 'Relay', 'Energy Meter', 'Solar Inverter',
  'DC Isolator', 'MC4', 'Solar Cable', 'EV Connector', 'SMPS', 'Power Supply', 'Cooling Fan', 'Enclosure',
];

const STEPS = ['Searching trusted sources', 'Extracting specifications', 'Scoring engineering quality', 'Ranking top products'];

export default function AISearch() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [result, setResult] = useState(null);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [favorites, setFavorites] = useState([]);
  const [basketVersion, setBasketVersion] = useState(0);
  const stepTimer = useRef(null);

  useEffect(() => {
    api.get('/favorites').then((res) => setFavorites(res.data)).catch(() => {});
    const onBasketUpdate = () => setBasketVersion((v) => v + 1);
    window.addEventListener('efuel-basket-updated', onBasketUpdate);
    return () => window.removeEventListener('efuel-basket-updated', onBasketUpdate);
  }, []);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      runSearch(q);
    }
  }, [searchParams]);

  const runSearch = async (q, forceRefresh = false) => {
    const searchQuery = (q || query).trim();
    if (!searchQuery) return;
    setLoading(true);
    setResult(null);
    setStep(0);
    stepTimer.current = setInterval(() => {
      setStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 2200);

    try {
      const res = await api.post('/research', { query: searchQuery, force_refresh: forceRefresh });
      setResult(res.data);
      setSelectedIdx(0);
    } catch (error) {
      toast.error(getErrorMessage(error, 'AI Research Engine could not process this request.'));
    } finally {
      clearInterval(stepTimer.current);
      setLoading(false);
      setStep(0);
    }
  };

  const handleFavoriteToggle = async (product) => {
    const existing = favorites.find((f) => f.product_name === product.name && f.brand === product.brand);
    if (existing) {
      await api.delete(`/favorites/${existing.id}`);
      setFavorites((f) => f.filter((x) => x.id !== existing.id));
      toast.success('Removed from favorites');
    } else {
      const res = await api.post('/favorites', {
        product_name: product.name, brand: product.brand, category: result?.category || '',
        engineering_score: product.engineering_score, query: result?.query || '',
      });
      setFavorites((f) => [...f, res.data]);
      toast.success('Added to favorites');
    }
  };

  const handleCompareToggle = (product) => {
    if (isInBasket(product)) {
      removeFromBasket(product.name, product.brand);
      toast.info('Removed from compare basket');
    } else {
      if (getBasket().length >= 4) {
        toast.error('You can compare up to 4 products at a time');
        return;
      }
      addToBasket(product, result?.category);
      toast.success('Added to compare basket');
    }
  };

  const selectedProduct = result?.products?.[selectedIdx];
  const basketCount = getBasket().length;

  return (
    <div>
      <PageHeader
        title="AI Search"
        description="Search any EV charger or solar component — the AI Research Engine handles sourcing, extraction and scoring automatically."
        actions={basketCount > 0 && (
          <Button variant="outline" onClick={() => navigate('/compare')} data-testid="go-to-compare-button">
            <GitCompareArrows className="h-4 w-4" /> Compare ({basketCount})
          </Button>
        )}
      />

      <form
        onSubmit={(e) => { e.preventDefault(); runSearch(); }}
        className="flex flex-col gap-3 sm:flex-row"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. MCB, Solar Inverter, EV Connector, Energy Meter..."
            className="pl-9 h-11 text-sm"
            data-testid="ai-search-input"
          />
        </div>
        <Button type="submit" size="lg" disabled={loading || !query.trim()} data-testid="ai-search-submit-button">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          Research Component
        </Button>
      </form>

      {!result && !loading && (
        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLE_CHIPS.map((chip) => (
            <button
              key={chip}
              onClick={() => { setQuery(chip); runSearch(chip); }}
              data-testid={`example-chip-${chip.toLowerCase().replace(/\s+/g, '-')}`}
              className="rounded-full border bg-secondary/40 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:border-primary/30 hover:bg-accent hover:text-foreground"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      <AnimatePresence mode="wait">
        {loading && (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-8">
            <div className="mb-6 flex flex-col items-center gap-2">
              {STEPS.map((s, i) => (
                <div key={s} className={`flex items-center gap-2 text-sm ${i === step ? 'font-semibold text-primary' : i < step ? 'text-muted-foreground line-through' : 'text-muted-foreground/50'}`}>
                  {i === step && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  {s}
                </div>
              ))}
            </div>
            <div className="grid gap-4 lg:grid-cols-12">
              <div className="space-y-3 lg:col-span-4">
                {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-16 w-full rounded-xl" />)}
              </div>
              <div className="lg:col-span-8">
                <Skeleton className="h-96 w-full rounded-xl" />
              </div>
            </div>
          </motion.div>
        )}

        {!loading && result && !result.no_data && (
          <motion.div key="results" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} className="mt-8">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-secondary/30 p-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="font-display text-lg font-semibold">{result.category}</h2>
                  <DataSourceBadge mode={result.data_source_mode} confidence={result.confidence} provider={result.search_provider_used} />
                </div>
                <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{result.summary}</p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => runSearch(query, true)} data-testid="refresh-research-button">
                Refresh Analysis
              </Button>
            </div>

            {result.top_recommendation && (
              <div className="mb-4 rounded-xl border border-primary/20 bg-accent/50 p-4 text-sm">
                <span className="font-semibold text-primary">Top Recommendation: </span>{result.top_recommendation}
              </div>
            )}

            <div className="grid gap-4 lg:grid-cols-12">
              <div className="space-y-2 lg:col-span-4">
                {result.products.map((p, idx) => (
                  <ProductRankedRow key={idx} product={p} active={idx === selectedIdx} onClick={() => setSelectedIdx(idx)} />
                ))}
              </div>
              <div className="lg:col-span-8">
                <ProductDetailPanel
                  product={selectedProduct}
                  isFavorite={favorites.some((f) => f.product_name === selectedProduct?.name && f.brand === selectedProduct?.brand)}
                  inCompare={selectedProduct ? isInBasket(selectedProduct) : false}
                  compareFull={basketCount >= 4}
                  onFavorite={() => handleFavoriteToggle(selectedProduct)}
                  onAddCompare={() => handleCompareToggle(selectedProduct)}
                  resultSources={result.sources}
                  lastCrawlTime={result.last_crawl_time}
                />
              </div>
            </div>
          </motion.div>
        )}

        {!loading && result && result.no_data && (
          <motion.div key="no-data" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} className="mt-8">
            <div className="mx-auto max-w-xl rounded-xl border border-warning/30 bg-warning/5 p-8 text-center" data-testid="no-live-data-state">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-warning/10 text-warning">
                <ShieldAlert className="h-6 w-6" />
              </div>
              <h3 className="font-display text-base font-semibold">No Verified Live Data Found</h3>
              <p className="mt-2 text-sm text-muted-foreground" data-testid="no-live-data-message">
                {result.message}
              </p>
              <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
                <Button variant="outline" size="sm" onClick={() => runSearch(query, true)} data-testid="retry-search-button">
                  Try Again
                </Button>
                <Button variant="ghost" size="sm" onClick={() => navigate('/admin')} data-testid="go-to-admin-integrations-button">
                  <KeyRound className="h-3.5 w-3.5" /> Configure API Keys
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {!loading && !result && (
        <div className="mt-10">
          <EmptyState
            icon={Sparkles}
            title="Search for any engineering component"
            description="Type a component name above or pick an example. The AI Research Engine will search trusted sources, extract specs, and rank the top 5 products automatically."
          />
        </div>
      )}
    </div>
  );
}
