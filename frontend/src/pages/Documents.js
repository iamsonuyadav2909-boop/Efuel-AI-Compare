import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { FileText, FileSpreadsheet, BookOpen, Award, Link as LinkIcon, Search, ExternalLink, Eye } from 'lucide-react';

const TYPE_ICON = { datasheet: FileText, catalogue: FileSpreadsheet, manual: BookOpen, certificate: Award, reference: LinkIcon };
const TYPE_LABEL = { datasheet: 'Datasheet', catalogue: 'Catalogue', manual: 'Manual', certificate: 'Certificate', reference: 'Reference' };

function fileUrl(d) {
  if (!d) return '#';
  // For uploaded documents, url is set to /api/documents/{id}/file by backend
  if (d.url && d.url.startsWith('/api/')) {
    const token = localStorage.getItem('efuel_token');
    return `${d.url}?token=${encodeURIComponent(token || '')}`;
  }
  // Fallback for documents without url
  return d.url || '#';
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [docType, setDocType] = useState('all');
  const [previewDoc, setPreviewDoc] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    api.get('/documents', { params: { q: q || undefined, doc_type: docType !== 'all' ? docType : undefined } })
      .then((res) => setDocuments(res.data))
      .finally(() => setLoading(false));
  }, [q, docType]);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <PageHeader
        title="Document Library"
        description="Datasheets, catalogues and manuals are automatically registered as the AI Research Engine discovers them from trusted manufacturer sources."
      />

      <div className="mb-6 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search documents..." className="pl-9" data-testid="documents-search-input" />
        </div>
        <Select value={docType} onValueChange={setDocType}>
          <SelectTrigger className="w-full sm:w-52" data-testid="documents-type-filter"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            <SelectItem value="datasheet">Datasheets</SelectItem>
            <SelectItem value="catalogue">Catalogues</SelectItem>
            <SelectItem value="manual">Manuals</SelectItem>
            <SelectItem value="certificate">Certificates</SelectItem>
            <SelectItem value="reference">Reference</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3, 4, 5, 6].map((i) => <Skeleton key={i} className="h-32 rounded-xl" />)}</div>
      ) : documents.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.map((d) => {
            const Icon = TYPE_ICON[d.doc_type] || LinkIcon;
            return (
              <div key={d.id} className="flex flex-col rounded-xl border bg-card p-4" data-testid="document-card">
                <div className="mb-3 flex items-start justify-between gap-2">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent text-primary"><Icon className="h-5 w-5" /></div>
                  <Badge variant="outline" className="text-[10px]">{TYPE_LABEL[d.doc_type] || d.doc_type}</Badge>
                </div>
                <p className="line-clamp-2 text-sm font-semibold">{d.title}</p>
                {d.category && <p className="mt-1 text-xs text-muted-foreground">{d.category}</p>}
                <div className="mt-auto flex gap-2 pt-3">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => setPreviewDoc(d)} data-testid="document-preview-button">
                    <Eye className="h-3.5 w-3.5" /> Preview
                  </Button>
                  <Button variant="secondary" size="sm" asChild data-testid="document-download-button">
                    <a href={fileUrl(d)} target="_blank" rel="noopener noreferrer"><ExternalLink className="h-3.5 w-3.5" /></a>
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState icon={FileText} title="No documents yet" description="Documents are automatically added as datasheets/catalogues are discovered during AI Search. Try researching a component first." />
      )}

      <Dialog open={!!previewDoc} onOpenChange={(o) => !o && setPreviewDoc(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader><DialogTitle>{previewDoc?.title}</DialogTitle></DialogHeader>
          {previewDoc && (
            <div className="h-[70vh] w-full overflow-hidden rounded-lg border bg-secondary/20">
              <iframe src={fileUrl(previewDoc)} title={previewDoc.title} className="h-full w-full" />
            </div>
          )}
          {previewDoc && (
            <p className="text-xs text-muted-foreground">
              If the preview doesn&apos;t load (some manufacturer sites block embedding),{' '}
              <a href={fileUrl(previewDoc)} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">open it in a new tab</a>.
            </p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
