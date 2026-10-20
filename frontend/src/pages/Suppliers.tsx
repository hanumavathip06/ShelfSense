import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSuppliers, updateSupplier } from '../lib/api';
import { toast } from 'react-hot-toast';
import { DataTable } from '../components/ui/DataTable';
import { useAuth } from '../contexts/AuthContext';
import { Check, X, Edit } from 'lucide-react';

export function Suppliers() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<any>({});
  
  const { data: suppliers, isLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: getSuppliers
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => updateSupplier(id, data),
    onSuccess: () => {
      toast.success('Supplier updated successfully');
      setEditingId(null);
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
    onError: () => toast.error('Failed to update supplier')
  });

  const handleSave = (id: number) => {
    updateMutation.mutate({ id, data: editForm });
  };

  const startEdit = (s: any) => {
    setEditingId(s.id);
    setEditForm({ ...s });
  };

  const columns = [
    { header: 'Name', cell: (row: any) => 
        editingId === row.id ? 
          <input className="bg-background border border-border p-1 text-sm rounded w-full" value={editForm.name} onChange={e => setEditForm({...editForm, name: e.target.value})} /> : 
          row.name 
    },
    { header: 'Email', cell: (row: any) => 
        editingId === row.id ? 
          <input className="bg-background border border-border p-1 text-sm rounded w-full" value={editForm.email} onChange={e => setEditForm({...editForm, email: e.target.value})} /> : 
          row.email 
    },
    { header: 'Contact Email', cell: (row: any) => 
        editingId === row.id ? 
          <input className="bg-background border border-border p-1 text-sm rounded w-full" value={editForm.contact_email || ''} onChange={e => setEditForm({...editForm, contact_email: e.target.value})} /> : 
          row.contact_email || '-' 
    },
    { header: 'Lead Time (Days)', cell: (row: any) => 
        editingId === row.id ? 
          <input type="number" className="bg-background border border-border p-1 text-sm rounded w-20" value={editForm.lead_time_days} onChange={e => setEditForm({...editForm, lead_time_days: parseInt(e.target.value)})} /> : 
          row.lead_time_days 
    },
    { header: 'MOQ', cell: (row: any) => 
        editingId === row.id ? 
          <input type="number" className="bg-background border border-border p-1 text-sm rounded w-20" value={editForm.moq} onChange={e => setEditForm({...editForm, moq: parseInt(e.target.value)})} /> : 
          row.moq 
    },
    { header: 'Pack Size', cell: (row: any) => 
        editingId === row.id ? 
          <input type="number" className="bg-background border border-border p-1 text-sm rounded w-20" value={editForm.pack_size} onChange={e => setEditForm({...editForm, pack_size: parseInt(e.target.value)})} /> : 
          row.pack_size 
    },
    { header: 'Trusted', cell: (row: any) => 
        editingId === row.id && user?.role === 'admin' ? 
          <input type="checkbox" checked={editForm.is_trusted} onChange={e => setEditForm({...editForm, is_trusted: e.target.checked})} /> : 
          (row.is_trusted ? <Check className="h-4 w-4 text-success" /> : <X className="h-4 w-4 text-secondary" />) 
    },
    { header: 'Auto Send', cell: (row: any) => 
        editingId === row.id && user?.role === 'admin' ? 
          <input type="checkbox" checked={editForm.auto_send_orders} onChange={e => setEditForm({...editForm, auto_send_orders: e.target.checked})} /> : 
          (row.auto_send_orders ? <Check className="h-4 w-4 text-success" /> : <X className="h-4 w-4 text-secondary" />) 
    },
    {
      header: 'Actions',
      cell: (row: any) => (
        editingId === row.id ? (
          <div className="flex gap-2">
            <Button size="sm" variant="success" onClick={() => handleSave(row.id)} disabled={updateMutation.isPending}>Save</Button>
            <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>Cancel</Button>
          </div>
        ) : (
          <Button size="sm" variant="outline" onClick={() => startEdit(row)}>
            <Edit className="h-4 w-4 mr-1" /> Edit
          </Button>
        )
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Suppliers</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Supplier Directory</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={suppliers || []} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
