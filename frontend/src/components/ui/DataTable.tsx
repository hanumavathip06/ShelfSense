import React from 'react';
import { twMerge } from 'tailwind-merge';

export function DataTable({ headers, children, className }: { headers: React.ReactNode[], children: React.ReactNode, className?: string }) {
  return (
    <div className={twMerge("w-full overflow-auto rounded-xl border border-border shadow-sm", className)}>
      <table className="w-full text-sm text-left">
        <thead className="bg-background text-secondary border-b border-border">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-6 py-3 font-bold text-[10px] uppercase tracking-widest">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {children}
        </tbody>
      </table>
    </div>
  );
}