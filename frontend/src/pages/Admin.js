import { useState, useEffect, useCallback, useRef } from 'react';
import api, { API, getErrorMessage } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription,
  AlertDialogFooter, AlertDialogCancel, AlertDialogAction,
} from '@/components/ui/alert-dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import {
  Users, Tag, Boxes, FileText, ScrollText, KeyRound, Trash2, Plus, Pencil, Search as SearchIcon,
  CheckCircle2, AlertTriangle, ShieldCheck, Sliders, UploadCloud, MoreVertical, Eye, Download,
  RefreshCw, History, FilesIcon, XCircle, Loader2, KeyRound as KeyIcon,
} from 'lucide-react';

function useAdminList(endpoint) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const load = useCallback(() => {
    setLoading(true);
    api.get(endpoint).then((res) => setData(res.data)).catch((e) => toast.error(getErrorMessage(e))).finally(() => setLoading(false));
  }, [endpoint]);
  useEffect(() => { load(); }, [load]);
  return [data, setData, loading, load];
}

function authFileUrl(docId, { download = false } = {}) {
  const token = localStorage.getItem('efuel_token');
  return `${API}/documents/${docId}/file?token=${encodeURIComponent(token || '')}${download ? '&download=true' : ''}`;
}

/* ===================================================================== USERS */

