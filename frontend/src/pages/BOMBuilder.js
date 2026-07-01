import { useState, useEffect } from 'react';
import api, { getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { ClipboardList, Loader2, Sparkles, FileDown, Trash2 } from 'lucide-react';

export default function BOMBuilder() {
  const [projectName, setProjectName] = useState('');
  const [requirement, setRequirement] = useState('');
  const [loading, setLoading] = useState(false);
  const [current, setCurrent] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  const loadProjects = () => {
    setLoadingProjects(true);
    api.get('/bom/projects').then((res) => setProjects(res.data)).finally(() => setLoadingProjects(false));
  };

  useEffect(() => { loadProjects(); }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!projectName.trim() || !requirement.trim()) return;
    setLoading(true);
    setCurrent(null);
    try {
      const res = await api.post('/bom/generate', { project_name: projectName, requirement });
      setCurrent(res.data);
      loadProjects();
      toast.success('Bill of Materials generated');
    } catch (error) {
      toast.error(getErrorMessage(error, 'AI BOM generation failed.'));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (project, format) => {
    try {
      const res = await api.get(`/bom/projects/${project.id}/export/${format}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.project_name.replace(/\s+/g, '_')}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Export failed. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    await api.delete(`/bom/projects/${id}`);
    setProjects((p) => p.filter((x) => x.id !== id));
    if (current?.id === id) setCurrent(null);
    toast.success('BOM project deleted');
  };

  const renderBOM = (bom) => (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-display text-base font-semibold">{bom.project_name}</h3>
          <p className="text-xs text-muted-foreground">{bom.requirement}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport(bom, 'csv')} data-testid="bom-export-csv-button"><FileDown className="h-3.5 w-3.5" /> CSV</Button>
          <Button variant="outline" size="sm" onClick={() => handleExport(bom, 'xlsx')} data-testid="bom-export-xlsx-button"><FileDown className="h-3.5 w-3.5" /> Excel</Button>
          <Button variant="outline" size="sm" onClick={() => handleExport(bom, 'pdf')} data-testid="bom-export-pdf-button"><FileDown className="h-3.5 w-3.5" /> PDF</Button>
        </div>
      </div>
      <div className="overflow-x-auto rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Category</TableHead>
              <TableHead>Qty</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Specification</TableHead>
              <TableHead>Unit Cost</TableHead>
              <TableHead>Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {bom.components?.map((c, i) => (
              <TableRow key={i}>
                <TableCell className="font-medium">{c.category}</TableCell>
                <TableCell className="tabular-nums">{c.quantity}</TableCell>
                <TableCell>{c.recommended_brand}</TableCell>
                <TableCell className="font-mono text-xs">{c.recommended_model}</TableCell>
                <TableCell className="text-xs text-muted-foreground">{c.specification_requirement}</TableCell>
                <TableCell className="font-mono tabular-nums">{c.estimated_unit_cost}</TableCell>
                <TableCell className="font-mono tabular-nums">{c.estimated_total_cost}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="mt-4 flex flex-col gap-1">
        <p className="text-sm font-semibold">Estimated Total Cost: <span className="font-mono text-primary">{bom.estimated_total_cost}</span></p>
        <p className="text-sm text-muted-foreground">{bom.engineering_notes}</p>
      </div>
    </div>
  );

  return (
    <div>
      <PageHeader title="BOM Builder" description="Describe a requirement like 30kW EV Charger and let AI generate a full engineering Bill of Materials." />

      <form onSubmit={handleGenerate} className="mb-8 grid gap-3 rounded-xl border bg-card p-5 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
        <div className="space-y-1.5">
          <Label>Project Name</Label>
          <Input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="Site A - DC Fast Charger" data-testid="bom-project-name-input" />
        </div>
        <div className="space-y-1.5">
          <Label>Requirement</Label>
          <Input value={requirement} onChange={(e) => setRequirement(e.target.value)} placeholder="30kW EV Charger" data-testid="bom-requirement-input" />
        </div>
        <Button type="submit" disabled={loading} data-testid="bom-generate-button">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />} Generate BOM
        </Button>
      </form>

      {loading && <Skeleton className="h-96 w-full rounded-xl" />}

      {!loading && current && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          {renderBOM(current)}
        </motion.div>
      )}

      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Saved BOM Projects</h3>
      {loadingProjects ? (
        <Skeleton className="h-24 w-full rounded-xl" />
      ) : projects.length > 0 ? (
        <div className="space-y-2">
          {projects.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded-lg border bg-card p-3" data-testid="bom-project-item">
              <button className="text-left" onClick={() => setCurrent(p)}>
                <p className="text-sm font-semibold">{p.project_name}</p>
                <p className="text-xs text-muted-foreground">{p.requirement} · {p.components?.length || 0} components</p>
              </button>
              <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)} data-testid="bom-delete-project-button">
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState icon={ClipboardList} title="No BOM projects yet" description="Generate your first bill of materials above." />
      )}
    </div>
  );
}
