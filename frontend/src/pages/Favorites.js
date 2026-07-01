import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { ScoreGauge } from '@/components/shared/ScoreGauge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';
import { Star, X, Sparkles } from 'lucide-react';

export default function Favorites() {
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/favorites').then((res) => setFavorites(res.data)).finally(() => setLoading(false));
  }, []);

  const handleRemove = async (id) => {
    await api.delete(`/favorites/${id}`);
    setFavorites((f) => f.filter((x) => x.id !== id));
    toast.success('Removed from favorites');
  };

  return (
    <div>
      <PageHeader title="Favorites" description="Components you've saved for quick access." />

      {loading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-24 rounded-xl" />)}</div>
      ) : favorites.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {favorites.map((f) => (
            <div key={f.id} className="relative flex items-center gap-3 rounded-xl border bg-card p-4" data-testid="favorite-item-card">
              <button onClick={() => handleRemove(f.id)} className="absolute right-2 top-2 rounded-full p-1 text-muted-foreground hover:bg-secondary hover:text-foreground" data-testid="favorite-remove-button">
                <X className="h-3.5 w-3.5" />
              </button>
              <ScoreGauge score={f.engineering_score} size="sm" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{f.product_name}</p>
                <p className="truncate text-xs text-muted-foreground">{f.brand} · {f.category}</p>
                <button
                  onClick={() => navigate(`/search?q=${encodeURIComponent(f.query || f.product_name)}`)}
                  className="mt-1 flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                >
                  <Sparkles className="h-3 w-3" /> View analysis
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Star}
          title="No favorites yet"
          description="Save components you're evaluating so you can find them quickly later."
          action={<Button onClick={() => navigate('/search')}>Search Components</Button>}
        />
      )}
    </div>
  );
}
