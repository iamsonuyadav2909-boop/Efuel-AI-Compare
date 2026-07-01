import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { PageHeader } from '@/components/shared/PageHeader';
import { StatCard } from '@/components/shared/StatCard';
import { ScoreGauge } from '@/components/shared/ScoreGauge';
import { EmptyState } from '@/components/shared/EmptyState';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';
import {
  Search, Sparkles, GitCompareArrows, ClipboardList, MessageSquareText, History,
  Star, TrendingUp, Activity, CheckCircle2, AlertTriangle, ArrowRight,
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  useEffect(() => {
    api.get('/dashboard/summary').then((res) => setSummary(res.data)).finally(() => setLoading(false));
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  const quickActions = [
    { label: 'New AI Search', icon: Sparkles, to: '/search', testId: 'quick-action-search' },
    { label: 'Compare Products', icon: GitCompareArrows, to: '/compare', testId: 'quick-action-compare' },
    { label: 'Build a BOM', icon: ClipboardList, to: '/bom-builder', testId: 'quick-action-bom' },
    { label: 'Ask AI Assistant', icon: MessageSquareText, to: '/assistant', testId: 'quick-action-assistant' },
  ];

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name?.split(' ')[0] || 'Engineer'}`}
        description="Here's what's happening across your engineering research workspace."
      />

      <motion.form onSubmit={handleSearch} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
        className="mb-6 flex items-center gap-2 rounded-2xl border bg-card p-2 shadow-[var(--shadow-sm)]">
        <Search className="ml-2 h-4.5 w-4.5 shrink-0 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Quick search: MCB, Solar Inverter, EV Connector..."
          className="border-0 shadow-none focus-visible:ring-0"
          data-testid="dashboard-quick-search-input"
        />
        <Button type="submit" data-testid="dashboard-quick-search-button">
          <Sparkles className="h-4 w-4" /> Search
        </Button>
      </motion.form>

      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard testId="stat-total-searches" icon={Search} label="Total Searches" value={loading ? '—' : summary?.total_searches ?? 0} />
        <StatCard testId="stat-products-researched" icon={TrendingUp} label="Products Researched" value={loading ? '—' : summary?.total_products_researched ?? 0} />
        <StatCard testId="stat-favorites" icon={Star} label="Favorites" value={loading ? '—' : summary?.favorites_count ?? 0} />
        <StatCard testId="stat-system-status" icon={Activity} label="System Status" value="Operational" sub="All services running" />
      </div>

      <div className="grid gap-4 lg:grid-cols-12 lg:gap-6">
        <div className="space-y-4 lg:col-span-8">
          <div className="rounded-xl border bg-card p-5">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-base font-semibold">Top Recommended Components</h3>
              <Button variant="ghost" size="sm" onClick={() => navigate('/library')} data-testid="dashboard-view-library">
                View Library <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </div>
            {loading ? (
              <div className="grid gap-3 sm:grid-cols-2">{[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-20 rounded-lg" />)}</div>
            ) : summary?.top_recommended_products?.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {summary.top_recommended_products.map((p, i) => (
                  <div key={i} className="flex items-center gap-3 rounded-lg border p-3" data-testid="top-recommended-product-card">
                    <ScoreGauge score={p.engineering_score} size="sm" />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">{p.name}</p>
                      <p className="truncate text-xs text-muted-foreground">{p.brand} · {p.category}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState icon={TrendingUp} title="No components researched yet" description="Run your first AI Search to see top recommendations here." />
            )}
          </div>

          <div className="rounded-xl border bg-card p-5">
            <h3 className="mb-4 font-display text-base font-semibold">Latest AI Analysis</h3>
            {loading ? (
              <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 rounded-lg" />)}</div>
            ) : summary?.latest_analyses?.length > 0 ? (
              <div className="space-y-3">
                {summary.latest_analyses.map((a, i) => (
                  <button
                    key={i}
                    onClick={() => navigate(`/search?q=${encodeURIComponent(a.query)}`)}
                    className="block w-full rounded-lg border p-3 text-left transition-colors hover:border-primary/30 hover:bg-accent/40"
                    data-testid="latest-analysis-item"
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold">{a.category}</p>
                      <Badge variant="outline" className="text-[10px]">{Math.round((a.confidence || 0) * 100)}% confidence</Badge>
                    </div>
                    <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{a.summary}</p>
                  </button>
                ))}
              </div>
            ) : (
              <EmptyState icon={Sparkles} title="No AI analysis yet" description="Search a component to generate your first engineering analysis." />
            )}
          </div>
        </div>

        <div className="space-y-4 lg:col-span-4">
          <div className="rounded-xl border bg-card p-5">
            <h3 className="mb-3 font-display text-sm font-semibold">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              {quickActions.map((a) => (
                <button
                  key={a.to}
                  onClick={() => navigate(a.to)}
                  data-testid={a.testId}
                  className="flex flex-col items-center gap-1.5 rounded-lg border p-3 text-center text-xs font-medium transition-colors hover:border-primary/30 hover:bg-accent/40"
                >
                  <a.icon className="h-4.5 w-4.5 text-primary" />
                  {a.label}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <h3 className="mb-3 font-display text-sm font-semibold">API &amp; System Status</h3>
            <div className="space-y-2.5">
              {summary?.api_status && Object.entries(summary.api_status).map(([key, ok]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</span>
                  {ok ? (
                    <Badge className="gap-1 bg-success/10 text-success hover:bg-success/10"><CheckCircle2 className="h-3 w-3" /> Live</Badge>
                  ) : (
                    <Badge variant="outline" className="gap-1 border-warning/30 text-warning"><AlertTriangle className="h-3 w-3" /> Fallback</Badge>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-display text-sm font-semibold">Recent Searches</h3>
              <Button variant="ghost" size="sm" onClick={() => navigate('/recent-searches')}>View all</Button>
            </div>
            {summary?.recent_searches?.length > 0 ? (
              <div className="space-y-2">
                {summary.recent_searches.map((s, i) => (
                  <button key={i} onClick={() => navigate(`/search?q=${encodeURIComponent(s.query)}`)}
                    className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-accent/40" data-testid="recent-search-item">
                    <History className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    <span className="truncate">{s.query}</span>
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No recent searches yet.</p>
            )}
          </div>

          <div className="rounded-xl border bg-card p-5">
            <h3 className="mb-3 font-display text-sm font-semibold">Recently Compared</h3>
            {summary?.recent_compares?.length > 0 ? (
              <div className="space-y-2">
                {summary.recent_compares.map((c, i) => (
                  <div key={i} className="rounded-lg border p-2.5 text-xs">
                    <p className="font-medium">{c.product_names?.join(' vs ')}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No comparisons yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
