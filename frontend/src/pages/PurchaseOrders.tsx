import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { useQuery } from '@tanstack/react-query';
import api from '../lib/axios'; // Direct call since we don't have it in lib/api.ts
import { DataTable } from '../components/ui/DataTable';

export function PurchaseOrders() {
  const [statusFilter, setStatusFilter] = useState('all');

  const { data: pos, isLoading } = useQuery({
    queryKey: ['manager-pos'],
    queryFn: async () => {
      const res = await api.get('/purchase-orders');
      return res.data;
    }
  });

  const filteredPos = pos?.filter((po: any) => statusFilter === 'all' || po.status === statusFilter) || [];

  const columns = [
    { header: 'PO #', accessorKey: 'id' },
    { header: 'Supplier', accessorKey: 'supplier_name' },
    { header: 'Total ($)', accessorKey: 'total_amount', cell: (row: any) => `$${row.total_amount?.toFixed(2)}` },
    { header: 'Created', accessorKey: 'created_at', cell: (row: any) => new Date(row.created_at).toLocaleDateString() },
    { 
      header: 'Status', 
      cell: (row: any) => (
        <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${
          row.status === 'approved' || row.status === 'fulfilled' ? 'bg-success/20 text-success' :
          row.status === 'rejected' || row.status === 'cancelled' ? 'bg-danger/20 text-danger' :
          'bg-accent/20 text-accent'
        }`}>
          {row.status.replace('_', ' ')}
        </span>
      )
    },
    { 
      header: 'Details', 
      cell: (row: any) => (
        <button 
          className="text-primary hover:text-accent underline text-sm"
          onClick={() => alert(`Showing details for PO #${row.id}\nStatus: ${row.status}\nManager cannot edit sent POs.`)}
        >
          View Details
        </button>
      )
    }
  ];

  return (
    <div className="space-y-6">

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Orders</CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-secondary font-medium">Filter by Status:</span>
            <select 
              className="bg-surface border border-border rounded-md px-3 py-1 text-sm text-primary outline-none"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All</option>
              <option value="draft">Draft</option>
              <option value="pending_approval">Pending Approval</option>
              <option value="approved">Approved</option>
              <option value="sent">Sent</option>
              <option value="partial">Partial</option>
              <option value="fulfilled">Fulfilled</option>
              <option value="rejected">Rejected</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={filteredPos} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
