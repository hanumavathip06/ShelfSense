import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';
import { updateReorderSettings, getReorderHistory } from '../lib/api';
import { toast } from 'react-hot-toast';
import { DataTable } from '../components/ui/DataTable';
import { Edit2, History } from 'lucide-react';
import { Modal } from '../components/ui/Modal';

export function ReorderSettings() {
  const queryClient = useQueryClient();
  const [editingPl, setEditingPl] = useState<any>(null);
  const [historyPl, setHistoryPl] = useState<any>(null);
  const [settings, setSettings] = useState({ reorder_threshold: 0, max_order_quantity: 0 });

  const { data: products, isLoading } = useQuery({
    queryKey: ['manager-inventory-locations'],
    queryFn: async () => {
      // Re-use products endpoint but maybe assume it includes product_locations info or fetch directly
      const res = await api.get('/products'); 
      return res.data.items; // Simplification: we might need a dedicated endpoint to get product locations
    }
  });

  const { data: history } = useQuery({
    queryKey: ['reorder-history', historyPl?.id],
    queryFn: () => getReorderHistory(historyPl?.id),
    enabled: !!historyPl
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => updateReorderSettings(id, data),
    onSuccess: () => {
      toast.success('Reorder settings updated');
      setEditingPl(null);
      queryClient.invalidateQueries({ queryKey: ['manager-inventory-locations'] });
    },
    onError: () => toast.error('Failed to update settings')
  });

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingPl) {
      updateMutation.mutate({ id: editingPl.id, data: settings }); // Uses product_location ID 
    }
  };

  const columns = [
    { header: 'Product ID', accessorKey: 'id' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'SKU', accessorKey: 'sku' },
    { header: 'Global Threshold', accessorKey: 'reorder_threshold' },
    { 
      header: 'Actions', 
      cell: (row: any) => (
        <div className="flex gap-2">
          <button 
            className="text-primary hover:text-accent"
            onClick={() => {
              setEditingPl(row); // Assuming row maps to a location for now
              setSettings({ 
                reorder_threshold: row.reorder_threshold || 0, 
                max_order_quantity: row.max_order_quantity || 0 
              });
            }}
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button 
            className="text-primary hover:text-accent"
            onClick={() => setHistoryPl(row)}
          >
            <History className="h-4 w-4" />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Reorder Settings</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>SKU Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={products || []} isLoading={isLoading} />
        </CardContent>
      </Card>

      <Modal isOpen={!!editingPl} onClose={() => setEditingPl(null)} title="Edit Settings">
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm text-secondary">Reorder Threshold</label>
            <input 
              type="number" 
              className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
              value={settings.reorder_threshold}
              onChange={e => setSettings({...settings, reorder_threshold: parseInt(e.target.value)})}
            />
          </div>
          <div>
            <label className="block text-sm text-secondary">Max Order Quantity</label>
            <input 
              type="number" 
              className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
              value={settings.max_order_quantity}
              onChange={e => setSettings({...settings, max_order_quantity: parseInt(e.target.value)})}
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <button type="button" onClick={() => setEditingPl(null)} className="px-4 py-2 border rounded">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-accent text-white rounded">Save</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={!!historyPl} onClose={() => setHistoryPl(null)} title="Change History">
        <div className="space-y-3">
          {history?.length === 0 ? <p className="text-sm text-secondary">No history found.</p> : null}
          {history?.map((log: any) => (
            <div key={log.id} className="text-sm p-3 border rounded bg-surface">
              <p className="font-semibold text-accent">{new Date(log.created_at).toLocaleString()}</p>
              <p className="text-secondary mt-1">User ID: {log.user_id}</p>
              <pre className="text-xs bg-background p-2 mt-2 overflow-auto">
                {JSON.stringify(log.details, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </Modal>
    </div>
  );
}
