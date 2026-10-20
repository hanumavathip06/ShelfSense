import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api from '../lib/axios';
import { Card, CardContent } from '../components/ui/Card';
import { DataTable } from '../components/ui/DataTable';
import { Modal } from '../components/ui/Modal';
import { Plus } from 'lucide-react';

export function StoresLocations() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['admin-locations'],
    queryFn: async () => (await api.get('/admin/locations')).data
  });

  const createMutation = useMutation({
    mutationFn: async (locationData: any) => (await api.post('/admin/locations', locationData)).data,
    onSuccess: () => {
      toast.success('Location created');
      queryClient.invalidateQueries({ queryKey: ['admin-locations'] });
      setIsModalOpen(false);
    },
    onError: () => toast.error('Failed to create location')
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    createMutation.mutate({
      name: formData.get('name'),
      address: formData.get('address'),
      type: formData.get('type')
    });
  };

  const columns = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'Address', accessorKey: 'address' },
    { header: 'Type', accessorKey: 'type' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-serif text-primary">Stores & Locations</h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-accent text-white rounded hover:bg-accent/90"
        >
          <Plus className="w-4 h-4" /> Add Location
        </button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable columns={columns} data={data || []} isLoading={isLoading} />
        </CardContent>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Location">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Name</label>
            <input name="name" required className="w-full bg-surface border rounded px-3 py-2 outline-none" />
          </div>
          <div>
            <label className="block text-sm mb-1">Address</label>
            <input name="address" className="w-full bg-surface border rounded px-3 py-2 outline-none" />
          </div>
          <div>
            <label className="block text-sm mb-1">Type</label>
            <select name="type" className="w-full bg-surface border rounded px-3 py-2 outline-none">
              <option value="store">Store</option>
              <option value="warehouse">Warehouse</option>
            </select>
          </div>
          <div className="flex justify-end pt-4">
            <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 bg-accent text-white rounded">
              Save
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
