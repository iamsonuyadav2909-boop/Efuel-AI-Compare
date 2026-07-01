import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from '@/components/ui/command';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { SidebarNav } from './SidebarNav';
import {
  Menu, Search, Bell, Sun, Moon, LogOut, Settings as SettingsIcon, User as UserIcon, AlertTriangle, CheckCircle2,
} from 'lucide-react';

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/search': 'AI Search',
  '/compare': 'Compare Engine',
  '/library': 'Component Library',
  '/documents': 'Document Library',
  '/bom-builder': 'BOM Builder',
  '/assistant': 'AI Assistant',
  '/favorites': 'Favorites',
  '/recent-searches': 'Recent Searches',
  '/settings': 'Settings',
  '/admin': 'Admin Panel',
};

function getBreadcrumb(pathname) {
  const base = Object.keys(PAGE_TITLES).find((p) => pathname.startsWith(p));
  return PAGE_TITLES[base] || 'EFUEL Engineering Hub';
}

export function Header({ onMobileMenuToggle }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [commandOpen, setCommandOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    const down = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandOpen((open) => !open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  useEffect(() => {
    api.get('/dashboard/summary').then((res) => setApiStatus(res.data.api_status)).catch(() => {});
  }, []);

  const initials = (user?.name || 'U').split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();
  const notConfiguredCount = apiStatus ? Object.values(apiStatus).filter((v) => !v).length : 0;

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden" data-testid="mobile-sidebar-toggle">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SidebarNav collapsed={false} onToggle={() => {}} />
        </SheetContent>
      </Sheet>

      <div className="flex min-w-0 flex-1 items-center gap-2">
        <span className="hidden text-sm font-medium text-muted-foreground sm:inline">EFUEL Engineering Hub</span>
        <span className="hidden text-muted-foreground/50 sm:inline">/</span>
        <span className="truncate font-display text-sm font-semibold" data-testid="breadcrumb-current-page">
          {getBreadcrumb(location.pathname)}
        </span>
      </div>

      <button
        onClick={() => setCommandOpen(true)}
        data-testid="global-search-button"
        className="hidden items-center gap-2 rounded-lg border bg-secondary/50 px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary sm:flex"
      >
        <Search className="h-3.5 w-3.5" />
        <span>Search components...</span>
        <kbd className="ml-6 rounded border bg-background px-1.5 py-0.5 text-[10px]">⌘K</kbd>
      </button>
      <Button variant="ghost" size="icon" className="sm:hidden" onClick={() => setCommandOpen(true)} data-testid="global-search-button-mobile">
        <Search className="h-5 w-5" />
      </Button>

      <CommandDialog open={commandOpen} onOpenChange={setCommandOpen}>
        <CommandInput placeholder="Search MCB, MCCB, Solar Inverter, EV Connector..." data-testid="ai-search-command-input" />
        <CommandList>
          <CommandEmpty>Press Enter to research this component with AI.</CommandEmpty>
          <CommandGroup heading="Quick Navigation">
            {Object.entries(PAGE_TITLES).map(([path, label]) => (
              <CommandItem key={path} onSelect={() => { setCommandOpen(false); navigate(path); }}>
                {label}
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>

      <Button variant="ghost" size="icon" onClick={toggleTheme} data-testid="theme-toggle">
        {theme === 'dark' ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="relative" data-testid="notification-center-button">
            <Bell className="h-4.5 w-4.5" />
            {notConfiguredCount > 0 && (
              <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-warning" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-80">
          <DropdownMenuLabel>System Notifications</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {apiStatus && Object.entries(apiStatus).map(([key, ok]) => (
            <div key={key} className="flex items-start gap-2 px-2 py-2 text-xs">
              {ok ? <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" /> : <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-warning" />}
              <span className="text-muted-foreground">
                <span className="font-medium text-foreground">{key.replace(/_/g, ' ')}</span>{' '}
                {ok ? 'operational' : '— not configured. Contact admin to enable live data.'}
              </span>
            </div>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex items-center gap-2 rounded-full outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring" data-testid="profile-menu-button">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary text-xs text-primary-foreground">{initials}</AvatarFallback>
            </Avatar>
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <p className="truncate text-sm font-medium">{user?.name}</p>
            <p className="truncate text-xs font-normal text-muted-foreground">{user?.email}</p>
            <Badge variant="secondary" className="mt-1.5 text-[10px] capitalize">{user?.role}</Badge>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => navigate('/settings')} data-testid="profile-menu-settings">
            <SettingsIcon className="h-4 w-4" /> Settings
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate('/settings')}>
            <UserIcon className="h-4 w-4" /> My Profile
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive" data-testid="logout-button">
            <LogOut className="h-4 w-4" /> Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
