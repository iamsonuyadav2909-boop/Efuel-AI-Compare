import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { Zap, Sun, ShieldCheck, ToggleLeft, Radio, PlugZap, Wrench, ArrowRight } from 'lucide-react';

const CATEGORY_ICONS = {
  'EV Charger': Zap,
  'Solar': Sun,
  'Electrical Protection': ShieldCheck,
  'Switchgear': ToggleLeft,
  'Communication': Radio,
  'Power Supply': PlugZap,
  'Accessories': Wrench,
};

export default function ComponentLibrary() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/categories').then((res) => setCategories(res.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Component Library"
        description="Browse by category, or click any component to run an instant AI Search."
      />
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => <Skeleton key={i} className="h-48 rounded-xl" />)}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat, i) => {
            const Icon = CATEGORY_ICONS[cat.name] || Zap;
            return (
              <motion.div
                key={cat.name}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="group cursor-pointer rounded-xl border bg-card p-5 transition-all hover:border-primary/30 hover:shadow-[var(--shadow-md)]"
                onClick={() => navigate(`/library/${encodeURIComponent(cat.name)}`)}
                data-testid={`category-card-${cat.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-lg bg-accent text-primary transition-transform group-hover:scale-105">
                  <Icon className="h-5.5 w-5.5" />
                </div>
                <h3 className="font-display text-base font-semibold">{cat.name}</h3>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {cat.components.slice(0, 4).map((c) => <Badge key={c} variant="secondary" className="text-[10px]">{c}</Badge>)}
                  {cat.components.length > 4 && <Badge variant="outline" className="text-[10px]">+{cat.components.length - 4} more</Badge>}
                </div>
                <div className="mt-4 flex items-center gap-1 text-xs font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
                  Explore <ArrowRight className="h-3 w-3" />
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
