import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { getJobs, retryJob } from '../lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { DataTable } from '../components/ui/DataTable';

export function JobsMonitor() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-jobs'],
    queryFn: getJobs,
    refetchInterval: 5000
  });

  const retryMutation = useMutation({
    mutationFn: (id: number) => retryJob(id),
    onSuccess: () => {
      toast.success('Job retried');
      queryClient.invalidateQueries({ queryKey: ['admin-jobs'] });
    },
    onError: () => toast.error('Failed to retry job')
  });

  const columns = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Name', accessorKey: 'name' },
    { 
      header: 'Status', 
      cell: (row: any) => (
        <span className={`px-2 py-1 rounded text-xs font-bold ${
          row.status === 'failed' ? 'bg-danger/20 text-danger' : 
          row.status === 'completed' ? 'bg-success/20 text-success' : 
          'bg-secondary/20 text-secondary'
        }`}>
          {row.status.toUpperCase()}
        </span>
      ) 
    },
    { header: 'Last Run', cell: (row: any) => row.last_run_at ? new Date(row.last_run_at).toLocaleString() : 'Never' },
    { header: 'Error', accessorKey: 'error_message' },
    { 
      header: 'Actions', 
      cell: (row: any) => row.status === 'failed' ? (
        <button 
          onClick={() => retryMutation.mutate(row.id)}
          className="text-accent hover:underline text-sm font-semibold"
        >
          Retry
        </button>
      ) : null
    }
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Background Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={data || []} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
