import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';

export function SpecTable({ specifications = [] }) {
  if (!specifications.length) {
    return <p className="py-6 text-center text-sm text-muted-foreground">No specifications available.</p>;
  }
  return (
    <div className="overflow-hidden rounded-lg border">
      <Table data-testid="spec-table">
        <TableHeader>
          <TableRow>
            <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Specification</TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {specifications.map((s, i) => (
            <TableRow key={i}>
              <TableCell className="text-sm font-medium">{s.name}</TableCell>
              <TableCell className="font-mono text-sm tabular-nums">{s.value} {s.unit || ''}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
