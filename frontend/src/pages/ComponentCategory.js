import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { ScoreGauge } from '@/components/shared/ScoreGauge';
import { Skeleton } from '@/components/ui/skeleton';
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from '@/components/ui/breadcrumb';
import { Sparkles, Boxes } from 'lucide-react';

export default function ComponentCategory() {
  const { categoryName } = useParams();
  const navigate = useNavigate();
  const [components, setComponents] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get('/categories'),
      api.get('/products', { params: { category: categoryName } }),
    ]).then(([catRes, prodRes]) => {
      const cat = catRes.data.find((c) => c.name === categoryName);
      setComponents(cat?.components || []);
      setProducts(prodRes.data);
    }).finally(() => setLoading(false));
  }, [categoryName]);

  return (
    <div>
      <Breadcrumb className="mb-3">
        <BreadcrumbList>
          <BreadcrumbItem><BreadcrumbLink asChild><Link to="/library">Component Library</Link></BreadcrumbLink></BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem><BreadcrumbPage>{categoryName}</BreadcrumbPage></BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <PageHeader title={categoryName} description="Click a component type to research it instantly, or browse previously researched products below." />

      <div className="mb-8">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Common Components</h3>
        <div className="flex flex-wrap gap-2">
          {components.map((c) => (
            <button
              key={c}
              onClick={() => navigate(`/search?q=${encodeURIComponent(c)}`)}
              className="flex items-center gap-1.5 rounded-full border bg-card px-3.5 py-2 text-sm font-medium transition-colors hover:border-primary/30 hover:bg-accent/40"
              data-testid={`component-chip-${c.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" /> {c}
            </button>
          ))}
        </div>
      </div>

      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Researched Products in this Category</h3>
      {loading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-24 rounded-xl" />)}</div>
      ) : products.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((p) => (
            <button
              key={p.id}
              onClick={() => navigate(`/product/${p.id}`)}
              className="flex items-center gap-3 rounded-xl border bg-card p-4 text-left transition-all hover:border-primary/30 hover:shadow-[var(--shadow-sm)]"
              data-testid="library-product-card"
            >
              <ScoreGauge score={p.engineering_score} size="sm" />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">{p.name}</p>
                <p className="truncate text-xs text-muted-foreground">{p.brand}</p>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <EmptyState icon={Boxes} title="No products researched yet" description="Click a component above to run your first AI search in this category." />
      )}
    </div>
  );
}
