import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface Column<T = any> {
  header: React.ReactNode;
  accessorKey?: string;
  cell?: (row: T) => React.ReactNode;
}

export interface DataTableProps<T = any> {
  columns?: Column<T>[];
  data?: T[];
  isLoading?: boolean;
  headers?: React.ReactNode[];
  children?: React.ReactNode;
  className?: string;
  emptyMessage?: string;
}

export function DataTable<T = any>({
  columns,
  data,
  isLoading = false,
  headers,
  children,
  className,
  emptyMessage = "No records found.",
}: DataTableProps<T>) {
  const headerList: React.ReactNode[] = (
    Array.isArray(headers)
      ? headers
      : Array.isArray(columns)
      ? columns.map((c) => c?.header ?? '')
      : []
  );

  const safeData = Array.isArray(data) ? data : [];

  return (
    <div className={twMerge("w-full overflow-auto rounded-xl border border-border shadow-sm", className)}>
      <table className="w-full text-sm text-left">
        {headerList.length > 0 && (
          <thead className="bg-background text-secondary border-b border-border">
            <tr>
              {headerList.map((h, i) => (
                <th key={i} className="px-6 py-3 font-bold text-[10px] uppercase tracking-widest">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody className="divide-y divide-border bg-surface">
          {children ? (
            children
          ) : isLoading ? (
            Array.from({ length: 4 }).map((_, rIdx) => (
              <tr key={rIdx} className="animate-pulse">
                {headerList.length > 0 ? (
                  headerList.map((_, cIdx) => (
                    <td key={cIdx} className="px-6 py-4">
                      <div className="h-4 bg-border/50 rounded w-3/4" />
                    </td>
                  ))
                ) : (
                  <td className="px-6 py-4">
                    <div className="h-4 bg-border/50 rounded w-3/4" />
                  </td>
                )}
              </tr>
            ))
          ) : safeData.length === 0 ? (
            <tr>
              <td colSpan={Math.max(1, headerList.length)} className="px-6 py-12 text-center text-secondary">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            safeData.map((row, rIdx) => (
              <tr key={(row as any)?.id ?? rIdx} className="hover:bg-background/40 transition-colors">
                {columns?.map((col, cIdx) => (
                  <td key={cIdx} className="px-6 py-4 text-primary">
                    {col?.cell
                      ? col.cell(row)
                      : col?.accessorKey
                      ? (row as any)?.[col.accessorKey] ?? '—'
                      : null}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}