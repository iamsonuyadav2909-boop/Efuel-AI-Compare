import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { CircuitBoard } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent text-primary">
        <CircuitBoard className="h-8 w-8" />
      </div>
      <h1 className="font-display text-3xl font-semibold">404</h1>
      <p className="max-w-sm text-sm text-muted-foreground">
        This module moved or you don&apos;t have access. Check the URL or head back to your dashboard.
      </p>
      <div className="mt-2 flex gap-3">
        <Button asChild data-testid="not-found-dashboard-link">
          <Link to="/dashboard">Back to Dashboard</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/search">Search Components</Link>
        </Button>
      </div>
    </div>
  );
}
