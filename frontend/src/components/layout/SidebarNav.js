import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Logo } from '@/components/shared/Logo';
import { useAuth } from '@/context/AuthContext';
import {
  LayoutDashboard, Sparkles, GitCompareArrows, Boxes, FileText,
  ClipboardList, MessageSquareText, Star, History, Settings, ShieldCheck, ChevronsLeft, ChevronsRight,
} from 'lucide-react';

const NAV_SECTIONS = [
  {
    label: 'Core',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, testId: 'sidebar-nav-dashboard' },
      { to: '/search', label: 'AI Search', icon: Sparkles, testId: 'sidebar-nav-ai-search' },
      { to: '/compare', label: 'Compare', icon: GitCompareArrows, testId: 'sidebar-nav-compare' },
      { to: '/library', label: 'Component Library', icon: Boxes, testId: 'sidebar-nav-library' },
      { to: '/documents', label: 'Documents', icon: FileText, testId: 'sidebar-nav-documents' },
      { to: '/bom-builder', label: 'BOM Builder', icon: ClipboardList, testId: 'sidebar-nav-bom' },
    ],
  },
  {
    label: 'AI',
    items: [
      { to: '/assistant', label: 'AI Assistant', icon: MessageSquareText, testId: 'sidebar-nav-assistant' },
    ],
  },
  {
    label: 'Personal',
    items: [
      { to: '/favorites', label: 'Favorites', icon: Star, testId: 'sidebar-nav-favorites' },
      { to: '/recent-searches', label: 'Recent Searches', icon: History, testId: 'sidebar-nav-recent' },
    ],
  },
  {
    label: 'System',
    items: [
      { to: '/settings', label: 'Settings', icon: Settings, testId: 'sidebar-nav-settings' },
    ],
  },
];

export function SidebarNav({ collapsed, onToggle, onNavigate }) {
  const { user } = useAuth();

  return (
    <div className={cn('flex h-full flex-col bg-sidebar text-sidebar-foreground', collapsed ? 'w-[72px]' : 'w-64')}>
      <div className={cn('flex h-14 items-center border-b px-4', collapsed && 'justify-center px-0')}>
        <Logo iconOnly={collapsed} />
      </div>
      <nav className="flex-1 space-y-5 overflow-y-auto scrollbar-thin px-3 py-4">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            {!collapsed && (
              <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                {section.label}
              </p>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onNavigate}
                  data-testid={item.testId}
                  title={collapsed ? item.label : undefined}
                  className={({ isActive }) => cn(
                    'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-foreground/5 hover:text-foreground',
                    collapsed && 'justify-center px-0',
                    isActive && 'bg-sidebar-activeBg text-foreground ring-1 ring-sidebar-active/20 hover:bg-sidebar-activeBg'
                  )}
                >
                  <item.icon className="h-4.5 w-4.5 shrink-0" size={18} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </NavLink>
              ))}
            </div>
          </div>
        ))}

        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <div>
            {!collapsed && (
              <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Admin</p>
            )}
            <NavLink
              to="/admin"
              onClick={onNavigate}
              data-testid="sidebar-nav-admin"
              title={collapsed ? 'Admin' : undefined}
              className={({ isActive }) => cn(
                'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-foreground/5 hover:text-foreground',
                collapsed && 'justify-center px-0',
                isActive && 'bg-sidebar-activeBg text-foreground ring-1 ring-sidebar-active/20'
              )}
            >
              <ShieldCheck className="h-4.5 w-4.5 shrink-0" size={18} />
              {!collapsed && <span>Admin</span>}
            </NavLink>
          </div>
        )}
      </nav>
      <button
        onClick={onToggle}
        data-testid="sidebar-collapse-toggle"
        className="hidden lg:flex items-center justify-center gap-2 border-t px-3 py-3 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        {collapsed ? <ChevronsRight className="h-4 w-4" /> : <><ChevronsLeft className="h-4 w-4" /> Collapse</>}
      </button>
    </div>
  );
}
