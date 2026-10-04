import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuditLogs } from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { DataTable } from '../components/ui/DataTable';

export function AuditLog() {
  const [params, setParams] = useState({ days: 7, action: '', user_id: '' });

  const { data, isLoading } = useQuery({
    queryKey: ['admin-audit-logs', params],
    queryFn: () => getAuditLogs(params)
  });

  const columns = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Date', cell: (row: any) => new Date(row.created_at).toLocaleString() },
    { header: 'User ID', accessorKey: 'user_id' },
    { header: 'Action', accessorKey: 'action' },
    { header: 'Resource', accessorKey: 'target_resource' },
    { header: 'Details', accessorKey: 'details' },
  ];

  const handleExport = () => {
    if (!data) return;
    const csvRows = [
      ['ID', 'Date', 'User ID', 'Action', 'Resource', 'Details'],
      ...data.map((r: any) => [
        r.id, 
        r.created_at, 
        r.user_id, 
        r.action, 
        r.target_resource, 
        `"${(r.details || '').replace(/"/g, '""')}"`
      ])
    ];
    const csvContent = "data:text/csv;charset=utf-8," + csvRows.map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "audit_logs.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-serif text-primary">Audit Log</h1>
        <button 
          onClick={handleExport}
          className="px-4 py-2 bg-accent text-white rounded hover:bg-accent/90"
        >
          Export CSV
        </button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <input 
              type="number" 
              placeholder="Days ago (e.g. 7)"
              className="border border-border rounded px-3 py-2 bg-surface text-sm"
              value={params.days}
              onChange={e => setParams({...params, days: parseInt(e.target.value) || 0})}
            />
            <input 
              type="text" 
              placeholder="Action"
              className="border border-border rounded px-3 py-2 bg-surface text-sm"
              value={params.action}
              onChange={e => setParams({...params, action: e.target.value})}
            />
            <input 
              type="text" 
              placeholder="User ID"
              className="border border-border rounded px-3 py-2 bg-surface text-sm"
              value={params.user_id}
              onChange={e => setParams({...params, user_id: e.target.value})}
            />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="pt-6">
          <DataTable columns={columns} data={data || []} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
