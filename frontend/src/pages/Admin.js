import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Users, Tag, Boxes, FileText, ScrollText, KeyRound, Trash2, Plus,
  CheckCircle2, AlertTriangle,
} from 'lucide-react';

function useAdminList(endpoint) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const load = useCallback(() => {
    setLoading(true);
    api.get(endpoint).then((res) => setData(res.data)).finally(() => setLoading(false));
  }, [endpoint]);
  useEffect(() => { load(); }, [load]);
  return [data, setData, loading, load];
}

function UsersTab() {
  const [users, setUsers, loading, reload] = useAdminList('/admin/users');

  const changeRole = async (id, role) => {
    await api.put(`/admin/users/${id}/role`, null, { params: { role } });
    setUsers((u) => u.map((x) => (x.id === id ? { ...x, role } : x)));
    toast.success('Role updated');
  };

  const toggleStatus = async (id, is_active) => {
    await api.put(`/admin/users/${id}/status`, null, { params: { is_active } });
    setUsers((u) => u.map((x) => (x.id === id ? { ...x, is_active } : x)));
    toast.success(is_active ? 'User activated' : 'User disabled');
  };

  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!users.length) return <EmptyState icon={Users} title="No users found" />;

  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Active</TableHead></TableRow>
      </TableHeader>
      <TableBody>
        {users.map((u) => (
          <TableRow key={u.id} data-testid="admin-user-row">
            <TableCell className="font-medium">{u.name}</TableCell>
            <TableCell className="text-xs text-muted-foreground">{u.email}</TableCell>
            <TableCell>
              <Select value={u.role} onValueChange={(v) => changeRole(u.id, v)}>
                <SelectTrigger className="w-32" data-testid="admin-user-role-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="engineer">Engineer</SelectItem>
                  <SelectItem value="viewer">Viewer</SelectItem>
                </SelectContent>
              </Select>
            </TableCell>
            <TableCell><Switch checked={u.is_active} onCheckedChange={(v) => toggleStatus(u.id, v)} data-testid="admin-user-active-switch" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function BrandsTab() {
  const [brands, setBrands, loading] = useAdminList('/admin/brands');
  const handleDelete = async (name) => {
    await api.delete(`/admin/brands/${encodeURIComponent(name)}`);
    setBrands((b) => b.filter((x) => x.name !== name));
    toast.success('Brand removed');
  };
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!brands.length) return <EmptyState icon={Tag} title="No brands yet" description="Brands are auto-registered as products are researched." />;
  return (
    <div className="flex flex-wrap gap-2">
      {brands.map((b) => (
        <Badge key={b.name} variant="secondary" className="gap-2 py-1.5 pl-3 pr-1.5 text-sm" data-testid="admin-brand-badge">
          {b.name}
          <button onClick={() => handleDelete(b.name)} className="rounded-full p-0.5 hover:bg-background/50"><Trash2 className="h-3 w-3" /></button>
        </Badge>
      ))}
    </div>
  );
}

function CategoriesTab() {
  const [categories, setCategories, loading] = useAdminList('/admin/categories');
  const [newCat, setNewCat] = useState('');

  const handleAdd = async () => {
    if (!newCat.trim()) return;
    await api.post('/admin/categories', null, { params: { name: newCat.trim() } });
    setCategories((c) => [...c, { name: newCat.trim() }]);
    setNewCat('');
    toast.success('Category added');
  };

  const handleDelete = async (name) => {
    await api.delete(`/admin/categories/${encodeURIComponent(name)}`);
    setCategories((c) => c.filter((x) => x.name !== name));
  };

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <Input value={newCat} onChange={(e) => setNewCat(e.target.value)} placeholder="Add a custom category" data-testid="admin-new-category-input" />
        <Button onClick={handleAdd} data-testid="admin-add-category-button"><Plus className="h-4 w-4" /> Add</Button>
      </div>
      {loading ? <Skeleton className="h-32 w-full rounded-xl" /> : (
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <Badge key={c.name} variant="secondary" className="gap-2 py-1.5 pl-3 pr-1.5 text-sm">
              {c.name}
              <button onClick={() => handleDelete(c.name)} className="rounded-full p-0.5 hover:bg-background/50"><Trash2 className="h-3 w-3" /></button>
            </Badge>
          ))}
          {categories.length === 0 && <p className="text-sm text-muted-foreground">No custom categories yet — the 7 core categories are always available in the Component Library.</p>}
        </div>
      )}
    </div>
  );
}

