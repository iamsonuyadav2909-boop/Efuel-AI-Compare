import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { ProductDetailPanel } from '@/components/shared/ProductResultCard';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from '@/components/ui/breadcrumb';
import { addToBasket, removeFromBasket, isInBasket, getBasket } from '@/lib/compareBasket';
import { toast } from 'sonner';
import { PackageSearch } from 'lucide-react';

export default function ProductDetail() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState([]);
  const [inCompare, setInCompare] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([api.get(`/products/${productId}`), api.get('/favorites')])
      .then(([prodRes, favRes]) => {
        setProduct(prodRes.data);
        setFavorites(favRes.data);
        setInCompare(isInBasket(prodRes.data));
      })
      .catch(() => setProduct(null))
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading) {
    return <Skeleton className="h-96 w-full rounded-xl" />;
  }

  if (!product) {
    return <EmptyState icon={PackageSearch} title="Product not found" description="This product may have been removed by an administrator." />;
  }

  const isFavorite = favorites.some((f) => f.product_name === product.name && f.brand === product.brand);

  const handleFavorite = async () => {
    const existing = favorites.find((f) => f.product_name === product.name && f.brand === product.brand);
    if (existing) {
      await api.delete(`/favorites/${existing.id}`);
      setFavorites((f) => f.filter((x) => x.id !== existing.id));
      toast.success('Removed from favorites');
    } else {
      const res = await api.post('/favorites', {
        product_name: product.name, brand: product.brand, category: product.category || '',
        engineering_score: product.engineering_score,
      });
      setFavorites((f) => [...f, res.data]);
      toast.success('Added to favorites');
    }
  };

  const handleCompare = () => {
    if (isInBasket(product)) {
      removeFromBasket(product.name, product.brand);
      setInCompare(false);
    } else {
      if (getBasket().length >= 4) { toast.error('Compare basket is full (max 4)'); return; }
      addToBasket(product, product.category);
      setInCompare(true);
    }
  };

  return (
    <div>
      <Breadcrumb className="mb-3">
        <BreadcrumbList>
          <BreadcrumbItem><BreadcrumbLink asChild><Link to="/library">Component Library</Link></BreadcrumbLink></BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem><BreadcrumbLink asChild><Link to={`/library/${encodeURIComponent(product.category)}`}>{product.category}</Link></BreadcrumbLink></BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbPage>{product.name}</BreadcrumbPage>
        </BreadcrumbList>
      </Breadcrumb>

      <ProductDetailPanel
        product={product}
        isFavorite={isFavorite}
        inCompare={inCompare}
        compareFull={getBasket().length >= 4}
        onFavorite={handleFavorite}
        onAddCompare={handleCompare}
      />
    </div>
  );
}