function UsersTab() {
  const [users, setUsers, loading, reload] = useAdminList('/admin/users');
  const [roles, setRoles] = useState([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'engineer' });
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => { api.get('/admin/roles').then((res) => setRoles(res.data)); }, []);

  const changeRole = async (id, role) => {
    try {
      await api.put(`/admin/users/${id}/role`, null, { params: { role } });
      setUsers((u) => u.map((x) => (x.id === id ? { ...x, role } : x)));
      toast.success('Role updated');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const toggleStatus = async (id, is_active) => {
    try {
      await api.put(`/admin/users/${id}/status`, null, { params: { is_active } });
      setUsers((u) => u.map((x) => (x.id === id ? { ...x, is_active } : x)));
      toast.success(is_active ? 'User activated' : 'User disabled');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const handleCreate = async () => {
    if (!form.name.trim() || !form.email.trim() || form.password.length < 6) {
      toast.error('Name, email and a password (min 6 chars) are required.');
      return;
    }
    setSaving(true);
    try {
      await api.post('/admin/users', form);
      toast.success('User created successfully');
      setCreateOpen(false);
      setForm({ name: '', email: '', password: '', role: 'engineer' });
      reload();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/admin/users/${deleteTarget.id}`);
      setUsers((u) => u.filter((x) => x.id !== deleteTarget.id));
      toast.success('User removed');
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setDeleteTarget(null); }
  };

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setCreateOpen(true)} data-testid="admin-create-user-button"><Plus className="h-4 w-4" /> New User</Button>
      </div>

      {loading ? <Skeleton className="h-64 w-full rounded-xl" /> : !users.length ? (
        <EmptyState icon={Users} title="No users found" />
      ) : (
        <Table>
          <TableHeader>
            <TableRow><TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Active</TableHead><TableHead></TableHead></TableRow>
          </TableHeader>
          <TableBody>
            {users.map((u) => (
              <TableRow key={u.id} data-testid="admin-user-row">
                <TableCell className="font-medium">{u.name}</TableCell>
                <TableCell className="text-xs text-muted-foreground">{u.email}</TableCell>
                <TableCell>
                  <Select value={u.role} onValueChange={(v) => changeRole(u.id, v)}>
                    <SelectTrigger className="w-40" data-testid="admin-user-role-select"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {(roles.length ? roles : [{ value: u.role, label: u.role }]).map((r) => (
                        <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </TableCell>
                <TableCell><Switch checked={u.is_active} onCheckedChange={(v) => toggleStatus(u.id, v)} data-testid="admin-user-active-switch" /></TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(u)} data-testid="admin-delete-user-button">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent data-testid="admin-create-user-dialog">
          <DialogHeader><DialogTitle>Create New User</DialogTitle><DialogDescription>Provision an internal team member account.</DialogDescription></DialogHeader>
          <div className="space-y-3">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="admin-user-name-input" /></div>
            <div><Label>Email</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} data-testid="admin-user-email-input" /></div>
            <div><Label>Password</Label><Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} data-testid="admin-user-password-input" /></div>
            <div>
              <Label>Role</Label>
              <Select value={form.role} onValueChange={(v) => setForm({ ...form, role: v })}>
                <SelectTrigger data-testid="admin-user-new-role-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {(roles.length ? roles : []).map((r) => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={saving} data-testid="admin-user-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Create User</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {deleteTarget?.name}?</AlertDialogTitle>
            <AlertDialogDescription>This permanently removes their account and login access. This cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="admin-confirm-delete-user-button">Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

/* ===================================================================== ROLES */

function RolesTab() {
  const [roles, , loading] = useAdminList('/admin/roles');
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {roles.map((r) => (
        <div key={r.value} className="rounded-xl border bg-card p-4" data-testid="admin-role-card">
          <div className="mb-2 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            <p className="font-display text-sm font-semibold">{r.label}</p>
          </div>
          <p className="text-sm text-muted-foreground">{r.description}</p>
        </div>
      ))}
    </div>
  );
}

/* ===================================================================== BRANDS */

function BrandsTab() {
  const [brands, setBrands, loading, reload] = useAdminList('/admin/brands');
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', website: '' });
  const [saving, setSaving] = useState(false);

  const handleDelete = async (name) => {
    try {
      await api.delete(`/admin/brands/${encodeURIComponent(name)}`);
      setBrands((b) => b.filter((x) => x.name !== name));
      toast.success('Brand removed');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const handleCreate = async () => {
    if (!form.name.trim()) { toast.error('Brand name is required'); return; }
    setSaving(true);
    try {
      await api.post('/admin/brands', form);
      toast.success('Brand added');
      setCreateOpen(false);
      setForm({ name: '', website: '' });
      reload();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setCreateOpen(true)} data-testid="admin-create-brand-button"><Plus className="h-4 w-4" /> New Brand</Button>
      </div>
      {loading ? <Skeleton className="h-64 w-full rounded-xl" /> : !brands.length ? (
        <EmptyState icon={Tag} title="No brands yet" description="Brands are auto-registered as products are researched, or add one manually." />
      ) : (
        <div className="flex flex-wrap gap-2">
          {brands.map((b) => (
            <Badge key={b.name} variant="secondary" className="gap-2 py-1.5 pl-3 pr-1.5 text-sm" data-testid="admin-brand-badge">
              {b.name}
              <button onClick={() => handleDelete(b.name)} className="rounded-full p-0.5 hover:bg-background/50" data-testid="admin-delete-brand-button"><Trash2 className="h-3 w-3" /></button>
            </Badge>
          ))}
        </div>
      )}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent data-testid="admin-create-brand-dialog">
          <DialogHeader><DialogTitle>Add Brand</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="admin-brand-name-input" /></div>
            <div><Label>Website</Label><Input value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} placeholder="https://..." data-testid="admin-brand-website-input" /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={saving} data-testid="admin-brand-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* ===================================================================== CATEGORIES */

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

/* ===================================================================== PRODUCTS */

function ProductsTab() {
  const [products, setProducts, loading, reload] = useAdminList('/admin/products');
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', brand: '', category: '', estimated_price_range: '', engineering_notes: '' });
  const [saving, setSaving] = useState(false);

  const handleDelete = async (id) => {
    await api.delete(`/admin/products/${id}`);
    setProducts((p) => p.filter((x) => x.id !== id));
    toast.success('Product removed');
  };

  const handleCreate = async () => {
    if (!form.name.trim() || !form.brand.trim()) { toast.error('Name and brand are required'); return; }
    setSaving(true);
    try {
      await api.post('/admin/products', form);
      toast.success('Product added');
      setCreateOpen(false);
      setForm({ name: '', brand: '', category: '', estimated_price_range: '', engineering_notes: '' });
      reload();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setCreateOpen(true)} data-testid="admin-create-product-button"><Plus className="h-4 w-4" /> New Product</Button>
      </div>
      {!products.length ? <EmptyState icon={Boxes} title="No products researched yet" /> : (
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
      )}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent data-testid="admin-create-product-dialog">
          <DialogHeader><DialogTitle>Add Product</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="admin-product-name-input" /></div>
            <div><Label>Brand</Label><Input value={form.brand} onChange={(e) => setForm({ ...form, brand: e.target.value })} data-testid="admin-product-brand-input" /></div>
            <div><Label>Category</Label><Input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
            <div><Label>Estimated Price Range (₹)</Label><Input value={form.estimated_price_range} onChange={(e) => setForm({ ...form, estimated_price_range: e.target.value })} placeholder="₹1,200 - ₹1,800" /></div>
            <div><Label>Engineering Notes</Label><Textarea value={form.engineering_notes} onChange={(e) => setForm({ ...form, engineering_notes: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={saving} data-testid="admin-product-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* ===================================================================== DOCUMENTS */

const DOC_TYPES = ['datasheet', 'catalogue', 'manual', 'certificate', 'reference'];

function UploadDocumentDialog({ open, onOpenChange, onUploaded }) {
  const [file, setFile] = useState(null);
  const [meta, setMeta] = useState({ title: '', doc_type: 'datasheet', category: '', brand: '', product_name: '' });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!file) { toast.error('Please select a PDF file'); return; }
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      Object.entries(meta).forEach(([k, v]) => fd.append(k, v));
      await api.post('/admin/documents/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success('Document uploaded successfully');
      onOpenChange(false);
      setFile(null);
      setMeta({ title: '', doc_type: 'datasheet', category: '', brand: '', product_name: '' });
      onUploaded();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="admin-upload-document-dialog">
        <DialogHeader><DialogTitle>Upload PDF Document</DialogTitle><DialogDescription>Max size 20MB. PDF files only.</DialogDescription></DialogHeader>
        <div className="space-y-3">
          <div>
            <Label>PDF File</Label>
            <Input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} data-testid="admin-document-file-input" />
          </div>
          <div><Label>Title</Label><Input value={meta.title} onChange={(e) => setMeta({ ...meta, title: e.target.value })} placeholder={file?.name || 'Document title'} data-testid="admin-document-title-input" /></div>
          <div>
            <Label>Type</Label>
            <Select value={meta.doc_type} onValueChange={(v) => setMeta({ ...meta, doc_type: v })}>
              <SelectTrigger data-testid="admin-document-type-select"><SelectValue /></SelectTrigger>
              <SelectContent>{DOC_TYPES.map((t) => <SelectItem key={t} value={t} className="capitalize">{t}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Brand</Label><Input value={meta.brand} onChange={(e) => setMeta({ ...meta, brand: e.target.value })} data-testid="admin-document-brand-input" /></div>
            <div><Label>Product</Label><Input value={meta.product_name} onChange={(e) => setMeta({ ...meta, product_name: e.target.value })} data-testid="admin-document-product-input" /></div>
          </div>
          <div><Label>Category</Label><Input value={meta.category} onChange={(e) => setMeta({ ...meta, category: e.target.value })} /></div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={saving} data-testid="admin-document-upload-submit">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Upload</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function BulkUploadDialog({ open, onOpenChange, onUploaded }) {
  const [files, setFiles] = useState([]);
  const [meta, setMeta] = useState({ doc_type: 'datasheet', category: '', brand: '', product_name: '' });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!files.length) { toast.error('Please select one or more PDF files'); return; }
    setSaving(true);
    try {
      const fd = new FormData();
      files.forEach((f) => fd.append('files', f));
      Object.entries(meta).forEach(([k, v]) => fd.append(k, v));
      const res = await api.post('/admin/documents/bulk-upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success(`Uploaded ${res.data.created.length} document(s)${res.data.errors.length ? `, ${res.data.errors.length} failed` : ''}`);
      onOpenChange(false);
      setFiles([]);
      onUploaded();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="admin-bulk-upload-dialog">
        <DialogHeader><DialogTitle>Bulk Upload PDFs</DialogTitle><DialogDescription>Shared metadata applies to all selected files.</DialogDescription></DialogHeader>
        <div className="space-y-3">
          <div>
            <Label>PDF Files</Label>
            <Input type="file" accept="application/pdf" multiple onChange={(e) => setFiles(Array.from(e.target.files || []))} data-testid="admin-bulk-file-input" />
            {files.length > 0 && <p className="mt-1 text-xs text-muted-foreground">{files.length} file(s) selected</p>}
          </div>
          <div>
            <Label>Type</Label>
            <Select value={meta.doc_type} onValueChange={(v) => setMeta({ ...meta, doc_type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{DOC_TYPES.map((t) => <SelectItem key={t} value={t} className="capitalize">{t}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Brand</Label><Input value={meta.brand} onChange={(e) => setMeta({ ...meta, brand: e.target.value })} /></div>
            <div><Label>Product</Label><Input value={meta.product_name} onChange={(e) => setMeta({ ...meta, product_name: e.target.value })} /></div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={saving} data-testid="admin-bulk-upload-submit">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Upload All</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function EditDocumentDialog({ doc, onOpenChange, onSaved }) {
  const [form, setForm] = useState(doc || {});
  const [saving, setSaving] = useState(false);
  useEffect(() => { setForm(doc || {}); }, [doc]);
  if (!doc) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put(`/admin/documents/${doc.id}`, {
        title: form.title, doc_type: form.doc_type, category: form.category, brand: form.brand, product_name: form.product_name,
      });
      toast.success('Metadata updated');
      onSaved();
      onOpenChange(false);
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  return (
    <Dialog open={!!doc} onOpenChange={onOpenChange}>
      <DialogContent data-testid="admin-edit-document-dialog">
        <DialogHeader><DialogTitle>Edit Document Metadata</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <div><Label>Title</Label><Input value={form.title || ''} onChange={(e) => setForm({ ...form, title: e.target.value })} data-testid="admin-edit-document-title-input" /></div>
          <div>
            <Label>Type</Label>
            <Select value={form.doc_type} onValueChange={(v) => setForm({ ...form, doc_type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{DOC_TYPES.map((t) => <SelectItem key={t} value={t} className="capitalize">{t}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Brand</Label><Input value={form.brand || ''} onChange={(e) => setForm({ ...form, brand: e.target.value })} /></div>
            <div><Label>Product</Label><Input value={form.product_name || ''} onChange={(e) => setForm({ ...form, product_name: e.target.value })} /></div>
          </div>
          <div><Label>Category</Label><Input value={form.category || ''} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSave} disabled={saving} data-testid="admin-edit-document-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DocumentsTab() {
  const [documents, setDocuments, loading, reload] = useAdminList('/admin/documents');
  const [selected, setSelected] = useState(new Set());
  const [uploadOpen, setUploadOpen] = useState(false);
  const [bulkOpen, setBulkOpen] = useState(false);
  const [editDoc, setEditDoc] = useState(null);
  const [previewDoc, setPreviewDoc] = useState(null);
  const [historyDoc, setHistoryDoc] = useState(null);
  const [bulkDeleteConfirm, setBulkDeleteConfirm] = useState(false);
  const replaceInputs = useRef({});

  const toggleSelect = (id) => setSelected((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });

  const handleDelete = async (id) => {
    try {
      await api.delete(`/admin/documents/${id}`);
      setDocuments((d) => d.filter((x) => x.id !== id));
      toast.success('Document deleted');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const handleBulkDelete = async () => {
    try {
      const ids = Array.from(selected);
      await api.post('/admin/documents/bulk-delete', ids);
      setDocuments((d) => d.filter((x) => !selected.has(x.id)));
      setSelected(new Set());
      toast.success(`${ids.length} document(s) deleted`);
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setBulkDeleteConfirm(false); }
  };

  const toggleActive = async (id, is_active) => {
    try {
      await api.put(`/admin/documents/${id}/status`, null, { params: { is_active } });
      setDocuments((d) => d.map((x) => (x.id === id ? { ...x, is_active } : x)));
      toast.success(is_active ? 'Document enabled' : 'Document disabled');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const handleReplace = async (id, file) => {
    if (!file) return;
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await api.post(`/admin/documents/${id}/replace`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success(`Replaced - now version ${res.data.version}`);
      reload();
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-end gap-2">
        {selected.size > 0 && (
          <Button variant="destructive" size="sm" onClick={() => setBulkDeleteConfirm(true)} data-testid="admin-bulk-delete-documents-button">
            <Trash2 className="h-3.5 w-3.5" /> Delete Selected ({selected.size})
          </Button>
        )}
        <Button variant="outline" onClick={() => setBulkOpen(true)} data-testid="admin-bulk-upload-button"><FilesIcon className="h-4 w-4" /> Bulk Upload</Button>
        <Button onClick={() => setUploadOpen(true)} data-testid="admin-upload-document-button"><UploadCloud className="h-4 w-4" /> Upload PDF</Button>
      </div>

      {!documents.length ? <EmptyState icon={FileText} title="No documents yet" description="Upload PDFs or research components to auto-discover datasheets." /> : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8"></TableHead>
              <TableHead>Title</TableHead><TableHead>Type</TableHead><TableHead>Brand / Product</TableHead>
              <TableHead>Version</TableHead><TableHead>Active</TableHead><TableHead>Source</TableHead><TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((d) => (
              <TableRow key={d.id} data-testid="admin-document-row">
                <TableCell><Checkbox checked={selected.has(d.id)} onCheckedChange={() => toggleSelect(d.id)} data-testid="admin-document-select-checkbox" /></TableCell>
                <TableCell className="max-w-xs truncate font-medium">{d.title}</TableCell>
                <TableCell><Badge variant="outline" className="capitalize">{d.doc_type}</Badge></TableCell>
                <TableCell className="text-xs text-muted-foreground">{[d.brand, d.product_name].filter(Boolean).join(' · ') || '—'}</TableCell>
                <TableCell>
                  {d.source === 'upload' ? (
                    <button onClick={() => setHistoryDoc(d)} className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline" data-testid="admin-document-version-button">
                      <History className="h-3 w-3" /> v{d.version || 1}
                    </button>
                  ) : <span className="text-xs text-muted-foreground">—</span>}
                </TableCell>
                <TableCell><Switch checked={d.is_active !== false} onCheckedChange={(v) => toggleActive(d.id, v)} data-testid="admin-document-active-switch" /></TableCell>
                <TableCell><Badge variant="secondary" className="capitalize">{d.source}</Badge></TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" data-testid="admin-document-actions-menu"><MoreVertical className="h-4 w-4" /></Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => setPreviewDoc(d)} data-testid="admin-document-preview-action"><Eye className="h-3.5 w-3.5" /> Preview</DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <a href={d.source === 'upload' ? authFileUrl(d.id, { download: true }) : d.url} target="_blank" rel="noopener noreferrer" data-testid="admin-document-download-action">
                          <Download className="h-3.5 w-3.5" /> Download
                        </a>
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setEditDoc(d)} data-testid="admin-document-edit-action"><Pencil className="h-3.5 w-3.5" /> Edit Metadata</DropdownMenuItem>
                      {d.source === 'upload' && (
                        <DropdownMenuItem onClick={() => replaceInputs.current[d.id]?.click()} data-testid="admin-document-replace-action">
                          <RefreshCw className="h-3.5 w-3.5" /> Replace PDF
                        </DropdownMenuItem>
                      )}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={() => handleDelete(d.id)} className="text-destructive focus:text-destructive" data-testid="admin-document-delete-action">
                        <Trash2 className="h-3.5 w-3.5" /> Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <input
                    type="file" accept="application/pdf" className="hidden"
                    ref={(el) => { replaceInputs.current[d.id] = el; }}
                    onChange={(e) => handleReplace(d.id, e.target.files?.[0])}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <UploadDocumentDialog open={uploadOpen} onOpenChange={setUploadOpen} onUploaded={reload} />
      <BulkUploadDialog open={bulkOpen} onOpenChange={setBulkOpen} onUploaded={reload} />
      <EditDocumentDialog doc={editDoc} onOpenChange={(o) => !o && setEditDoc(null)} onSaved={reload} />

      <Dialog open={!!previewDoc} onOpenChange={(o) => !o && setPreviewDoc(null)}>
        <DialogContent className="max-w-3xl" data-testid="admin-document-preview-dialog">
          <DialogHeader><DialogTitle>{previewDoc?.title}</DialogTitle></DialogHeader>
          {previewDoc && (
            <div className="h-[70vh] w-full overflow-hidden rounded-lg border bg-secondary/20">
              <iframe src={previewDoc.source === 'upload' ? authFileUrl(previewDoc.id) : previewDoc.url} title={previewDoc.title} className="h-full w-full" />
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={!!historyDoc} onOpenChange={(o) => !o && setHistoryDoc(null)}>
        <DialogContent data-testid="admin-document-history-dialog">
          <DialogHeader><DialogTitle>Version History - {historyDoc?.title}</DialogTitle></DialogHeader>
          <div className="space-y-2">
            {(historyDoc?.versions || []).slice().reverse().map((v) => (
              <div key={v.version} className="flex items-center justify-between rounded-lg border p-2.5 text-sm">
                <span className="font-medium">v{v.version} - {v.original_filename}</span>
                <span className="text-xs text-muted-foreground">{new Date(v.uploaded_at).toLocaleString('en-IN')}</span>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={bulkDeleteConfirm} onOpenChange={setBulkDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {selected.size} document(s)?</AlertDialogTitle>
            <AlertDialogDescription>This will remove them from all document libraries. This cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleBulkDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="admin-confirm-bulk-delete-button">Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

/* ===================================================================== SEARCH LOGS */

function SearchLogsTab() {
  const [logs, setLogs, loading, reload] = useAdminList('/admin/search-logs');
  const [clearConfirm, setClearConfirm] = useState(false);

  const handleClearAll = async () => {
    try {
      const res = await api.delete('/admin/search-logs');
      setLogs([]);
      toast.success(`Cleared ${res.data.deleted_count} search log entries`);
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setClearConfirm(false); }
  };

  const handleDeleteOne = async (id) => {
    await api.delete(`/admin/search-logs/${id}`);
    setLogs((l) => l.filter((x) => x.id !== id));
  };

  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button variant="destructive" size="sm" onClick={() => setClearConfirm(true)} disabled={!logs.length} data-testid="admin-clear-search-history-button">
          <XCircle className="h-3.5 w-3.5" /> Clear All Search History
        </Button>
      </div>
      {!logs.length ? <EmptyState icon={SearchIcon} title="No search history yet" /> : (
        <Table>
          <TableHeader><TableRow><TableHead>Query</TableHead><TableHead>Category</TableHead><TableHead>Top Product</TableHead><TableHead>Time</TableHead><TableHead></TableHead></TableRow></TableHeader>
          <TableBody>
            {logs.map((l) => (
              <TableRow key={l.id} data-testid="admin-search-log-row">
                <TableCell className="max-w-[220px] truncate font-medium">{l.query}</TableCell>
                <TableCell><Badge variant="outline">{l.category}</Badge></TableCell>
                <TableCell className="text-xs text-muted-foreground">{l.top_product || '—'}</TableCell>
                <TableCell className="text-xs text-muted-foreground">{new Date(l.created_at).toLocaleString('en-IN')}</TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon" onClick={() => handleDeleteOne(l.id)} data-testid="admin-delete-search-log-button">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      <AlertDialog open={clearConfirm} onOpenChange={setClearConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Clear all search history?</AlertDialogTitle>
            <AlertDialogDescription>This permanently deletes every user&apos;s search history entries. This cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleClearAll} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="admin-confirm-clear-search-history-button">Clear All</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

/* ===================================================================== AI LOGS */

function AiLogsTab() {
  const [logs, , loading] = useAdminList('/admin/logs');
  if (loading) return <Skeleton className="h-64 w-full rounded-xl" />;
  if (!logs.length) return <EmptyState icon={ScrollText} title="No AI pipeline logs yet" />;
  return (
    <Table>
      <TableHeader>
        <TableRow><TableHead>Stage</TableHead><TableHead>Query</TableHead><TableHead>Success</TableHead><TableHead>Duration (ms)</TableHead><TableHead>Time</TableHead></TableRow>
      </TableHeader>
      <TableBody>
        {logs.map((l, i) => (
          <TableRow key={i} data-testid="admin-ai-log-row">
            <TableCell><Badge variant="outline">{l.stage}</Badge></TableCell>
            <TableCell className="max-w-[160px] truncate">{l.query}</TableCell>
            <TableCell>{l.success ? <CheckCircle2 className="h-4 w-4 text-success" /> : <AlertTriangle className="h-4 w-4 text-destructive" />}</TableCell>
            <TableCell className="font-mono tabular-nums">{l.duration_ms}</TableCell>
            <TableCell className="text-xs text-muted-foreground">{new Date(l.created_at).toLocaleString('en-IN')}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/* ===================================================================== API INTEGRATIONS */

function UpdateKeyDialog({ provider, open, onOpenChange, onSaved }) {
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (apiKey.trim().length < 3) { toast.error('Please enter a valid API key'); return; }
    setSaving(true);
    try {
      await api.put(`/admin/integrations/${provider}/key`, { api_key: apiKey.trim(), enabled: true });
      toast.success('API key updated - live immediately, no restart needed');
      setApiKey('');
      onOpenChange(false);
      onSaved();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="admin-update-key-dialog">
        <DialogHeader><DialogTitle>Update API Key</DialogTitle><DialogDescription>Encrypted and stored securely. Takes effect immediately.</DialogDescription></DialogHeader>
        <Input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="Paste new API key" data-testid="admin-update-key-input" />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSave} disabled={saving} data-testid="admin-update-key-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Save Key</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function IntegrationsTab() {
  const [status, setStatus] = useState(null);
  const [keyDialogProvider, setKeyDialogProvider] = useState(null);
  const [testing, setTesting] = useState(null);

  const reload = useCallback(() => { api.get('/admin/integrations').then((res) => setStatus(res.data)); }, []);
  useEffect(() => { reload(); }, [reload]);

  const handleToggle = async (provider, enabled) => {
    try {
      await api.put(`/admin/integrations/${provider}/toggle`, { enabled });
      setStatus((s) => ({ ...s, [provider]: { ...s[provider], enabled } }));
      toast.success(enabled ? 'Integration enabled' : 'Integration disabled');
    } catch (e) { toast.error(getErrorMessage(e)); }
  };

  const handleTest = async (provider) => {
    setTesting(provider);
    try {
      const res = await api.post(`/admin/integrations/${provider}/test`);
      if (res.data.success) toast.success(res.data.message);
      else toast.error(res.data.message);
      reload();
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setTesting(null); }
  };

  if (!status) return <Skeleton className="h-48 w-full rounded-xl" />;

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {Object.entries(status).map(([key, info]) => (
        <div key={key} className="rounded-xl border bg-card p-4" data-testid="admin-integration-card">
          <div className="mb-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <KeyIcon className="h-4 w-4 text-primary" />
              <p className="font-display text-sm font-semibold">{info.label}</p>
            </div>
            <Switch checked={info.enabled} onCheckedChange={(v) => handleToggle(key, v)} data-testid="admin-integration-enabled-switch" />
          </div>
          {info.configured ? (
            <Badge className="gap-1 bg-success/10 text-success hover:bg-success/10"><CheckCircle2 className="h-3 w-3" /> Configured ({info.source})</Badge>
          ) : (
            <Badge variant="outline" className="gap-1 border-warning/30 text-warning"><AlertTriangle className="h-3 w-3" /> Not Configured</Badge>
          )}
          <div className="mt-3 space-y-1 text-xs text-muted-foreground">
            <p>Usage count: <span className="font-mono text-foreground">{info.usage_count}</span></p>
            <p>Last success: {info.last_success_at ? new Date(info.last_success_at).toLocaleString('en-IN') : 'Never'}</p>
            {info.last_error && <p className="text-destructive">Last error: {info.last_error}</p>}
          </div>
          <div className="mt-3 flex gap-2">
            <Button variant="outline" size="sm" onClick={() => handleTest(key)} disabled={testing === key} data-testid="admin-test-connection-button">
              {testing === key ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ShieldCheck className="h-3.5 w-3.5" />} Test Connection
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setKeyDialogProvider(key)} data-testid="admin-update-key-button">
              <KeyRound className="h-3.5 w-3.5" /> Update Key
            </Button>
          </div>
        </div>
      ))}
      <UpdateKeyDialog provider={keyDialogProvider} open={!!keyDialogProvider} onOpenChange={(o) => !o && setKeyDialogProvider(null)} onSaved={reload} />
    </div>
  );
}

/* ===================================================================== SYSTEM SETTINGS */

function SystemSettingsTab() {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => { api.get('/admin/settings').then((res) => setSettings(res.data)); }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.put('/admin/settings', settings);
      setSettings(res.data);
      toast.success('System settings saved');
    } catch (e) { toast.error(getErrorMessage(e)); } finally { setSaving(false); }
  };

  if (!settings) return <Skeleton className="h-48 w-full rounded-xl" />;

  return (
    <div className="max-w-lg space-y-4 rounded-xl border bg-card p-5">
      <div className="flex items-center gap-2"><Sliders className="h-4 w-4 text-primary" /><p className="font-display text-sm font-semibold">AI Provider Configuration</p></div>
      <p className="text-xs text-muted-foreground">
        Switch the AI model used for engineering analysis - all billed through the same Emergent LLM key.
        Takes effect on the very next request, no code changes or restart required.
      </p>
      <div>
        <Label>Provider</Label>
        <Select value={settings.llm_provider} onValueChange={(v) => setSettings({ ...settings, llm_provider: v })}>
          <SelectTrigger data-testid="admin-llm-provider-select"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="openai">OpenAI</SelectItem>
            <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
            <SelectItem value="gemini">Google (Gemini)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>Model</Label>
        <Input value={settings.llm_model} onChange={(e) => setSettings({ ...settings, llm_model: e.target.value })} placeholder="e.g. gpt-4o, claude-sonnet-4-5, gemini-2.5-pro" data-testid="admin-llm-model-input" />
      </div>
      <div>
        <Label>Research Rate Limit (requests/min per user)</Label>
        <Input type="number" min={1} value={settings.research_rate_limit_per_min} onChange={(e) => setSettings({ ...settings, research_rate_limit_per_min: parseInt(e.target.value, 10) || 1 })} data-testid="admin-rate-limit-input" />
      </div>
      <Button onClick={handleSave} disabled={saving} data-testid="admin-settings-save-button">{saving && <Loader2 className="h-4 w-4 animate-spin" />} Save Settings</Button>
    </div>
  );
}

/* ===================================================================== ROOT */

export default function Admin() {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === 'super_admin';

  return (
    <div>
      <PageHeader title="Admin Panel" description="Manage users, roles, taxonomy, catalog data, documents, integrations and system health." />
      <Tabs defaultValue={isSuperAdmin ? 'users' : 'brands'}>
        <TabsList className="flex-wrap h-auto">
          {isSuperAdmin && <TabsTrigger value="users" data-testid="admin-tab-users"><Users className="h-3.5 w-3.5" /> Users</TabsTrigger>}
          {isSuperAdmin && <TabsTrigger value="roles" data-testid="admin-tab-roles"><ShieldCheck className="h-3.5 w-3.5" /> Roles</TabsTrigger>}
          <TabsTrigger value="brands" data-testid="admin-tab-brands"><Tag className="h-3.5 w-3.5" /> Brands</TabsTrigger>
          <TabsTrigger value="categories" data-testid="admin-tab-categories"><Boxes className="h-3.5 w-3.5" /> Categories</TabsTrigger>
          <TabsTrigger value="products" data-testid="admin-tab-products"><Boxes className="h-3.5 w-3.5" /> Products</TabsTrigger>
          <TabsTrigger value="documents" data-testid="admin-tab-documents"><FileText className="h-3.5 w-3.5" /> Documents</TabsTrigger>
          <TabsTrigger value="search-logs" data-testid="admin-tab-search-logs"><SearchIcon className="h-3.5 w-3.5" /> Search Logs</TabsTrigger>
          <TabsTrigger value="ai-logs" data-testid="admin-tab-ai-logs"><ScrollText className="h-3.5 w-3.5" /> AI Logs</TabsTrigger>
          {isSuperAdmin && <TabsTrigger value="integrations" data-testid="admin-tab-integrations"><KeyRound className="h-3.5 w-3.5" /> API Integrations</TabsTrigger>}
          {isSuperAdmin && <TabsTrigger value="settings" data-testid="admin-tab-settings"><Sliders className="h-3.5 w-3.5" /> System Settings</TabsTrigger>}
        </TabsList>
        {isSuperAdmin && <TabsContent value="users" className="mt-4"><UsersTab /></TabsContent>}
        {isSuperAdmin && <TabsContent value="roles" className="mt-4"><RolesTab /></TabsContent>}
        <TabsContent value="brands" className="mt-4"><BrandsTab /></TabsContent>
        <TabsContent value="categories" className="mt-4"><CategoriesTab /></TabsContent>
        <TabsContent value="products" className="mt-4"><ProductsTab /></TabsContent>
        <TabsContent value="documents" className="mt-4"><DocumentsTab /></TabsContent>
        <TabsContent value="search-logs" className="mt-4"><SearchLogsTab /></TabsContent>
        <TabsContent value="ai-logs" className="mt-4"><AiLogsTab /></TabsContent>
        {isSuperAdmin && <TabsContent value="integrations" className="mt-4"><IntegrationsTab /></TabsContent>}
        {isSuperAdmin && <TabsContent value="settings" className="mt-4"><SystemSettingsTab /></TabsContent>}
      </Tabs>
    </div>
  );
}