function ProductsTab() {
  const [products, setProducts, loading] = useAdminList('/admin/products');
  const handleDelete = async (id) => {
    await api.delete(`/admin/products/${id}`);
    setProducts((p) => p.filter((x) => x.id !== id));
    toast.success('Product removed');
  };
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!products.length) return <EmptyState icon={Boxes} title="No products researched yet" />;
  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Name</TableHead><TableHead>Brand</TableHead><TableHead>Category</TableHead><TableHead>Score</TableHead><TableHead></TableHead></TableRow>
      </TableHeader>
      <TableBody>
        {products.map((p) => (
          <TableRow key={p.id} data-testid="admin-product-row">
            <TableCell className="font-medium">{p.name}</TableCell>
            <TableCell>{p.brand}</TableCell>
            <TableCell><Badge variant="outline">{p.category}</Badge></TableCell>
            <TableCell className="font-mono tabular-nums">{p.engineering_score}</TableCell>
            <TableCell>
              <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)} data-testid="admin-delete-product-button">
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function DocumentsTab() {
  const [documents, setDocuments, loading] = useAdminList('/admin/documents');
  const handleDelete = async (id) => {
    await api.delete(`/admin/documents/${id}`);
    setDocuments((d) => d.filter((x) => x.id !== id));
    toast.success('Document removed');
  };
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!documents.length) return <EmptyState icon={FileText} title="No documents yet" />;
  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Title</TableHead><TableHead>Type</TableHead><TableHead>Category</TableHead><TableHead>Source</TableHead><TableHead></TableHead></TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((d) => (
          <TableRow key={d.id} data-testid="admin-document-row">
            <TableCell className="max-w-xs truncate font-medium">{d.title}</TableCell>
            <TableCell><Badge variant="outline">{d.doc_type}</Badge></TableCell>
            <TableCell className="text-xs text-muted-foreground">{d.category}</TableCell>
            <TableCell><Badge variant="secondary">{d.source}</Badge></TableCell>
            <TableCell>
              <Button variant="ghost" size="icon" onClick={() => handleDelete(d.id)} data-testid="admin-delete-document-button">
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function LogsTab() {
  const [logs, , loading] = useAdminList('/admin/logs');
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!logs.length) return <EmptyState icon={ScrollText} title="No pipeline logs yet" />;
  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Stage</TableHead><TableHead>Query</TableHead><TableHead>Success</TableHead><TableHead>Duration (ms)</TableHead><TableHead>Time</TableHead></TableRow>
      </TableHeader>
      <TableBody>
        {logs.map((l, i) => (
          <TableRow key={i} data-testid="admin-log-row">
            <TableCell><Badge variant="outline">{l.stage}</Badge></TableCell>
            <TableCell className="max-w-[160px] truncate">{l.query}</TableCell>
            <TableCell>{l.success ? <CheckCircle2 className="h-4 w-4 text-success" /> : <AlertTriangle className="h-4 w-4 text-destructive" />}</TableCell>
            <TableCell className="font-mono tabular-nums">{l.duration_ms}</TableCell>
            <TableCell className="text-xs text-muted-foreground">{new Date(l.created_at).toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function ApiKeysTab() {
  const [status, setStatus] = useState(null);
  useEffect(() => { api.get('/admin/api-keys/status').then((res) => setStatus(res.data)); }, []);
  if (!status) return <Skeleton className="h-48 w-full rounded-xl" />;
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {Object.entries(status).map(([key, info]) => (
        <div key={key} className="rounded-xl border bg-card p-4" data-testid="admin-api-key-card">
          <div className="mb-2 flex items-center justify-between">
            <KeyRound className="h-4 w-4 text-primary" />
            {info.configured ? (
              <Badge className="gap-1 bg-success/10 text-success hover:bg-success/10"><CheckCircle2 className="h-3 w-3" /> Configured</Badge>
            ) : (
              <Badge variant="outline" className="gap-1 border-warning/30 text-warning"><AlertTriangle className="h-3 w-3" /> Missing</Badge>
            )}
          </div>
          <p className="font-display text-sm font-semibold capitalize">{key.replace(/_/g, ' ')}</p>
          <p className="mt-1 text-xs text-muted-foreground">{info.description}</p>
          <p className="mt-2 font-mono text-[10px] text-muted-foreground">ENV: {info.env_var}</p>
        </div>
      ))}
    </div>
  );
}

export default function Admin() {
  return (
    <div>
      <PageHeader title="Admin Panel" description="Manage users, taxonomy, catalog data and system health." />
      <Tabs defaultValue="users">
        <TabsList className="flex-wrap h-auto">
          <TabsTrigger value="users" data-testid="admin-tab-users"><Users className="h-3.5 w-3.5" /> Users</TabsTrigger>
          <TabsTrigger value="brands" data-testid="admin-tab-brands"><Tag className="h-3.5 w-3.5" /> Brands</TabsTrigger>
          <TabsTrigger value="categories" data-testid="admin-tab-categories"><Boxes className="h-3.5 w-3.5" /> Categories</TabsTrigger>
          <TabsTrigger value="products" data-testid="admin-tab-products"><Boxes className="h-3.5 w-3.5" /> Products</TabsTrigger>
          <TabsTrigger value="documents" data-testid="admin-tab-documents"><FileText className="h-3.5 w-3.5" /> Documents</TabsTrigger>
          <TabsTrigger value="logs" data-testid="admin-tab-logs"><ScrollText className="h-3.5 w-3.5" /> Logs</TabsTrigger>
          <TabsTrigger value="api-keys" data-testid="admin-tab-api-keys"><KeyRound className="h-3.5 w-3.5" /> API Keys</TabsTrigger>
        </TabsList>
        <TabsContent value="users" className="mt-4"><UsersTab /></TabsContent>
        <TabsContent value="brands" className="mt-4"><BrandsTab /></TabsContent>
        <TabsContent value="categories" className="mt-4"><CategoriesTab /></TabsContent>
        <TabsContent value="products" className="mt-4"><ProductsTab /></TabsContent>
        <TabsContent value="documents" className="mt-4"><DocumentsTab /></TabsContent>
        <TabsContent value="logs" className="mt-4"><LogsTab /></TabsContent>
        <TabsContent value="api-keys" className="mt-4"><ApiKeysTab /></TabsContent>
      </Tabs>
    </div>
  );
}
