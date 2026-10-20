import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getTeamActivity, assignTask, getUsers } from '../lib/api';
import { toast } from 'react-hot-toast';
import { Skeleton } from '../components/ui/Skeleton';

export function Team() {
  const [selectedUser, setSelectedUser] = useState('');
  const [taskType, setTaskType] = useState('cycle_count');
  const [taskDesc, setTaskDesc] = useState('');

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['team-activity'],
    queryFn: getTeamActivity
  });

  const { data: usersData } = useQuery({
    queryKey: ['staff-users'],
    queryFn: () => getUsers({ limit: 100 })
  });

  const staffUsers = usersData?.data?.filter((u: any) => u.role === 'staff') || [];

  const assignMutation = useMutation({
    mutationFn: assignTask,
    onSuccess: () => {
      toast.success('Task assigned successfully');
      setSelectedUser('');
      setTaskDesc('');
    },
    onError: () => toast.error('Failed to assign task')
  });

  const handleAssign = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) {
      toast.error('Please select a staff member');
      return;
    }
    assignMutation.mutate({
      user_id: parseInt(selectedUser),
      type: taskType,
      description: taskDesc
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-serif text-primary">Team Management</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Assign Task</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAssign} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Staff Member</label>
                <select 
                  className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                >
                  <option value="">Select Staff...</option>
                  {staffUsers.map((u: any) => (
                    <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Task Type</label>
                <select 
                  className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                >
                  <option value="cycle_count">Cycle Count</option>
                  <option value="receiving">Receiving</option>
                  <option value="picking">Picking</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-1">Task Description</label>
                <input 
                  type="text" 
                  className="w-full bg-surface border border-border rounded-md px-3 py-2 text-primary outline-none"
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                  placeholder="e.g. Aisle 4, Electronics"
                />
              </div>

              <Button type="submit" variant="primary" className="w-full" disabled={assignMutation.isPending}>
                {assignMutation.isPending ? 'Assigning...' : 'Assign Task'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Team Activity (Your Location)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activityLoading ? <Skeleton className="h-64" /> : 
                (!activity || activity.length === 0) ? (
                  <p className="text-secondary text-sm">No recent activity.</p>
                ) : (
                  activity.map((m: any) => (
                    <div key={`m-${m.id}`} className="text-sm p-3 bg-background rounded-lg border border-border flex justify-between">
                      <div>
                        <span className="font-semibold text-primary capitalize">{m.reason.replace('_', ' ')}</span>
                        <span className="text-secondary ml-2">User #{m.performed_by} &bull; Product #{m.product_id}</span>
                      </div>
                      <span className={`font-mono ${m.change_qty > 0 ? 'text-success' : 'text-danger'}`}>
                        {m.change_qty > 0 ? '+' : ''}{m.change_qty}
                      </span>
                    </div>
                  ))
                )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
