import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { PageHeader } from '@/components/shared/PageHeader';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { CheckCircle2, AlertTriangle, Sun, Moon, User, Mail, ShieldCheck } from 'lucide-react';

export default function Settings() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    api.get('/dashboard/summary').then((res) => setApiStatus(res.data.api_status)).catch(() => {});
  }, []);

  const initials = (user?.name || 'U').split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();

  return (
    <div className="max-w-3xl">
      <PageHeader title="Settings" description="Manage your profile, appearance, and view integration status." />

      <div className="space-y-6">
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-display text-sm font-semibold">Profile</h3>
          <div className="flex items-center gap-4">
            <Avatar className="h-14 w-14">
              <AvatarFallback className="bg-primary text-lg text-primary-foreground">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{user?.name}</p>
              <p className="flex items-center gap-1.5 text-sm text-muted-foreground"><Mail className="h-3.5 w-3.5" /> {user?.email}</p>
              <Badge variant="secondary" className="mt-1.5 gap-1 capitalize"><ShieldCheck className="h-3 w-3" /> {user?.role}</Badge>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-display text-sm font-semibold">Appearance</h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              <Label htmlFor="theme-switch">Dark Mode</Label>
            </div>
            <Switch id="theme-switch" checked={theme === 'dark'} onCheckedChange={toggleTheme} data-testid="settings-theme-switch" />
          </div>
        </div>

        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-1 font-display text-sm font-semibold">Integration Status</h3>
          <p className="mb-4 text-xs text-muted-foreground">
            Tavily &amp; Firecrawl API keys enable live manufacturer search/extraction. Without them, the AI
            Research Engine still works using expert engineering knowledge. Contact an Admin to configure keys.
          </p>
          <div className="space-y-3">
            {apiStatus && Object.entries(apiStatus).map(([key, ok]) => (
              <div key={key} className="flex items-center justify-between rounded-lg border p-3 text-sm">
                <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                {ok ? (
                  <Badge className="gap-1 bg-success/10 text-success hover:bg-success/10"><CheckCircle2 className="h-3 w-3" /> Configured</Badge>
                ) : (
                  <Badge variant="outline" className="gap-1 border-warning/30 text-warning"><AlertTriangle className="h-3 w-3" /> Not configured</Badge>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
