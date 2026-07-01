import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { History, Search, GitCompareArrows } from 'lucide-react';

export default function RecentSearches() {
  const navigate = useNavigate();
  const [searches, setSearches] = useState([]);
  const [compares, setCompares] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/research/history'), api.get('/compare/history')])
      .then(([s, c]) => { setSearches(s.data); setCompares(c.data); })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader title="Recent Searches" description="Your search and comparison history." />

      <Tabs defaultValue="searches">
        <TabsList>
          <TabsTrigger value="searches" data-testid="tab-recent-searches">Searches</TabsTrigger>
          <TabsTrigger value="compares" data-testid="tab-recent-compares">Comparisons</TabsTrigger>
        </TabsList>

        <TabsContent value="searches" className="mt-4">
          {loading ? (
            <Skeleton className="h-48 w-full rounded-xl" />
          ) : searches.length > 0 ? (
            <div className="space-y-2">
              {searches.map((s, i) => (
                <button
                  key={i}
                  onClick={() => navigate(`/search?q=${encodeURIComponent(s.query)}`)}
                  className="flex w-full items-center justify-between rounded-lg border bg-card p-4 text-left transition-colors hover:border-primary/30"
                  data-testid="recent-search-history-item"
                >
                  <div className="flex items-center gap-3">
                    <History className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-semibold">{s.query}</p>
                      <p className="text-xs text-muted-foreground">{s.category} · Top pick: {s.top_product}</p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">{new Date(s.created_at).toLocaleDateString()}</span>
                </button>
              ))}
            </div>
          ) : (
            <EmptyState icon={Search} title="No searches yet" description="Your AI Search history will appear here." action={<Button onClick={() => navigate('/search')}>Search Components</Button>} />
          )}
        </TabsContent>

        <TabsContent value="compares" className="mt-4">
          {loading ? (
            <Skeleton className="h-48 w-full rounded-xl" />
          ) : compares.length > 0 ? (
            <div className="space-y-2">
              {compares.map((c, i) => (
                <div key={i} className="rounded-lg border bg-card p-4" data-testid="recent-compare-history-item">
                  <div className="flex items-center gap-2">
                    <GitCompareArrows className="h-4 w-4 text-muted-foreground" />
                    <p className="text-sm font-semibold">{c.product_names?.join(' vs ')}</p>
                  </div>
                  {c.category && <Badge variant="secondary" className="mt-2 text-[10px]">{c.category}</Badge>}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={GitCompareArrows} title="No comparisons yet" description="Your comparison history will appear here." action={<Button onClick={() => navigate('/compare')}>Compare Components</Button>} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
